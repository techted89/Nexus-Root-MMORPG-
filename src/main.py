from src.server.web_server import WebServer
from src.core.config import NexusConfig

def main():
    """Main entry point"""
    config = NexusConfig.load_from_file()
    server = WebServer(config)
    server.run()

if __name__ == "__main__":
    main()
