import sqlite3
from utils import get_db_connection

def migrate():
    print("Migrating database...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if columns exist
        cursor.execute("PRAGMA table_info(financials)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'per' not in columns:
            print("Adding 'per' column to financials table...")
            cursor.execute("ALTER TABLE financials ADD COLUMN per REAL")
            
        if 'pbr' not in columns:
            print("Adding 'pbr' column to financials table...")
            cursor.execute("ALTER TABLE financials ADD COLUMN pbr REAL")
            
        conn.commit()
        print("Migration completed successfully.")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
