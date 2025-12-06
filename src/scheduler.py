import schedule
import time
import datetime
import sys
import os

# Ensure src module is accessible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.collector import run_collector, collect_winning_stores, get_last_round
from src.auditor import run_auditor
from src.analyst import run_analyst

class DualLogger:
    def __init__(self, filepath):
        self.terminal = sys.stdout
        self.log = open(filepath, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

def weekly_job():
    # Logging Setup
    log_dir = "/var/log/lottogenie"
    os.makedirs(log_dir, exist_ok=True)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"lottogenie_{today}.log")
    
    # Redirect stdout and stderr to the log file
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    sys.stdout = DualLogger(log_file)
    sys.stderr = sys.stdout # Redirect stderr to same log
    
    print(f"\n[Scheduler] Starting Weekly Job at {datetime.datetime.now()}")

    try:
        # 1. Update Data (Collector)
        print("Step 1: Running Collector...")
        last_round = get_last_round()
        # Optimization: Start checking from the last known round to find new data
        start_round = max(1, last_round)
        target_end = last_round + 10 if last_round > 0 else 1200 
        run_collector(start_round=start_round, end_round=target_end)
        
        # 2. Update Winning Stores
        print("Step 2: Collecting Winning Stores...")
        current_last_round = get_last_round()
        if current_last_round > 0:
            start_store_check = current_last_round
            collect_winning_stores(start_round=start_store_check, end_round=current_last_round)
        
        # 3. Check Predictions (Auditor)
        print("Step 3: Checking Predictions...")
        run_auditor()
        
        # 4. Train Model
        print("Step 4: Training Model...")
        run_analyst(mode='train')
        
        # 5. Generate New Predictions
        print("Step 5: Generating New Predictions...")
        run_analyst()
        
        print("Success: Weekly job completed.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Restore stdout/stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr

def main():
    print("[Scheduler] Service Started. Waiting for Schedule...")
    
    # Schedule every Saturday at 21:15 (9:15 PM)
    # Lottery draw is usually around 20:35, broadcast ends 20:45. 
    # Website update might take a bit. 21:15 is safe.
    schedule.every().saturday.at("21:15").do(weekly_job)
    
    # For testing: run immediately on startup if env var set?
    # if os.getenv("RUN_ON_STARTUP"):
    #     weekly_job()
    
    print(f"[Scheduler] Next run expected at: {schedule.next_run()}")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
