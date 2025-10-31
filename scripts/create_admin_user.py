import sqlite3
import uuid
import hashlib

def create_admin_user(db_path, username, password):
    """Create a new admin user"""
    try:
        with sqlite3.connect(db_path) as conn:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            admin_id = str(uuid.uuid4())

            conn.execute(
                "INSERT INTO admin_users (id, username, password_hash) VALUES (?, ?, ?)",
                (admin_id, username, password_hash)
            )

            conn.commit()
            print(f"Admin user '{username}' created successfully.")

    except sqlite3.Error as e:
        print(f"Error creating admin user: {e}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create a new admin user")
    parser.add_argument("--db_path", default="nexus_root.db", help="Path to the database file")
    parser.add_argument("--username", required=True, help="Admin username")
    parser.add_argument("--password", required=True, help="Admin password")
    args = parser.parse_args()

    create_admin_user(args.db_path, args.username, args.password)