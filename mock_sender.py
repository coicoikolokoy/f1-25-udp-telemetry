# tests/mock_sender.py
import socket
import struct
import time
import math

TARGET_IP = "127.0.0.1"
TARGET_PORT = 20777

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Injecting F1 25 Multi-Packet Racing Simulation (Motion, LapData, Telemetry)...")
print("Press Ctrl+C to stop.")

# Simulation State Parameters
fake_session_uid = 987654321012345
speed = 100.0          # Velocity (km/h)
throttle = 1.0         # Gas pedal (0.0 to 1.0)
brake = 0.0            # Brake pedal (0.0 to 1.0)
steer = 0.0            # Steering angle (-1.0 to 1.0)
lap_distance = 0.0     # Lap distance around track (meters)
current_lap_num = 1    # Active lap counter
timer = 0              # Loop step timer

def build_header(packet_id: int) -> bytearray:
    """Builds official 29-byte F1 25 base header."""
    packet_bytes = bytearray(1400)
    struct.pack_into("<H", packet_bytes, 0, 2025)     # packetFormat
    packet_bytes[2] = 1                              # gameMajorVersion
    packet_bytes[3] = 0                              # gameMinorVersion
    packet_bytes[4] = 1                              # packetVersion
    packet_bytes[5] = 0                              # m_packetVersion
    packet_bytes[6] = packet_id                      # m_packetId (0, 2, or 6)
    struct.pack_into("<Q", packet_bytes, 7, fake_session_uid)  # m_sessionUID
    packet_bytes[27] = 0                             # m_playerCarIndex
    return packet_bytes

try:
    while True:
        timer += 1
        loop_step = timer % 400

        # --- 1. SIMULATE VEHICLE PHYSICS & DISTANCE ---
        if loop_step < 160:
            # Main Straight
            throttle = 1.0
            brake = 0.0
            steer = 0.0
            speed += 1.8 if speed < 320 else 0.2
        elif loop_step < 220:
            # Heavy Braking Zone
            throttle = 0.0
            brake = 1.0
            steer = 0.15
            speed -= 3.5 if speed > 80 else 0.5
        elif loop_step < 320:
            # Corner Apex Trailing
            throttle = 0.3
            brake = 0.0
            steer = 0.5
            speed += 0.5 if speed < 110 else -1.0
        else:
            # Corner Exit Acceleration
            throttle = 1.0
            brake = 0.0
            steer = max(0.0, steer - 0.1)
            speed += 1.2

        # Increment distance based on speed (Spa circuit loop is ~7004 meters)
        lap_distance += (speed / 3.6) * 0.05  # meters moved in 50ms interval
        
        # Check for Lap Completion (7000 meters = new lap!)
        if lap_distance >= 7000.0:
            lap_distance = 0.0
            current_lap_num += 1
            print(f"\n🏁 SIMULATOR COMPLETED LAP! Advancing to Lap #{current_lap_num}\n")

        # Simulate 2D GPS World Coordinates (Elliptical track loop)
        angle = (lap_distance / 7000.0) * (2 * math.pi)
        world_x = math.sin(angle) * 500.0
        world_z = math.cos(angle) * 1000.0

        # --- 2. PACKET ID 0: MOTION DATA (GPS World Coordinates) ---
        motion_packet = build_header(packet_id=0)
        offset_m = 29 + (0 * 60)
        struct.pack_into("<fff", motion_packet, offset_m, world_x, 0.0, world_z)
        sock.sendto(motion_packet, (TARGET_IP, TARGET_PORT))

        # --- 3. PACKET ID 2: LAP DATA (Lap Distance & Lap Number) ---
        lap_packet = build_header(packet_id=2)
        offset_l = 29 + (0 * 57)
        struct.pack_into("<f", lap_packet, offset_l + 12, float(lap_distance))
        lap_packet[offset_l + 26] = current_lap_num
        sock.sendto(lap_packet, (TARGET_IP, TARGET_PORT))

        # --- 4. PACKET ID 6: CAR TELEMETRY (Mechanical Metrics) ---
        telemetry_packet = build_header(packet_id=6)
        offset_t = 29 + (0 * 60)
        packed_metrics = struct.pack("<Hfff", int(speed), throttle, steer, brake)
        telemetry_packet[offset_t : offset_t + 14] = packed_metrics
        sock.sendto(telemetry_packet, (TARGET_IP, TARGET_PORT))

        time.sleep(0.05)  # Maintain 20Hz simulation cadence

except KeyboardInterrupt:
    print("\nF1 25 simulation loop halted cleanly.")