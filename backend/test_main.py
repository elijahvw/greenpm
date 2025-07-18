"""
Simple test version of the API
"""
from fastapi import FastAPI
import os

app = FastAPI(title="Green PM Test", version="1.0.0")

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "port": os.getenv("PORT", "8000")
    }

@app.get("/")
async def root():
    return {"message": "Green PM API is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)