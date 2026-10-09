
import json
from pathlib import Path

# Lokasi folder utama FinFlow
BASE_DIR = Path(__file__).resolve().parents[2]


def extract_offline(symbol):
    """
    Membaca data saham dari JSON lokal
    tanpa melakukan request ke API.
    """
    symbol = symbol.upper().strip()

    print(f"Starting offline extraction for {symbol}...")

    # 1. Lokasi file JSON mentah
    raw_file = (
        BASE_DIR / "data" / "raw"
        / f"{symbol}_raw.json"
    )

    # 2. Memastikan file tersedia
    if not raw_file.is_file():
        raise FileNotFoundError(
            f"Raw data for {symbol} not found: {raw_file}"
        )

    # 3. Membaca JSON lokal
    with raw_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    # 4. Memeriksa struktur respons Alpha Vantage
    time_series = data.get("Time Series (Daily)")

    if not isinstance(time_series, dict) or not time_series:
        raise ValueError(
            f"Invalid or empty stock data for {symbol}"
        )

    # 5. Memeriksa simbol saham jika tersedia
    metadata = data.get("Meta Data", {})
    if isinstance(metadata, dict):
        file_symbol = metadata.get("2. Symbol")

        if file_symbol and file_symbol.upper() != symbol:
            raise ValueError(
                f"Symbol mismatch: expected {symbol}, "
                f"found {file_symbol}"
            )

    print(f"SUCCESS: {symbol} offline extraction completed!")
    print("Total Records:", len(time_series))
    print("Source: Local JSON")
    print("File:", raw_file)

    return data


if __name__ == "__main__":
    extract_offline("MSFT")
