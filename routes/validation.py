from __future__ import annotations

import asyncio
import os

from database import Issue, get_db
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from models import (BatchValidationResult, DataIssue, DataRecord,
                    SeverityLevel, ValidationResult)
from pydantic import BaseModel
from sqlalchemy.orm import Session
from validator import validate_record

router = APIRouter(tags=["validation"])

load_dotenv()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


class SuggestRequest(BaseModel):
    field: str
    bad_value: str
    issue_type: str


class SuggestResponse(BaseModel):
    suggestion: str
    confidence: float
    source: str


def _openai_suggestion(payload: SuggestRequest) -> SuggestResponse:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not set. Add it to the .env file.",
        )

    # Imported here so the service still starts when the optional SDK is
    # missing and only /suggest is affected.
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a data quality assistant. Return a short, actionable fix suggestion "
                        "for the given field validation issue."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Field: {payload.field}\n"
                        f"Bad value: {payload.bad_value}\n"
                        f"Issue type: {payload.issue_type}\n"
                        "Provide one concise correction suggestion."
                    ),
                },
            ],
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI request failed: {exc}") from exc

    suggestion_text = (response.output_text or "").strip()
    if not suggestion_text:
        suggestion_text = (
            f"Replace '{payload.bad_value}' in '{payload.field}' with a value that satisfies "
            f"'{payload.issue_type}'."
        )

    return SuggestResponse(suggestion=suggestion_text, confidence=0.85, source="llm")


# One-line swap point: replace this provider with another LLM integration if needed.
_suggestion_provider = _openai_suggestion


@router.post("/validate", response_model=ValidationResult)
def validate_data(record: DataRecord, db: Session = Depends(get_db)) -> ValidationResult:
    """Validate a data record, persist detected issues, and return validation details."""
    issues = validate_record(record)
    record_id_str = str(record.id) if record.id is not None else None

    for issue in issues:
        db_issue = Issue(
            record_id=record_id_str,
            field=issue.field,
            issue_type=issue.issue_type,
            severity=issue.severity.value,
            suggested_fix=issue.suggested_fix,
        )
        db.add(db_issue)

    db.commit()

    return ValidationResult(
        record_id=record_id_str,
        issues=issues,
        is_valid=len(issues) == 0,
    )


async def _validate_record_async(record: DataRecord) -> ValidationResult:
    """Async wrapper for validate_record that handles exceptions gracefully."""
    record_id_str = str(record.id) if record.id is not None else None
    try:
        issues = validate_record(record)
        return ValidationResult(
            record_id=record_id_str,
            issues=issues,
            is_valid=len(issues) == 0,
        )
    except Exception as exc:
        # Return result with system_error issue instead of failing the whole batch
        system_error_issue = DataIssue(
            field="_system",
            issue_type="system_error",
            severity=SeverityLevel.HIGH,
            suggested_fix=f"System error during validation: {str(exc)}",
        )
        return ValidationResult(
            record_id=record_id_str,
            issues=[system_error_issue],
            is_valid=False,
        )


@router.post("/validate/batch", response_model=BatchValidationResult)
async def validate_batch(
    records: list[DataRecord], db: Session = Depends(get_db)
) -> BatchValidationResult:
    """Validate multiple data records in parallel, persist detected issues, and return batch results.
    
    - Accepts up to 100 data records
    - Validates all records concurrently using asyncio.gather
    - Returns total count, valid count, invalid count, and detailed results
    - Gracefully handles validation errors by returning system_error issues
    """
    # Enforce max 100 records per batch
    if len(records) > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 records allowed per batch request.",
        )
    
    if not records:
        return BatchValidationResult(total=0, valid_count=0, invalid_count=0, results=[])
    
    # Validate all records in parallel
    validation_results = await asyncio.gather(
        *[_validate_record_async(record) for record in records]
    )
    
    # Persist all issues to database
    for validation_result in validation_results:
        for issue in validation_result.issues:
            db_issue = Issue(
                record_id=validation_result.record_id,
                field=issue.field,
                issue_type=issue.issue_type,
                severity=issue.severity.value,
                suggested_fix=issue.suggested_fix,
            )
            db.add(db_issue)
    
    db.commit()
    
    # Calculate statistics
    valid_count = sum(1 for result in validation_results if result.is_valid)
    invalid_count = len(validation_results) - valid_count
    
    return BatchValidationResult(
        total=len(validation_results),
        valid_count=valid_count,
        invalid_count=invalid_count,
        results=validation_results,
    )


@router.get("/issues", response_model=list[DataIssue])
def list_issues(
    severity: SeverityLevel | None = None,
    db: Session = Depends(get_db),
) -> list[DataIssue]:
    """Return stored issues, optionally filtered by severity."""
    query = db.query(Issue)
    if severity is not None:
        query = query.filter(Issue.severity == severity.value)

    rows = query.all()
    return [
        DataIssue(
            field=row.field,
            issue_type=row.issue_type,
            severity=row.severity,
            suggested_fix=row.suggested_fix,
        )
        for row in rows
    ]


@router.post("/suggest", response_model=SuggestResponse)
def suggest_fix(payload: SuggestRequest) -> SuggestResponse:
    """Generate a fix suggestion for a validation issue using the configured LLM provider."""
    return _suggestion_provider(payload)
