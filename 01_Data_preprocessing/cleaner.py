import os
from bs4 import BeautifulSoup
import glob

def clean_html_file(file_path: str):
    """
    Reads a raw HTML file, strips all tags, and returns clean text.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # BeautifulSoup is our "Janitor"
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove script and style elements (we don't need CSS/JS)
    for script in soup(["script", "style"]):
        script.extract()
    
    # Get text
    text = soup.get_text(separator="\n")
    
    # Break into lines and remove leading/trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

def process_filings():
    """
    Loops through all downloaded filings and creates clean versions.
    """
    # Path where ingestion.py saved data: sec-edgar-filings/AAPL/10-K/....txt
    # We want to search RECURSIVELY for all .txt files in that folder
    # Note: The downloader saves them as .txt even if they are HTML inside.
    raw_files = glob.glob("sec-edgar-filings/**/*.txt", recursive=True)
    
    print(f"🧹 Found {len(raw_files)} raw filings to clean...")
    
    os.makedirs("data/processed", exist_ok=True)
    
    for raw_file in raw_files:
        # Extract ticker from path (e.g., sec-edgar-filings\AAPL\...)
        # This structure depends on the OS, so we verify it.
        parts = os.path.normpath(raw_file).split(os.sep)
        # parts might look like ['sec-edgar-filings', 'AAPL', '10-K', '000...', 'primary-document.txt']
        if len(parts) > 1:
            ticker = parts[1] # AAPL
            
            print(f"   - Cleaning {ticker}...")
            clean_text = clean_html_file(raw_file)
            
            # Save to new home
            output_path = f"data/processed/{ticker}_10k_clean.txt"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(clean_text)
                
    print("✨ All files cleaned! Check 'data/processed/' folder.")

if __name__ == "__main__":
    process_filings()
