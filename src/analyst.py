import sqlite3
import random
import numpy as np
import os
from datetime import datetime
from collections import Counter
from src.database import get_connection
from src.notifier import send_message

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input



# Constants for Hyperparameters and Model Path
MODEL_PATH = 'data/lotto_model.keras'
SEQUENCE_LENGTH = 10
EPOCHS_NEW = 100
EPOCHS_UPDATE = 10
BATCH_SIZE = 32

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
    
    # Multi-hot encoding manually
    encoded_draws = []
    for draw in draws:
        encoded = [0] * 45
        for num in draw:
            if 1 <= num <= 45:
                encoded[num-1] = 1
        encoded_draws.append(encoded)
    
    encoded_draws = np.array(encoded_draws)
    
    X, y = [], []
    for i in range(len(encoded_draws) - sequence_length):
        X.append(encoded_draws[i:i+sequence_length])
        y.append(encoded_draws[i+sequence_length])
        
    return np.array(X).astype('float32'), np.array(y).astype('float32')

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

def train_model(history_data, fine_tune=True):
    """Trains or fine-tunes the LSTM model."""
    print("Preparing data for training...")
    X, y = prepare_data(history_data, SEQUENCE_LENGTH)
    
    if len(X) == 0:
        print("Not enough data to train model.")
        return

    if fine_tune and os.path.exists(MODEL_PATH):
        print(f"Loading existing model from {MODEL_PATH} for fine-tuning...")
        model = load_model(MODEL_PATH)
        epochs = EPOCHS_UPDATE
    else:
        print("Creating and training new model...")
        model = create_model((SEQUENCE_LENGTH, 45))
        epochs = EPOCHS_NEW
    
    print(f"Training model for {epochs} epochs...")
    model.fit(X, y, epochs=epochs, batch_size=BATCH_SIZE, verbose=1)
    
    model.save(MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

def generate_numbers_ml(history_data):
    """Generates prediction numbers using LSTM model (Prediction Only)."""
    # Just load and predict. No training here.
    
    if not os.path.exists(MODEL_PATH):
        print(f"Model not found at {MODEL_PATH}. Cannot predict.")
        return []
        
    print(f"Loading model from {MODEL_PATH}...")
    model = load_model(MODEL_PATH)
    
    # Prepare data just for the last sequence
    # optimizing prepare_data is possible but reusing is fine for now
    X, y = prepare_data(history_data, SEQUENCE_LENGTH)
    
    if len(X) == 0:
        return []
        
    last_sequence = X[-1].reshape(1, SEQUENCE_LENGTH, 45)
    
    predictions = []
    
    predicted_probs = model.predict(last_sequence, verbose=0)[0]
    
    attempts = 0
    num_sets = 5
    while len(predictions) < num_sets and attempts < num_sets * 20:
        attempts += 1
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

def run_analyst(user_id=None, mode='predict'):
    """
    Main function to run the analyst agent.
    mode: 'predict' (default) or 'train'
    """
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
    
    if mode == 'train':
        train_model(history)
        # After training, we might also want to predict or just exit.
        # Let's predict too if it's the weekly run.
        # But weekly run calls predict as well?
        # Let's just return if training only.
        print("Training completed.")
    
    # 3. Generate
    predictions = generate_numbers_ml(history)
    print(f"Generated: {predictions}")
    
    # 4. Save
    save_predictions(target_round, predictions, user_id)
    
    # 5. Notify
    try:
        msg = f"✅ 예측 완료 (회차: {target_round})\n생성된 번호: {predictions}"
        send_message(msg)
    except Exception as e:
        print(f"Notification failed: {e}")

if __name__ == "__main__":
    run_analyst()
