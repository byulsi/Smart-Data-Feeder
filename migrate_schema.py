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
            
            print("Adding 'pbr' column to financials table...")
            cursor.execute("ALTER TABLE financials ADD COLUMN pbr REAL")

            print("Adding 'rnd_expenses' column to financials table...")
            cursor.execute("ALTER TABLE financials ADD COLUMN rnd_expenses BIGINT")

        # Create company_narratives table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_narratives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                period TEXT NOT NULL,
                section_type TEXT NOT NULL,
                title TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, period, section_type, title)
            )
        """)
        print("Created/Verified company_narratives table.")
            
        conn.commit()
        print("Migration completed successfully.")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
