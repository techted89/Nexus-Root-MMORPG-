import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.repositories.sqlite_player_repository import SQLitePlayerRepository

def initialize_database(db_path):
    """Initialize the database"""
    try:
        print("Initializing database...")
        SQLitePlayerRepository(db_path)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    db_path = "nexus_root.db"
    initialize_database(db_path)