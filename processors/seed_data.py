import sys
import os
import sqlite3
from datetime import datetime, timedelta

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_db_connection, init_db

def seed_samsung():
    print("Seeding data for Samsung Electronics (005930)...")
    
    # Force fresh DB
    if os.path.exists("data.db"):
        os.remove("data.db")
        
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Company Info
    cursor.execute("""
        INSERT OR REPLACE INTO companies (ticker, name, sector, market_type, desc_summary, market_cap)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('005930', 'Samsung Electronics', 'Technology', 'KOSPI', 
          'Samsung Electronics Co., Ltd. is a global leader in consumer electronics, semiconductors, and telecommunications.', 
          400000000000000)) # Approx 400T KRW

    # 2. Financials (4 Quarters)
    financials = [
        ('005930', 2024, 3, 79000000000000, 9100000000000, 10000000000000, 300000000000000, 100000000000000, 200000000000000, 5000000000000, 15.5, 20.0, 30.0),
        ('005930', 2024, 2, 74000000000000, 10400000000000, 9800000000000, 290000000000000, 95000000000000, 195000000000000, 4800000000000, 14.0, 18.0, 32.0),
        ('005930', 2024, 1, 71000000000000, 6600000000000, 6700000000000, 280000000000000, 90000000000000, 190000000000000, 4500000000000, 12.0, 15.0, 35.0),
        ('005930', 2023, 4, 67000000000000, 2800000000000, 6000000000000, 270000000000000, 85000000000000, 185000000000000, 4000000000000, 10.0, 12.0, 38.0),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO financials 
        (ticker, year, quarter, revenue, op_profit, net_income, assets, liabilities, equity, rnd_expenses, roe, roa, debt_ratio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, financials)

    # 3. Market Data (Recent)
    today = datetime.now()
    market_data = []
    price = 70000
    for i in range(30):
        date_str = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        market_data.append(('005930', date_str, price, price+1000, price-1000, price, 10000000))
        price += 500 if i % 2 == 0 else -300
    
    cursor.executemany("""
        INSERT OR REPLACE INTO market_daily (ticker, date, close, high, low, open, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, market_data)

    # 4. Segments
    segments = [
        ('005930', '2024.3Q', 'DX (Device eXperience)', '45000000000000', '3500000000000'),
        ('005930', '2024.3Q', 'DS (Device Solutions)', '29000000000000', '4000000000000'),
        ('005930', '2024.3Q', 'SDC (Display)', '8000000000000', '1500000000000'),
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO company_segments (ticker, period, division, revenue, op_profit)
        VALUES (?, ?, ?, ?, ?)
    """, segments)

    conn.commit()
    conn.close()
    print("Seeding complete.")

if __name__ == "__main__":
    seed_samsung()
