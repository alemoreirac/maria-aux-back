from datetime import datetime, timezone, timedelta  
import logging 
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

engine = create_async_engine(
    os.getenv("ASYNC_PG_CONN_STR"),
    echo=False,
    pool_recycle=1800,
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False)
  
class UserCreditRepository: 
    async def _ensure_table_exists(self):
        """Ensures the user_credits table exists."""
        async with AsyncSessionLocal() as session:
            try:
                create_table_sql = text("""
                    CREATE TABLE IF NOT EXISTS arq.user_credits (
                        user_id TEXT PRIMARY KEY,
                        credits INTEGER NOT NULL DEFAULT 0
                    );
                """)
                await session.execute(create_table_sql)
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"SQLAlchemy error during user_credits table creation: {e}", exc_info=True)
                raise # Re-raise the exception as table creation failure is critical
            except Exception as e:
                await session.rollback()
                logger.error(f"Unexpected error during user_credits table creation: {e}", exc_info=True)
                raise # Re-raise other exceptions


    async def add_credits(self, user_id: str, amount: int) -> None:
        """Adds a specified amount of credits to a user's balance."""
        if amount < 0:
            logger.warning(f"Attempted to add negative credits ({amount}) for user: {user_id}")
            return # Do not add negative credits

        # Ensure the table exists before interacting
        await self._ensure_table_exists()

        async with AsyncSessionLocal() as session:
            try:
                # Use INSERT ON CONFLICT DO UPDATE for atomic upsert (insert or update if exists)
                insert_sql = text("""
                    INSERT INTO arq.user_credits (user_id, credits)
                    VALUES (:user_id, :amount)
                    ON CONFLICT (user_id)
                    DO UPDATE SET credits = user_credits.credits + EXCLUDED.credits;
                """)

                await session.execute(
                    insert_sql,
                    {
                        "user_id": user_id,
                        "amount": amount,
                    },
                )
                await session.commit()
                logger.info(f"Added {amount} credits for user: {user_id}")

            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"SQLAlchemy error adding credits for {user_id}: {e}", exc_info=True)
            except Exception as e:
                await session.rollback()
                logger.error(f"Unexpected error adding credits for {user_id}: {e}", exc_info=True)
 
    async def deduct_credit(self, user_id: str) -> bool:  
        await self._ensure_table_exists()

        async with AsyncSessionLocal() as session:
            try: 
                update_sql = text("""
                    UPDATE arq.user_credits
                    SET credits = credits - 1
                    WHERE user_id = :user_id AND credits > 0;
                """)

                result = await session.execute(
                    update_sql,
                    {
                        "user_id": user_id,
                    },
                )

                # Check if any row was updated
                if result.rowcount == 1:
                    await session.commit()
                    logger.info(f"Deducted 1 credit for user: {user_id}")
                    return True
                else:
                    # No row updated means user_id wasn't found or credits were 0
                    await session.rollback() # No change occurred, but rollback is harmless
                    logger.warning(f"Failed to deduct credit for user {user_id}: user not found or insufficient credits.")
                    return False

            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"SQLAlchemy error deducting credit for {user_id}: {e}", exc_info=True)
                return False
            except Exception as e:
                await session.rollback()
                logger.error(f"Unexpected error deducting credit for {user_id}: {e}", exc_info=True)
                return False
                
    async def get_credits(self, user_id: str) -> int:
        """Gets the current credit balance for a user."""
        # Ensure the table exists before interacting
        await self._ensure_table_exists()

        async with AsyncSessionLocal() as session:
            try:
                select_sql = text("""
                    SELECT credits FROM arq.user_credits WHERE user_id = :user_id;
                """)
                
                result = await session.execute(
                    select_sql,
                    {
                        "user_id": user_id,
                    },
                )
                
                # Fetch one row; if no row, user doesn't exist in this table yet
                row = result.fetchone()
                
                if row:
                    credits = row[0]
                    logger.debug(f"Retrieved {credits} credits for user: {user_id}")
                    return credits
                else:
                    # User not found in the user_credits table, assume 0 credits
                    logger.debug(f"User {user_id} not found in credits table, assuming 0 credits.")
                    return 0

            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"SQLAlchemy error retrieving credits for {user_id}: {e}", exc_info=True)
                return 0 # Return 0 or raise an error depending on desired behavior on failure
            except Exception as e:
                await session.rollback()
                logger.error(f"Unexpected error retrieving credits for {user_id}: {e}", exc_info=True)
                return 0 # Return 0 or raise

    async def has_credits(self, user_id: str) -> bool:
        """
        Checks if a user has at least one credit.
        Returns True if credits >= 1, False otherwise (credits = 0 or user not found).
        """
        await self._ensure_table_exists() # Ensure table exists

        async with AsyncSessionLocal() as session:
            try:
                # Select credits and check if it's greater than 0
                select_sql = text("""
                    SELECT 1 FROM arq.user_credits WHERE user_id = :user_id AND credits > 0;
                """)
                
                result = await session.execute(
                    select_sql,
                    {
                        "user_id": user_id,
                    },
                )
                
                # If fetchone returns a row, it means a user was found AND had > 0 credits
                row = result.fetchone()
                
                has_credit = row is not None
                logger.debug(f"User {user_id} has credits: {has_credit}")
                return has_credit

            except SQLAlchemyError as e:
                await session.rollback() # Rollback is generally not needed for SELECT, but harmless
                logger.error(f"SQLAlchemy error checking credits for {user_id}: {e}", exc_info=True)
                return False # Assume no credits on database error
            except Exception as e:
                await session.rollback() # Rollback is generally not needed for SELECT, but harmless
                logger.error(f"Unexpected error checking credits for {user_id}: {e}", exc_info=True)
                return False # Assume no credits on other errors

