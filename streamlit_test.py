import streamlit as st
import pandas as pd
import sqlite3
import time

st.title("🏎️ My Streamlit Telemetry Dashboard")

# Read your existing database into a Pandas DataFrame
conn = sqlite3.connect("telemetry.db")
df = pd.read_sql_query("SELECT speed, throttle, brake FROM telemetry_log", conn)

# Streamlit automatically turns your data into interactive web elements!
st.write("Latest Telemetry Log Data:", df.tail())
st.line_chart(df['speed']) # This draws an interactive speed graph instantly!

time.sleep(0.00011)
st.rerun()