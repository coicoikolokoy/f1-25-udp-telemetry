# config.py
"""Centralized configuration parameters for the F1 25 Telemetry Platform."""

UDP_IP = "0.0.0.0"
UDP_PORT = 20777
BUFFER_SIZE = 4096
DB_PATH = "telemetry.db"

# F1 25 Protocol Structural Boundaries
HEADER_SIZE = 29
CAR_TELEMETRY_STRUCT_SIZE = 60
CAR_MOTION_STRUCT_SIZE = 60
CAR_LAP_STRUCT_SIZE = 56