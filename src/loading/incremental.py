
import os
from pathlib import Path
from decimal import Decimal

import pandas as pd
import pg8000.dbapi
from dotenv import load_dotenv

# ==========================================
# FINFLOW - INCREMENTAL DATA CHECK
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


def classify_record(new_values, existing_values):
    """
    Menentukan status record:
    NEW, CHANGED, atau UNCHANGED.
    """
    if existing_values is None:
        return "NEW"

    if new_values != existing_values:
        return "CHANGED"

    return "UNCHANGED"


def check_incremental(symbol):
    print(f"Checking incremental data for {symbol}...")

    # 1. Membaca CSV hasil Transformation
    csv_path = (
        BASE_DIR / "data" / "processed"
        / f"{symbol}_processed.csv"
    )

    df = pd.read_csv(csv_path, dtype={"symbol": str})

    if df.empty:
        raise ValueError("CSV is empty")

    if not df["symbol"].eq(symbol).all():
        raise ValueError("Stock symbol mismatch")

    # 2. Menghubungkan Python ke PostgreSQL
    connection = pg8000.dbapi.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT date, open, high, low, close, volume
            FROM stock_prices
            WHERE symbol = %s
            """,
            (symbol,)
        )

        # 3. Menyimpan data database berdasarkan tanggal
        existing = {}

        for stock_date, open_, high, low, close, volume in cursor.fetchall():
            existing[str(stock_date)] = (
                Decimal(str(open_)),
                Decimal(str(high)),
                Decimal(str(low)),
                Decimal(str(close)),
                int(volume)
            )

        # 4. Membandingkan setiap record CSV
        new_records = 0
        changed_records = 0
        unchanged_records = 0

        for row in df.itertuples(index=False):
            stock_date = str(row.date)

            new_values = (
                Decimal(str(row.open)),
                Decimal(str(row.high)),
                Decimal(str(row.low)),
                Decimal(str(row.close)),
                int(row.volume)
            )

            existing_values = existing.get(stock_date)

            status = classify_record(
                new_values,
                existing_values
            )

            if status == "NEW":
                new_records += 1

            elif status == "CHANGED":
                changed_records += 1

            else:
                unchanged_records += 1

        # 5. Menampilkan hasil pemeriksaan
        print(f"SUCCESS: Incremental check for {symbol}")
        print("NEW:", new_records)
        print("CHANGED:", changed_records)
        print("UNCHANGED:", unchanged_records)

        return {
            "new": new_records,
            "changed": changed_records,
            "unchanged": unchanged_records
        }

    finally:
        connection.close()


if __name__ == "__main__":
    check_incremental("AAPL")
