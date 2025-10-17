"""
Simple HTTP server for the Game API
"""

import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from ..api.game_api import GameAPI
from ..api.admin_api import AdminAPI
from ..api.auth_api import AuthAPI
from ..services.auth_service import AuthService
from ..services.admin_service import AdminService
from ..services.admin_auth_service import AdminAuthService
from ..core.config import NexusConfig
from ..core.logger import NexusLogger

class CustomAPIHandler(BaseHTTPRequestHandler):
    """HTTP handler for Game API requests"""
    
    def __init__(self, *args, game_api: GameAPI = None, admin_api: AdminAPI = None, admin_auth_service: AdminAuthService = None, auth_api: AuthAPI = None, **kwargs):
        self.game_api = game_api
        self.admin_api = admin_api
        self.admin_auth_service = admin_auth_service
        self.auth_api = auth_api
        super().__init__(*args, **kwargs)
    
    def is_admin_authenticated(self):
        """Check if the request is from an authenticated admin"""
        auth_header = self.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return False

        token = auth_header.split(" ")[1]
        return self.admin_auth_service.is_authenticated(token)

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
            elif path == "/admin":
                self.serve_admin_panel()
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
            elif path == "/api/announcement":
                self.handle_get_announcement()
            elif path == "/admin/api/login":
                self.handle_admin_login(data)
            elif path == "/admin/api/players":
                if not self.is_admin_authenticated():
                    self.send_error(401, "Unauthorized")
                    return
                search = query_params.get("search")
                sort = query_params.get("sort", "name")
                order = query_params.get("order", "asc")
                self.handle_get_all_players(search, sort, order)
            elif path == "/admin/api/banned-players":
                if not self.is_admin_authenticated():
                    self.send_error(401, "Unauthorized")
                    return
                self.handle_get_banned_players()
            else:
                self.send_error(404, "Not Found")
                
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 500)
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            content_type = self.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                try:
                    data = json.loads(post_data.decode('utf-8')) if post_data else {}
                except json.JSONDecodeError:
                    self.send_json_response({"success": False, "error": "Invalid JSON"}, 400)
                    return
            elif 'application/x-www-form-urlencoded' in content_type:
                data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            else:
                data = {}
            
            path = self.path
            
            if path == "/api/register":
                self.handle_register(data)
            elif path == "/api/login":
                self.handle_login(data)
            elif path == "/api/player/create":
                self.handle_create_player(data)
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
            elif path.startswith("/admin/api/players/"):
                if not self.is_admin_authenticated():
                    self.send_error(401, "Unauthorized")
                    return
                parts = path.split("/")
                player_id = parts[-2]
                action = parts[-1]
                if action == "ban":
                    self.handle_ban_player(player_id)
                elif action == "unban":
                    self.handle_unban_player(player_id)
                else:
                    self.send_error(404, "Not Found")
            elif path == "/admin/api/announcement":
                if not self.is_admin_authenticated():
                    self.send_error(401, "Unauthorized")
                    return
                self.handle_send_announcement(data)
            elif path == "/admin/api/ips/ban":
                if not self.is_admin_authenticated():
                    self.send_error(401, "Unauthorized")
                    return
                self.handle_ban_ip(data)
            elif path == "/admin/api/ips/unban":
                if not self.is_admin_authenticated():
                    self.send_error(401, "Unauthorized")
                    return
                self.handle_unban_ip(data)
            elif path == "/admin/api/login":
                self.handle_admin_login(data)
            elif path == "/admin/api/logout":
                if not self.is_admin_authenticated():
                    self.send_error(401, "Unauthorized")
                    return
                self.handle_admin_logout()
            else:
                self.send_error(404, "Not Found")
                
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 500)
    
    def serve_index(self):
        """Serve index page"""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Nexus Root</title>
            <style>
                body {
                    background-color: #000;
                    color: #0f0;
                    font-family: 'Courier New', Courier, monospace;
                    font-size: 16px;
                }
                #terminal {
                    padding: 10px;
                    height: 100vh;
                    overflow-y: scroll;
                }
                .line {
                    margin-bottom: 5px;
                }
                .prompt {
                    color: #0f0;
                }
                #input-line {
                    display: flex;
                }
                #input {
                    background-color: transparent;
                    border: none;
                    color: #0f0;
                    font-family: 'Courier New', Courier, monospace;
                    font-size: 16px;
                    flex-grow: 1;
                }
                #input:focus {
                    outline: none;
                }
            </style>
        </head>
        <body>
            <div id="terminal">
                <div class="line">Welcome to Nexus Root.</div>
                <div class="line">Type 'help' for a list of commands.</div>
                <div id="output"></div>
                <div id="input-line">
                    <span class="prompt">&gt; </span>
                    <input type="text" id="input" autofocus>
                </div>
            </div>
            <script>
                const terminal = document.getElementById('terminal');
                const output = document.getElementById('output');
                const input = document.getElementById('input');

                input.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        const command = input.value;
                        input.value = '';

                        const line = document.createElement('div');
                        line.classList.add('line');
                        line.innerHTML = `<span class="prompt">&gt; </span>${command}`;
                        output.appendChild(line);

                        handleCommand(command);

                        terminal.scrollTop = terminal.scrollHeight;
                    }
                });

                let sessionToken = null;

                function handleCommand(command) {
                    const parts = command.split(' ');
                    const cmd = parts[0].toLowerCase();
                    const args = parts.slice(1);

                    const responseLine = document.createElement('div');
                    responseLine.classList.add('line');

                    switch (cmd) {
                        case 'help':
                            responseLine.innerHTML = `
                                <div>Available commands:</div>
                                <div>- help: Show this help dialog</div>
                                <div>- register &lt;username&gt; &lt;password&gt;: Create a new account</div>
                                <div>- login &lt;username&gt; &lt;password&gt;: Log in to your account</div>
                                <div>- dos_attack &lt;target_player&gt;: Launch a DoS attack against another player</div>
                            `;
                            break;
                        case 'register':
                            if (args.length === 2) {
                                register(args[0], args[1]);
                            } else {
                                responseLine.textContent = 'Usage: register <username> <password>';
                                output.appendChild(responseLine);
                            }
                            break;
                        case 'login':
                            if (args.length === 2) {
                                login(args[0], args[1]);
                            } else {
                                responseLine.textContent = 'Usage: login <username> <password>';
                                output.appendChild(responseLine);
                            }
                            break;
                        case 'dos_attack':
                            if (args.length === 1) {
                                executeCommand(`dos_attack ${args[0]}`);
                            } else {
                                responseLine.textContent = 'Usage: dos_attack <target_player>';
                                output.appendChild(responseLine);
                            }
                            break;
                        default:
                            responseLine.textContent = `Command not found: ${cmd}`;
                    }

                    if (cmd !== 'register' && cmd !== 'login') {
                        output.appendChild(responseLine);
                    }
                }

                async function register(username, password) {
                    const response = await fetch('/api/register', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ username, password })
                    });
                    const data = await response.json();
                    const responseLine = document.createElement('div');
                    responseLine.classList.add('line');
                    responseLine.textContent = data.message;
                    output.appendChild(responseLine);
                }

                async function login(username, password) {
                    const response = await fetch('/api/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ username, password })
                    });
                    const data = await response.json();
                    const responseLine = document.createElement('div');
                    responseLine.classList.add('line');
                    if (data.success) {
                        sessionToken = data.token;
                        responseLine.textContent = `Login successful. Welcome, ${username}.`;
                    } else {
                        responseLine.textContent = `Login failed: ${data.error}`;
                    }
                    output.appendChild(responseLine);
                }

                async function executeCommand(command) {
                    const response = await fetch('/api/command/execute', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${sessionToken}`
                        },
                        body: JSON.stringify({ command, player_name: 'test_user' })
                    });
                    const data = await response.json();
                    const responseLine = document.createElement('div');
                    responseLine.classList.add('line');
                    if (data.success) {
                        responseLine.textContent = data.output;
                    } else {
                        responseLine.textContent = `Error: ${data.error}`;
                    }
                    output.appendChild(responseLine);
                }
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def serve_admin_panel(self):
        """Serve admin panel"""
        try:
            with open("src/server/admin.html", "rb") as f:
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_error(404, "Admin panel not found")

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

    def handle_get_announcement(self):
        """Handle get announcement request"""
        result = self.game_api.get_announcement()
        self.send_json_response(result)

    def handle_register(self, data: dict):
        """Handle register request"""
        result = self.auth_api.register(data)
        self.send_json_response(result)

    def handle_login(self, data: dict):
        """Handle login request"""
        result = self.auth_api.login(data)
        self.send_json_response(result)

    def handle_create_player(self, data: dict):
        """Handle create player request"""
        name = data.get("name")
        if isinstance(name, list):
            name = name[0]

        # The create_player method in the game_api expects a dictionary,
        # but the form submission sends a dictionary where the values are lists.
        # We need to convert the dictionary to the correct format.
        if isinstance(data, dict) and all(isinstance(v, list) for v in data.values()):
            data = {k: v[0] for k, v in data.items()}
        is_vip = data.get("is_vip", False)
        session_id = data.get("session_id")
        
        if not name:
            self.send_json_response({"success": False, "error": "Missing player name"}, 400)
            return
        
        result = self.game_api.create_player(name, is_vip, session_id)
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
        
        if not command:
            self.send_json_response({"success": False, "error": "Missing command"}, 400)
            return

        if not player_name:
            # Get the player name from the session token
            # This is a placeholder for a real implementation.
            player_name = "test_user"
        
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
    
    def handle_get_all_players(self, search: str, sort: str, order: str):
        """Handle get all players request"""
        result = self.admin_api.get_all_players(search, sort, order)
        self.send_json_response(result)

    def handle_get_banned_players(self):
        """Handle get banned players request"""
        result = self.admin_api.get_banned_players()
        self.send_json_response(result)

    def handle_ban_player(self, player_id: str):
        """Handle ban player request"""
        result = self.admin_api.ban_player(player_id)
        self.send_json_response(result)

    def handle_unban_player(self, player_id: str):
        """Handle unban player request"""
        result = self.admin_api.unban_player(player_id)
        self.send_json_response(result)

    def handle_send_announcement(self, data: dict):
        """Handle send announcement request"""
        message = data.get("message")

        if not message:
            self.send_json_response({"success": False, "error": "Missing message"}, 400)
            return

        result = self.admin_api.send_announcement(message)
        self.send_json_response(result)

    def handle_admin_login(self, data: dict):
        """Handle admin login request"""
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            self.send_json_response({"success": False, "error": "Missing username or password"}, 400)
            return

        try:
            token = self.admin_auth_service.authenticate(username, password)
            self.send_json_response({"success": True, "token": token})
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, 401)

    def handle_admin_logout(self):
        """Handle admin logout request"""
        auth_header = self.headers.get("Authorization")
        token = auth_header.split(" ")[1]
        self.admin_auth_service.logout(token)
        self.send_json_response({"success": True})

    def handle_ban_ip(self, data: dict):
        """Handle ban IP request"""
        ip_address = data.get("ip_address")

        if not ip_address:
            self.send_json_response({"success": False, "error": "Missing ip_address"}, 400)
            return

        result = self.admin_api.ban_ip(ip_address)
        self.send_json_response(result)

    def handle_unban_ip(self, data: dict):
        """Handle unban IP request"""
        ip_address = data.get("ip_address")

        if not ip_address:
            self.send_json_response({"success": False, "error": "Missing ip_address"}, 400)
            return

        result = self.admin_api.unban_ip(ip_address)
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
        
        # Initialize Admin API
        player_repository = self.game_api.player_repository
        admin_service = AdminService(player_repository)
        self.admin_api = AdminAPI(self.game_api.player_service, admin_service)

        # Initialize Admin Auth Service
        self.admin_auth_service = AdminAuthService(config.database.database)

        # Initialize Auth Service and API
        auth_service = AuthService(config.database.database, self.game_api.player_repository)
        self.auth_api = AuthAPI(auth_service)

        # Create handler class with game_api, admin_api, and admin_auth_service
        def handler_factory(*args, **kwargs):
            return CustomAPIHandler(*args, game_api=self.game_api, admin_api=self.admin_api, admin_auth_service=self.admin_auth_service, auth_api=self.auth_api, **kwargs)
        
        self.handler_class = handler_factory
        
    def run(self):
        """Run the web server"""
        server_address = (self.config.server.host, self.config.server.port)
        
        try:
            httpd = HTTPServer(server_address, self.handler_class)
            
            self.logger.info(f"Starting server on {self.config.server.host}:{self.config.server.port}")
            print(f"Nexus Root API Server running on http://{self.config.server.host}:{self.config.server.port}")
            print(f"Admin Panel available at http://{self.config.server.host}:{self.config.server.port}/admin")
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