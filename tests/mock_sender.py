import socket
import struct
import time

TARGET_IP = "127.0.0.1"
TARGET_PORT = 20777

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Injecting valid relational simulation data... Press Ctrl+C to terminate.")

fake_speed = 120
# Mocking a fixed, valid 8-byte session number integer
fake_session_uid = 987654321012345

try:
    while True:
        packet_bytes = bytearray(200)
        packet_bytes[5] = 6  # Packet ID 6
        packet_bytes[27] = 0 # Player car index 0

        # Pack the 8-byte unique identifier directly into offset 6
        struct.pack_into("<Q", packet_bytes, 6, fake_session_uid)

        # Dynamic variable loop
        fake_speed = (fake_speed + 3) if fake_speed < 315 else 120
        
        # Pack mechanical telemetry configurations into driving block array
        packed_metrics = struct.pack("<Hfff", fake_speed, 1.0, 0.0, 0.0)
        packet_bytes[29:29+14] = packed_metrics

        sock.sendto(packet_bytes, (TARGET_IP, TARGET_PORT))
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nSimulation halted.")
