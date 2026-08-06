# streamlit_test.py
import streamlit as st
import pandas as pd
import sqlite3
import time
from config import DB_PATH

st.set_page_config(page_title="F1 25 Telemetry Dashboard", page_icon="🏎️", layout="wide")

st.title("🏎️ F1 25 Real-Time Telemetry Dashboard")

# 1. Connect to SQLite
conn = sqlite3.connect(DB_PATH)

# 2. Fetch all available laps for the sidebar selector
try:
    laps_df = pd.read_sql_query("SELECT lap_id, lap_number, created_at FROM laps ORDER BY lap_id DESC", conn)
except Exception:
    laps_df = pd.DataFrame()

if laps_df.empty:
    st.warning("No lap sessions found in database! Make sure main.py and mock_sender.py are running.")
    time.sleep(2)
    st.rerun()

# Sidebar: Select Lap Session
st.sidebar.header("Lap Session Selector")
selected_lap_id = st.sidebar.selectbox(
    "Active Lap ID:", 
    options=laps_df['lap_id'].tolist(),
    format_func=lambda x: f"Lap Session #{x}"
)

# 3. Query telemetry samples for selected lap_id
query = """
    SELECT lap_distance, speed, throttle, brake, steer, world_x, world_z
    FROM telemetry_samples
    WHERE lap_id = ?
    ORDER BY lap_distance ASC
"""
df = pd.read_sql_query(query, conn, params=(selected_lap_id,))

if not df.empty:
    # Top KPI Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Top Speed", f"{int(df['speed'].max())} km/h")
    col2.metric("Max Throttle", f"{int(df['throttle'].max() * 100)}%")
    col3.metric("Max Brake", f"{int(df['brake'].max() * 100)}%")
    col4.metric("Logged Samples", f"{len(df)} rows")

    # Chart 1: Velocity Curve vs Lap Distance
    st.subheader("🏎️ Speed Profile (km/h) vs Lap Distance (m)")
    st.line_chart(df.set_index('lap_distance')['speed'])

    # Chart 2: Driver Pedal Inputs (Throttle, Brake, Steer) vs Lap Distance
    st.subheader("🎮 Pedal Inputs & Steering Angle vs Lap Distance (m)")
    st.line_chart(df.set_index('lap_distance')[['throttle', 'brake', 'steer']])

    # Table View
    with st.expander("📄 Raw Telemetry Data Tail"):
        st.dataframe(df.tail(10))

else:
    st.info(f"Waiting for telemetry samples for Lap ID #{selected_lap_id}...")

conn.close()

# Refresh loop (1 second interval to keep CPU usage low)
time.sleep(1.0)
st.rerun()