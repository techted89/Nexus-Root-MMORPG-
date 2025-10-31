import argparse
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.repositories.sqlite_player_repository import SQLitePlayerRepository
from scripts.create_admin_user import create_admin_user

def main():
    """Run the setup script"""
    parser = argparse.ArgumentParser(description="Setup the Nexus Root MMORPG")
    parser.add_argument("--username", required=True, help="Admin username")
    parser.add_argument("--password", required=True, help="Admin password")
    args = parser.parse_args()

    db_path = "nexus_root.db"

    print("Initializing database...")
    SQLitePlayerRepository(db_path)
    print("Database initialized successfully.")

    print("Creating admin user...")
    create_admin_user(db_path, args.username, args.password)
    print("Admin user created successfully.")

if __name__ == "__main__":
    main()