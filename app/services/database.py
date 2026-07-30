from neo4j import GraphDatabase
import psycopg2.pool

NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "senha123")

PG_HOST = "localhost"
PG_PORT = "5432"
PG_DB = "recsys_db"
PG_USER = "postgres"
PG_PASSWORD = "senha123"

driver = None
pg_pool = None


def init_db() -> None:
    """Initialize database connection drivers and pools.

    Instantiates the Neo4j GraphDatabase driver and establishes a connection
    pool for PostgreSQL.
    """
    global driver, pg_pool
    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    pg_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
    )


def close_db() -> None:
    """Close active database drivers and connection pools gracefully."""
    global driver, pg_pool
    if driver:
        driver.close()
    if pg_pool:
        pg_pool.closeall()