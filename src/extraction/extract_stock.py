
import os
import sys
import json
from pathlib import Path

import requests
from dotenv import load_dotenv

# Lokasi folder utama FinFlow
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

from config import (
    STOCK_SYMBOLS,
    API_BASE_URL,
    API_FUNCTION,
    REQUEST_TIMEOUT
)

load_dotenv(BASE_DIR / ".env")


def extract_stock(symbol):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

    if not api_key:
        raise ValueError("ALPHA_VANTAGE_API_KEY is missing in .env")

    print(f"Starting extraction for {symbol}...")

    params = {
        "function": API_FUNCTION,
        "symbol": symbol,
        "apikey": api_key
    }

    response = requests.get(
        API_BASE_URL,
        params=params,
        timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()

    data = response.json()

    if "Time Series (Daily)" not in data:
        raise ValueError(
            f"Alpha Vantage did not return stock data for {symbol}: "
            f"{list(data.keys())}"
        )

    stock_data = data["Time Series (Daily)"]

    if not stock_data:
        raise ValueError(f"No stock records returned for {symbol}")

    # Menyimpan data mentah
    raw_folder = BASE_DIR / "data" / "raw"
    raw_folder.mkdir(parents=True, exist_ok=True)

    output_file = raw_folder / f"{symbol}_raw.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print(f"SUCCESS: {symbol} extraction completed!")
    print("Total Records:", len(stock_data))
    print("Saved to:", output_file)

    return output_file


if __name__ == "__main__":
    # Pengujian awal: hanya satu saham
    extract_stock(STOCK_SYMBOLS[0])
