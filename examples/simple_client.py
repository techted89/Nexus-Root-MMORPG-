"""
Simple client example for Nexus Root MMORPG API
"""

import requests
import json
from typing import Dict, Any, Optional

class NexusClient:
    """Simple HTTP client for Nexus Root MMORPG API"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        """Initialize client with server URL"""
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.player_name: Optional[str] = None
        self.session_id: Optional[str] = None
    
    def _request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=data)
            else:
                response = self.session.post(url, json=data)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}
        except json.JSONDecodeError:
            return {"success": False, "error": "Invalid JSON response"}
    
    def create_player(self, name: str, is_vip: bool = False) -> Dict[str, Any]:
        """Create a new player"""
        return self._request("POST", "/api/player/create", {
            "name": name,
            "is_vip": is_vip
        })
    
    def login(self, name: str, session_id: str = None) -> Dict[str, Any]:
        """Login with a player"""
        result = self._request("POST", "/api/player/login", {
            "name": name,
            "session_id": session_id or f"session_{name}"
        })
        
        if result.get("success"):
            self.player_name = name
            self.session_id = session_id or f"session_{name}"
        
        return result
    
    def logout(self) -> Dict[str, Any]:
        """Logout current player"""
        if not self.player_name:
            return {"success": False, "error": "No player logged in"}
        
        result = self._request("POST", "/api/player/logout", {
            "name": self.player_name
        })
        
        if result.get("success"):
            self.player_name = None
            self.session_id = None
        
        return result
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a game command"""
        if not self.player_name:
            return {"success": False, "error": "No player logged in"}
        
        return self._request("POST", "/api/command/execute", {
            "player_name": self.player_name,
            "command": command
        })
    
    def get_player_info(self, name: str = None) -> Dict[str, Any]:
        """Get player information"""
        target_name = name or self.player_name
        if not target_name:
            return {"success": False, "error": "No player specified"}
        
        return self._request("GET", f"/api/player/{target_name}")
    
    def get_leaderboard(self, category: str = "level", limit: int = 10) -> Dict[str, Any]:
        """Get leaderboard"""
        return self._request("GET", "/api/leaderboard", {
            "category": category,
            "limit": limit
        })
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get server statistics"""
        return self._request("GET", "/api/statistics")
    
    def start_mission(self, mission_id: str) -> Dict[str, Any]:
        """Start a mission"""
        if not self.player_name:
            return {"success": False, "error": "No player logged in"}
        
        return self._request("POST", "/api/mission/start", {
            "player_name": self.player_name,
            "mission_id": mission_id
        })
    
    def upgrade_hardware(self, component: str) -> Dict[str, Any]:
        """Upgrade hardware component"""
        if not self.player_name:
            return {"success": False, "error": "No player logged in"}
        
        return self._request("POST", "/api/hardware/upgrade", {
            "player_name": self.player_name,
            "component": component
        })
    
    def start_mining(self, hours: int = 1) -> Dict[str, Any]:
        """Start passive mining"""
        if not self.player_name:
            return {"success": False, "error": "No player logged in"}
        
        return self._request("POST", "/api/mining/start", {
            "player_name": self.player_name,
            "hours": hours
        })
    
    def check_mining(self) -> Dict[str, Any]:
        """Check mining status"""
        if not self.player_name:
            return {"success": False, "error": "No player logged in"}
        
        return self._request("POST", "/api/mining/check", {
            "player_name": self.player_name
        })

def main():
    """Example usage of the client"""
    # Create client
    client = NexusClient("http://localhost:8080")
    
    print("Nexus Root Client Example")
    print("=" * 30)
    
    # Check server status
    stats = client.get_statistics()
    if stats.get("success"):
        print(f"Server online - {stats['data']['total_players']} players registered")
    else:
        print(f"Server error: {stats.get('error')}")
        return
    
    # Create or login player
    player_name = "ClientTest"
    
    # Try to create player
    result = client.create_player(player_name, is_vip=False)
    if not result.get("success") and "already taken" in result.get("error", ""):
        print(f"Player {player_name} already exists")
    elif result.get("success"):
        print(f"Created player: {player_name}")
    
    # Login
    result = client.login(player_name)
    if result.get("success"):
        print(f"Logged in as: {player_name}")
        player_data = result["data"]
        print(f"Level: {player_data['level']}, Credits: {player_data['credits']}")
    else:
        print(f"Login failed: {result.get('error')}")
        return
    
    # Execute some commands
    print("\nExecuting commands:")
    
    commands = ["ls", "cat data.txt", "status"]
    for cmd in commands:
        print(f"\n> {cmd}")
        result = client.execute_command(cmd)
        if result.get("success"):
            print(result.get("output", ""))
        else:
            print(f"Error: {result.get('error')}")
    
    # Get leaderboard
    print("\nLeaderboard:")
    result = client.get_leaderboard()
    if result.get("success"):
        for i, entry in enumerate(result["data"][:5], 1):
            print(f"{i}. {entry['name']} (Level {entry['level']}, {entry['credits']} credits)")
    
    # Logout
    client.logout()
    print(f"\nLogged out {player_name}")

if __name__ == "__main__":
    main()