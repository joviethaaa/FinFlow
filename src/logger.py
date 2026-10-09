
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Lokasi folder utama project
BASE_DIR = Path(__file__).resolve().parents[1]

# Lokasi penyimpanan log
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "finflow.log"


def setup_logger():
    logger = logging.getLogger("FinFlow")
    logger.setLevel(logging.INFO)

    # Menghindari handler ganda
    if logger.handlers:
        return logger

    # Format catatan log
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Menyimpan log ke file
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # Menampilkan log di terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
