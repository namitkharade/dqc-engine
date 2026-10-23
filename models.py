from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DataRecord(BaseModel):
    id: int | str | None = None
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    price: float | None = None
    country: str | None = None


class DataIssue(BaseModel):
    field: str
    issue_type: str
    severity: SeverityLevel
    suggested_fix: str


class ValidationResult(BaseModel):
    record_id: str | None
    issues: list[DataIssue]
    is_valid: bool


class BatchValidationResult(BaseModel):
    total: int
    valid_count: int
    invalid_count: int
    results: list[ValidationResult]
