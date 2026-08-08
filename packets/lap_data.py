# packets/lap_data.py
import struct
from .base_header import Header
from config import HEADER_SIZE, CAR_LAP_STRUCT_SIZE

class LapData:
    def __init__(self, raw_bytes: bytes, header: Header):
        # Force player car index to 0 for single-player / time-trial stability
        player_idx = header.player_car_index if header.player_car_index < 22 else 0
        offset = HEADER_SIZE + (player_idx * CAR_LAP_STRUCT_SIZE)
        
        # Offsets verified directly from F1 25 PDF Spec (Page 5 & 6):
        # Offset 20: m_lapDistance (float)
        # Offset 33: m_currentLapNum (uint8)
        lap_distance, = struct.unpack_from("<f", raw_bytes, offset + 20)
        current_lap_num = raw_bytes[offset + 33]
        
        # SANITY FILTER: Valid track distances are strictly between 0m and 10,000m
        if 0.0 <= lap_distance <= 10000.0:
            self.lap_distance = lap_distance
        else:
            self.lap_distance = 0.0  # Reject garbage out-of-bounds floats

        # SANITY FILTER: Lap numbers in a session are between 0 and 200
        self.current_lap_num = current_lap_num if current_lap_num < 200 else 0