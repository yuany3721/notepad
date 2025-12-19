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
        await websocket.accept()
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
    print(f"WebSocket connection attempt for file: {filename}")
    try:
        await manager.connect(websocket, filename)
        print(f"WebSocket connected for file: {filename}")
    except Exception as e:
        print(f"WebSocket connection failed: {e}")
        await websocket.close(code=1006)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理保存请求
            if message.get("type") == "save":
                try:
                    content = message.get("content", "")
                    
                    # 检查内容是否为空
                    if not content or content.strip() == "":
                        # 删除空文件
                        if file_service.file_exists(filename):
                            file_service.delete_file(filename)
                            response = {
                                "type": "save_response",
                                "status": "success",
                                "message": "空文件已删除",
                                "timestamp": message.get("timestamp")
                            }
                        else:
                            response = {
                                "type": "save_response",
                                "status": "success",
                                "message": "文件不存在",
                                "timestamp": message.get("timestamp")
                            }
                    else:
                        # 保存非空文件
                        file_service.write_file(filename, content)
                        response = {
                            "type": "save_response",
                            "status": "success",
                            "message": "保存成功",
                            "timestamp": message.get("timestamp")
                        }
                except Exception as e:
                    # 发送失败响应
                    response = {
                        "type": "save_response", 
                        "status": "error",
                        "message": str(e),
                        "timestamp": message.get("timestamp")
                    }
                
                await manager.send_message(response, filename)
            
    except WebSocketDisconnect:
        manager.disconnect(filename)
    except Exception as e:
        # 发送错误响应
        error_response = {
            "type": "error",
            "message": str(e)
        }
        await manager.send_message(error_response, filename)
        manager.disconnect(filename)