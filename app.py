# app.py
import sqlite3
from flask import Flask, jsonify, render_template
from config import DB_PATH
from database import get_lap_telemetry_arrays, init_db

app = Flask(__name__)

# Ensure DB schema exists on startup
init_db()


@app.route("/")
def index():
    """Main Full Pit Wall Dashboard (GPS Map + Steering Wheel)."""
    return render_template("index.html")

@app.route("/lite")
def lite():
    """Lite Streamlit-style Telemetry View."""
    return render_template("lite.html")

@app.route("/api/laps", methods=["GET"])
def get_all_laps():
    """Returns a list of all logged lap IDs and track metadata."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.lap_id, l.lap_number, t.track_name, l.created_at
            FROM laps l
            JOIN tracks t ON t.track_id = l.track_id
            ORDER BY l.lap_id DESC
        """)
        rows = cursor.fetchall()

    laps_list = [
        {"lap_id": r[0], "lap_number": r[1], "track_name": r[2], "created_at": r[3]}
        for r in rows
    ]
    return jsonify({"laps": laps_list})


@app.route("/api/telemetry/<int:lap_id>", methods=["GET"])
def get_telemetry_by_lap(lap_id: int):
    """
    Returns high-frequency telemetry sample arrays for a given lap_id,
    ordered by lap_distance ASC.
    """
    data = get_lap_telemetry_arrays(lap_id)
    return jsonify(data)


@app.route("/api/telemetry/latest", methods=["GET"])
def get_latest_telemetry():
    """Fetches telemetry arrays for the most recent active lap."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT lap_id FROM laps ORDER BY lap_id DESC LIMIT 1")
        row = cursor.fetchone()

    if not row:
        return jsonify({
            "lap_id": 0, "lap_distance": [], "speed": [], 
            "throttle": [], "brake": [], "steer": [], 
            "world_x": [], "world_z": []
        })

    latest_lap_id = row[0]
    data = get_lap_telemetry_arrays(latest_lap_id)
    return jsonify(data)


if __name__ == "__main__":
    print("🚀 Starting F1 25 Telemetry Flask API on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5001, debug=True)
