# Nexus Root MMORPG - Redesigned Architecture

## Overview

This is a complete redesign of the Nexus Root MMORPG with a modern, object-oriented architecture that provides:

- **Clean separation of concerns** with distinct layers
- **Comprehensive error handling** and logging
- **RESTful API** for external integration
- **Modular command system** with easy extensibility
- **Robust data persistence** with repository pattern
- **Event-driven architecture** for loose coupling
- **Extensive testing framework** for reliability

## Architecture

### Core Components

```
src/
├── core/           # Core framework (config, logging, events, exceptions)
├── models/         # Data models (Player, Mission, VirtualComputer)
├── repositories/   # Data persistence layer
├── services/       # Business logic layer
├── api/           # API layer for external integration
├── server/        # HTTP server for API access
└── nexus_script/  # Original scripting engine
```

### Design Principles

1. **Single Responsibility**: Each class has one clear purpose
2. **Dependency Injection**: Services receive dependencies rather than creating them
3. **Interface Segregation**: Clean interfaces with minimal dependencies
4. **Error Isolation**: Errors are contained and don't cascade
5. **Event-Driven**: Components communicate through events, not direct calls

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd webapp

# Install dependencies (optional)
pip install -r requirements.txt
```

### Running the Shell

```bash
# Interactive shell
python main.py shell

# Shell with specific player
python main.py shell --player Alice

# Debug mode
python main.py shell --debug
```

### Running the API Server

```bash
# Start API server
python main.py server

# Custom port
python main.py server --port 8080

# Debug mode
python main.py server --debug
```

### Running Tests

```bash
# Run all tests
python main.py test

# Or with pytest directly
pytest tests/ -v
```

## API Usage

### Starting the Server

The API server provides HTTP endpoints for all game functionality:

```bash
python main.py server --port 8080
```

Visit `http://localhost:8080` for API documentation.

### Basic API Examples

#### Create a Player
```bash
curl -X POST http://localhost:8080/api/player/create \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "is_vip": false}'
```

#### Login
```bash
curl -X POST http://localhost:8080/api/player/login \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "session_id": "session123"}'
```

#### Execute Command
```bash
curl -X POST http://localhost:8080/api/command/execute \
  -H "Content-Type: application/json" \
  -d '{"player_name": "Alice", "command": "ls"}'
```

#### Get Leaderboard
```bash
curl "http://localhost:8080/api/leaderboard?category=level&limit=10"
```

### Python Client Example

```python
from examples.simple_client import NexusClient

# Create client
client = NexusClient("http://localhost:8080")

# Create player
client.create_player("TestPlayer")

# Login
client.login("TestPlayer")

# Execute commands
result = client.execute_command("ls")
print(result["output"])

# Get player info
info = client.get_player_info()
print(f"Level: {info['data']['level']}")
```

## Configuration

### Configuration File

Create `config.json` for custom settings:

```bash
python main.py config
```

Example configuration:

```json
{
  "database": {
    "type": "sqlite",
    "database": "nexus_root.db"
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "debug": false
  },
  "game": {
    "max_players": 1000,
    "credit_multiplier": 1.0,
    "xp_multiplier": 1.0
  },
  "log_level": "INFO",
  "log_file": "nexus.log"
}
```

### Environment Variables

```bash
export NEXUS_DB_NAME="nexus_root.db"
export NEXUS_SERVER_PORT="8080"
export NEXUS_LOG_LEVEL="INFO"
```

## Development

### Adding New Commands

Create a new command class:

```python
from src.services.command_service import Command, CommandResult

class MyCommand(Command):
    def __init__(self):
        super().__init__("mycommand", "My custom command", "mycommand <arg>")
    
    def execute(self, player, args, context=None):
        # Command logic here
        return CommandResult(True, "Command executed successfully")

# Register in CommandService
command_service.register_command(MyCommand())
```

### Adding New Missions

```python
from src.models.mission import Mission, MissionType, MissionReward, MissionObjective

mission = Mission(
    mission_id="custom_001",
    name="Custom Mission",
    description="A custom mission",
    mission_type=MissionType.MAIN,
    reward=MissionReward(experience=100, credits=50)
)

mission.add_objective(MissionObjective("objective1", "Complete task", 1))
mission_service.repository.save(mission)
```

### Event Handling

```python
from src.core.events import EventHandler, Event

class MyEventHandler(EventHandler):
    def handle(self, event: Event) -> bool:
        print(f"Received event: {event.event_type}")
        return True

event_bus.subscribe("game.command_executed", MyEventHandler())
```

## Testing

### Running Tests

```bash
# All tests
python main.py test

# Specific test file
pytest tests/test_player_service.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Writing Tests

```python
import pytest
from src.api.game_api import GameAPI

class TestMyFeature:
    @pytest.fixture
    def game_api(self):
        return GameAPI()
    
    def test_my_feature(self, game_api):
        result = game_api.some_method()
        assert result["success"] == True
```

## Deployment

### Production Setup

1. **Database**: Configure PostgreSQL or MySQL for production
2. **Logging**: Set up centralized logging (ELK stack, etc.)
3. **Monitoring**: Add health checks and metrics
4. **Security**: Implement authentication and rate limiting
5. **Scaling**: Use load balancers and multiple instances

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["python", "main.py", "server", "--port", "8080"]
```

## Monitoring

### Server Status

```bash
python main.py status
```

### Logs

Logs are written to `logs/nexus.log` and include:
- Command executions
- Player actions
- Errors and exceptions
- Performance metrics

### Health Checks

```bash
curl http://localhost:8080/api/status
```

## Migration from Original

### Key Differences

1. **Modular Design**: Code is split into logical modules
2. **Error Handling**: Comprehensive exception handling
3. **API Layer**: RESTful API for integration
4. **Testing**: Full test coverage
5. **Configuration**: Flexible configuration system
6. **Logging**: Structured logging throughout

### Migration Steps

1. **Data Migration**: Player data is automatically migrated
2. **Configuration**: Update configuration files
3. **Custom Commands**: Port to new command system
4. **Integrations**: Update to use new API endpoints

## Contributing

### Code Style

- Follow PEP 8 for Python code style
- Use type hints for all functions
- Document all public methods
- Write tests for new features

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Write tests for your changes
4. Ensure all tests pass
5. Submit a pull request

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure you're in the project directory
cd /path/to/webapp
python main.py shell
```

#### Database Issues
```bash
# Reset database
rm nexus_root.db
python main.py shell  # Will recreate
```

#### Permission Errors
```bash
# Check file permissions
chmod +x main.py
```

### Getting Help

1. Check the logs in `logs/nexus.log`
2. Run with `--debug` flag for verbose output
3. Review the API documentation at `http://localhost:8080`
4. Check the test suite for usage examples

## License

This project is licensed under the MIT License - see the LICENSE file for details.