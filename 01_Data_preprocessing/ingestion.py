import os
from sec_edgar_downloader import Downloader

def download_10k_filings(ticker: str, amount: int = 1):
    """
    Downloads the latest 10-K filings for a given company ticker.
    Using a user-agent string as required by SEC API.
    
    What is a 10-K?
    A 10-K is an annual comprehensive report filed with the SEC. 
    It contains: 
    - Determine Risk Factors (Item 1A) -> THIS IS OUR GOLD MINE.
    - Financial Statements (Item 8) -> Numerical data.
    - Management Discussion (Item 7) -> Future outlook.
    """
    
    # 1. Initialize the Downloader
    # The SEC requires you to identify yourself (Company Name, Email).
    # If you don't provide this, they block your IP.
    email = "shahdeepam96@gmail.com" 
    dl = Downloader("MyPersonalProject", email)
    
    # 2. Define where to save (though this library has a default behavior)
    # The library defaults to creating a 'sec-edgar-filings' folder in the current directory.
    print(f"📥 Downloading latest {amount} 10-K(s) for {ticker}...")
    
    try:
        # 3. The Download Command
        # "10-K": The document type (Annual Report).
        # ticker: "AAPL" (Apple), "MSFT" (Microsoft).
        # limit: How many filings to download (updated from 'amount' to 'limit' for v5+).
        dl.get("10-K", ticker, limit=amount)
        
        print(f"✅ Successfully downloaded {ticker} filings.")
        
    except Exception as e:
        print(f"❌ Failed to download {ticker}: {e}")

if __name__ == "__main__":
    # 4. Our Target Companies
    # We pick these because they have complex supply chains (good for graphs).
    tickers = ["AAPL", "MSFT", "TSLA"]
    
    print("🚀 Starting SEC Download...")
    for t in tickers:
        download_10k_filings(t, amount=1)
    print("✨ Done! Check the 'sec-edgar-filings' folder.")
