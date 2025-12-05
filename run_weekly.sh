#!/bin/bash

# LottoGenie Weekly Automation Script
# This script is designed to be run by crontab every Saturday night (e.g., 21:00 or 21:30)

# 1. Navigate to project directory (Adjust path as needed)
cd "$(dirname "$0")"

# 2. Activate virtual environment (if applicable)
# source venv/bin/activate

# 3. Collect Data
# Runs collector to fetch any missing rounds up to round 2000 (future-proof)
echo "[$(date)] Starting Data Collection..."
python main.py load

# 4. Check Previous Predictions
# Verifies if last week's predictions won
echo "[$(date)] Checking Previous Results..."
python main.py check

# 5. Train Model
# Fine-tunes the model with the latest data
echo "[$(date)] Training/Updating Model..."
python main.py train

# 6. Generate New Predictions
# Generates predictions for the next round
echo "[$(date)] Generating New Predictions..."
python main.py predict

echo "[$(date)] Weekly Task Completed."
