import os
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

load_dotenv()
db_url = os.getenv("DATABASE_URL")

pool = ConnectionPool(conninfo=db_url, max_size=4)

def get_customer_profile(email: str):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT u.user_id, u.name, u.account_tier, s.status, s.failed_attempts_count 
                FROM users u
                LEFT JOIN subscriptions s ON u.user_id = s.user_id
                WHERE u.email = %s;
            """
            cur.execute(query, (email,))
            result = cur.fetchone()
            
            if not result:
                return None
                
            return {
                "user_id": result[0],
                "name": result[1],
                "tier": result[2],
                "status": result[3],
                "failed_attempts": result[4]
            }