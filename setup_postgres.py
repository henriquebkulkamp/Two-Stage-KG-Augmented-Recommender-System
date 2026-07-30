import csv
import psycopg2

PG_HOST = "localhost"
PG_PORT = "5432"
PG_DB = "recsys_db"
PG_USER = "postgres"
PG_PASSWORD = "senha123"

FILE_PATH = "users_mapping.tsv"


def setup_database():
    print("1. Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
    )
    cursor = conn.cursor()

    print("2. Creating table 'users' and Hash Index...")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
        -- Hash Index for exact equality searches by name in O(1)
        CREATE INDEX IF NOT EXISTS idx_users_name_hash ON users USING HASH (name);
        """
    )

    print("3. Loading data from TSV file...")
    with open(FILE_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)  # Skip the header

        insert_query = """
            INSERT INTO users (user_id, name) 
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO UPDATE SET name = EXCLUDED.name;
        """

        users_data = [(row[0], row[1]) for row in reader if len(row) >= 2]
        print(f"   Inserindo {len(users_data)} usuários...")
        cursor.executemany(insert_query, users_data)

    conn.commit()
    cursor.close()
    conn.close()
    print("PostgreSQL configured with success and Hash Index created!")


if __name__ == "__main__":
    setup_database()