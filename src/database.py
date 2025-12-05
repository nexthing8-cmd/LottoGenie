import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import create_engine

def get_connection():
    """Establishes a connection to the MariaDB database."""
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        port=int(os.getenv('DB_PORT', 3306)),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def get_engine():
    """Creates a SQLAlchemy engine for pandas integration."""
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    port = int(os.getenv('DB_PORT', 3306))
    dbname = os.getenv('DB_NAME')
    
    # pymysql is used as the driver
    db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}?charset=utf8mb4"
    return create_engine(db_url)

def init_db():
    """Initializes the database tables."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Table 1: history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    round_no INT PRIMARY KEY,
                    num1 INT,
                    num2 INT,
                    num3 INT,
                    num4 INT,
                    num5 INT,
                    num6 INT,
                    bonus INT,
                    draw_date VARCHAR(20)
                )
            ''')

            # Table 2: my_predictions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS my_predictions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    round_no INT,
                    num1 INT,
                    num2 INT,
                    num3 INT,
                    num4 INT,
                    num5 INT,
                    num6 INT,
                    rank_val VARCHAR(20) DEFAULT '미추첨',
                    user_id INT,
                    created_at VARCHAR(30),
                    memo TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            # Table 3: users
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at VARCHAR(30)
                )
            ''')

            # Table 4: winning_stores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS winning_stores (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    round_no INT,
                    store_name VARCHAR(100),
                    choice_type VARCHAR(20),
                    address VARCHAR(255),
                    FOREIGN KEY (round_no) REFERENCES history(round_no)
                )
            ''')

            # Table 5: prizes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prizes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    round_no INT,
                    rank_no INT,
                    total_price BIGINT,
                    winner_count INT,
                    win_amount BIGINT,
                    FOREIGN KEY (round_no) REFERENCES history(round_no)
                )
            ''')
            
            # Alter history table to add auto/manual/semiauto columns if not exist
            # Note: Checking column existence in MySQL/MariaDB inside python block without explicit check query is tricky.
            # Usually "ADD COLUMN IF NOT EXISTS" is supported in MariaDB 10.2+. 
            # If standard MySQL, might need try-except.
            # Assuming MariaDB per context.
            try:
                cursor.execute("ALTER TABLE history ADD COLUMN first_prize_auto INT DEFAULT 0")
            except Exception:
                pass # Exists
            try:
                cursor.execute("ALTER TABLE history ADD COLUMN first_prize_manual INT DEFAULT 0")
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE history ADD COLUMN first_prize_semi_auto INT DEFAULT 0")
            except Exception:
                pass
        conn.commit()
        print(f"Database initialized at {os.getenv('DB_HOST')}:{os.getenv('DB_NAME')}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
