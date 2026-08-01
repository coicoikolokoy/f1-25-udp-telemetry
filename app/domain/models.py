# Add or update this property block inside your existing TelemetryPacket class
class TelemetryPacket:
    HEADER_SIZE = 29
    CAR_STRUCT_SIZE = 60

    def __init__(self, raw_bytes: bytes):
        self.raw_bytes = raw_bytes
        
        # Extract packet ID (byte 5)
        raw_id = raw_bytes[5]
        try:
            self.packet_id = PacketID(raw_id)
        except ValueError:
            self.packet_id = None

        # COMPSCI 210 style: Extract the 8-byte Unsigned Long Long (Q) at offset 6
        # This gives us the absolute unique identifier for the current race weekend
        session_raw = struct.unpack("<Q", raw_bytes[6:14])[0]
        self.session_uid = str(session_raw)

        # Extract player car index (byte 27)
        self.player_car_index = raw_bytes[27]

    def is_car_telemetry(self) -> bool:
        return self.packet_id == PacketID.CAR_TELEMETRY
