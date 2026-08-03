from typing import List
from fastapi import HTTPException
from services import database, users
# import time

TOP_K = 50

# Query otimizada: busca direto do índice HNSW por COSINE (sem REDUCE manual)
MIPS_QUERY = """
MATCH (item:Item)
SEARCH item IN (
  VECTOR INDEX item_embeddings
  FOR $vector
  LIMIT $top_k
) SCORE as score
ORDER BY score DESC
RETURN collect(item.id) AS itemId
"""


def fetch_recommendations(vector: List[float], top_k: int = TOP_K) -> List[str]:
    """Fetch Top-K item recommendations using vector search in Neo4j.

    Args:
        vector (List[float]): Raw vector embedding.
        top_k (int, optional): Number of recommendations to return. Defaults to 50.

    Returns:
        List[str]: List of recommended item IDs.

    Raises:
        HTTPException: 400 if top_k > TOP_K or 500 on database error.
    """
    if top_k > TOP_K:
        raise HTTPException(
            status_code=400,
            detail=f"top_k não pode ser maior que {TOP_K}.",
        )

    try:
        with database.driver.session() as session:
            result = session.run(
                MIPS_QUERY,
                vector=vector,
                top_k=top_k,
            )
            record = result.single()
            items_id = record["itemId"] if record else []

            return items_id
    except Exception as e:
        print("Erro:", e)
        raise HTTPException(
            status_code=500, detail=f"Erro na recomendação (Neo4j): {str(e)}"
        )


def get_recommendations_by_identifier(identifier: str, top_k: int = 10) -> List[str]:
    """Fetch user embedding vector and execute recommendation search.

    Args:
        identifier (str): Exact user display name or unique user ID.
        top_k (int, optional): Number of recommendations to return. Defaults to 10.

    Returns:
        List[str]: Recommended item IDs.
    """
    user_data = users.get_user_embedding_by_identifier(identifier)

    return fetch_recommendations(vector=user_data.embedding, top_k=top_k)