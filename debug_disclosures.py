import os
import OpenDartReader
from dotenv import load_dotenv

load_dotenv()

def debug_disclosures(ticker):
    api_key = os.getenv("DART_API_KEY")
    if not api_key:
        print("DART_API_KEY not found")
        return

    dart = OpenDartReader(api_key)
    
    # Get recent annual report
    print(f"Fetching recent reports for {ticker}...")
    df = dart.list(ticker, kind='A', start='20240101', end='20251231')
    
    if df is None or df.empty:
        print("No reports found.")
        return
        
    # Pick the first one (latest)
    target_report = df.iloc[0]
    rcept_no = target_report['rcept_no']
    report_nm = target_report['report_nm']
    print(f"Target Report: {report_nm} ({rcept_no})")
    
    try:
        # 1. List Sub Documents
        print("\n--- Sub Documents ---")
        sub_docs = dart.sub_docs(rcept_no)
        
        target_url = None
        for idx, row in sub_docs.iterrows():
            title = row['title']
            print(f"[{idx}] {title}")
            if "사업의 내용" in title:
                target_url = row['url']
                print(f"Found Target Section: {title} -> {target_url}")
                # We can't use URL directly with OpenDartReader usually, 
                # but OpenDartReader might have a method to fetch by URL or we use requests?
                # Actually OpenDartReader's attach_files or similar might help.
                # Wait, sub_docs returns a DataFrame with 'url', 'title', 'rcept_no', 'dcm_no', 'ele_id', 'offset', 'length', 'dtd'.
                # We can use 'dart.attach_files' to get files? No, that's for attachments.
                # We want the text content.
                # OpenDartReader doesn't have a direct 'get_sub_doc_content'.
                # But we can use the 'url' to fetch HTML if we have a session? 
                # Or use 'dart.document(rcept_no)' and parse the huge XML.
                
                # Let's see if OpenDartReader has a helper.
                # It seems OpenDartReader (the library) mainly supports 'document' (whole XML) or 'sub_docs' (list).
                # If we want specific section text, we might need to parse the whole XML or fetch the sub-doc URL.
                # The sub-doc URL is usually a viewer URL.
                
                pass
        
        # 2. Fetch Whole Document
        print("\n--- Fetching Document XML ---")
        xml_text = dart.document(rcept_no)
        
        if not xml_text:
            print("Failed to fetch document XML.")
            return

        print(f"XML Length: {len(xml_text)}")
        
        # Simple Extraction Logic (Regex or String Search)
        # We look for "II. 사업의 내용" and "III. 재무에 관한 사항"
        # Note: The XML might contain tags like <TITLE>II. 사업의 내용</TITLE> or similar.
        # Let's try to find the start and end indices.
        
        start_marker = "II. 사업의 내용"
        end_marker = "III. 재무에 관한 사항"
        
        start_idx = xml_text.find(start_marker)
        end_idx = xml_text.find(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            print(f"Found section from {start_idx} to {end_idx}")
            section_content = xml_text[start_idx:end_idx]
            
            # Clean HTML/XML tags
            import re
            clean_text = re.sub('<[^<]+?>', '', section_content)
            # Remove extra whitespace
            clean_text = ' '.join(clean_text.split())
            
            print(f"\n--- Extracted Text (First 500 chars) ---")
            print(clean_text[:500])
            print(f"\n--- Extracted Text (Last 500 chars) ---")
            print(clean_text[-500:])
        else:
            print("Markers not found in XML.")
            # Print a snippet to see structure
            print(xml_text[:1000])
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_disclosures("005930")
