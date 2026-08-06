# packets/base_header.py
import struct
from enum import IntEnum

class PacketID(IntEnum):
    MOTION = 0
    SESSION = 1
    LAP_DATA = 2
    EVENT = 3
    PARTICIPANTS = 4
    CAR_SETUPS = 5
    CAR_TELEMETRY = 6
    CAR_STATUS = 7

class Header:
    HEADER_SIZE = 29

    def __init__(self, raw_bytes: bytes):
        if len(raw_bytes) < self.HEADER_SIZE:
            raise ValueError("Raw payload smaller than 29-byte header boundary.")
            
        self.packet_format = struct.unpack_from("<H", raw_bytes, 0)[0]
        
        try:
            self.packet_id = PacketID(raw_bytes[6])
        except ValueError:
            self.packet_id = None
            
        self.session_uid = struct.unpack_from("<Q", raw_bytes, 7)[0]
        self.player_car_index = raw_bytes[27]