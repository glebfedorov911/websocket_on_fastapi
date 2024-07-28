from fastapi import WebSocket, APIRouter, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates


router = APIRouter(prefix="/websocket", tags=["WebSocket"])

templates = Jinja2Templates(directory="templates")

class ConnectionManager:
    def __init__(self):
        self.active_connection: list[WebSocket] = []

    async def activate(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connection.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connection.remove(websocket)

    async def show_message(self, data: str):
        for conn in self.active_connection:
            await conn.send_text(data)

manager = ConnectionManager()

@router.get("/")
async def get(request: Request):
    return templates.TemplateResponse(
        request=request, name="websocket.html"
    )

@router.websocket("/ws/{id}")
async def websocket_endpoint(id: int, websocket: WebSocket):
    await manager.show_message(f"{id} присоединился к чату")
    await manager.activate(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            await manager.show_message(f"{id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.show_message(f"{id} покинул чат")