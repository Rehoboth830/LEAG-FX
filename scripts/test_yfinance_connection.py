"""
Phase 3 / Step 2 - connection proof only.

This is deliberately NOT the ingestion pipeline (that's Step 3). Its only
job is to prove we can pull real USD/JPY data from yfinance before we
build anything more permanent on top of it.
"""

import yfinance as yf

def main():
    ticker = yf.Ticker("USDJPY=X")
    data = ticker.history(period="5d")

    print("Columns returned:", list(data.columns))
    print()
    print(data)

    if data.empty:
        print("\nFAILED: no data returned. Connection or symbol issue.")
    else:
        print(f"\nSUCCESS: pulled {len(data)} rows of real USD/JPY data.")


if __name__ == "__main__":
    main()
