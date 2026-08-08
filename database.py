# database.py
import sqlite3
from typing import Dict, Any, List
from config import DB_PATH

def init_db(db_path: str = DB_PATH):
    """Initializes the SQLite relational database enforcing Foreign Keys and cascade rules."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # 1. Tracks Lookup Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                track_id INTEGER PRIMARY KEY,
                track_name TEXT NOT NULL,
                total_sectors INTEGER NOT NULL DEFAULT 3
            );
        """)
        
        # 2. Laps Session Summary
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS laps (
                lap_id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER NOT NULL,
                lap_number INTEGER NOT NULL,
                sector_1_time_ms INTEGER DEFAULT 0,
                sector_2_time_ms INTEGER DEFAULT 0,
                sector_3_time_ms INTEGER DEFAULT 0,
                total_lap_time_ms INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (track_id) REFERENCES tracks(track_id) ON DELETE RESTRICT
            );
        """)
        
        # 3. Telemetry Samples (High-Frequency Stream Log)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry_samples (
                sample_id INTEGER PRIMARY KEY AUTOINCREMENT,
                lap_id INTEGER NOT NULL,
                lap_distance REAL NOT NULL,
                speed INTEGER NOT NULL,
                throttle REAL NOT NULL,
                brake REAL NOT NULL,
                steer REAL NOT NULL,
                world_x REAL DEFAULT 0.0,
                world_z REAL DEFAULT 0.0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lap_id) REFERENCES laps(lap_id) ON DELETE CASCADE
            );
        """)
        
       # Seed favorite testing tracks (Official F1 25 IDs)
        cursor.execute("""
            INSERT OR IGNORE INTO tracks (track_id, track_name, total_sectors) 
            VALUES 
                (0, 'Melbourne', 3),
                (5, 'Monaco', 3),
                (7, 'Silverstone (Britain)', 3),
                (10, 'Spa-Francorchamps', 3),
                (11, 'Monza', 3),
                (17, 'Austria (Red Bull Ring)', 3);
        """)
        
        conn.commit()
    print("Database schema successfully initialized with Foreign Key cascades.")


def create_new_lap(track_id: int, lap_number: int, db_path: str = DB_PATH) -> int:
    """Inserts a new lap record and returns the generated lap_id."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("""
            INSERT INTO laps (track_id, lap_number)
            VALUES (?, ?)
        """, (track_id, lap_number))
        conn.commit()
        return cursor.lastrowid


def insert_telemetry_sample(
    lap_id: int, 
    lap_distance: float, 
    speed: int, 
    throttle: float, 
    brake: float, 
    steer: float, 
    world_x: float = 0.0, 
    world_z: float = 0.0, 
    db_path: str = DB_PATH
):
    """Inserts a high-frequency telemetry sample bound to a specific lap_id."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("""
            INSERT INTO telemetry_samples 
            (lap_id, lap_distance, speed, throttle, brake, steer, world_x, world_z)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (lap_id, lap_distance, speed, throttle, brake, steer, world_x, world_z))
        conn.commit()


def get_lap_telemetry_arrays(lap_id: int, db_path: str = DB_PATH) -> Dict[str, Any]:
    """Extracts telemetry sample arrays ordered by lap_distance ASC matching API contract shape."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT lap_distance, speed, throttle, brake, steer, world_x, world_z
            FROM telemetry_samples
            WHERE lap_id = ?
            ORDER BY lap_distance ASC
        """, (lap_id,))
        rows = cursor.fetchall()

    if not rows:
        return {
            "lap_id": lap_id,
            "lap_distance": [], "speed": [], "throttle": [],
            "brake": [], "steer": [], "world_x": [], "world_z": []
        }

    lap_distance, speed, throttle, brake, steer, world_x, world_z = zip(*rows)

    return {
        "lap_id": lap_id,
        "lap_distance": list(lap_distance),
        "speed": list(speed),
        "throttle": list(throttle),
        "brake": list(brake),
        "steer": list(steer),
        "world_x": list(world_x),
        "world_z": list(world_z)
    }

if __name__ == "__main__":
    init_db()