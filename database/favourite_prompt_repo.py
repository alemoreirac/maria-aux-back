# database/favourite_prompt_repo.py
from datetime import datetime, timezone
import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database.db_config import AsyncSessionLocal # Assuming this is correctly configured
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class FavoritePromptRepository:
    async def add_favourite_prompt(self, user_id: str, prompt_id: int) -> str:
        """
        Adds a prompt to a user's favourites.

        Args:
            user_id (str): The ID of the user.
            prompt_id (int): The ID of the prompt to favourite.

        Returns:
            str: The ID of the newly created favourite record.

        Raises:
            SQLAlchemyError: If a database error occurs (e.g., duplicate entry, integrity constraint).
            Exception: For any other unexpected errors.
        """
        async with AsyncSessionLocal() as session:
            try:
                # Ensure the aux schema exists and the table is created if it doesn't.
                # For production, consider using Alembic for migrations.
                create_table_sql = text("""
                    CREATE SCHEMA IF NOT EXISTS aux;
                    CREATE TABLE IF NOT EXISTS aux.favourite_prompt (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id TEXT NOT NULL,
                        prompt_id INTEGER NOT NULL,
                        favourited_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, prompt_id) -- Ensures a user can favourite a prompt only once
                    );
                """)
                logger.debug("Executing CREATE SCHEMA and CREATE TABLE IF NOT EXISTS for aux.favourite_prompt...")
                await session.execute(create_table_sql)
                await session.commit()
                logger.debug("Schema and table creation/check committed.")

                insert_sql = text("""
                    INSERT INTO aux.favourite_prompt (user_id, prompt_id)
                    VALUES (:user_id, :prompt_id)
                    RETURNING id;
                """)

                result = await session.execute(
                    insert_sql,
                    {
                        "user_id": user_id,
                        "prompt_id": prompt_id,
                    },
                )

                inserted_id = result.fetchone()[0]
                await session.commit()
                logger.info(f"Prompt {prompt_id} favourited by user {user_id} with ID: {inserted_id}")
                return str(inserted_id)

            except SQLAlchemyError as e:
                await session.rollback()
                # Check for unique constraint violation specifically
                if "duplicate key value violates unique constraint" in str(e).lower():
                    logger.warning(f"User {user_id} already favourited prompt {prompt_id}.")
                    raise ValueError(f"Prompt {prompt_id} is already in favourites for user {user_id}.")
                logger.error(f"SQLAlchemy error adding favourite prompt: {e}", exc_info=True)
                raise
            except Exception as e:
                await session.rollback()
                logger.error(f"Unexpected error adding favourite prompt: {e}", exc_info=True)
                raise

    async def get_favourite_prompts_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all favourite prompts for a given user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                                   represents a favourite prompt record.
        """
        async with AsyncSessionLocal() as session:
            try:
                select_sql = text("""
                    SELECT id, user_id, prompt_id, favourited_at
                    FROM aux.favourite_prompt
                    WHERE user_id = :user_id
                    ORDER BY favourited_at DESC;
                """)

                result = await session.execute(select_sql, {"user_id": user_id})
                favourites = [
                    {
                        "id": str(row.id),
                        "user_id": row.user_id,
                        "prompt_id": row.prompt_id,
                        "favourited_at": row.favourited_at.isoformat() if row.favourited_at else None,
                    }
                    for row in result.fetchall()
                ]
                logger.debug(f"Retrieved {len(favourites)} favourite prompts for user_id: {user_id}")
                return favourites
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error retrieving favourite prompts for user {user_id}: {e}", exc_info=True)
                raise
            except Exception as e:
                logger.error(f"Unexpected error retrieving favourite prompts for user {user_id}: {e}", exc_info=True)
                raise

    async def remove_favourite_prompt(self, user_id: str, prompt_id: int) -> bool:
        """
        Removes a prompt from a user's favourites.

        Args:
            user_id (str): The ID of the user.
            prompt_id (int): The ID of the prompt to remove.

        Returns:
            bool: True if the favourite was successfully removed, False otherwise.
        """
        async with AsyncSessionLocal() as session:
            try:
                delete_sql = text("""
                    DELETE FROM aux.favourite_prompt
                    WHERE user_id = :user_id AND prompt_id = :prompt_id;
                """)

                result = await session.execute(delete_sql, {"user_id": user_id, "prompt_id": prompt_id})
                await session.commit()
                if result.rowcount > 0:
                    logger.info(f"Prompt {prompt_id} removed from favourites for user {user_id}.")
                    return True
                else:
                    logger.info(f"No favourite found for user {user_id} and prompt {prompt_id} to remove.")
                    return False
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"SQLAlchemy error removing favourite prompt: {e}", exc_info=True)
                raise
            except Exception as e:
                await session.rollback()
                logger.error(f"Unexpected error removing favourite prompt: {e}", exc_info=True)
                raise