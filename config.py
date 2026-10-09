
# ==========================================
# FINFLOW - PIPELINE CONFIGURATION
# ==========================================

# Daftar saham yang akan diproses
STOCK_SYMBOLS = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "NVDA"
]

# Konfigurasi Alpha Vantage
API_BASE_URL = "https://www.alphavantage.co/query"

# Jenis data saham yang diambil
API_FUNCTION = "TIME_SERIES_DAILY"

# Batas waktu permintaan API (detik)
REQUEST_TIMEOUT = 30

# Jeda antarpermintaan API (detik)
# Nilai ini tidak menjamin kepatuhan terhadap kuota harian.
REQUEST_DELAY = 15
