"""
WebSocket server for real-time communication.
"""

import asyncio
import websockets
import json
from ..api.game_api import GameAPI

class WebSocketServer:
    """
    Manages the WebSocket server and client connections.
    """
    def __init__(self, host: str, port: int, game_api: GameAPI):
        self.host = host
        self.port = port
        self.game_api = game_api
        self.server = None

    async def handler(self, websocket, path):
        """
        Handles incoming WebSocket connections and messages.
        """
        print(f"Client connected: {websocket.remote_address}")
        try:
            async for message in websocket:
                data = json.loads(message)
                if data["event"] == "EXECUTE_COMMAND":
                    player_name = "test_user"  # This should be dynamic
                    result = await self.game_api.execute_command(player_name, data["payload"])
                    await websocket.send(json.dumps({
                        "event": "COMMAND_RESPONSE",
                        "payload": result["output"] if result["success"] else result["error"]
                    }))
        except websockets.exceptions.ConnectionClosed:
            print(f"Client disconnected: {websocket.remote_address}")

    async def start(self):
        """
        Starts the WebSocket server.
        """
        self.server = await websockets.serve(self.handler, self.host, self.port)
        print(f"WebSocket server started on {self.host}:{self.port}")

    async def stop(self):
        """
        Stops the WebSocket server.
        """
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("WebSocket server stopped.")
