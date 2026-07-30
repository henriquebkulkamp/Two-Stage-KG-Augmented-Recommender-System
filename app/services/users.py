import math
from fastapi import HTTPException
from schemas.models import NamesPaginatedResponse, UserEmbeddingResponse, UserItem
from services import database


def fetch_paginated_users(page: int, page_size: int) -> NamesPaginatedResponse:
    """Fetch a paginated list of users ordered by name.

    Queries the PostgreSQL database to retrieve a subset of users based on pagination
    parameters, including overall metadata for pagination control.

    Args:
        page (int): The target page number (1-indexed).
        page_size (int): The number of user records to retrieve per page.

    Returns:
        NamesPaginatedResponse: Schema containing the paginated list of users,
            current page info, total user count, and pagination status.

    Raises:
        HTTPException: 500 status code if a database query execution fails.
    """
    offset = (page - 1) * page_size
    conn = database.pg_pool.getconn()

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users;")
            total_users = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT user_id, name 
                FROM users 
                ORDER BY name ASC 
                LIMIT %s OFFSET %s;
                """,
                (page_size, offset),
            )
            rows = cursor.fetchall()

            total_pages = math.ceil(total_users / page_size) if total_users > 0 else 0
            has_next = page < total_pages

            users_list = [UserItem(user_id=row[0], name=row[1]) for row in rows]

            return NamesPaginatedResponse(
                page=page,
                page_size=page_size,
                total_users=total_users,
                has_next=has_next,
                users=users_list,
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar usuários (PostgreSQL): {str(e)}"
        )
    finally:
        database.pg_pool.putconn(conn)


def get_user_embedding_by_identifier(identifier: str) -> UserEmbeddingResponse:
    """Fetch user embedding vector by name or user ID in O(1) time complexity.

    Performs an O(1) indexed lookup in PostgreSQL (using a hash or primary key index)
    to resolve the user identity, then retrieves the vector representation from
    Neo4j via its primary key constraint index.

    Args:
        identifier (str): Exact user display name or unique user ID.

    Returns:
        UserEmbeddingResponse: Schema containing user ID, resolved display name,
            and the 64-dimensional float embedding vector.

    Raises:
        HTTPException: 404 status code if the user identity or embedding vector is not found.
        HTTPException: 500 status code on underlying database execution errors.
    """
    conn = database.pg_pool.getconn()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, name 
                FROM users 
                WHERE name = %s OR user_id = %s 
                LIMIT 1;
                """,
                (identifier, identifier),
            )
            row = cursor.fetchone()

            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"Usuário '{identifier}' não foi encontrado.",
                )

            user_id, name = row[0], row[1]

        cypher_query = "MATCH (u:User {id: $user_id}) RETURN u.embedding AS embedding"
        with database.driver.session() as session:
            result = session.run(cypher_query, user_id=user_id)
            record = result.single()

            if not record or not record["embedding"]:
                raise HTTPException(
                    status_code=404,
                    detail=f"Embedding do usuário ID '{user_id}' não encontrado no Neo4j.",
                )

            embedding = list(record["embedding"])

        return UserEmbeddingResponse(
            user_id=user_id, name=name, embedding=embedding
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar embedding: {str(e)}"
        )
    finally:
        database.pg_pool.putconn(conn)