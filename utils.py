import sqlite3
import os
from datetime import datetime, date

# Use absolute path for DB_FILE to ensure it works from any CWD
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "data.db")

def get_db_connection():
    """Establishes a connection to the local SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database with tables if they don't exist."""
    if os.path.exists(DB_FILE) and os.path.getsize(DB_FILE) > 0:
        return

    print("Initializing local SQLite database...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # SQLite compatible schema
    schema = """
    CREATE TABLE IF NOT EXISTS companies (
        ticker TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        sector TEXT,
        market_type TEXT,
        est_dt TEXT,
        listing_dt TEXT,
        market_cap INTEGER,
        shares_outstanding INTEGER,
        desc_summary TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS financials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        year INTEGER NOT NULL,
        quarter INTEGER NOT NULL,
        revenue INTEGER,
        op_profit INTEGER,
        net_income INTEGER,
        assets INTEGER,
        liabilities INTEGER,
        equity INTEGER,
        current_assets INTEGER,
        current_liabilities INTEGER,
        ocf INTEGER,
        eps REAL,
        bps REAL,
        dps REAL,
        roe REAL,
        roa REAL,
        debt_ratio REAL,
        current_ratio REAL,
        rnd_expenses INTEGER,
        is_estimated BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(ticker, year, quarter),
        FOREIGN KEY(ticker) REFERENCES companies(ticker)
    );

    CREATE TABLE IF NOT EXISTS disclosures (
        rcept_no TEXT PRIMARY KEY,
        ticker TEXT NOT NULL,
        report_nm TEXT NOT NULL,
        rcept_dt DATE NOT NULL,
        flr_nm TEXT,
        url TEXT,
        summary_body TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(ticker) REFERENCES companies(ticker)
    );

    CREATE TABLE IF NOT EXISTS market_daily (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        date DATE NOT NULL,
        close REAL,
        open REAL,
        high REAL,
        low REAL,
        volume INTEGER,
        ma5 REAL,
        ma20 REAL,
        ma60 REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(ticker, date),
        FOREIGN KEY(ticker) REFERENCES companies(ticker)
    );

    CREATE TABLE IF NOT EXISTS company_segments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        period TEXT NOT NULL,
        division TEXT NOT NULL,
        revenue TEXT,
        op_profit TEXT,
        insight TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(ticker, period, division),
        FOREIGN KEY(ticker) REFERENCES companies(ticker)
    );

    CREATE TABLE IF NOT EXISTS company_narratives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        period TEXT NOT NULL,
        section_type TEXT NOT NULL,
        title TEXT,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(ticker, period, section_type),
        FOREIGN KEY(ticker) REFERENCES companies(ticker)
    );

    CREATE TABLE IF NOT EXISTS shareholders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        holder_name TEXT NOT NULL,
        rel_type TEXT,
        share_count INTEGER,
        share_ratio REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(ticker, holder_name),
        FOREIGN KEY(ticker) REFERENCES companies(ticker)
    );
    """
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    print("Database initialized.")

def upsert_data(table, data, conflict_columns, update_columns=None):
    """
    Upserts data into a table using SQLite.
    """
    if not data:
        return

    # Ensure DB is initialized
    init_db()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        keys = data[0].keys()
        columns = ', '.join(keys)
        placeholders = ', '.join(['?'] * len(keys))
        
        # SQLite UPSERT syntax: INSERT INTO ... ON CONFLICT (...) DO UPDATE SET ...
        conflict_str = ', '.join(conflict_columns)
        
        if update_columns is None:
            # Update all columns except conflict columns
            update_columns = [k for k in keys if k not in conflict_columns]
            
        update_set = ', '.join([f"{col}=excluded.{col}" for col in update_columns])
        
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        if conflict_columns:
            sql += f" ON CONFLICT({conflict_str}) DO UPDATE SET {update_set}"
            
        values = [tuple(row[k] for k in keys) for row in data]
        
        cursor.executemany(sql, values)
        conn.commit()
        print(f"Successfully upserted {len(data)} rows into {table}.")
        
    except Exception as e:
        print(f"Error upserting data to {table}: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
