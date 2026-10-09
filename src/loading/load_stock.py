
import os
import sys
from pathlib import Path
from decimal import Decimal
from datetime import date

import pandas as pd
import pg8000.dbapi
from dotenv import load_dotenv

# Lokasi utama project FinFlow
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

from config import STOCK_SYMBOLS
from src.loading.incremental import classify_record

load_dotenv(BASE_DIR / ".env")


def load_stock(symbol):
    print(f"Starting incremental loading for {symbol}...")

    # 1. Membaca CSV hasil Transformation
    input_file = (
        BASE_DIR / "data" / "processed"
        / f"{symbol}_processed.csv"
    )

    df = pd.read_csv(input_file, dtype={"symbol": str})

    if df.empty:
        raise ValueError(f"No records available for {symbol}")

    if not df["symbol"].eq(symbol).all():
        raise ValueError(f"Symbol mismatch for {symbol}")

    if df.duplicated(subset=["symbol", "date"]).any():
        raise ValueError("Duplicate records detected")

    # 2. Membuka koneksi PostgreSQL
    connection = pg8000.dbapi.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    counts = {
        "new": 0,
        "changed": 0,
        "unchanged": 0
    }

    try:
        cursor = connection.cursor()

        # 3. Mengambil data lama dari PostgreSQL
        cursor.execute(
            """
            SELECT date, open, high, low, close, volume
            FROM stock_prices
            WHERE symbol = %s
            """,
            (symbol,)
        )

        existing = {}

        for record in cursor.fetchall():
            stock_date, open_, high, low, close, volume = record

            existing[str(stock_date)] = (
                Decimal(str(open_)),
                Decimal(str(high)),
                Decimal(str(low)),
                Decimal(str(close)),
                int(volume)
            )

        # 4. Query UPSERT
        upsert_query = """
            INSERT INTO stock_prices
                (symbol, date, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, date)
            DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume
        """

        # 5. Membandingkan data dan menyimpan perubahan
        for row in df.itertuples(index=False):
            stock_date = date.fromisoformat(str(row.date))

            new_values = (
                Decimal(str(row.open)),
                Decimal(str(row.high)),
                Decimal(str(row.low)),
                Decimal(str(row.close)),
                int(row.volume)
            )

            existing_values = existing.get(str(stock_date))

            status = classify_record(
                new_values,
                existing_values
            )

            counts[status.lower()] += 1

            # Lewati data yang tidak berubah
            if status == "UNCHANGED":
                continue

            cursor.execute(
                upsert_query,
                (symbol, stock_date, *new_values)
            )

        # 6. Menyimpan perubahan ke database
        connection.commit()

        print(f"SUCCESS: {symbol} incremental loading completed!")
        print("NEW:", counts["new"])
        print("CHANGED:", counts["changed"])
        print("UNCHANGED:", counts["unchanged"])
        print("Total Records Checked:", len(df))

        return counts

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    load_stock(STOCK_SYMBOLS[0])
