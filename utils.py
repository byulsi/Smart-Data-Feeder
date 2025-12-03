import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Establishes a connection to the Supabase PostgreSQL database."""
    try:
        # Prefer DATABASE_URL if available
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            conn = psycopg2.connect(db_url)
            return conn
        
        # Fallback to individual credentials if needed (though URL is standard for Supabase)
        host = os.getenv("SUPABASE_HOST", "db.supabase.co")
        user = os.getenv("SUPABASE_USER", "postgres")
        password = os.getenv("SUPABASE_PASSWORD")
        dbname = os.getenv("SUPABASE_DB", "postgres")
        
        if not password:
             raise ValueError("DATABASE_URL or SUPABASE_PASSWORD must be set in .env")

        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=dbname
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise

def upsert_data(table, data, conflict_columns, update_columns=None):
    """
    Upserts data into a table.
    data: List of dictionaries matching table columns.
    conflict_columns: List of columns to check for conflict (e.g. ['ticker']).
    update_columns: List of columns to update on conflict. If None, updates all except conflict columns.
    """
    if not data:
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    columns = data[0].keys()
    query = f"INSERT INTO {table} ({','.join(columns)}) VALUES %s"
    
    conflict_str = ','.join(conflict_columns)
    
    if update_columns is None:
        update_columns = [col for col in columns if col not in conflict_columns]
        
    update_set = ', '.join([f"{col} = EXCLUDED.{col}" for col in update_columns])
    
    query += f" ON CONFLICT ({conflict_str}) DO UPDATE SET {update_set}"
    
    values = [[row[col] for col in columns] for row in data]
    
    try:
        execute_values(cursor, query, values)
        conn.commit()
        print(f"Successfully upserted {len(data)} rows into {table}.")
    except Exception as e:
        conn.rollback()
        print(f"Error upserting data: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
