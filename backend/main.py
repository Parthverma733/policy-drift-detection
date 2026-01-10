"""Main FastAPI application for Policy Drift Detection."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from db.mongodb import mongodb_client
from api import policies, datasets, drift, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    await mongodb_client.connect()
    yield
    await mongodb_client.disconnect()


app = FastAPI(
    title="Policy Drift Detection API",
    description="NLP-Driven Detection of Policy–Implementation Drift",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(policies.router)
app.include_router(datasets.router)
app.include_router(drift.router)
app.include_router(chat.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "mongodb_connected": mongodb_client.connected
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
