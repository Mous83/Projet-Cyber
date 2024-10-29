import sqlite3
from datetime import datetime

class ConnectedUserDB:
    def __init__(self, db_name='connected_users.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS connected_users (
                    username TEXT PRIMARY KEY,
                    connected_at TEXT,
                    disconnected_at TEXT
                )
            ''')

    def add_user(self, username):
        connected_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with self.conn:
            self.conn.execute('''
                INSERT OR REPLACE INTO connected_users (username, connected_at, disconnected_at)
                VALUES (?, ?, NULL)
            ''', (username, connected_at))

    def update_disconnected_at(self, username):
        disconnected_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with self.conn:
            self.conn.execute('''
                UPDATE connected_users
                SET disconnected_at = ?
                WHERE username = ?
            ''', (disconnected_at, username))

    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT username FROM connected_users WHERE disconnected_at IS NULL')
        users = cursor.fetchall()
        return [user[0] for user in users]

    def user_exists(self, username):
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM connected_users WHERE username = ? AND disconnected_at IS NULL', (username,))
        return cursor.fetchone() is not None
