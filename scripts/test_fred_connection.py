"""
Phase 3 / Step 4 — connection proof only.

Deliberately NOT the ingestion pipeline (that's Step 5). Just proves we
can pull real US economic data from FRED before building anything
permanent on top of it.
"""

import os

from dotenv import load_dotenv
from fredapi import Fred

load_dotenv()


def main():
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        print("FAILED: FRED_API_KEY not found in .env")
        return

    fred = Fred(api_key=api_key)

    # CPIAUCSL = US Consumer Price Index, a real, well-known FRED series
    data = fred.get_series("CPIAUCSL", observation_start="2025-01-01")

    print(data.tail())

    if data.empty:
        print("\nFAILED: no data returned.")
    else:
        print(f"\nSUCCESS: pulled {len(data)} rows of real US CPI data from FRED.")


if __name__ == "__main__":
    main()
