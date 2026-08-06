# packets/motion.py
import struct
from .base_header import Header
from config import HEADER_SIZE, CAR_MOTION_STRUCT_SIZE

class MotionData:
    def __init__(self, raw_bytes: bytes, header: Header):
        offset = HEADER_SIZE + (header.player_car_index * CAR_MOTION_STRUCT_SIZE)
        
        # Unpack World X (float), World Y (float), World Z (float) coordinates
        world_x, world_y, world_z = struct.unpack_from("<fff", raw_bytes, offset)
        
        self.world_x = world_x
        self.world_z = world_z