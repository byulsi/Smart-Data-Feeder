import sqlite3
from utils import get_db_connection, upsert_data

class RatioCalculator:
    def __init__(self):
        pass

    def calculate_ratios(self, ticker):
        """
        Calculates financial ratios for the given ticker and updates the financials table.
        """
        print(f"Calculating ratios for {ticker}...")
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 1. Get Company Info (Shares, Market Cap)
            cursor.execute("SELECT shares_outstanding, market_cap FROM companies WHERE ticker = ?", (ticker,))
            company = cursor.fetchone()
            if not company:
                print(f"Company not found: {ticker}")
                return

            shares = company['shares_outstanding']
            market_cap = company['market_cap']

            # 2. Get Financials (All periods)
            cursor.execute("SELECT * FROM financials WHERE ticker = ? ORDER BY year ASC, quarter ASC", (ticker,))
            financials = cursor.fetchall()

            updates = []

            for row in financials:
                # Basic Data
                net_income = row['net_income'] or 0
                equity = row['equity'] or 0
                assets = row['assets'] or 0
                liabilities = row['liabilities'] or 0
                current_assets = row['current_assets'] or 0
                current_liabilities = row['current_liabilities'] or 0
                
                # 1. EPS (Earnings Per Share)
                # Note: Using current shares outstanding. Ideally should use weighted average shares.
                eps = 0
                if shares > 0:
                    eps = net_income / shares

                # 2. BPS (Book Value Per Share)
                bps = 0
                if shares > 0:
                    bps = equity / shares

                # 3. ROE (Return on Equity)
                # Net Income / Equity
                roe = 0
                if equity > 0:
                    roe = (net_income / equity) * 100

                # 4. ROA (Return on Assets)
                roa = 0
                if assets > 0:
                    roa = (net_income / assets) * 100

                # 5. Debt Ratio (Liabilities / Equity)
                debt_ratio = 0
                if equity > 0:
                    debt_ratio = (liabilities / equity) * 100

                # 6. Current Ratio (Current Assets / Current Liabilities)
                current_ratio = 0
                if current_liabilities > 0:
                    current_ratio = (current_assets / current_liabilities) * 100

                # 7. PER & PBR (Valuation)
                per = 0
                pbr = 0
                
                # Determine approximate quarter end date
                # Q1: 03-31, Q2: 06-30, Q3: 09-30, Q4: 12-31
                # For yearly (Q0), use 12-31
                q_month = {1: '03', 2: '06', 3: '09', 4: '12', 0: '12'}.get(row['quarter'], '12')
                q_day = {1: '31', 2: '30', 3: '30', 4: '31', 0: '31'}.get(row['quarter'], '31')
                target_date = f"{row['year']}-{q_month}-{q_day}"
                
                # Fetch close price near this date
                # We need to find the closest available trading day on or before target_date
                cursor.execute("""
                    SELECT close FROM market_daily 
                    WHERE ticker = ? AND date <= ? 
                    ORDER BY date DESC LIMIT 1
                """, (ticker, target_date))
                price_row = cursor.fetchone()
                
                if price_row:
                    price = price_row['close']
                    
                    # Calculate PER (Price / EPS)
                    if eps > 0:
                        per = price / eps
                        
                    # Calculate PBR (Price / BPS)
                    if bps > 0:
                        pbr = price / bps

                update_data = {
                    "ticker": ticker,
                    "year": row['year'],
                    "quarter": row['quarter'],
                    "eps": round(eps, 2),
                    "bps": round(bps, 2),
                    "roe": round(roe, 2),
                    "roa": round(roa, 2),
                    "debt_ratio": round(debt_ratio, 2),
                    "current_ratio": round(current_ratio, 2),
                    "per": round(per, 2),
                    "pbr": round(pbr, 2)
                }
                updates.append(update_data)

            # Bulk Update
            if updates:
                upsert_data(
                    table="financials",
                    data=updates,
                    conflict_columns=["ticker", "year", "quarter"],
                    update_columns=["eps", "bps", "roe", "roa", "debt_ratio", "current_ratio", "per", "pbr"]
                )
                print(f"Updated ratios for {len(updates)} financial records.")

        except Exception as e:
            print(f"Error calculating ratios: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    calculator = RatioCalculator()
    calculator.calculate_ratios("005930")
