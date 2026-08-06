# list_laps.py
import sqlite3
import pandas as pd
from config import DB_PATH

def list_saved_laps(db_path=DB_PATH):
    query = """
        SELECT 
            l.lap_id,
            t.track_name,
            l.lap_number,
            COUNT(ts.sample_id) as total_logged_samples,
            l.created_at
        FROM laps l
        JOIN tracks t ON t.track_id = l.track_id
        LEFT JOIN telemetry_samples ts ON ts.lap_id = l.lap_id
        GROUP BY l.lap_id
        ORDER BY l.lap_id DESC;
    """
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("No laps found in database.")
    else:
        print("\n--- SAVED TELEMETRY LAPS ---")
        print(df.to_string(index=False))

if __name__ == "__main__":
    list_saved_laps()