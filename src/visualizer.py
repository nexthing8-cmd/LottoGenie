import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from src.database import get_engine

def get_history_df():
    """Loads history data into a pandas DataFrame."""
    engine = get_engine()
    query = "SELECT round_no, num1, num2, num3, num4, num5, num6, bonus, draw_date FROM history"
    df = pd.read_sql_query(query, engine)
    # Engine connection is managed by SQLAlchemy, but we can dispose if needed.
    # For this simple app, letting it persist or GC is fine.
    return df

def get_frequency_data(top_n=45, limit=None):
    """Returns frequency data for all numbers, optionally limited to recent rounds."""
    df = get_history_df()
    if df.empty:
        return {}
    
    if limit:
        df = df.sort_values('round_no', ascending=False).head(limit)
        
    # Melt the dataframe to get all numbers in one column
    nums = pd.concat([df[f'num{i}'] for i in range(1, 7)])
    counts = nums.value_counts().sort_index() # Sort by number (1-45)
    
    # Return as dict: {number: count}
    return counts.to_dict()

def get_trend_data(last_n_rounds=None):
    """Returns winning numbers for trend chart.
    If last_n_rounds is None, returns all data.
    Otherwise returns only the last N rounds."""
    df = get_history_df()
    if df.empty:
        return []
    
    if last_n_rounds is None:
        # Return all data
        result_df = df.sort_values('round_no', ascending=True) # Oldest to newest for chart
    else:
        # Return only last N rounds
        recent_df = df.sort_values('round_no', ascending=False).head(last_n_rounds)
        result_df = recent_df.sort_values('round_no', ascending=True) # Oldest to newest for chart
    
    # Format: list of {round_no: N, num1: ..., num6: ...}
    return result_df.to_dict(orient='records')

def get_winner_count_data():
    """Returns 1st prize winner counts for trend chart."""
    engine = get_engine()
    query = """
        SELECT p.round_no, h.draw_date, p.winner_count 
        FROM prizes p 
        JOIN history h ON p.round_no = h.round_no 
        WHERE p.rank_no = 1 
        ORDER BY p.round_no ASC
    """
    df = pd.read_sql_query(query, engine)
    
    if df.empty:
        return []

    return df.to_dict(orient='records')
