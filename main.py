import socket
from app.domain.models import TelemetryPacket
from app.domain.database import TelemetryRepository

def main():
    # 1. Initialize the relational database layout
    db = TelemetryRepository("telemetry.db")
    print("Database system initialized successfully.")

    # 2. Setup the loopback socket to receive your data stream
    UDP_IP = "127.0.0.1" 
    UDP_PORT = 20777
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Network socket bound. Listening on port {UDP_PORT}...")

    # 3. Continuous processing loop
    try:
        while True:
            raw_bytes, addr = sock.recvfrom(2048)
            packet = TelemetryPacket(raw_bytes)
            
            # Filter for Packet ID 6 (Car Telemetry)
            if packet.is_car_telemetry():
                # First, ensure the parent session row exists (INFOSYS 220 rule)
                db.create_session_if_missing(packet.session_uid, track_id=1, weather_id=0)
                
                # Second, unpack the mechanical attributes from the player's car block
                player_metrics = packet.unpack_player_data()
                
                # Third, save the entry bound strictly to that session UID via foreign keys
                db.save_entry(packet.session_uid, player_metrics)
                
                # Immediately push the scrolling trace updates live onto your screen
                print(f"Logged [Session: {packet.session_uid[-6:]}] -> {player_metrics}", flush=True)
                
    except KeyboardInterrupt:
        print("\nLogging stopped cleanly. Telemetry tables are saved.")

if __name__ == "__main__":
    main()
