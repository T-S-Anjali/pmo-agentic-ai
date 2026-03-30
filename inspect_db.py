import sqlite3
import json

db_path = "backend/pmo_agent.db"

def inspect():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables: {tables}")
        
        for table in tables:
            tname = table[0]
            print(f"\n--- {tname} (last 5 rows) ---")
            try:
                cursor.execute(f"SELECT * FROM {tname} ORDER BY rowid DESC LIMIT 5")
                rows = cursor.fetchall()
                for row in rows:
                    print(row)
            except Exception as e:
                print(f"Error reading {tname}: {e}")
        
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    inspect()
