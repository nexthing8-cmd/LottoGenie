import sqlite3
import random
import numpy as np
import pandas as pd
import os
from datetime import datetime
from collections import Counter
from src.database import get_connection

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input

from sklearn.preprocessing import MultiLabelBinarizer

def load_history():
    """Loads all history data from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT num1, num2, num3, num4, num5, num6 FROM history ORDER BY round_no ASC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def prepare_data(history_data, sequence_length=5):
    """Prepares data for LSTM model."""
    # Convert list of dicts to list of lists (sorted numbers)
    draws = []
    for row in history_data:
        # Extract values and sort
        nums = sorted([v for v in row.values()])
        draws.append(nums)
    
    # Multi-hot encoding
    mlb = MultiLabelBinarizer(classes=range(1, 46))
    encoded_draws = mlb.fit_transform(draws)
    
    X, y = [], []
    for i in range(len(encoded_draws) - sequence_length):
        X.append(encoded_draws[i:i+sequence_length])
        y.append(encoded_draws[i+sequence_length])
        
    return np.array(X), np.array(y), mlb

def create_model(input_shape):
    """Creates an LSTM model."""
    model = Sequential([
        Input(shape=input_shape),
        LSTM(128, return_sequences=True),
        Dropout(0.2),
        LSTM(64),
        Dropout(0.2),
        Dense(45, activation='sigmoid') # 45 numbers, probability of each
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def generate_numbers_ml(history_data, num_sets=5):
    """Generates prediction numbers using LSTM model."""
    print("Training ML model... (This may take a while)")
    
    sequence_length = 10 # Look back 10 rounds
    X, y, mlb = prepare_data(history_data, sequence_length)
    
    if len(X) == 0:
        print("Not enough data to train model.")
        return []

    # Create and train model
    # Note: In a real production system, we would save/load the model.
    # For this demo, we retrain or use a lightweight approach.
    # To save time, we'll use fewer epochs.
    model = create_model((sequence_length, 45))
    model.fit(X, y, epochs=10, batch_size=32, verbose=0)
    
    # Predict next round
    last_sequence = X[-1].reshape(1, sequence_length, 45)
    
    predictions = []
    
    # Generate multiple sets by adding some noise or sampling
    # Since the model is deterministic for a given input, we need a way to vary predictions.
    # Approach: Get probabilities, then sample based on them or pick top N with noise.
    
    predicted_probs = model.predict(last_sequence, verbose=0)[0]
    
    # Strategy: Weighted random sampling based on predicted probabilities
    # Normalize probabilities to sum to 1 for sampling (if needed, but random.choices handles weights)
    
    # We want to generate 'num_sets' unique combinations
    attempts = 0
    while len(predictions) < num_sets and attempts < num_sets * 20:
        attempts += 1
        
        # Sample 6 numbers based on probabilities
        # We use the probabilities as weights.
        # Note: classes are 1-45. predicted_probs index 0 corresponds to 1.
        
        candidates = np.random.choice(
            range(1, 46), 
            size=6, 
            replace=False, 
            p=predicted_probs / predicted_probs.sum()
        )
        candidates = sorted(candidates.tolist())
        
        if candidates not in predictions:
            predictions.append(candidates)
            
    return predictions

def save_predictions(round_no, predictions, user_id=None):
    """Saves the generated predictions to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for nums in predictions:
        cursor.execute('''
            INSERT INTO my_predictions (round_no, num1, num2, num3, num4, num5, num6, user_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (round_no, nums[0], nums[1], nums[2], nums[3], nums[4], nums[5], user_id, created_at))
    
    conn.commit()
    conn.close()
    print(f"Saved {len(predictions)} predictions for round {round_no} (User ID: {user_id})")

def run_analyst(user_id=None):
    """Main function to run the analyst agent."""
    # 1. Identify the target round (next round)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(round_no) as max_round FROM history')
    result = cursor.fetchone()
    last_round = result['max_round'] if result and result['max_round'] else 0
    conn.close()
    
    if not last_round:
        print("No history data found. Cannot generate predictions.")
        return

    target_round = last_round + 1
    print(f"Generating predictions for round {target_round} using LSTM...")
    
    # 2. Load data
    history = load_history()
    
    # 3. Generate
    predictions = generate_numbers_ml(history)
    print(f"Generated: {predictions}")
    
    # 4. Save
    save_predictions(target_round, predictions, user_id)

if __name__ == "__main__":
    run_analyst()
