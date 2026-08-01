import socket
import struct
import time

TARGET_IP = "127.0.0.1"
TARGET_PORT = 20777

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Injecting realistic racing lap simulation... Press Ctrl+C to stop.")

# Simulation State Variables
fake_session_uid = 987654321012345
speed = 100.0       # Current velocity (km/h)
throttle = 1.0      # Gas pedal position (0.0 to 1.0)
brake = 0.0         # Brake pedal position (0.0 to 1.0)
steer = 0.0         # Steering angle (-1.0 to 1.0)
timer = 0           # Incremental step timer to map out track sectors

try:
    while True:
        timer += 1
        packet_bytes = bytearray(200)
        packet_bytes[5] = 6   # Packet ID 6 (Car Telemetry)
        packet_bytes[27] = 0  # Player index 0
        struct.pack_into("<Q", packet_bytes, 6, fake_session_uid)

        # SIMULATION LOGIC: Map out a dynamic racing circuit layout over a 20-second loop
        # (Running at 20Hz means 20 steps per second, so 400 total step intervals)
        loop_step = timer % 400

        if loop_step < 160:
            # 1. THE MAIN STRAIGHT (0 to 8 seconds): Full throttle acceleration
            throttle = 1.0
            brake = 0.0
            steer = 0.0
            speed += 1.8 if speed < 320 else 0.2  # Accelerating towards top velocity

        elif loop_step < 220:
            # 2. HEAVY BRAKING ZONE FOR TURN 1 (8 to 11 seconds): Slam brakes, ease off gas
            throttle = 0.0
            brake = 1.0
            steer = 0.1  # Slight turn-in preparation
            speed -= 3.5 if speed > 80 else 0.5   # Rapidly shedding velocity

        elif loop_step < 320:
            # 3. APEX CORNERING TRAILING (11 to 16 seconds): Feather throttle, sharp steering
            throttle = 0.3
            brake = 0.0
            steer = 0.6  # Holding the steering wheel sharp into the corner apex
            # Stabilise around mid-cornering speed parameters
            if speed > 110: speed -= 1.0
            elif speed < 100: speed += 0.5

        else:
            # 4. CORNER EXIT ACCELERATION (16 to 20 seconds): Straighten wheel, launch away
            throttle = 1.0
            brake = 0.0
            steer = max(0.0, steer - 0.1) # Smoothly unwinding the steering wheel lock
            speed += 1.2                  # Powering out back onto the next straight

        # Pack values into the standard little-endian byte array blueprint layout
        # Speed requires an integer, pedal metrics require 32-bit floating values
        packed_metrics = struct.pack("<Hfff", int(speed), throttle, steer, brake)
        packet_bytes[29:29+14] = packed_metrics

        sock.sendto(packet_bytes, (TARGET_IP, TARGET_PORT))
        time.sleep(0.05) # Maintain a strict 20Hz telemetry broadcast cadence rate

except KeyboardInterrupt:
    print("\nRacing track simulator halted cleanly.")
