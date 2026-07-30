# Two-Stage KG-Augmented Recommender System

A two-stage recommendation pipeline that combines a **knowledge-graph-based GNN** (LightKG) for embedding generation with a **Neo4j vector index** for fast candidate retrieval, backed by **PostgreSQL** for structured metadata.

## Architecture

This repo currently implements **Stage 1 — Candidate Generation** of a two-stage recommender system. A second, heavier ranking stage is planned to re-rank the candidates produced here.

1. **Embedding generation:** [LightKG](https://github.com/henriquebkulkamp/LightKG) (a GNN trained on a knowledge graph built from user-item interactions) generates dense embeddings for users and items.
2. **Candidate retrieval:** Embeddings are indexed in **Neo4j**, used as a vector store to retrieve the top-K nearest candidates for a given user via similarity search.
3. **Metadata layer:** **PostgreSQL** stores structured user/item metadata and ID mappings, joined with the retrieved candidates to build the final response.

The candidate generation pipeline (embedding lookup → vector retrieval → metadata join) achieves an average **69.84ms warm-request latency**, making it suitable for near real-time serving.

**Planned — Stage 2 — Heavy Ranking:** a more expensive ranking model to re-rank the candidates retrieved in Stage 1, using richer user/item features.

## Repository Structure

```
.
├── LightKG/              # GNN model (git submodule)
├── app/                  # Serving application
├── setup_neo4j.py        # Provisions the Neo4j graph/vector index
├── setup_postgres.py     # Provisions the PostgreSQL schema
└── users_mapping.tsv     # User ID mapping between datasets/stores
```

## Prerequisites

- Python 3.9+
- Docker (used to run Neo4j and PostgreSQL)
- LightKG dependencies (PyTorch, RecBole) — see the [LightKG fork](https://github.com/henriquebkulkamp/LightKG)

## Setup

> A virtual environment isn't set up yet — it's recommended to create one (`python -m venv venv`) before installing dependencies.

1. **Clone with submodules**

   ```bash
   git clone --recurse-submodules https://github.com/henriquebkulkamp/Two-Stage-KG-Augmented-Recommender-System.git
   cd Two-Stage-KG-Augmented-Recommender-System
   ```

2. **Train LightKG and generate embeddings**

   Follow the [LightKG fork README](https://github.com/henriquebkulkamp/LightKG) to install its dependencies and train the model:

   ```bash
   cd LightKG
   python main.py
   ```

   Once training is done, generate the user and item embeddings that will feed the vector index:

   ```bash
   python generate_embeddings.py
   ```

3. **Spin up the databases with Docker**

   ```bash
   docker run --name postgres-recsys \
     -e POSTGRES_PASSWORD=senha123 \
     -e POSTGRES_DB=recsys_db \
     -p 5432:5432 \
     -d postgres

   docker run --name neo4j \
     -p7474:7474 \
     -p7687:7687 \
     -e NEO4J_AUTH=neo4j/senha123 \
     -e NEO4J_PLUGINS='["graph-data-science"]' \
     -v $HOME/neo4j/data:/data \
     -d neo4j:2026
   ```

4. **Provision the databases**

   Back in the project root:

   ```bash
   python setup_postgres.py
   python setup_neo4j.py
   ```

   This creates the PostgreSQL schema and loads the LightKG-generated embeddings into the Neo4j vector index.

5. **Run the app**

   ```bash
   cd app
   python app.py
   ```

## Performance

| Metric | Value |
|---|---|
| Avg. warm-request latency (Reqs #2–#10) | **69.84 ms** |

### LightKG standalone ranking quality (Amazon Luxury Beauty, @10)

| Metric | Value |
|---|---|
| Recall | 0.2633 |
| MRR | 0.2354 |
| NDCG | 0.2394 |
| Hit Rate | 0.2774 |
| Precision | 0.0365 |

## Tech Stack

- **Modeling:** PyTorch, RecBole, LightKG (GNN)
- **Vector retrieval / Knowledge Graph:** Neo4j, Cypher
- **Metadata store:** PostgreSQL

## Related

- [LightKG fork](https://github.com/henriquebkulkamp/LightKG) — extended GNN architecture, adapted for the Amazon Luxury Beauty dataset with custom preprocessing and 5-core filtering.

## License

This project is licensed under the [MIT License](LICENSE).
