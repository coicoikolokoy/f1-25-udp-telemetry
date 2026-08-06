# packets/lap_data.py
import struct
from .base_header import Header
from config import HEADER_SIZE, CAR_LAP_STRUCT_SIZE

class LapData:
    def __init__(self, raw_bytes: bytes, header: Header):
        offset = HEADER_SIZE + (header.player_car_index * CAR_LAP_STRUCT_SIZE)
        
        # Extract lap distance (float at offset + 12) and current lap number (uint8 at offset + 26)
        lap_distance, = struct.unpack_from("<f", raw_bytes, offset + 12)
        current_lap_num = raw_bytes[offset + 26]
        
        self.lap_distance = lap_distance
        self.current_lap_num = current_lap_num