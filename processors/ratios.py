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
                # Note: This is a snapshot based on current market cap or close price.
                # For historical PER, we need historical price.
                # Here we calculate "Trailing PER" based on the financial report's EPS and *current* price?
                # Or *price at that time*?
                # For simplicity in this MVP, let's calculate based on the *latest* market cap if it's the latest report.
                # But actually, it's better to leave PER/PBR for the frontend to calculate using real-time price,
                # OR calculate it here if we want to store it.
                # Let's store it if it's the latest available financial report.
                
                # We will just store EPS/BPS here. PER/PBR can be derived.
                # But the user asked for "Investment Indicators".
                # Let's calculate PER/PBR if we have price data.
                # We can fetch the close price for the report date?
                # Let's stick to fundamental ratios first.
                
                update_data = {
                    "ticker": ticker,
                    "year": row['year'],
                    "quarter": row['quarter'],
                    "eps": round(eps, 2),
                    "bps": round(bps, 2),
                    "roe": round(roe, 2),
                    "roa": round(roa, 2),
                    "debt_ratio": round(debt_ratio, 2),
                    "current_ratio": round(current_ratio, 2)
                }
                updates.append(update_data)

            # Bulk Update
            if updates:
                upsert_data(
                    table="financials",
                    data=updates,
                    conflict_columns=["ticker", "year", "quarter"],
                    update_columns=["eps", "bps", "roe", "roa", "debt_ratio", "current_ratio"]
                )
                print(f"Updated ratios for {len(updates)} financial records.")

        except Exception as e:
            print(f"Error calculating ratios: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    calculator = RatioCalculator()
    calculator.calculate_ratios("005930")
