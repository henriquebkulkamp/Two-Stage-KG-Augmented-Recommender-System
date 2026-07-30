import pandas as pd
from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "senha123")

ITEMS_PARQUET = "/home/henrique/kg/teste_github/Two-Stage KG-Augmented Recommender System/LightKG/embeddings/items-LightKG-Jul-28-2026_09-28-32.parquet"
USERS_PARQUET = "/home/henrique/kg/teste_github/Two-Stage KG-Augmented Recommender System/LightKG/embeddings/users-LightKG-Jul-28-2026_09-28-32.parquet"

DIMENSION = 64
BATCH_SIZE = 1000


def populate_node_type(session, label: str, index_name: str, file_path: str):
    print(f"\n--- Processing {label}s ---")

    print(f"1. Ensuring primary index on :{label}(id)...")
    session.run(
        f"CREATE CONSTRAINT constraint_{label.lower()}_id IF NOT EXISTS FOR (n:{label}) REQUIRE n.id IS UNIQUE"
    )

    print(f"2. Creating vector index '{index_name}'...")
    session.run(
        f"""
        CREATE VECTOR INDEX `{index_name}` IF NOT EXISTS
        FOR (n:{label}) ON (n.embedding)
        OPTIONS {{
          indexConfig: {{
            `vector.dimensions`: {DIMENSION},
            `vector.similarity_function`: 'cosine'
          }}
        }}
        """
    )

    # Loading Parquet and Insert
    print(f"3. Loading data from {file_path}...")
    df = pd.read_parquet(file_path)

    if "id" not in df.columns and "item_id" in df.columns:
        df.rename(columns={"item_id": "id"}, inplace=True)
    elif "id" not in df.columns and "user_id" in df.columns:
        df.rename(columns={"user_id": "id"}, inplace=True)

    total_rows = len(df)
    records = df[["id", "embedding"]].to_dict(orient="records")

    query = f"""
    UNWIND $batch AS row
    MERGE (n:{label} {{id: row.id}})
    SET n.embedding = row.embedding
    """

    print(f"4. Inserting nodes and embeddings in batches...")
    for i in range(0, total_rows, BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        for entry in batch:
            if not isinstance(entry["embedding"], list):
                entry["embedding"] = list(entry["embedding"])

        session.run(query, batch=batch)
        print(f"   Inserted {min(i + BATCH_SIZE, total_rows)}/{total_rows} {label.lower()}s...")


def setup_neo4j():
    print("Connecting to Neo4j...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)

    with driver.session() as session:
        populate_node_type(session, "Item", "item_embeddings", ITEMS_PARQUET)
        populate_node_type(session, "User", "user_embeddings", USERS_PARQUET)

    driver.close()
    print("\n✓ Neo4j populated and indexed")


if __name__ == "__main__":
    setup_neo4j()