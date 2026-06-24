# Day 2 Revision: The Data Pipeline Story

## The "Data Pipeline" Analogy
In the industry, building the pipeline is often 80% of the job. Here is the story of what your code (`ingestion.py` and `cleaner.py`) actually did today.

### Part 1: The Courier (`ingestion.py`)
**Goal:** Specific documents from a massive government library (The SEC).

1.  **The ID Card (`user_agent`):** 
    *   **Concept:** You can't just walk into the SEC database anonymously. The library requires you to state your name and email. 
    *   **Code:** `Downloader("MyProj", "my@email.com")` puts on this badge. If we didn't wear it, we get blocked (403 Forbidden).

2.  **The Order:** 
    *   **Concept:** You told the courier: "Go to the Apple (AAPL), Microsoft (MSFT), and Tesla (TSLA) sections. Get me the *latest* Annual Report (10-K), but just 1 copy."
    *   **Code:** `dl.get("10-K", ticker, limit=1)`

3.  **The Delivery:** 
    *   **Result:** The courier grabbed the raw files.
    *   **Problem:** These files are messy. They are full of computer code (`<HTML>`, `<DIV>`, `<XBRL>`). They are not ready for reading.

### Part 2: The Filter (`cleaner.py`)
**Goal:** Turn "Computer Language" into "Human Language".

1.  **The Scanner (`glob`):** 
    *   **Concept:** A robot that walks through every folder (`sec-edgar-filings/**/*.txt`) looking for files to clean.
    
2.  **The Translatr (`BeautifulSoup`):** 
    *   **Concept:** This is the smart tool. It looks at a mess like:
        > `<div style="bold">Item 1A: Risk Factors</div>`
    *   And strips away the tags to just keep:
        > **Item 1A: Risk Factors**
    
3.  **The Result:** 
    *   It saved clean, readable English text into `data/processed`.
    *   **Why this matters:** If we fed the HTML to our AI (NER models), it would try to learn what `<div>` means. We want it to learn what "Apple Inc" means.

---

## Technical Key Terms
*   **SEC EDGAR:** The database of all US Public Company filings.
*   **10-K:** The Annual Report (The "Truth" document).
*   **User-Agent:** The string identifying who you are to a web server.
*   **BeautifulSoup:** A Python library for pulling data out of HTML and XML files.
