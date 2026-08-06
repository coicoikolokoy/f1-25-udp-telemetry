# streamlit_test.py (or tests/streamlit_test.py)
import streamlit as st
import pandas as pd
import sqlite3
import time
from config import DB_PATH

st.set_page_config(page_title="F1 25 Telemetry Inspector", page_icon="🏎️", layout="wide")

st.title("🏎️ F1 25 Telemetry Data Inspector")
st.caption("Post-Session Lap Analytics & Raw Data Export Tool")

# 1. Connect to SQLite
conn = sqlite3.connect(DB_PATH)

# 2. Fetch Laps
try:
    laps_df = pd.read_sql_query("SELECT lap_id, lap_number, created_at FROM laps ORDER BY lap_id DESC", conn)
except Exception:
    laps_df = pd.DataFrame()

if laps_df.empty:
    st.warning("No lap sessions found in database! Make sure main.py and mock_sender.py are running.")
    st.stop()

# Sidebar: Select Lap Session
st.sidebar.header("Session Inspector")
selected_lap_id = st.sidebar.selectbox(
    "Active Lap Session:", 
    options=laps_df['lap_id'].tolist(),
    format_func=lambda x: f"Lap Session #{x}"
)

# 3. Query telemetry samples for selected lap
query = """
    SELECT lap_distance, speed, throttle, brake
    FROM telemetry_samples
    WHERE lap_id = ?
    ORDER BY lap_distance ASC
"""
df = pd.read_sql_query(query, conn, params=(selected_lap_id,))

if not df.empty:
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Top Speed", f"{int(df['speed'].max())} km/h")
    col2.metric("Max Throttle", f"{int(df['throttle'].max() * 100)}%")
    col3.metric("Max Brake", f"{int(df['brake'].max() * 100)}%")
    col4.metric("Logged Samples", f"{len(df)} rows")

    # Chart 1: Speed Profile
    st.subheader("🏎️ Speed Profile (km/h) vs Lap Distance (m)")
    st.line_chart(df.set_index('lap_distance')['speed'])

    # Chart 2: Driver Pedals Only (Throttle vs Brake)
    st.subheader("🎮 Driver Pedal Inputs (Throttle vs Brake)")
    st.line_chart(df.set_index('lap_distance')[['throttle', 'brake']])

    # Interactive Data Inspector & CSV Export
    st.subheader("📄 Raw Telemetry Sample Table")
    st.dataframe(df, use_container_width=True)

    # Download CSV Button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Lap Telemetry as CSV",
        data=csv,
        file_name=f"f1_25_telemetry_lap_{selected_lap_id}.csv",
        mime="text/csv"
    )

else:
    st.info(f"Waiting for telemetry samples for Lap Session #{selected_lap_id}...")

conn.close()

# Refresh loop (1 second interval)
time.sleep(1.0)
st.rerun()