# --- How to Link log_message and deduct_credit ---

# In your FastAPI endpoint or service logic that handles the AI call:

# Instantiate your repositories
# history_repo = LLMHistoryRepository(AsyncSessionLocal)
# credit_repo = UserCreditRepository(AsyncSessionLocal)

# Example usage in an async function (like a FastAPI endpoint)
"""
async def process_user_request(user_id: str, user_query: str):
    history_repo = LLMHistoryRepository(AsyncSessionLocal)
    credit_repo = UserCreditRepository(AsyncSessionLocal)

    # 1. Check and deduct credit *before* calling the expensive AI service
    credit_deducted = await credit_repo.deduct_credit(user_id)

    if not credit_deducted:
        logger.warning(f"User {user_id} has no credits. AI call prevented.")
        # Return an error response to the user
        return {"error": "Você não tem fichas suficientes para usar a IA."}

    # 2. If credit was successfully deducted, proceed with AI call
    logger.info(f"Credit deducted for user {user_id}. Calling AI service...")
    try:
        # --- CALL YOUR AI SERVICE HERE ---
        gpt_response = "This is a simulated AI response." # Replace with actual AI call
        # ----------------------------------

        # 3. If AI call is successful, log the message
        await history_repo.log_message(user_id, user_query, gpt_response)
        
        # Return the AI response to the user
        return {"response": gpt_response}

    except Exception as ai_error:
        # If AI call fails *after* credit deduction, you might want to
        # consider refunding the credit or logging the failure.
        # For simplicity here, we just log the error and potentially don't log the message.
        logger.error(f"AI service call failed for user {user_id}: {ai_error}", exc_info=True)
        # Depending on policy, you might refund the credit here,
        # but that adds complexity (handling refund failures).
        # For a simple model, if the AI call fails, the credit is still spent
        # as the service *attempted* to provide value.
        return {"error": "Ocorreu um erro ao processar sua solicitação de IA."}

# Example of adding credits (e.g., via an admin endpoint or purchase flow)
async def grant_user_credits(user_id: str, amount: int):
     credit_repo = UserCreditRepository(AsyncSessionLocal)
     await credit_repo.add_credits(user_id, amount)
     logger.info(f"Granted {amount} credits to user {user_id}")

async def check_user_credits(user_id: str):
    credit_repo = UserCreditRepository(AsyncSessionLocal)
    credits = await credit_repo.get_credits(user_id)
    logger.info(f"User {user_id} has {credits} credits.")
    return credits
"""