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

def weekly_job():
    print(f"\n[Scheduler] Starting Weekly Job at {datetime.datetime.now()}")
    
    # Logging Setup
    log_dir = "/var/log/lottogenie"
    os.makedirs(log_dir, exist_ok=True)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"lottogenie_{today}.log")
    
    # Simple file append logger
    def log(message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        print(formatted) # stdout
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(formatted + "\n")
        except Exception as log_err:
            print(f"Failed to write to log file: {log_err}")

    try:
        # 1. Update Data (Collector)
        log("Step 1: Running Collector...")
        last_round = get_last_round()
        target_end = last_round + 10 if last_round > 0 else 1200 
        run_collector(start_round=1, end_round=2000)
        
        # 2. Update Winning Stores
        log("Step 2: Collecting Winning Stores...")
        current_last_round = get_last_round()
        if current_last_round > 0:
            start_store_check = max(1, current_last_round - 5)
            collect_winning_stores(start_round=start_store_check, end_round=current_last_round)
        
        # 3. Check Predictions (Auditor)
        log("Step 3: Checking Predictions...")
        run_auditor()
        
        # 4. Train Model
        log("Step 4: Training Model...")
        run_analyst(mode='train')
        
        # 5. Generate New Predictions
        log("Step 5: Generating New Predictions...")
        run_analyst()
        
        log("Success: Weekly job completed.")
        
    except Exception as e:
        log(f"Error: {e}")

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
