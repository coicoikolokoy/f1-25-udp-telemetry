import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

def plot_telemetry_traces(db_path="telemetry.db"):
    # 1. Establish database connection and extract the logged data via SQL
    # We grab data from our high-frequency child table
    query = """
        SELECT id, speed, throttle, brake 
        FROM telemetry_log 
        ORDER BY id ASC
    """
    
    with sqlite3.connect(db_path) as conn:
        # Load the SQL query directly into a convenient Pandas DataFrame pandas structure
        df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("Your telemetry database is currently empty! Run your main receiver pipeline first.")
        return

    print(f"Successfully extracted {len(df)} telemetry rows. Constructing charts...")

    # 2. Setup a dual-plot canvas layout (Subplot 1: Speed, Subplot 2: Pedals)
    # sharex=True locks the timelines together so zooming on speed aligns with the pedals
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.suptitle("F1 25 Engineering Telemetry - Simulated Racing Lap", fontsize=16, fontweight='bold')

    # ---- CHART 1: Velocity Curve ----
    ax1.plot(df['id'], df['speed'], color='gold', linewidth=2, label='Speed (km/h)')
    ax1.set_ylabel("Speed (km/h)", fontsize=12, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='upper right')
    ax1.set_facecolor('#111111') # Dark stealth-style engineering theme background

    # ---- CHART 2: Driver Pedal Inputs (Throttle vs Brake) ----
    ax2.plot(df['id'], df['throttle'], color='limegreen', linewidth=2, label='Throttle %')
    ax2.plot(df['id'], df['brake'], color='crimson', linewidth=2, label='Brake %')
    ax2.set_ylabel("Pedal Position (0.0 - 1.0)", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Time Step (Telemetry Packets @ 60Hz)", fontsize=12, fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper right')
    ax2.set_facecolor('#111111')

    # 3. Format and output the final graphical window visual canvas
    plt.tight_layout()
    
    # Save a high-resolution PNG image directly to your root folder file catalog
    output_img = "telemetry_chart.png"
    plt.savefig(output_img, dpi=300)
    print(f"Success! High-resolution chart exported and saved as: '{output_img}'")
    
    # Launch the interactive popup window window chart to view it live
    plt.show()

if __name__ == "__main__":
    plot_telemetry_traces()
