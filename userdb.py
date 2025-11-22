import sqlite3
from datetime import datetime

class UserDB:
    def __init__(self, path="database.db"):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            language_code TEXT,
            is_bot BOOLEAN,
            join_date TIMESTAMP,
            last_seen TIMESTAMP,
            trust TEXT DEFAULT 'limited',
            approved_posts INTEGER DEFAULT 0,
            rejected_posts INTEGER DEFAULT 0,
            warn_count INTEGER DEFAULT 0,
            kick_count INTEGER DEFAULT 0,
            mute_count INTEGER DEFAULT 0,
            ban_count INTEGER DEFAULT 0,
            actual_state TEXT DEFAULT 'active'
        );
        """
        self.conn.execute(query)
        self.conn.commit()

    def ensure_user(self, user):
        query = """
        INSERT OR IGNORE INTO users (id, username, first_name, last_name, phone,
                                     language_code, is_bot, join_date, last_seen)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            user.id,
            user.username,
            user.first_name,
            user.last_name,
            user.phone,
            user.lang_code if hasattr(user, "lang_code") else None,
            user.bot if hasattr(user, "bot") else False,
            datetime.now(),
            datetime.now(),
        )

        self.conn.execute(query, params)
        self.conn.commit()

    def increment(self, user_id, field):
        query = f"""
            UPDATE users
            SET {field} = {field} + 1,
                last_seen = ?
            WHERE id = ?
        """
        self.conn.execute(query, (datetime.now(), user_id))
        self.conn.commit()

    def set_state(self, user_id, state):
        query = """
            UPDATE users
            SET actual_state = ?, last_seen = ?
            WHERE id = ?
        """
        self.conn.execute(query, (state, datetime.now(), user_id))
        self.conn.commit()


    def check_db_columns(self, column):
        ALLOWED_COLUMNS = {
            "*", "id", "username", "first_name", "last_name", "phone",
            "language_code", "is_bot", "last_seen", "trust",
            "approved_posts", "rejected_posts",
            "warn_count", "kick_count", "mute_count", "ban_count",
            "actual_state"
        }
        if column not in ALLOWED_COLUMNS:
            raise ValueError(f"Invalid column name: {column}")

    def update_entry(self, user_id, column, value):
        # Protect from SQL injection
        self.check_db_columns(column)

        # Update Query
        query = f"""
            UPDATE users
            SET {column} = ?, last_seen = ?
            WHERE id = ?
        """
        self.conn.execute(query, (value, datetime.now(), user_id))
        self.conn.commit()

    def get_user(self, user_id, column="*"):
        # Protect from SQL injection
        self.check_db_columns(column)

        # Build query
        q = f"SELECT {column} FROM users WHERE id = ?"
        cur = self.conn.execute(q, (user_id,))
        row = cur.fetchone()

        if row is None:
            return None

        columns = [column[0] for column in cur.description]
        return dict(zip(columns, row))

