from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json
import asyncio
from ..services.file_service import FileService

router = APIRouter()
file_service = FileService()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, filename: str):
        self.active_connections[filename] = websocket

    def disconnect(self, filename: str):
        if filename in self.active_connections:
            del self.active_connections[filename]

    async def send_message(self, message: dict, filename: str):
        if filename in self.active_connections:
            websocket = self.active_connections[filename]
            try:
                await websocket.send_text(json.dumps(message))
            except:
                # 连接已断开，清理
                self.disconnect(filename)


manager = ConnectionManager()


@router.websocket("/{filename}")
async def websocket_endpoint(websocket: WebSocket, filename: str):
    # print(f"WebSocket connection attempt for file: {filename}")
    # print(f"WebSocket headers: {websocket.headers}")
    try:
        await websocket.accept()
        await manager.connect(websocket, filename)
        # print(f"WebSocket connected for file: {filename}")
    except Exception as e:
        # print(f"WebSocket connection failed: {e}")
        # print(f"Exception type: {type(e)}")
        try:
            await websocket.close(code=1006)
        except:
            pass
        return

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "save":
                try:
                    content = message.get("content", "")

                    if not content or content.strip() == "":
                        if file_service.file_exists(filename):
                            file_service.delete_file(filename)
                            response = {
                                "type": "save_response",
                                "status": "success",
                                "message": "空文件已删除",
                                "timestamp": message.get("timestamp"),
                            }
                        else:
                            response = {
                                "type": "save_response",
                                "status": "success",
                                "message": "文件不存在",
                                "timestamp": message.get("timestamp"),
                            }
                    else:
                        file_service.write_file(filename, content)
                        response = {
                            "type": "save_response",
                            "status": "success",
                            "message": "保存成功",
                            "timestamp": message.get("timestamp"),
                        }
                except Exception as e:
                    response = {
                        "type": "save_response",
                        "status": "error",
                        "message": str(e),
                        "timestamp": message.get("timestamp"),
                    }

                await manager.send_message(response, filename)

    except WebSocketDisconnect:
        manager.disconnect(filename)
    except Exception as e:
        error_response = {"type": "error", "message": str(e)}
        await manager.send_message(error_response, filename)
        manager.disconnect(filename)
