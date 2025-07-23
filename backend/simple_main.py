"""
Simple FastAPI app for testing deployment
"""
from fastapi import FastAPI
import os

app = FastAPI(title="Green PM API - Simple", version="1.0.0")

@app.get("/")
async def root():
    return {
        "message": "Green PM API - Simple Version",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "port": os.getenv("PORT", "8000")
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "unknown")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )