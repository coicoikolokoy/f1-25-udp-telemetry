import sqlite3
from app.domain.models import CarTelemetry

class TelemetryRepository:
    """Handles persistent storage of telemetry entries in an SQLite database."""
    
    def __init__(self, db_path: str = "telemetry.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Creates the telemetry table structure if it does not exist yet."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS telemetry_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    speed INTEGER,
                    throttle REAL,
                    brake REAL
                );
            """)
            conn.commit()

    def save_entry(self, telemetry: CarTelemetry):
        """Inserts a clean domain instance directly into the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO telemetry_log (speed, throttle, brake) VALUES (?, ?, ?)",
                (telemetry.speed, telemetry.throttle, telemetry.brake)
            )
            conn.commit()
