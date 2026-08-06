# packets/telemetry.py
import struct
from .base_header import Header
from config import HEADER_SIZE, CAR_TELEMETRY_STRUCT_SIZE

class CarTelemetryData:
    def __init__(self, raw_bytes: bytes, header: Header):
        # Calculate dynamic player car block offset
        offset = HEADER_SIZE + (header.player_car_index * CAR_TELEMETRY_STRUCT_SIZE)
        
        # Unpack 14 bytes: Speed (uint16), Throttle (float), Steer (float), Brake (float)
        speed, throttle, steer, brake = struct.unpack_from("<Hfff", raw_bytes, offset)
        
        self.speed = speed
        self.throttle = throttle
        self.steer = steer
        self.brake = brake