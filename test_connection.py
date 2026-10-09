import os
import pg8000.dbapi
from dotenv import load_dotenv

load_dotenv()

try:
    connection = pg8000.dbapi.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    print("SUCCESS: Connected to PostgreSQL!")
    print("Database:", os.getenv("DB_NAME"))

    connection.close()

except Exception as error:
    print("FAILED: Could not connect to PostgreSQL!")
    print("Error type:", type(error).__name__)
    print("Error details:", str(error))