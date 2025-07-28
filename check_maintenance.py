# File: check_maintenance.py

import os
import sys
from datetime import datetime, timedelta

# Add the root directory to the Python path to find our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# We import the main function from our existing maintenance script
from run_maintenance import main as run_full_maintenance

# --- Configuration ---
# The file where we'll store the timestamp of the last run
LOG_FILE = "data/maintenance_log.txt"
# How many days must pass before we run maintenance again
DAYS_BETWEEN_RUNS = 2
# --- End of Configuration ---

def main():
    """
    Checks if maintenance is due and runs it if necessary.
    """
    run_maintenance = False
    
    # 1. Check if the log file exists
    if not os.path.exists(LOG_FILE):
        print("Maintenance log not found. Running maintenance for the first time.")
        run_maintenance = True
    else:
        # 2. If it exists, read the last run time
        with open(LOG_FILE, 'r') as f:
            try:
                last_run_str = f.read().strip()
                last_run_time = datetime.fromisoformat(last_run_str)
                
                # 3. Compare the time difference
                if datetime.now() - last_run_time > timedelta(days=DAYS_BETWEEN_RUNS):
                    print(f"Last maintenance was run more than {DAYS_BETWEEN_RUNS} days ago. Running now.")
                    run_maintenance = True
                else:
                    print("Maintenance is up-to-date. Skipping.")
            except ValueError:
                print("Could not read timestamp from log file. Running maintenance.")
                run_maintenance = True

    # 4. If we decided to run it, call the main function
    if run_maintenance:
        # This will run the full purge and AI translation process
        run_full_maintenance()
        
        # 5. After it's done, update the log file with the new timestamp
        with open(LOG_FILE, 'w') as f:
            f.write(datetime.now().isoformat())
        print(f"Updated maintenance log with new timestamp.")
    
    print("\n--- Maintenance check complete ---")


if __name__ == "__main__":
    main()
