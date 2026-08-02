import sqlite3
import pandas as pd

def list_saved_sessions(db_path="telemetry.db"):
    # SQL query to count how many data rows are saved under each unique session ID
    query = """
        SELECT session_uid, COUNT(*) as total_logged_rows
        FROM telemetry_log tl
        JOIN game_sessions gs ON gs.session_uid = tl.session_uid
        GROUP BY session_uid
    """
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("No sessions found in the database.")
    else:
        print("\n--- SAVED TELEMETRY SESSIONS ---")
        print(df.to_string(index=False))

if __name__ == "__main__":
    list_saved_sessions()
