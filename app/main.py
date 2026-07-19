from fastapi import FastAPI
from typing import Dict

from app.routers import titles, users

app = FastAPI(title="MediaTracker API")

app.include_router(titles.router)
app.include_router(users.router)

@app.get("/")
def root() -> Dict:
    return {"message": "MediaTracker API is running"}