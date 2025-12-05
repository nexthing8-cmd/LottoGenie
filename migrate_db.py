import sqlite3
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'lotto.db')

def get_mariadb_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        port=int(os.getenv('DB_PORT', 3306)),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def migrate():
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"SQLite database not found at {SQLITE_DB_PATH}. Skipping migration.")
        return

    print("Starting migration...")
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    # Connect to MariaDB
    mariadb_conn = get_mariadb_connection()
    mariadb_cursor = mariadb_conn.cursor()

    try:
        # 1. Migrate 'history' table
        print("Migrating 'history' table...")
        sqlite_cursor.execute("SELECT * FROM history")
        rows = sqlite_cursor.fetchall()
        
        for row in rows:
            sql = """
                INSERT IGNORE INTO history (round_no, num1, num2, num3, num4, num5, num6, bonus, draw_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            mariadb_cursor.execute(sql, (
                row['round_no'], row['num1'], row['num2'], row['num3'], 
                row['num4'], row['num5'], row['num6'], row['bonus'], row['draw_date']
            ))
        print(f"Migrated {len(rows)} rows to 'history'.")

        # 2. Migrate 'my_predictions' table
        print("Migrating 'my_predictions' table...")
        sqlite_cursor.execute("SELECT * FROM my_predictions")
        rows = sqlite_cursor.fetchall()

        for row in rows:
            # Note: Mapping 'rank' from SQLite to 'rank_val' in MariaDB
            sql = """
                INSERT INTO my_predictions (round_no, num1, num2, num3, num4, num5, num6, rank_val, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            mariadb_cursor.execute(sql, (
                row['round_no'], row['num1'], row['num2'], row['num3'], 
                row['num4'], row['num5'], row['num6'], row['rank'], row['created_at']
            ))
        print(f"Migrated {len(rows)} rows to 'my_predictions'.")

        mariadb_conn.commit()
        print("Migration completed successfully.")

    except Exception as e:
        print(f"Error during migration: {e}")
        mariadb_conn.rollback()
    finally:
        sqlite_conn.close()
        mariadb_conn.close()

if __name__ == "__main__":
    # Ensure tables exist in MariaDB
    from src.database import init_db
    init_db()
    
    migrate()
