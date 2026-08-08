# tests/export_track_maps.py
import sys
sys.path.append(".")  # Root import resolution

import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

BACKUP_DIR = "backup_data"
MAP_OUTPUT_DIR = os.path.join("static", "images", "maps")
os.makedirs(MAP_OUTPUT_DIR, exist_ok=True)

TRACK_DATABASES = [
    ("Melbourne (Australia)", os.path.join(BACKUP_DIR, "melbourne_telemetry.db")),
    ("Monaco", os.path.join(BACKUP_DIR, "monaco_lap_backup.db")),
    ("Silverstone (Britain)", os.path.join(BACKUP_DIR, "silverstone_telemetry.db")),
    ("Spa-Francorchamps", os.path.join(BACKUP_DIR, "spa_telemetry.db")),
    ("Monza (Italy)", os.path.join(BACKUP_DIR, "monza_telemetry.db")),
    ("Active Session (Root)", "telemetry.db")
]

def export_track_map(track_name: str, db_file: str):
    if not os.path.exists(db_file):
        print(f"⚠️ Skipping {track_name}: '{db_file}' not found.")
        return

    print(f"📍 Extracting spatial coordinates for {track_name} from '{db_file}'...")
    
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        
        # Check if table is telemetry_samples (New Schema) or telemetry_log (Old Schema)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='telemetry_samples';")
        is_new_schema = cursor.fetchone()

        if is_new_schema:
            # 1. Try fetching second-to-last lap (OFFSET 1)
            cursor.execute("SELECT lap_id FROM laps ORDER BY lap_id DESC LIMIT 1 OFFSET 1;")
            row = cursor.fetchone()
            
            # 2. If single-lap database, fallback to the 1 available lap (LIMIT 1)
            if not row:
                cursor.execute("SELECT lap_id FROM laps ORDER BY lap_id DESC LIMIT 1;")
                row = cursor.fetchone()

            if row:
                target_lap_id = row[0]
                query = f"SELECT world_x, world_z FROM telemetry_samples WHERE lap_id = {target_lap_id} AND world_x != 0 AND world_z != 0"
            else:
                query = "SELECT world_x, world_z FROM telemetry_samples WHERE world_x != 0 AND world_z != 0"
        else:
            # Legacy Schema (monaco_lap_backup.db / spa_telemetry.db)
            query = "SELECT world_x, world_z FROM telemetry_log WHERE world_x != 0 AND world_z != 0"

        try:
            df = pd.read_sql_query(query, conn)
        except Exception as e:
            print(f"⚠️ Could not read spatial coordinates from '{db_file}': {e}")
            return

    if df.empty:
        print(f"⚠️ No non-zero spatial (X, Z) coordinates found in '{db_file}'.")
        return

    # Create Dark Mode Stealth Figure
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('#0b0e14')
    ax.set_facecolor('#0b0e14')

    # Plot Cyan Track Path (Equal Aspect Ratio)
    ax.plot(df['world_x'], df['world_z'], color='#00e5ff', linewidth=3.5, label='Circuit Outline')
    
    # Plot Crimson Start/Finish Marker
    ax.scatter(df['world_x'].iloc[0], df['world_z'].iloc[0], color='#ff1744', s=150, zorder=5, label='Start/Finish')

    # Formatting
    ax.set_title(f"F1 25 Reference Circuit Map — {track_name}", color='#ffffff', fontsize=14, fontweight='bold', pad=15)
    ax.axis('equal')
    ax.axis('off')

    file_basename = os.path.basename(db_file).replace('.db', '')
    output_png = os.path.join(MAP_OUTPUT_DIR, f"{file_basename}_map.png")
    plt.savefig(output_png, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    
    print(f"✅ Success! Saved 300 DPI Track Map: '{output_png}'")


def export_all_maps():
    print("\n🗺️ --- F1 25 TRACK MAP EXPORTER ---")
    for track_name, db_file in TRACK_DATABASES:
        export_track_map(track_name, db_file)
    print("✨ Map export process complete!\n")


if __name__ == "__main__":
    export_all_maps()