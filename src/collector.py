import requests
from bs4 import BeautifulSoup
import sqlite3
from src.database import get_connection

def get_last_round():
    """Retrieves the last recorded round number from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(round_no) as max_round FROM history')
    result = cursor.fetchone()
    conn.close()
    # result is a dict like {'max_round': 1200} or {'max_round': None}
    return result['max_round'] if result and result['max_round'] else 0

def fetch_lotto_data(round_no):
    """Fetches lottery data for a specific round from the website."""
    url = f"https://dhlottery.co.kr/gameResult.do?method=byWin&drwNo={round_no}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check if the round exists (basic check based on title or content)
        # Note: This is a simplified check. Real implementation might need more robust validation.
        title = soup.find('title').text
        if "회차별 당첨번호" not in title:
             return None

        # Extract numbers
        # The structure might change, but typically it's in a specific div
        # Example structure (needs verification with actual HTML if possible, but using standard assumption)
        win_result = soup.find('div', class_='win_result')
        if not win_result:
            return None
            
        nums = []
        # Main numbers
        for span in win_result.find('div', class_='num win').find_all('span'):
            nums.append(int(span.text))
        
        # Bonus number
        bonus = int(win_result.find('div', class_='num bonus').find('span').text)
        
        # Date
        date_str = soup.find('p', class_='desc').text.replace('추첨', '').strip() # (2023년 01월 01일)
        
        return {
            'round_no': round_no,
            'nums': nums,
            'bonus': bonus,
            'date': date_str
        }

    except Exception as e:
        print(f"Error fetching round {round_no}: {e}")
        return None

def save_to_db(data):
    """Saves the fetched data to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT IGNORE INTO history (round_no, num1, num2, num3, num4, num5, num6, bonus, draw_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data['round_no'],
            data['nums'][0],
            data['nums'][1],
            data['nums'][2],
            data['nums'][3],
            data['nums'][4],
            data['nums'][5],
            data['bonus'],
            data['date']
        ))
        conn.commit()
        print(f"Saved round {data['round_no']}")
    except Exception as e:
        print(f"Error saving round {data['round_no']}: {e}")
    finally:
        conn.close()

def get_existing_rounds():
    """Retrieves all recorded round numbers from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT round_no FROM history')
    rounds = {row[0] for row in cursor.fetchall()}
    conn.close()
    return rounds

def run_collector(start_round=1, end_round=1200):
    """Main function to run the collector agent."""
    existing_rounds = get_existing_rounds()
    print(f"Found {len(existing_rounds)} existing rounds.")
    
    # Target range
    target_rounds = set(range(start_round, end_round + 1))
    missing_rounds = sorted(list(target_rounds - existing_rounds))
    
    if not missing_rounds:
        print(f"All rounds {start_round}-{end_round} are present.")
    else:
        print(f"Found {len(missing_rounds)} missing rounds in range {start_round}-{end_round}. Starting fetch...")
        for round_no in missing_rounds:
            print(f"Fetching round {round_no}...")
            data = fetch_lotto_data(round_no)
            if data:
                save_to_db(data)
            else:
                print(f"Failed to fetch round {round_no}")
    
    # Check for new rounds beyond end_round if it's the latest
    # For CLI specific range, we might strictly stick to the range.
    # But let's keep the "check next" logic only if we are at the edge of known history?
    # Actually, if the user specifies a range, they probably just want that range.
    # Let's remove the auto-check-next logic for the CLI version to be precise, 
    # or make it optional. For now, let's remove it to strictly follow "load --from --to".
    pass

if __name__ == "__main__":
    run_collector()
