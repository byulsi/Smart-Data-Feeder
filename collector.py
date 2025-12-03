import argparse
from collectors.companies import CompanyCollector
from collectors.financials import FinancialsCollector
from collectors.disclosures import DisclosuresCollector
from collectors.market import MarketCollector
from datetime import datetime

def collect_all(ticker):
    print(f"Starting data collection for {ticker}...")
    
    # 1. Company Info
    print("\n[1/4] Collecting Company Info...")
    try:
        company_collector = CompanyCollector()
        company_collector.collect_and_save(ticker)
    except Exception as e:
        print(f"Error collecting company info: {e}")

    # 2. Financials (Last 3 years)
    print("\n[2/4] Collecting Financials...")
    try:
        financials_collector = FinancialsCollector()
        current_year = datetime.now().year
        for year in range(current_year - 3, current_year + 1):
            financials_collector.fetch_financials(ticker, year, 0) # Yearly
            # financials_collector.fetch_financials(ticker, year, 1) # Q1 (Optional for MVP)
    except Exception as e:
        print(f"Error collecting financials: {e}")

    # 3. Disclosures (Last 1 year)
    print("\n[3/4] Collecting Disclosures...")
    try:
        disclosures_collector = DisclosuresCollector()
        disclosures_collector.fetch_disclosures(ticker, days=1095)
    except Exception as e:
        print(f"Error collecting disclosures: {e}")

    # 4. Market Data (Last 1 year)
    print("\n[4/4] Collecting Market Data...")
    try:
        market_collector = MarketCollector()
        market_collector.fetch_daily_data(ticker, days=365)
    except Exception as e:
        print(f"Error collecting market data: {e}")

    print(f"\nData collection for {ticker} completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart Data Feeder Collector")
    parser.add_argument("ticker", type=str, help="Stock ticker (e.g., 005930)")
    args = parser.parse_args()
    
    collect_all(args.ticker)
