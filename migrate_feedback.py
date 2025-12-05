import sqlite3
from utils import get_db_connection

def migrate():
    print("Migrating database for Feedback System...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create feedbacks table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type VARCHAR(50) NOT NULL, -- 'bug', 'suggestion', 'other'
            content TEXT NOT NULL,
            contact VARCHAR(100),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
            
        conn.commit()
        print("Migration completed successfully: 'feedbacks' table created.")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
