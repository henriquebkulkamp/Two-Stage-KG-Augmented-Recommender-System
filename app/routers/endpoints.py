from typing import List
from fastapi import APIRouter, Query
from schemas.models import (
    NamesPaginatedResponse,
    RecommendationRequest,
    UserEmbeddingResponse,
)
from services import rec, users

router = APIRouter()


# --- RECOMMENDATION ENDPOINTS ---

@router.post(
    "/recommendations",
    response_model=List[str],
    summary="Obter recomendações MIPS enviando um vetor bruto",
)
async def get_recommendations(payload: RecommendationRequest) -> List[str]:
    """Fetch Top-K item recommendations using a raw input embedding vector.

    Args:
        payload (RecommendationRequest): Request body containing the raw vector.

    Returns:
        List[str]: List of recommended item IDs ordered by relevance score.
    """
    return rec.fetch_recommendations(payload.vector)


@router.get(
    "/recommendations/user",
    response_model=List[str],
    summary="Obter recomendações Top-K a partir do Nome ou ID do Usuário",
)
async def get_recommendations_by_user(
    identifier: str = Query(
        ...,
        description="Nome exato ou User ID do usuário para gerar os candidatos",
    ),
    top_k: int = Query(
        10,
        ge=1,
        le=100,
        description="Quantidade de produtos recomendados a retornar",
    ),
) -> List[str]:
    """Generate Top-K recommendations for a user resolved by name or ID.

    Fetches the user's vector embedding in O(1) time complexity and executes
    a MIPS candidate generation query on Neo4j.

    Args:
        identifier (str): Exact user display name or unique user ID.
        top_k (int, optional): Number of recommendations to return. Defaults to 10.

    Returns:
        List[str]: List of top recommended item IDs.
    """
    return rec.get_recommendations_by_identifier(identifier, top_k=top_k)


# --- USER ENDPOINTS ---

@router.get(
    "/names",
    response_model=NamesPaginatedResponse,
    summary="Listar nomes de usuários paginados",
)
async def get_names(
    page: int = Query(1, ge=1, description="Número da página (inicia em 1)"),
    page_size: int = Query(30, ge=1, le=100, description="Tamanho da página"),
) -> NamesPaginatedResponse:
    """Retrieve a paginated list of registered user names.

    Args:
        page (int, optional): Page index starting at 1. Defaults to 1.
        page_size (int, optional): Number of items per page. Defaults to 30.

    Returns:
        NamesPaginatedResponse: Paginated result set containing users and metadata.
    """
    return users.fetch_paginated_users(page, page_size)


@router.get(
    "/user-embedding",
    response_model=UserEmbeddingResponse,
    summary="Obter embedding por Nome ou User ID",
)
async def get_user_embedding(
    identifier: str = Query(
        ...,
        description="Nome exato ou User ID do usuário para busca rápida em O(1)",
    ),
) -> UserEmbeddingResponse:
    """Retrieve user metadata and embedding vector by name or user ID.

    Args:
        identifier (str): Exact user display name or unique user ID.

    Returns:
        UserEmbeddingResponse: Schema containing user metadata and vector embedding.
    """
    return users.get_user_embedding_by_identifier(identifier)