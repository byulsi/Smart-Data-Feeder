import FinanceDataReader as fdr

try:
    df = fdr.StockListing('KRX')
    print("Columns:", df.columns.tolist())
    
    # Check LG Electronics
    row = df[df['Code'] == '066570']
    if not row.empty:
        print("\nLG Electronics Data:")
        print(row.iloc[0])
    else:
        print("\nLG Electronics not found in KRX listing")
        
except Exception as e:
    print(f"Error: {e}")
