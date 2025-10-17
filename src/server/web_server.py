"""
Simple HTTP server for the Game API
"""

import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from ..api.game_api import GameAPI
from ..core.config import NexusConfig
from ..core.logger import NexusLogger

class GameAPIHandler(BaseHTTPRequestHandler):
    """HTTP handler for Game API requests"""
    
    def __init__(self, *args, game_api: GameAPI = None, **kwargs):
        self.game_api = game_api
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            path_parts = self.path.split('?')
            path = path_parts[0]
            query_params = {}
            
            if len(path_parts) > 1:
                query_params = dict(urllib.parse.parse_qsl(path_parts[1]))
            
            if path == "/":
                self.serve_index()
            elif path == "/api/status":
                self.handle_status()
            elif path == "/api/leaderboard":
                category = query_params.get("category", "level")
                limit = int(query_params.get("limit", "10"))
                self.handle_leaderboard(category, limit)
            elif path == "/api/statistics":
                self.handle_statistics()
            elif path.startswith("/api/player/"):
                player_name = path.split("/")[-1]
                self.handle_get_player(player_name)
            else:
                self.send_error(404, "Not Found")
                
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 500)
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8')) if post_data else {}
            except json.JSONDecodeError:
                self.send_json_response({"success": False, "error": "Invalid JSON"}, 400)
                return
            
            path = self.path
            
            if path == "/api/player/create":
                self.handle_create_player(data)
            elif path == "/api/player/login":
                self.handle_login(data)
            elif path == "/api/player/logout":
                self.handle_logout(data)
            elif path == "/api/command/execute":
                self.handle_execute_command(data)
            elif path == "/api/mission/start":
                self.handle_start_mission(data)
            elif path == "/api/mission/abandon":
                self.handle_abandon_mission(data)
            elif path == "/api/hardware/upgrade":
                self.handle_upgrade_hardware(data)
            elif path == "/api/mining/start":
                self.handle_start_mining(data)
            elif path == "/api/mining/check":
                self.handle_check_mining(data)
            else:
                self.send_error(404, "Not Found")
                
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 500)
    
    def serve_index(self):
        """Serve index page"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Nexus Root MMORPG API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .endpoint { margin: 20px 0; padding: 10px; background: #f5f5f5; }
                .method { font-weight: bold; color: #0066cc; }
            </style>
        </head>
        <body>
            <h1>Nexus Root MMORPG API</h1>
            <p>Welcome to the Nexus Root MMORPG API server.</p>
            
            <h2>Available Endpoints:</h2>
            
            <div class="endpoint">
                <div class="method">GET /api/status</div>
                <div>Get server status</div>
            </div>
            
            <div class="endpoint">
                <div class="method">GET /api/statistics</div>
                <div>Get server statistics</div>
            </div>
            
            <div class="endpoint">
                <div class="method">GET /api/leaderboard?category=level&limit=10</div>
                <div>Get player leaderboard</div>
            </div>
            
            <div class="endpoint">
                <div class="method">GET /api/player/{name}</div>
                <div>Get player information</div>
            </div>
            
            <div class="endpoint">
                <div class="method">POST /api/player/create</div>
                <div>Create new player: {"name": "...", "is_vip": false}</div>
            </div>
            
            <div class="endpoint">
                <div class="method">POST /api/player/login</div>
                <div>Login player: {"name": "...", "session_id": "..."}</div>
            </div>
            
            <div class="endpoint">
                <div class="method">POST /api/command/execute</div>
                <div>Execute command: {"player_name": "...", "command": "..."}</div>
            </div>
            
            <div class="endpoint">
                <div class="method">POST /api/mission/start</div>
                <div>Start mission: {"player_name": "...", "mission_id": "..."}</div>
            </div>
            
            <div class="endpoint">
                <div class="method">POST /api/hardware/upgrade</div>
                <div>Upgrade hardware: {"player_name": "...", "component": "cpu|ram|nic|ssd"}</div>
            </div>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def handle_status(self):
        """Handle status request"""
        result = {"success": True, "status": "running", "message": "Nexus Root API Server"}
        self.send_json_response(result)
    
    def handle_statistics(self):
        """Handle statistics request"""
        result = self.game_api.get_server_statistics()
        self.send_json_response(result)
    
    def handle_leaderboard(self, category: str, limit: int):
        """Handle leaderboard request"""
        result = self.game_api.get_leaderboard(category, limit)
        self.send_json_response(result)
    
    def handle_get_player(self, player_name: str):
        """Handle get player request"""
        result = self.game_api.get_player_by_name(player_name)
        self.send_json_response(result)
    
    def handle_create_player(self, data: dict):
        """Handle create player request"""
        name = data.get("name")
        is_vip = data.get("is_vip", False)
        session_id = data.get("session_id")
        
        if not name:
            self.send_json_response({"success": False, "error": "Missing player name"}, 400)
            return
        
        result = self.game_api.create_player(name, is_vip, session_id)
        self.send_json_response(result)
    
    def handle_login(self, data: dict):
        """Handle login request"""
        name = data.get("name")
        session_id = data.get("session_id")
        
        if not name:
            self.send_json_response({"success": False, "error": "Missing player name"}, 400)
            return
        
        result = self.game_api.authenticate_player(name, session_id)
        self.send_json_response(result)
    
    def handle_logout(self, data: dict):
        """Handle logout request"""
        name = data.get("name")
        
        if not name:
            self.send_json_response({"success": False, "error": "Missing player name"}, 400)
            return
        
        result = self.game_api.logout_player(name)
        self.send_json_response(result)
    
    def handle_execute_command(self, data: dict):
        """Handle command execution request"""
        player_name = data.get("player_name")
        command = data.get("command")
        
        if not player_name or not command:
            self.send_json_response({"success": False, "error": "Missing player_name or command"}, 400)
            return
        
        result = self.game_api.execute_command(player_name, command)
        self.send_json_response(result)
    
    def handle_start_mission(self, data: dict):
        """Handle start mission request"""
        player_name = data.get("player_name")
        mission_id = data.get("mission_id")
        
        if not player_name or not mission_id:
            self.send_json_response({"success": False, "error": "Missing player_name or mission_id"}, 400)
            return
        
        result = self.game_api.start_mission(player_name, mission_id)
        self.send_json_response(result)
    
    def handle_abandon_mission(self, data: dict):
        """Handle abandon mission request"""
        player_name = data.get("player_name")
        mission_id = data.get("mission_id")
        
        if not player_name or not mission_id:
            self.send_json_response({"success": False, "error": "Missing player_name or mission_id"}, 400)
            return
        
        result = self.game_api.abandon_mission(player_name, mission_id)
        self.send_json_response(result)
    
    def handle_upgrade_hardware(self, data: dict):
        """Handle hardware upgrade request"""
        player_name = data.get("player_name")
        component = data.get("component")
        
        if not player_name or not component:
            self.send_json_response({"success": False, "error": "Missing player_name or component"}, 400)
            return
        
        result = self.game_api.upgrade_hardware(player_name, component)
        self.send_json_response(result)
    
    def handle_start_mining(self, data: dict):
        """Handle start mining request"""
        player_name = data.get("player_name")
        hours = data.get("hours", 1)
        
        if not player_name:
            self.send_json_response({"success": False, "error": "Missing player_name"}, 400)
            return
        
        result = self.game_api.start_passive_mining(player_name, hours)
        self.send_json_response(result)
    
    def handle_check_mining(self, data: dict):
        """Handle check mining request"""
        player_name = data.get("player_name")
        
        if not player_name:
            self.send_json_response({"success": False, "error": "Missing player_name"}, 400)
            return
        
        result = self.game_api.check_passive_mining(player_name)
        self.send_json_response(result)
    
    def send_json_response(self, data: dict, status_code: int = 200):
        """Send JSON response"""
        response_json = json.dumps(data, indent=2)
        
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        
        self.wfile.write(response_json.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def log_message(self, format, *args):
        """Override log message to use our logger"""
        logger = NexusLogger.get_logger("web_server")
        logger.info(f"{self.address_string()} - {format % args}")

class WebServer:
    """Web server for the Game API"""
    
    def __init__(self, config: NexusConfig):
        self.config = config
        self.logger = NexusLogger.get_logger("web_server")
        
        # Initialize Game API
        self.game_api = GameAPI(config)
        
        # Create handler class with game_api
        def handler_factory(*args, **kwargs):
            return GameAPIHandler(*args, game_api=self.game_api, **kwargs)
        
        self.handler_class = handler_factory
        
    def run(self):
        """Run the web server"""
        server_address = (self.config.server.host, self.config.server.port)
        
        try:
            httpd = HTTPServer(server_address, self.handler_class)
            
            self.logger.info(f"Starting server on {self.config.server.host}:{self.config.server.port}")
            print(f"Nexus Root API Server running on http://{self.config.server.host}:{self.config.server.port}")
            print("Press Ctrl+C to stop the server")
            
            httpd.serve_forever()
            
        except KeyboardInterrupt:
            self.logger.info("Server stopped by user")
            
        except Exception as e:
            self.logger.error(f"Server error: {str(e)}")
            raise
        
        finally:
            self.game_api.shutdown()
            self.logger.info("Server shutdown complete")