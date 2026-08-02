import socket
import struct
import time

TARGET_IP = "127.0.0.1"
TARGET_PORT = 20777

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Injecting F1 25 structural racing lap simulation... Press Ctrl+C to stop.")

# Simulation State Parameters
fake_session_uid = 987654321012345
speed = 100.0       # Current velocity (km/h)
throttle = 1.0      # Gas pedal position (0.0 to 1.0)
brake = 0.0         # Brake pedal position (0.0 to 1.0)
steer = 0.0         # Steering angle (-1.0 to 1.0)
timer = 0           # Incremental step timer to map out track sectors

try:
    while True:
        timer += 1
        # F1 25 Telemetry packets are massive arrays holding 22 car blocks
        packet_bytes = bytearray(1400)
        
        # --- BUILD OFFICIAL F1 25 HEADER (29 BYTES) ---
        # Byte 0-1: packetFormat (uint16) -> 2025
        struct.pack_into("<H", packet_bytes, 0, 2025)
        # Byte 2: gameMajorVersion (uint8)
        packet_bytes[2] = 1
        # Byte 3: gameMinorVersion (uint8)
        packet_bytes[3] = 0
        # Byte 4: packetVersion (uint8)
        packet_bytes[4] = 1
        # Byte 5: m_packetVersion (uint8) -> legacy slot, left at 0
        packet_bytes[5] = 0
        # Byte 6: m_packetId (uint8) -> SET TO 6 FOR CAR TELEMETRY!
        packet_bytes[6] = 6
        # Byte 7-14: m_sessionUID (uint64) -> Packed directly across index 7:15
        struct.pack_into("<Q", packet_bytes, 7, fake_session_uid)
        # Byte 27: m_playerCarIndex (uint8) -> Target player car index slot position
        packet_bytes[27] = 0

        # --- SIMULATION PHYSICS ENGINE LAYOUT (20HZ CIRCUIT LOOP) ---
        loop_step = timer % 400

        if loop_step < 160:
            # 1. THE MAIN STRAIGHT: Full throttle acceleration
            throttle = 1.0
            brake = 0.0
            steer = 0.0
            speed += 1.8 if speed < 320 else 0.2

        elif loop_step < 220:
            # 2. HEAVY BRAKING ZONE: Slam brakes, drop gas completely
            throttle = 0.0
            brake = 1.0
            steer = 0.1
            speed -= 3.5 if speed > 80 else 0.5

        elif loop_step < 320:
            # 3. CORNER APEX TRAILING: Feather throttle around bend
            throttle = 0.3
            brake = 0.0
            steer = 0.6
            if speed > 110: speed -= 1.0
            elif speed < 100: speed += 0.5

        else:
            # 4. CORNER EXIT ACCELERATION: Power out back onto straight
            throttle = 1.0
            brake = 0.0
            steer = max(0.0, steer - 0.1)
            speed += 1.2

        # --- PACK MECHANICAL METRICS INTO THE PLAYER CAR BLOCK ---
        # F1 25 telemetry structure block offset starts exactly at index 29 (HEADER_SIZE)
        start_offset = 29 + (0 * 60) # player_car_index is 0, car block size is 60 bytes
        
        # Pack Speed (uint16), Throttle (float), Steer (float), Brake (float)
        packed_metrics = struct.pack("<Hfff", int(speed), throttle, steer, brake)
        packet_bytes[start_offset : start_offset + 14] = packed_metrics

        # Fire packet into local loopback socket network
        sock.sendto(packet_bytes, (TARGET_IP, TARGET_PORT))
        time.sleep(0.05) # Maintain a strict 20Hz cadence 

except KeyboardInterrupt:
    print("\nF1 25 simulation loop halted cleanly.")
