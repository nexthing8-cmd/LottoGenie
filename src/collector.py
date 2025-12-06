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
        response = requests.get(url, timeout=10)
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
        
        # Parse Prize Data (New)
        prizes = []
        meta = {'auto': 0, 'manual': 0, 'semi_auto': 0}
        
        # Finding the prize table
        # Usually checking class 'tbl_data tbl_data_col' or finding caption
        tables = soup.find_all('table', class_='tbl_data')
        prize_table = None
        for t in tables:
            if "등위별 총 당첨금액" in t.text:
                prize_table = t
                break
        
        if prize_table:
            tbody = prize_table.find('tbody')
            rows = tbody.find_all('tr')
            # Rows: 1st, 2nd, 3rd, 4th, 5th
            for idx, row in enumerate(rows):
                rank = idx + 1
                cols = row.find_all('td')
                
                # Column indices change because of rowspan in first row
                # Row 1 (1st): [Rank, Total, Count, PerPerson, Criteria, Remarks(rowspan)]
                # Row 2-5: [Rank, Total, Count, PerPerson, Criteria] (Remarks is shared)
                
                if rank == 1:
                    # 1st place row
                    # cols[1]: Total, cols[2]: Count, cols[3]: PerPerson
                    total = int(cols[1].text.replace(',', '').replace('원', '').strip())
                    count = int(cols[2].text.replace(',', '').strip())
                    per_person = int(cols[3].text.replace(',', '').replace('원', '').strip())
                    
                    # Parse Remarks for Auto/Manual
                    # The remark cell is the last one (index 5)
                    remark_cell = cols[5]
                    remark_text = remark_cell.text
                    
                    # Example text: "1등자동10수동2" or structured with <br>
                    # Simple parsing: look for "자동n", "수동n", "반자동n"
                    # Or use regex
                    import re
                    auto_match = re.search(r'자동(\d+)', remark_text)
                    manual_match = re.search(r'수동(\d+)', remark_text)
                    semi_match = re.search(r'반자동(\d+)', remark_text)
                    
                    meta['auto'] = int(auto_match.group(1)) if auto_match else 0
                    meta['manual'] = int(manual_match.group(1)) if manual_match else 0
                    meta['semi_auto'] = int(semi_match.group(1)) if semi_match else 0
                    
                else:
                    # Other rows
                    total = int(cols[1].text.replace(',', '').replace('원', '').strip())
                    count = int(cols[2].text.replace(',', '').strip())
                    per_person = int(cols[3].text.replace(',', '').replace('원', '').strip())
                
                prizes.append({
                    'rank': rank,
                    'total': total,
                    'count': count,
                    'per_person': per_person
                })

        return {
            'round_no': round_no,
            'nums': nums,
            'bonus': bonus,
            'date': date_str,
            'prizes': prizes,
            'meta': meta
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
            INSERT IGNORE INTO history (
                round_no, num1, num2, num3, num4, num5, num6, bonus, draw_date, 
                first_prize_auto, first_prize_manual, first_prize_semi_auto
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                first_prize_auto = VALUES(first_prize_auto),
                first_prize_manual = VALUES(first_prize_manual),
                first_prize_semi_auto = VALUES(first_prize_semi_auto)
        ''', (
            data['round_no'],
            data['nums'][0],
            data['nums'][1],
            data['nums'][2],
            data['nums'][3],
            data['nums'][4],
            data['nums'][5],
            data['bonus'],
            data['date'],
            data.get('meta', {}).get('auto', 0),
            data.get('meta', {}).get('manual', 0),
            data.get('meta', {}).get('semi_auto', 0)
        ))
        
        # Save Prizes
        if 'prizes' in data:
            for p in data['prizes']:
                cursor.execute('''
                    INSERT INTO prizes (round_no, rank_no, total_price, winner_count, win_amount)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        total_price = VALUES(total_price),
                        winner_count = VALUES(winner_count),
                        win_amount = VALUES(win_amount)
                ''', (
                    data['round_no'],
                    p['rank'],
                    p['total'],
                    p['count'],
                    p['per_person']
                ))

        conn.commit()
        print(f"Saved round {data['round_no']} (Win Info + Prizes)")
    except Exception as e:
        print(f"Error saving round {data['round_no']}: {e}")
    finally:
        conn.close()

def get_existing_rounds():
    """Retrieves rounds that have both history and prize data recorded."""
    conn = get_connection()
    cursor = conn.cursor()
    # Check prizes table to ensure we have full data
    # We treat a round as 'existing' only if it is in history AND has prize info.
    # Since prizes table has FK to history, checking prizes is sufficient (usually).
    # But to be safe? yes, prizes table.
    try:
        cursor.execute('SELECT DISTINCT round_no FROM prizes')
        prizes_rounds = {row['round_no'] for row in cursor.fetchall()}
    except Exception:
        # If table doesn't exist or error, assume empty
        prizes_rounds = set()
        
    conn.close()
    return prizes_rounds

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
            # Throttling per request (3~5s)
            time.sleep(random.uniform(3.0, 5.0))
            
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

def save_store_to_db(round_no, store_name, choice_type, address):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO winning_stores (round_no, store_name, choice_type, address)
            VALUES (%s, %s, %s, %s)
        ''', (round_no, store_name, choice_type, address))
        conn.commit()
    except Exception as e:
        print(f"Error saving store for round {round_no}: {e}")
    finally:
        conn.close()

import time
import random

def collect_winning_stores(start_round, end_round):
    """Collects 1st place winning stores."""
    print(f"Collecting winning stores for rounds {start_round}-{end_round}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for round_no in range(start_round, end_round + 1):
        url = f"https://dhlottery.co.kr/store.do?method=topStore&pageGubun=L645&drwNo={round_no}"
        try:
            # Random delay to be polite
            time.sleep(random.uniform(0.5, 2.0))
            
            response = requests.get(url, headers=headers, timeout=10)
            # encoding might need to be set manually if korean chars are broken, usually utf-8 or euc-kr
            # dhlottery usually uses euc-kr. let's check content encoding or just try auto.
            # response.encoding = 'euc-kr' # often needed for korean sites
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the first group_content (1st place)
            group_contents = soup.find_all('div', class_='group_content')
            if not group_contents:
                print(f"No store data found for round {round_no}")
                continue
                
            first_place_group = group_contents[0]
            
            # Additional check if it's indeed 1st place
            title = first_place_group.find('h4', class_='title')
            if not title or "1등 배출점" not in title.text:
                # Try finding by text if order is not guaranteed, but usually it is.
                print(f"Warning: Unexpected structure for round {round_no}. Skipping.")
                continue

            table = first_place_group.find('table', class_='tbl_data')
            if not table:
                continue
                
            tbody = table.find('tbody')
            rows = tbody.find_all('tr')
            
            count = 0
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 4:
                    continue
                
                # cols[1]: Name, cols[2]: Type, cols[3]: Address
                store_name = cols[1].text.strip()
                choice_type = cols[2].text.strip().replace('\n', '').replace('\r', '').replace('\t', '')
                address = cols[3].text.strip()
                
                # Check for "Empty" row (sometimes happens if no data)
                if "조회 결과가 없습니다" in store_name:
                    continue

                save_store_to_db(round_no, store_name, choice_type, address)
                count += 1
            
            print(f"Round {round_no}: Saved {count} stores.")
            
        except Exception as e:
            print(f"Error fetching stores for round {round_no}: {e}")

if __name__ == "__main__":
    run_collector()
