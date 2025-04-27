import sqlite3
import os


class DataBase:
    def __init__(self):
        self.db_path = "eventhub.db"
        self._initialize_db_if_needed()

    def _initialize_db_if_needed(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
            )
            if cur.fetchone():
                return  # Table exists, do nothing
            schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
            with open(schema_path, "r") as f:
                schema = f.read()
            conn.executescript(schema)
            conn.commit()

    def __enter__(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # This allows accessing columns by name
            self.cursor = self.conn.cursor()
            return self
        except sqlite3.Error as error:
            print("Error while connecting to SQLite", error)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    # User-related methods
    def create_user(self, name, email, password_hash):
        self.cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        return self.cursor.lastrowid

    def get_user_by_id(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return self.cursor.fetchone()

    def get_user_by_email(self, email):
        self.cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        return self.cursor.fetchone()

    # Event-related methods
    def create_event(self, user_id, name, description, date, location):
        self.cursor.execute(
            "INSERT INTO events (user_id, name, description, date, location) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, description, date, location),
        )
        return self.cursor.lastrowid

    def get_all_events(self):
        self.cursor.execute(
            """
            SELECT e.*, u.name as creator_name 
            FROM events e
            JOIN users u ON e.user_id = u.id
            ORDER BY e.date
        """
        )
        return self.cursor.fetchall()

    def get_event_by_id(self, event_id):
        self.cursor.execute(
            """
            SELECT e.*, u.name as creator_name 
            FROM events e
            JOIN users u ON e.user_id = u.id
            WHERE e.id = ?
        """,
            (event_id,),
        )
        return self.cursor.fetchone()

    def get_events_by_user_id(self, user_id):
        self.cursor.execute(
            """
            SELECT e.*, u.name as creator_name 
            FROM events e
            JOIN users u ON e.user_id = u.id
            WHERE e.user_id = ?
            ORDER BY e.date
            """,
            (user_id,),
        )
        return self.cursor.fetchall()

    # Registration-related methods
    def create_registration(self, user_id, event_id):
        try:
            self.cursor.execute(
                "INSERT INTO registrations (user_id, event_id) VALUES (?, ?)",
                (user_id, event_id),
            )
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def delete_registration(self, user_id, event_id):
        self.cursor.execute(
            "DELETE FROM registrations WHERE user_id = ? AND event_id = ?",
            (user_id, event_id),
        )
        return self.cursor.rowcount > 0

    def get_registration(self, user_id, event_id):
        self.cursor.execute(
            "SELECT * FROM registrations WHERE user_id = ? AND event_id = ?",
            (user_id, event_id),
        )
        return self.cursor.fetchone()

    def get_registrations_by_user_id(self, user_id):
        self.cursor.execute(
            """
            SELECT r.id as registration_id, r.user_id, r.event_id, 
                  e.id, e.user_id as event_user_id, e.name, e.description, e.date, e.location, 
                  u.name as creator_name
            FROM registrations r
            JOIN events e ON r.event_id = e.id
            JOIN users u ON e.user_id = u.id
            WHERE r.user_id = ?
            ORDER BY e.date
        """,
            (user_id,),
        )
        return self.cursor.fetchall()

    def get_registrations_by_event_id(self, event_id):
        self.cursor.execute(
            """
            SELECT r.*, u.id as user_id, u.name, u.email
            FROM registrations r
            JOIN users u ON r.user_id = u.id
            WHERE r.event_id = ?
        """,
            (event_id,),
        )
        return self.cursor.fetchall()

    def search_events(self, search_term):
        """Search for events matching the search term in name, description, or location."""
        search_pattern = f"%{search_term}%"
        self.cursor.execute(
            """
            SELECT e.*, u.name as creator_name 
            FROM events e
            JOIN users u ON e.user_id = u.id
            WHERE e.name LIKE ? 
            OR e.description LIKE ? 
            OR e.location LIKE ?
            ORDER BY e.date
        """,
            (search_pattern, search_pattern, search_pattern),
        )
        return self.cursor.fetchall()

    def update_event(self, event_id, name, description, date, location):
        """Update an existing event"""
        self.cursor.execute(
            """
            UPDATE events 
            SET name = ?, description = ?, date = ?, location = ?
            WHERE id = ?
        """,
            (name, description, date, location, event_id),
        )
        return self.cursor.rowcount > 0

    def delete_event(self, event_id):
        """Delete an event and all its registrations"""
        self.cursor.execute("DELETE FROM registrations WHERE event_id = ?", (event_id,))

        self.cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        return self.cursor.rowcount > 0
