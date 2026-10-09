
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

from config import STOCK_SYMBOLS


REQUIRED_COLUMNS = [
    "date", "symbol", "open", "high",
    "low", "close", "volume"
]


def validate_stock(symbol):
    input_file = (
        BASE_DIR / "data" / "processed" /
        f"{symbol}_processed.csv"
    )

    print(f"Starting validation for {symbol}...")

    # 1. Membaca data hasil Transformation
    df = pd.read_csv(input_file)
    errors = []

    # 2. Memeriksa kelengkapan kolom
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        errors.append(f"Missing columns: {missing_columns}")
        print("FAILED:", errors)
        return False

    # 3. Memeriksa data kosong
    if df.empty:
        errors.append("Dataset is empty")
    elif df[REQUIRED_COLUMNS].isnull().any().any():
        errors.append("Missing values detected")

    # 4. Memeriksa simbol saham
    if not df.empty and not df["symbol"].eq(symbol).all():
        errors.append("Stock symbol does not match")

    # 5. Memeriksa duplikat
    if df.duplicated(subset=["symbol", "date"]).any():
        errors.append("Duplicate records detected")

    # 6. Memeriksa tanggal
    dates = pd.to_datetime(
        df["date"],
        errors="coerce",
        format="%Y-%m-%d"
    )

    if dates.isnull().any():
        errors.append("Invalid dates detected")

    # 7. Memeriksa harga
    price_columns = ["open", "high", "low", "close"]

    prices = df[price_columns].apply(
        pd.to_numeric,
        errors="coerce"
    )

    if prices.isnull().any().any():
        errors.append("Invalid price values detected")

    if (prices <= 0).any().any():
        errors.append("Stock prices must be positive")

    if (prices["high"] < prices["low"]).any():
        errors.append("High price cannot be below low")

    for column in ["open", "close"]:
        if (
            (prices[column] < prices["low"]) |
            (prices[column] > prices["high"])
        ).any():
            errors.append(
                f"{column} must be between low and high"
            )

    # 8. Memeriksa volume
    volume = pd.to_numeric(
        df["volume"],
        errors="coerce"
    )

    if volume.isnull().any():
        errors.append("Invalid volume detected")

    if (volume < 0).any():
        errors.append("Volume cannot be negative")

    if ((volume % 1) != 0).any():
        errors.append("Volume must be a whole number")

    # 9. Hasil validasi
    if errors:
        print(f"FAILED: {symbol} validation failed!")

        for error in errors:
            print("-", error)

        return False

    print(f"SUCCESS: {symbol} validation completed!")
    print("Total Records:", len(df))
    print("Data is ready for PostgreSQL loading.")

    return True


if __name__ == "__main__":
    # Pengujian awal: AAPL saja
    if not validate_stock(STOCK_SYMBOLS[0]):
        sys.exit(1)
