
# Base image Apache Airflow
FROM apache/airflow:2.11.2

# Install library Python untuk FinFlow
# Gunakan pip sebagai user airflow (non-root)
RUN pip install --no-cache-dir \
    pandas \
    requests \
    pg8000 \
    python-dotenv
