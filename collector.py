import argparse
from collectors.companies import CompanyCollector
from collectors.financials import FinancialsCollector
from collectors.disclosures import DisclosuresCollector
from collectors.market import MarketCollector
from processors.markdown_generator import MarkdownGenerator
from processors.ratios import RatioCalculator
from datetime import datetime

def collect_all(ticker):
    print(f"Starting data collection for {ticker}...")
    
    # 1. Company Info & Shareholders
    print("\n[1/6] Collecting Company Info & Shareholders...")
    try:
        company_collector = CompanyCollector()
        company_collector.collect_and_save(ticker)
        company_collector.fetch_shareholders(ticker)
    except Exception as e:
        print(f"Error collecting company info: {e}")

    # 2. Financials (Last 3 years)
    print("\n[2/6] Collecting Financials...")
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
    print("\n[4/6] Collecting Market Data...")
    try:
        market_collector = MarketCollector()
        market_collector.fetch_daily_data(ticker, days=365)
    except Exception as e:
        print(f"Error collecting market data: {e}")

    # 5. Calculate Ratios
    print("\n[5/6] Calculating Financial Ratios...")
    ratio_calculator = RatioCalculator()
    ratio_calculator.calculate_ratios(ticker)

    # 6. Generate Markdown Reports
    print("\n[6/6] Generating Markdown Reports...")
    generator = MarkdownGenerator(ticker)
    generator.save_files()

    print(f"\nData collection for {ticker} completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antz Collector")
    parser.add_argument("ticker", type=str, help="Stock ticker (e.g., 005930) or Name (e.g., 삼성전자)")
    args = parser.parse_args()
    
    # Resolve ticker if name is provided
    company_collector = CompanyCollector()
    resolved_ticker = company_collector.resolve_ticker(args.ticker)
    
    if resolved_ticker:
        if resolved_ticker != args.ticker:
            print(f"Resolved '{args.ticker}' to ticker: {resolved_ticker}")
        collect_all(resolved_ticker)
    else:
        print(f"Error: Could not resolve ticker for '{args.ticker}'. Please check the name or use the 6-digit ticker directly.")
