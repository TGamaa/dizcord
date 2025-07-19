# database.py
import sqlite3

def init_db():
    """Initializes the database and creates the messages table if it doesn't exist."""
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    # For simplicity, we'll just have one messages table for a global chat
    # A full friend/chat system would require tables for users, friends, and chats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_message(username, message):
    """Adds a new message to the database."""
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (username, message) VALUES (?, ?)", (username, message))
    conn.commit()
    conn.close()

def get_messages():
    """Retrieves all messages from the database."""
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, message, timestamp FROM messages ORDER BY timestamp ASC")
    messages = cursor.fetchall()
    conn.close()
    return messages