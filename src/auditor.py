import sqlite3
from src.database import get_connection

def get_pending_predictions():
    """Retrieves predictions that haven't been checked yet."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, round_no, num1, num2, num3, num4, num5, num6 FROM my_predictions WHERE rank_val = "미추첨"')
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_win_numbers(round_no):
    """Retrieves winning numbers for a specific round."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT num1, num2, num3, num4, num5, num6, bonus FROM history WHERE round_no = %s', (round_no,))
    result = cursor.fetchone()
    conn.close()
    if result:
        # result is a dict
        win_nums = {result['num1'], result['num2'], result['num3'], result['num4'], result['num5'], result['num6']}
        return win_nums, result['bonus']
    return None, None

def calculate_rank(my_nums, win_nums, bonus):
    """Calculates the rank based on matching numbers."""
    match_count = len(my_nums & win_nums)
    is_bonus_match = bonus in my_nums
    
    if match_count == 6:
        return "1등"
    elif match_count == 5 and is_bonus_match:
        return "2등"
    elif match_count == 5:
        return "3등"
    elif match_count == 4:
        return "4등"
    elif match_count == 3:
        return "5등"
    else:
        return "낙첨"

def update_prediction_rank(pred_id, rank):
    """Updates the rank of a prediction in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE my_predictions SET rank_val = %s WHERE id = %s', (rank, pred_id))
    conn.commit()
    conn.close()

def run_auditor(round_no=None):
    """Main function to run the auditor agent."""
    pending = get_pending_predictions()
    
    if round_no:
        pending = [p for p in pending if p['round_no'] == round_no]
        print(f"Checking predictions for round {round_no}...")
    else:
        print(f"Found {len(pending)} pending predictions.")
    
    for pred in pending:
        pred_id = pred['id']
        r_no = pred['round_no']
        my_nums = {pred['num1'], pred['num2'], pred['num3'], pred['num4'], pred['num5'], pred['num6']}
        
        win_nums, bonus = get_win_numbers(r_no)
        
        if win_nums:
            rank = calculate_rank(my_nums, win_nums, bonus)
            update_prediction_rank(pred_id, rank)
            print(f"Prediction {pred_id} for round {r_no}: {rank}")
        else:
            print(f"Round {r_no} results not yet available.")

if __name__ == "__main__":
    run_auditor()
