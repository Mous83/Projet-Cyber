import sqlite3

class MessageDB:
    def __init__(self, db_name= 'messages.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    message TEXT NOT NULL,
                    recipient TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP         
                )
            """)


    def add_message(self, username, message, recipient=None):
        with self.conn:
            self.conn.execute("INSERT INTO messages (username, message, recipient) VALUES (?, ?, ?)",
                              (username, message, recipient))
            

    def get_all_messages(self):
        with self.conn:
            messages = self.conn.execute("SELECT username, message, recipient, timestamp FROM messages ORDER BY timestamp").fetchall()
        return messages        