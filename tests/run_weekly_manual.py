import sys
import os

# Add project root to sys.path to allow imports from src
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from src.scheduler import weekly_job

if __name__ == "__main__":
    print("🚀 Manually triggering Weekly Job...")
    print(f"Project Root: {project_root}")
    
    # Execute the job
    weekly_job()
    
    print("✅ Manual execution finished.")
