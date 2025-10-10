import sqlite3

def initialize_database():
    conn = sqlite3.connect('nexus_root.db')
    c = conn.cursor()

    # Create players table
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            level INTEGER NOT NULL,
            experience INTEGER NOT NULL
        )
    ''')

    # Create missions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS missions (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            reward INTEGER NOT NULL
        )
    ''')

    # Create commands table
    c.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            syntax TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_database()
    print("Database 'nexus_root.db' initialized successfully.")
