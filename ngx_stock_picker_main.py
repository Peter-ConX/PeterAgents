#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime

from stock_picker.crew import StockPicker

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the NGX stock research crew.
    """
    inputs = {
        "sector": "Technology",   # Example: Technology, Banking, Oil & Gas, Consumer Goods
        "current_date": str(datetime.now().date())
    }

    try:
        # Create and run the crew
        result = StockPicker().crew().kickoff(inputs=inputs)

        # Print the result
        print("\n\n=== FINAL DECISION ===\n\n")
        print(result.raw)

        # Save output for record keeping
        os.makedirs("output", exist_ok=True)
        with open("output/decision.log", "w", encoding="utf-8") as f:
            f.write(result.raw)

    except Exception as e:
        print(f"❌ Error running crew: {e}")


if __name__ == "__main__":
    run()
