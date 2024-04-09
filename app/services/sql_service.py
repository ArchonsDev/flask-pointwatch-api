import mysql.connector.pooling
import json
import os

class MySQLPool:
    def __init__(self) -> None:
        with open(os.path.join(os.path.dirname(__file__),"..", "settings.json"), "r") as f:
            DB_CONFIG = json.load(f)

        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="myPool",
            pool_size=16,
            **DB_CONFIG
        )

    def __enter__(self) -> mysql.connector.pooling.PooledMySQLConnection:
        self.conn = self.connection_pool.get_connection()
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.conn.commit()
        self.conn.close()
        self.conn = None