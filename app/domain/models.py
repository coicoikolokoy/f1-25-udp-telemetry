from enum import Enum
import struct

class PacketID(Enum):
    MOTION = 0
    SESSION = 1
    LAP_DATA = 2
    PARTICIPANTS = 4
    CAR_TELEMETRY = 6
    CAR_STATUS = 7
    DAMAGE = 10

class CarTelemetry:
    def __init__(self, speed: int, throttle: float, brake: float):
        self.speed = speed          
        self.throttle = throttle    
        self.brake = brake          

    def __repr__(self):
        return f"<CarTelemetry Speed={self.speed}km/h T={self.throttle:.2f} B={self.brake:.2f}>"

class TelemetryPacket:
    HEADER_SIZE = 29
    CAR_STRUCT_SIZE = 60 

    def __init__(self, raw_bytes: bytes):
        self.raw_bytes = raw_bytes
        
        # Byte index 5 is packet type
        try:
            self.packet_id = PacketID(raw_bytes[5])
        except (ValueError, IndexError):
            self.packet_id = None

        # Extract 8-byte session UID at index 6
        try:
            session_raw = struct.unpack("<Q", raw_bytes[6:14])[0]
            self.session_uid = str(session_raw)
        except Exception:
            self.session_uid = "0"

        # Byte index 27 is player car index
        self.player_car_index = raw_bytes[27] if len(raw_bytes) > 27 else 0

    def is_car_telemetry(self) -> bool:
        return self.packet_id == PacketID.CAR_TELEMETRY

    def unpack_player_data(self) -> CarTelemetry:
        if not self.is_car_telemetry():
            raise ValueError("Not a telemetry packet.")

        start_offset = self.HEADER_SIZE + (self.player_car_index * self.CAR_STRUCT_SIZE)
        car_data_slice = self.raw_bytes[start_offset : start_offset + 14]
        speed, throttle, steer, brake = struct.unpack("<Hfff", car_data_slice)

        return CarTelemetry(speed=speed, throttle=throttle, brake=brake)
