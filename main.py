import socket
from app.domain.models import TelemetryPacket
from app.domain.database import TelemetryRepository

def main():
    # MOVE THIS TO LINE 1: Initialize the database setup first!
    db = TelemetryRepository("telemetry.db")
    print("Database system initialized successfully.") # Diagnostic print

    # Setup the network sockets second
    UDP_IP = "127.0.0.1" # Change to local loopback to guarantee local connection
    UDP_PORT = 20777
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Network socket bound. Listening on port {UDP_PORT}...")

    try:
        while True:
            raw_bytes, addr = sock.recvfrom(2048)
            packet = TelemetryPacket(raw_bytes)
            
            if packet.is_car_telemetry():
                player_metrics = packet.unpack_player_data()
                db.save_entry(player_metrics)
                # Flush the print line immediately to the terminal screen
                print(f"Logged to Database -> {player_metrics}", flush=True)
                
    except KeyboardInterrupt:
        print("\nLogging stopped cleanly.")

if __name__ == "__main__":
    main()
