import psycopg2
from psycopg2 import pool

class Database:
    def __init__(self):
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=20,
            user="postgres",
            password="@qeadzc",
            host="localhost",
            port="5431",
            database="invoice-db"
        )
    
    def get_connection(self):
        return self.connection_pool.getconn()
    
    def put_connection(self, conn):
        self.connection_pool.putconn(conn)
    
    def close_all(self):
        self.connection_pool.closeall()

# Initialize database connection
db = Database()