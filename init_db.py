import os
from dotenv import load_dotenv
import psycopg

load_dotenv()
db_url = os.getenv("DATABASE_URL")

print("--- Attempting to connect to PostgreSQL ---")

try:
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            print("Connected successfully! Reading schema.sql...")
            
            with open("schema.sql", "r") as f:
                schema_sql = f.read()
            
            cur.execute(schema_sql)
            print("Tables created and seed data inserted successfully!")
            
except Exception as e:
    print("\n[ERROR] Connection failed. Check your password or service status.")
    print(f"Details: {e}")