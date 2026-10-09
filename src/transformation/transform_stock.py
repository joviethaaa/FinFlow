
import json
import sys
from pathlib import Path

import pandas as pd

# Lokasi folder utama FinFlow
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

from config import STOCK_SYMBOLS


def transform_stock(symbol):
    input_file = BASE_DIR / "data" / "raw" / f"{symbol}_raw.json"
    output_file = BASE_DIR / "data" / "processed" / f"{symbol}_processed.csv"

    print(f"Starting transformation for {symbol}...")

    # 1. Membaca JSON hasil Extraction
    with open(input_file, "r", encoding="utf-8") as file:
        raw_data = json.load(file)

    if "Time Series (Daily)" not in raw_data:
        raise ValueError(f"Invalid stock data for {symbol}")

    stock_data = raw_data["Time Series (Daily)"]

    if not stock_data:
        raise ValueError(f"No stock records for {symbol}")

    # 2. Mengubah JSON menjadi DataFrame
    df = pd.DataFrame.from_dict(stock_data, orient="index")

    # 3. Merapikan nama kolom
    df = df.rename(columns={
        "1. open": "open",
        "2. high": "high",
        "3. low": "low",
        "4. close": "close",
        "5. volume": "volume"
    })

    # 4. Menambahkan tanggal dan simbol saham
    df.index.name = "date"
    df = df.reset_index()
    df["symbol"] = symbol

    # 5. Mengubah tipe data
    df["date"] = pd.to_datetime(df["date"])

    for column in ["open", "high", "low", "close"]:
        df[column] = pd.to_numeric(df[column])

    df["volume"] = pd.to_numeric(df["volume"]).astype("int64")

    # 6. Menghapus duplikat dan mengurutkan tanggal
    df = df.drop_duplicates(subset=["symbol", "date"])
    df = df.sort_values("date").reset_index(drop=True)

    # 7. Mengatur urutan kolom
    df = df[
        ["date", "symbol", "open", "high", "low", "close", "volume"]
    ]

    # 8. Menyimpan CSV hasil transformasi
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)

    print(f"SUCCESS: {symbol} transformation completed!")
    print("Total Records:", len(df))
    print("Saved to:", output_file)

    return output_file


if __name__ == "__main__":
    # Pengujian awal: hanya saham pertama (AAPL)
    transform_stock(STOCK_SYMBOLS[0])
