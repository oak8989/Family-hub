from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, family_id: str):
        await websocket.accept()
        if family_id not in self.active_connections:
            self.active_connections[family_id] = []
        self.active_connections[family_id].append(websocket)

    def disconnect(self, websocket: WebSocket, family_id: str):
        if family_id in self.active_connections:
            self.active_connections[family_id] = [
                ws for ws in self.active_connections[family_id] if ws != websocket
            ]
            if not self.active_connections[family_id]:
                del self.active_connections[family_id]

    async def broadcast(self, family_id: str, message: dict):
        if family_id not in self.active_connections:
            return
        dead = []
        for ws in self.active_connections[family_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active_connections[family_id].remove(ws)


manager = ConnectionManager()


@router.websocket("/api/ws/{family_id}")
async def websocket_endpoint(websocket: WebSocket, family_id: str):
    await manager.connect(websocket, family_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, family_id)
    except Exception:
        manager.disconnect(websocket, family_id)


async def notify_family(family_id: str, event_type: str, module: str, data: dict = None):
    await manager.broadcast(family_id, {
        "type": event_type,
        "module": module,
        "data": data or {}
    })
