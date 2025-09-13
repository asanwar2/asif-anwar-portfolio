import csv
import time
import random
import argparse
from datetime import datetime

# --- Configuration ---
FILE_PATH = "reactor_data.csv"
FIELDNAMES = ["timestamp", "power_mw", "temperature_c", "rod_position_mm"]

# --- Normal Operating Ranges ---
POWER_NORMAL = (0.8, 1.2)
TEMP_NORMAL = (80, 100)
ROD_NORMAL = (150, 200)

# --- Warning Levels ---
POWER_WARN = 1.5
TEMP_WARN = 110
ROD_WARN_LOWER = 100

# --- Danger Levels ---
POWER_DANGER = 1.8
TEMP_DANGER = 125
ROD_DANGER_LOWER = 50

# --- Simulation Parameters ---
UPDATE_INTERVAL_SECONDS = 1

def generate_initial_data():
    """Generates a starting point for the data."""
    return {
        "power_mw": round(random.uniform(*POWER_NORMAL), 2),
        "temperature_c": round(random.uniform(*TEMP_NORMAL), 2),
        "rod_position_mm": round(random.uniform(*ROD_NORMAL)),
    }

def simulate_normal_fluctuations(data):
    """Simulates small, random fluctuations around normal operating values."""
    data["power_mw"] += round(random.uniform(-0.05, 0.05), 2)
    data["temperature_c"] += round(random.uniform(-1, 1), 2)
    data["rod_position_mm"] += random.randint(-5, 5)

    # Clamp values to stay within a reasonable normal range
    data["power_mw"] = max(POWER_NORMAL[0] - 0.1, min(data["power_mw"], POWER_NORMAL[1] + 0.1))
    data["temperature_c"] = max(TEMP_NORMAL[0] - 5, min(data["temperature_c"], TEMP_NORMAL[1] + 5))
    data["rod_position_mm"] = max(ROD_NORMAL[0] - 10, min(data["rod_position_mm"], ROD_NORMAL[1] + 10))
    return data

def simulate_accident_conditions(data):
    """Simulates a rapid increase in power and temperature, and control rod insertion."""
    data["power_mw"] += round(random.uniform(0.1, 0.3), 2)
    data["temperature_c"] += round(random.uniform(2, 5), 2)
    # Control rods are inserted to try and control the reaction
    data["rod_position_mm"] -= random.randint(10, 20)

    # Clamp values at a max/min
    data["power_mw"] = min(data["power_mw"], 2.5)
    data["temperature_c"] = min(data["temperature_c"], 150)
    data["rod_position_mm"] = max(data["rod_position_mm"], 0)
    return data

def write_header():
    """Writes the CSV header if the file doesn't exist."""
    try:
        with open(FILE_PATH, 'x', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writeheader()
    except FileExistsError:
        pass # File already exists

def append_data(data):
    """Appends a new row of data to the CSV."""
    with open(FILE_PATH, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writerow(data)

def main(accident_mode=False):
    """Main loop to generate and write data."""
    print("--- Real-Time Reactor Data Simulator ---")
    print(f"Mode: {'ACCIDENT' if accident_mode else 'NORMAL'}")
    print(f"Writing data to {FILE_PATH} every {UPDATE_INTERVAL_SECONDS} second(s).")
    print("Press Ctrl+C to stop.")

    write_header()
    current_data = generate_initial_data()

    try:
        while True:
            if accident_mode:
                current_data = simulate_accident_conditions(current_data)
            else:
                current_data = simulate_normal_fluctuations(current_data)

            # Prepare data for writing
            data_to_write = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "power_mw": round(current_data["power_mw"], 2),
                "temperature_c": round(current_data["temperature_c"], 1),
                "rod_position_mm": int(current_data["rod_position_mm"]),
            }

            append_data(data_to_write)
            print(f"Logged: {data_to_write}")

            time.sleep(UPDATE_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nSimulator stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate reactor data.")
    parser.add_argument(
        '--accident',
        action='store_true',
        help='If set, simulates accident conditions.'
    )
    args = parser.parse_args()
    main(accident_mode=args.accident)
