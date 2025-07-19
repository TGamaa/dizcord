# main.py
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from database import init_db, add_message, get_messages

app = FastAPI()

# Mount the 'static' directory to serve HTML, CSS, and JS files
app.mount("/static", StaticFiles(directory="static"), name="static")

class ConnectionManager:
    """Manages active WebSocket connections."""
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize the database on application startup."""
    init_db()

@app.get("/")
async def get():
    """Serves the main HTML file."""
    with open("static/index.html") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time chat."""
    await manager.connect(websocket)
    try:
        # Send existing messages to the newly connected client
        history = get_messages()
        for username, message, timestamp in history:
            await websocket.send_text(json.dumps({
                "username": username,
                "message": message,
                "timestamp": timestamp
            }))

        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            username = message_data['username']
            message = message_data['message']
            
            # Add message to the database
            add_message(username, message)

            # Broadcast the new message to all connected clients
            await manager.broadcast(json.dumps({
                "username": username,
                "message": message,
                "timestamp": "now" # Or generate a proper timestamp
            }))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(json.dumps({"username": "System", "message": f"{client_id} has left the chat"}))