# tests/data_viewer.py
import sys
sys.path.append(".")  # Root import resolution

import argparse
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from config import DB_PATH

def plot_telemetry_traces(mode="latest", lap_id=None, db_path=DB_PATH):
    with sqlite3.connect(db_path) as conn:
        
        # --- MODE 1: FULL STINT MODE (All Laps across Time) ---
        if mode == "all":
            query = "SELECT sample_id, speed, throttle, brake FROM telemetry_samples ORDER BY sample_id ASC"
            df = pd.read_sql_query(query, conn)
            x_axis = 'sample_id'
            x_label = "Time Step (Telemetry Packets @ 60Hz)"
            title_text = "F1 25 Telemetry - Full Driving Stint Overview"
            output_img = "telemetry_full_stint.png"

        # --- MODE 2: SINGLE LAP MODE (Targeted Lap by Distance) ---
        else:
            if lap_id is None:
                lap_df = pd.read_sql_query("SELECT lap_id FROM laps ORDER BY lap_id DESC LIMIT 1", conn)
                if lap_df.empty:
                    print("No laps found in database! Run main.py first.")
                    return
                lap_id = int(lap_df.iloc[0]['lap_id'])

            query = """
                SELECT lap_distance, speed, throttle, brake 
                FROM telemetry_samples 
                WHERE lap_id = ?
                ORDER BY lap_distance ASC
            """
            df = pd.read_sql_query(query, conn, params=(lap_id,))
            x_axis = 'lap_distance'
            x_label = "Lap Distance (meters)"
            title_text = f"F1 25 Telemetry - Lap ID #{lap_id}"
            output_img = f"telemetry_lap_{lap_id}.png"

    if df.empty:
        print("No telemetry samples found.")
        return

    print(f"Extracted {len(df)} samples ({title_text}). Rendering Matplotlib charts...")

    # Subplot 1: Speed | Subplot 2: Pedals
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.suptitle(title_text, fontsize=16, fontweight='bold')

    # Chart 1: Speed Curve
    ax1.plot(df[x_axis], df['speed'], color='gold', linewidth=2, label='Speed (km/h)')
    ax1.set_ylabel("Speed (km/h)", fontsize=12, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='upper right')
    ax1.set_facecolor('#111111')

    # Chart 2: Driver Pedals (Throttle & Brake)
    ax2.plot(df[x_axis], df['throttle'], color='limegreen', linewidth=2, label='Throttle %')
    ax2.plot(df[x_axis], df['brake'], color='crimson', linewidth=2, label='Brake %')
    ax2.set_ylabel("Pedal Position (0.0 - 1.0)", fontsize=12, fontweight='bold')
    ax2.set_xlabel(x_label, fontsize=12, fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper right')
    ax2.set_facecolor('#111111')

    plt.tight_layout()
    plt.savefig(output_img, dpi=300)
    print(f"Success! High-resolution chart exported as: '{output_img}'")
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="F1 25 Telemetry Plotter")
    
    # Flag 1: Plot all laps across time
    parser.add_argument("--all", action="store_true", help="Plot full multi-lap stint overview across time")
    
    # Flag 2: Pass a specific Lap ID integer (e.g. --lap 2 or -l 2)
    parser.add_argument("--lap", "-l", type=int, help="Plot a specific Lap ID (e.g. --lap 2)")
    
    args = parser.parse_args()

    if args.all:
        plot_telemetry_traces(mode="all")
    elif args.lap:
        plot_telemetry_traces(mode="latest", lap_id=args.lap)  # Plots requested Lap ID!
    else:
        plot_telemetry_traces(mode="latest")                    # Defaults to latest active lap!