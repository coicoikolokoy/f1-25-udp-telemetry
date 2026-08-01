from enum import Enum
import struct

class PacketID(Enum):
    """Official Specification Packet IDs provided by the Developer Document."""
    MOTION = 0
    SESSION = 1
    LAP_DATA = 2
    EVENT = 3
    PARTICIPANTS = 4
    CAR_SETUPS = 5
    CAR_TELEMETRY = 6       # Confirmed official telemetry packet ID
    CAR_STATUS = 7
    FINAL_CLASSIFICATION = 8
    LOBBY_INFO = 9
    CAR_DAMAGE = 10
    SESSION_HISTORY = 11

class CarTelemetry:
    def __init__(self, speed: int, throttle: float, brake: float):
        self.speed = speed          
        self.throttle = throttle    
        self.brake = brake          

    def __repr__(self):
        return f"<CarTelemetry Speed={self.speed}km/h T={self.throttle:.2f} B={self.brake:.2f}>"

class TelemetryPacket:
    # UPDATED: F1 25 structural header size boundary is exactly 29 bytes
    HEADER_SIZE = 29  
    CAR_STRUCT_SIZE = 60 

    def __init__(self, raw_bytes: bytes):
        self.raw_bytes = raw_bytes
        
        # UPDATED: m_packetId moved to Index 6
        try:
            self.packet_id = PacketID(raw_bytes[6])
        except (ValueError, IndexError):
            self.packet_id = None

        # UPDATED: m_sessionUID shifted to Index range 7 through 15
        try:
            session_raw = struct.unpack("<Q", raw_bytes[7:15])
            self.session_uid = str(session_raw[0])
        except Exception:
            self.session_uid = "0"

        # UPDATED: m_playerCarIndex pushed back to Index 27
        try:
            self.player_car_index = raw_bytes[27]
        except IndexError:
            self.player_car_index = 0

    def is_car_telemetry(self) -> bool:
        return self.packet_id == PacketID.CAR_TELEMETRY

    def unpack_player_data(self) -> CarTelemetry:
        if not self.is_car_telemetry():
            raise ValueError("Not a telemetry packet.")

        # Calculate exactly where your car's slice block begins
        start_offset = self.HEADER_SIZE + (self.player_car_index * self.CAR_STRUCT_SIZE)
        
        # Extract Speed (uint16), Throttle (float), Steer (float), Brake (float)
        car_data_slice = self.raw_bytes[start_offset : start_offset + 14]
        speed, throttle, steer, brake = struct.unpack("<Hfff", car_data_slice)

        return CarTelemetry(speed=speed, throttle=throttle, brake=brake)
