
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

# Konfigurasi pengujian
STOCK_SYMBOL = "MSFT"
EXTRACTION_MODE = "offline"


def run_extraction():
    if EXTRACTION_MODE == "offline":
        from src.extraction.extract_offline import extract_offline

        extract_offline(STOCK_SYMBOL)

    elif EXTRACTION_MODE == "live":
        from src.extraction.extract_stock import extract_stock

        extract_stock(STOCK_SYMBOL)

    else:
        raise ValueError(
            f"Unknown extraction mode: {EXTRACTION_MODE}"
        )


def run_transformation():
    from src.transformation.transform_stock import transform_stock

    transform_stock(STOCK_SYMBOL)


def run_validation():
    from src.validation.validate_stock import validate_stock

    if not validate_stock(STOCK_SYMBOL):
        raise ValueError(
            f"Validation failed for {STOCK_SYMBOL}"
        )


def run_loading():
    from src.loading.load_stock import load_stock

    load_stock(STOCK_SYMBOL)


with DAG(
    dag_id="finflow_financial_pipeline",
    description="FinFlow financial ETL pipeline with offline testing",
    start_date=datetime(2026, 10, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["finflow", "data-engineering", "etl"],
) as dag:

    extraction = PythonOperator(
        task_id="extract_stock_data",
        python_callable=run_extraction,
        retries=0,
    )

    transformation = PythonOperator(
        task_id="transform_stock_data",
        python_callable=run_transformation,
    )

    validation = PythonOperator(
        task_id="validate_stock_data",
        python_callable=run_validation,
    )

    loading = PythonOperator(
        task_id="load_stock_data",
        python_callable=run_loading,
    )

    extraction >> transformation >> validation >> loading
