from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from src.api import notes, files, websocket
from src.utils.config import get_settings

settings = get_settings()
app = FastAPI(title=f"{settings.app_name} API", description="NOTEPAD API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=(
        settings.allow_origin_regex
        if settings.allow_origin_regex
        else r"http[s]?://localhost:5173|http[s]?://127\.0\.0\.1:5173|http[s]?://172\.30\.0\..*:5173|ws[s]?://localhost:5173|ws[s]?://127\.0\.0\.1:5173"
    ),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(notes.router, prefix="/notepad", tags=["notes"])
app.include_router(files.router, prefix="/notepad", tags=["files"])
app.include_router(websocket.router, prefix="/notepad/ws", tags=["websocket"])


@app.get("/notepad/health")
async def health_check():
    return {"status": "healthy"}


if os.path.exists("./static"):
    app.mount("/", StaticFiles(directory="./static", html=True), name="static")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7024))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True, log_level="info")
