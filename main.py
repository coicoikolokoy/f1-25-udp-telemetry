# main.py
import socket
import sys
from config import UDP_IP, UDP_PORT, BUFFER_SIZE
from database import init_db, create_new_lap, insert_telemetry_sample
from packets import Header, PacketID, CarTelemetryData, MotionData, LapData

def main():
    # 1. Ensure database schema is initialized
    init_db()
    print("Database system initialized.")

    # 2. Bind UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Network socket bound. Listening on {UDP_IP}:{UDP_PORT}...")

    # State tracking parameters
    current_track_id = 11  # Default to Spa-Francorchamps (or update dynamically)
    active_lap_num = None
    active_lap_id = None

    # Transient buffers to align multi-packet data before DB insert
    latest_motion = None
    latest_lap_data = None

    try:
        while True:
            raw_bytes, addr = sock.recvfrom(BUFFER_SIZE)
            
            try:
                header = Header(raw_bytes)
            except ValueError:
                continue  # Skip corrupt/malformed datagrams

            # --- PACKET TYPE 0: MOTION DATA (GPS World Coordinates) ---
            if header.packet_id == PacketID.MOTION:
                latest_motion = MotionData(raw_bytes, header)

            # --- PACKET TYPE 2: LAP DATA (Lap Distance & Lap Numbers) ---
            # In main.py under PACKET TYPE 2 (LAP DATA):
            elif header.packet_id == PacketID.LAP_DATA:
                latest_lap_data = LapData(raw_bytes, header)
                
                # 1. Startup: Create initial lap session (e.g. Lap 1)
                if active_lap_id is None:
                    active_lap_num = latest_lap_data.current_lap_num
                    active_lap_id = create_new_lap(current_track_id, active_lap_num)
                    print(f"🏎️ SESSION STARTED: Lap #{active_lap_num} (lap_id={active_lap_id})")

                # 2. Sequential Check: Create a new lap ONLY when lap number genuinely advances (+1)
                elif latest_lap_data.current_lap_num == active_lap_num + 1:
                    active_lap_num = latest_lap_data.current_lap_num
                    active_lap_id = create_new_lap(current_track_id, active_lap_num)
                    print(f"🏁 NEW LAP DETECTED: Lap #{active_lap_num} (Created lap_id={active_lap_id})")

            # --- PACKET TYPE 6: CAR TELEMETRY (Mechanical Metrics) ---
            elif header.packet_id == PacketID.CAR_TELEMETRY:
                # Gate Check 1: We must have an active lap_id and valid lap data
                if active_lap_id is None or latest_lap_data is None:
                    continue

                # Gate Check 2: Pre-Start Filter (Ignore negative lap distances before start line)
                if latest_lap_data.lap_distance < 0:
                    continue

                telemetry = CarTelemetryData(raw_bytes, header)

                # Pull spatial coordinates from motion buffer if available
                world_x = latest_motion.world_x if latest_motion else 0.0
                world_z = latest_motion.world_z if latest_motion else 0.0

                # Commit sample directly to SQLite
                insert_telemetry_sample(
                    lap_id=active_lap_id,
                    lap_distance=latest_lap_data.lap_distance,
                    speed=telemetry.speed,
                    throttle=telemetry.throttle,
                    brake=telemetry.brake,
                    steer=telemetry.steer,
                    world_x=world_x,
                    world_z=world_z
                )

                print(
                    f"🏎️ LAP #{active_lap_num} [{latest_lap_data.lap_distance:.1f}m] -> "
                    f"Speed: {telemetry.speed} km/h | T: {telemetry.throttle:.2f} | "
                    f"B: {telemetry.brake:.2f} | Steer: {telemetry.steer:.2f}",
                    flush=True
                )

    except KeyboardInterrupt:
        print("\nTelemetry ingestion stopped cleanly.")
        sock.close()

if __name__ == "__main__":
    main()