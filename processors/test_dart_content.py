import os
import OpenDartReader
from dotenv import load_dotenv

load_dotenv()

def test_fetch_content():
    api_key = os.getenv("DART_API_KEY")
    if not api_key:
        print("Error: DART_API_KEY not found")
        return

    dart = OpenDartReader(api_key)
    
    # Samsung Electronics (005930)
    # Let's try to fetch a recent report.
    # We need a 'rcept_no' (Receipt Number).
    # From previous output: 2025-11-14 [분기보고서 (2025.09)] rcpNo=20251114002447
    # Note: The rcpNo in the URL is usually the one we need.
    
    rcept_no = "20241114002447" # Using a likely valid one (2024.11.14 for 3Q 2024)
    # Wait, the previous output showed "2025-11-14" which is in the future relative to "2025-12-04" (current time).
    # Ah, the user provided "2025.3Q" data in the prompt, implying we are in late 2025?
    # The additional metadata says "Current local time is: 2025-12-04".
    # So "2025-11-14" is in the past.
    
    # Let's try to find a real rcept_no for Samsung.
    # We can list first to get a valid one.
    
    print("Fetching list...")
    lst = dart.list("005930", start="20250101", end="20251201", kind='A')
    
    if lst is None or lst.empty:
        print("No reports found in 2025. Trying 2024...")
        lst = dart.list("005930", start="20240101", end="20241201", kind='A')
        
    if lst is None or lst.empty:
        print("No reports found.")
        return

    print("Found reports:")
    print(lst[['rcept_no', 'report_nm', 'rcept_dt']].head())
    
    target_rcept_no = lst.iloc[0]['rcept_no']
    print(f"\nTargeting Report: {target_rcept_no}")
    
    # Try to fetch sub_docs (Table of Contents)
    try:
        print("\nFetching sub_docs...")
        sub_docs = dart.sub_docs(target_rcept_no)
        print(sub_docs)
        
        # Try to find "Business Overview" (사업의 내용)
        # Usually title contains "사업의 내용"
        business_doc = None
        if sub_docs is not None:
            for _, row in sub_docs.iterrows():
                if "사업의 내용" in row['title']:
                    business_doc = row
                    break
        
        if business_doc is not None:
            print(f"\nFound Business Overview: {business_doc['title']} (URL: {business_doc['url']})")
            # OpenDartReader might have a method to get content?
            # It seems OpenDartReader wraps the API.
            # The API 'document' returns the HTML body.
            # Let's try dart.document() if it exists, or we might need to use the URL.
            
            # Checking if dart.document exists or similar
            if hasattr(dart, 'document'):
                print("Fetching document content...")
                # document(rcept_no) returns the main document?
                # Or attach_file?
                # Let's try to see what methods exist or just try `dart.attach_files(target_rcept_no)`
                pass
            
            # Actually, OpenDartReader's `sub_docs` returns a DataFrame with 'url'.
            # We might need to scrape that URL if the library doesn't provide content fetching.
            # But wait, `dart.document(rcept_no)` downloads the XML/HTML?
            
            try:
                # This is a guess on the method name based on common usage
                # If this fails, we know we need to research more.
                xml_text = dart.document(target_rcept_no) 
                print(f"\nDocument Content (First 500 chars):\n{xml_text[:500]}")
            except Exception as e:
                print(f"\ndart.document() failed: {e}")
                
    except Exception as e:
        print(f"Error fetching sub_docs: {e}")

if __name__ == "__main__":
    test_fetch_content()
