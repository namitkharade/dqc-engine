# DQC Mini Engine

A small data-quality validation service built to show how I approach a backend project end to end: clear API contract, deterministic validation rules, batch processing, and one place where a smarter fix suggestion can be plugged in.

## What it does

- Accepts individual or batched data records over a typed REST API.
- Runs rule-based validation on email, phone, price, country, and name fields.
- Persists detected issues to SQLite and returns structured results.
- Supports async batch validation for up to 100 records at once.
- Ships one OpenAI-backed endpoint that suggests a concrete fix for a given validation issue.

## Why this project exists

It is a compact example of how I like to build: start with the API shape and the data model, keep the validation logic testable and isolated, and leave a clean swap point for heavier intelligence later instead of hardcoding it into the core flow.

## Tech stack

- Python, FastAPI, Pydantic, SQLAlchemy
- SQLite for local persistence
- OpenAI Responses API for the suggestion endpoint
- Environment-based configuration via `.env`

## Project structure

```text
dqc-engine/
├── main.py            # Application entrypoint and router wiring
├── database.py        # SQLite setup and issue model
├── models.py          # Request/response models and severity enum
├── validator.py       # Deterministic validation rules
├── routes/
│   └── validation.py  # Validation, batch, issues, and suggestion endpoints
├── middleware/
│   └── logging.py     # Request logging middleware
├── requirements.txt
└── README.md
```

## Endpoints

- `POST /api/v1/validate` — validate a single record
- `POST /api/v1/validate/batch` — validate up to 100 records concurrently
- `GET /api/v1/issues` — list persisted issues, optionally filtered by severity
- `POST /api/v1/suggest` — ask for one fix suggestion for a validation issue

## Running locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# edit .env and set OPENAI_API_KEY=sk-...
python main.py
```

## Repository

https://github.com/namitkharade/dqc-engine

## Note

This is a code-sample project included as part of a job application. The core validation logic is deterministic and self-contained. The OpenAI suggestion endpoint is an optional feature and requires an API key in `.env`.
