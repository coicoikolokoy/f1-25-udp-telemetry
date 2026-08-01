import sqlite3
from app.domain.models import CarTelemetry

class TelemetryRepository:
    def __init__(self, db_path: str = "telemetry.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_sessions (
                    session_uid TEXT PRIMARY KEY,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    track_id INTEGER,
                    weather_id INTEGER
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS telemetry_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_uid TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    speed INTEGER,
                    throttle REAL,
                    brake REAL,
                    FOREIGN KEY (session_uid) REFERENCES game_sessions(session_uid)
                );
            """)
            conn.commit()

    def create_session_if_missing(self, session_uid: str, track_id: int, weather_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO game_sessions (session_uid, track_id, weather_id)
                VALUES (?, ?, ?)
            """, (session_uid, track_id, weather_id))
            conn.commit()

    def save_entry(self, session_uid: str, telemetry: CarTelemetry):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO telemetry_log (session_uid, speed, throttle, brake) 
                VALUES (?, ?, ?, ?)
            """, (session_uid, telemetry.speed, telemetry.throttle, telemetry.brake))
            conn.commit()
