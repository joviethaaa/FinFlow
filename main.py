
import sys
import time
from pathlib import Path
from time import perf_counter

# Lokasi utama project FinFlow
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config import STOCK_SYMBOLS, REQUEST_DELAY
from src.logger import setup_logger
from src.extraction.extract_stock import extract_stock
from src.transformation.transform_stock import transform_stock
from src.validation.validate_stock import validate_stock
from src.loading.load_stock import load_stock

# Mengaktifkan logger
logger = setup_logger()


def run_pipeline(symbol):
    start_time = perf_counter()

    logger.info("Starting pipeline for %s", symbol)

    try:
        # 1. Extraction
        logger.info("Starting extraction: %s", symbol)
        extract_stock(symbol)
        logger.info("Extraction completed: %s", symbol)

        # 2. Transformation
        logger.info("Starting transformation: %s", symbol)
        transform_stock(symbol)
        logger.info("Transformation completed: %s", symbol)

        # 3. Validation
        logger.info("Starting validation: %s", symbol)

        if not validate_stock(symbol):
            raise ValueError(f"Validation failed for {symbol}")

        logger.info("Validation completed: %s", symbol)

        # 4. Incremental Loading
        logger.info("Starting incremental loading: %s", symbol)

        result = load_stock(symbol)

        logger.info(
            "Loading completed: %s | NEW=%d | CHANGED=%d | UNCHANGED=%d",
            symbol,
            result["new"],
            result["changed"],
            result["unchanged"]
        )

        duration = perf_counter() - start_time

        logger.info(
            "Pipeline completed: %s | Duration: %.2f seconds",
            symbol,
            duration
        )

    except Exception:
        logger.exception("Pipeline failed for %s", symbol)
        raise


def main():
    logger.info("FINFLOW PIPELINE STARTED")

    # Tetap gunakan MSFT untuk sementara
    symbols_to_process = ["MSFT"]

    try:
        for index, symbol in enumerate(symbols_to_process):
            run_pipeline(symbol)

            if index < len(symbols_to_process) - 1:
                time.sleep(REQUEST_DELAY)

        logger.info("FINFLOW PIPELINE COMPLETED SUCCESSFULLY")

    except Exception:
        logger.error("FINFLOW PIPELINE STOPPED")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
