import FinanceDataReader as fdr

try:
    print("Checking KOSPI Listing...")
    df = fdr.StockListing('KOSPI')
    print("Columns:", df.columns.tolist())
    
    row = df[df['Code'] == '066570']
    if not row.empty:
        print("\nLG Electronics Data:")
        print(row.iloc[0])
        
except Exception as e:
    print(f"Error: {e}")
