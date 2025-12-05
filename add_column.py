import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        port=int(os.getenv('DB_PORT', 3306)),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def add_column():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            print("Checking if 'user_id' column exists in 'my_predictions'...")
            cursor.execute("DESCRIBE my_predictions")
            columns = [row['Field'] for row in cursor.fetchall()]
            
            if 'user_id' not in columns:
                print("Adding 'user_id' column...")
                # Add user_id column, nullable for now to support existing records, but ideally should be linked.
                # Since we have existing data without users, we keep it nullable or set a default.
                # Let's make it nullable.
                cursor.execute("ALTER TABLE my_predictions ADD COLUMN user_id INT")
                cursor.execute("ALTER TABLE my_predictions ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(id)")
                conn.commit()
                print("'user_id' column added successfully.")
            else:
                print("'user_id' column already exists.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_column()
