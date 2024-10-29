import sqlite3

class PersonDB:
    def __init__(self, db_name= 'users.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_table()


    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    mail TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    confirmed INTEGER DEFAULT 0
                )
            """)

    def add_user(self, username, mail, password):
        try:
            with self.conn:
                self.conn.execute("INSERT INTO users (username, mail, password) VALUES (?,?,?)", (username, mail, password))
            return True, "User added successfully."
        except sqlite3.IntegrityError as e:
            return False, str(e)

    def check_user(self, username, password):
        user = self.conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        return user is not None

    def exists_user(self, username):
        user = self.conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return user is not None    
    
    def exists_mail(self, mail):
        user = self.conn.execute("SELECT * FROM users WHERE username = ?", (mail,)).fetchone()
        return user is not None    
    
    def confirm_user(self, mail):
        try:
            with self.conn:
                self.conn.execute("""
                    UPDATE users SET confirmed = 1 WHERE mail = ?
                """, (mail,))
                return True
        except sqlite3.IntegrityError as e:
            return False
        
    def get_user_by_username_and_email(self, username, email):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND mail = ?", (username, email))
            return cursor.fetchone() is not None
        
    def get_user_by_username(self, username):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            return cursor.fetchone()  # Returns the user record or None


        
    def update_password(self, mail, password_hashed):
        try:
            with self.conn:
                self.conn.execute("""
                    UPDATE users SET password = ? WHERE mail = ?
                """, (password_hashed, mail))
                return True
        except sqlite3.IntegrityError as e:
            print(f"IntegrityError: {str(e)}")
            return False