from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from src.api import notes, files, websocket
from src.utils.config import get_settings

app = FastAPI(
    title="Vue3 + Python Notepad API",
    description="简单的文本编辑器API，支持文件读写和列表功能",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "ws://localhost:5173"],  # Vue开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(notes.router, prefix="/api", tags=["notes"])
app.include_router(files.router, prefix="/api", tags=["files"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

# 静态文件服务（用于生产环境）
if os.path.exists("./static"):
    app.mount("/", StaticFiles(directory="./static", html=True), name="static")

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )