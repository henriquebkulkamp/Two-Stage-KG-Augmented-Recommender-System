from typing import List
from pydantic import BaseModel, Field

DIMENSION = 64


class RecommendationRequest(BaseModel):
    """Schema representing a raw vector search request payload."""

    vector: List[float] = Field(
        ...,
        min_items=DIMENSION,
        max_items=DIMENSION,
        description=f"Vetor de busca contendo exatamente {DIMENSION} dimensões.",
    )


class UserItem(BaseModel):
    """Schema representing basic user metadata for list views."""

    user_id: str
    name: str


class NamesPaginatedResponse(BaseModel):
    """Schema for paginated user listing responses."""

    page: int
    page_size: int
    total_users: int
    has_next: bool
    users: List[UserItem]


class UserEmbeddingResponse(BaseModel):
    """Schema representing resolved user metadata alongside their embedding vector."""

    user_id: str
    name: str
    embedding: List[float]