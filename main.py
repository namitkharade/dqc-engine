from __future__ import annotations

from contextlib import asynccontextmanager

from database import create_tables
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middleware.logging import RequestLoggingMiddleware
from routes.validation import router as validation_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="DQC Mini Engine",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(validation_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "DQC Mini Engine",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/v1"
    }


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000)
