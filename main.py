import socket
from app.domain.models import TelemetryPacket
from app.domain.database import TelemetryRepository

def main():
    db = TelemetryRepository("telemetry.db")
    print("Relational Database system initialized successfully.")

    UDP_IP = "0.0.0.0" 
    UDP_PORT = 20777
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Network socket bound. Listening on port {UDP_PORT}...")

    try:
        while True:
            raw_bytes, addr = sock.recvfrom(4096)
            packet = TelemetryPacket(raw_bytes)
            
            # Look strictly for Packet ID 1 (F1 25 Car Telemetry)
            if packet.is_car_telemetry():
                # Verify parent session is logged in the database
                db.create_session_if_missing(packet.session_uid, track_id=1, weather_id=0)
                
                # Unpack velocity, gas, and braking variables
                player_metrics = packet.unpack_player_data()
                
                # Commit straight to your SQLite child table logs
                db.save_entry(packet.session_uid, player_metrics)
                
                # Print clean, scrolling trace lines onto the screen
                print(f"🏎️ TRACKING LIVE -> {player_metrics}", flush=True)
                
    except KeyboardInterrupt:
        print("\nLogging stopped cleanly.")

if __name__ == "__main__":
    main()
