from datetime import datetime, timezone
import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database.db_config import AsyncSessionLocal # Assuming this is correctly configured
from typing import List, Any, Dict

logger = logging.getLogger(__name__)

class ReportRepository:
    async def insert_report(
        self,
        user_id: str,
        request_id: str,
        report_text: str,
    ) -> str:
        async with AsyncSessionLocal() as session:
            try:
                create_table_sql = text("""
                    CREATE SCHEMA IF NOT EXISTS aux;
                    CREATE TABLE IF NOT EXISTS aux.reports (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id TEXT NOT NULL,
                        request_id TEXT NOT NULL,
                        report_text TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                logger.debug("Executing CREATE SCHEMA and CREATE TABLE IF NOT EXISTS for aux.reports...")
                await session.execute(create_table_sql)
                await session.commit()
                logger.debug("Schema and table creation/check committed.")

                insert_sql = text("""
                    INSERT INTO aux.reports (user_id, request_id, report_text)
                    VALUES (:user_id, :request_id, :report_text)
                    RETURNING id;
                """)

                result = await session.execute(
                    insert_sql,
                    {
                        "user_id": user_id,
                        "request_id": request_id,
                        "report_text": report_text,
                    },
                )

                inserted_id = result.fetchone()[0]
                await session.commit()
                logger.debug(f"Report inserted successfully with ID: {inserted_id}")
                return str(inserted_id)

            except SQLAlchemyError as e:
                await session.rollback() # Rollback on error
                logger.error(f"SQLAlchemy error inserting report: {e}", exc_info=True)
                raise
            except Exception as e:
                await session.rollback() # Rollback on error
                logger.error(f"Unexpected error inserting report: {e}", exc_info=True)
                raise

    async def get_all_reports_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        async with AsyncSessionLocal() as session:
            try:
                select_sql = text("""
                    SELECT id, user_id, request_id, report_text, created_at
                    FROM aux.reports
                    WHERE user_id = :user_id
                    ORDER BY created_at DESC;
                """)

                result = await session.execute(select_sql, {"user_id": user_id})
                # Fetch all results and convert them to a list of dictionaries
                reports = [
                    {
                        "id": str(row.id),
                        "user_id": row.user_id,
                        "request_id": row.request_id,
                        "report_text": row.report_text,
                        "created_at": row.created_at.isoformat() if row.created_at else None,
                    }
                    for row in result.fetchall()
                ]
                logger.debug(f"Retrieved {len(reports)} reports for user_id: {user_id}")
                return reports
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error retrieving reports for user {user_id}: {e}", exc_info=True)
                raise
            except Exception as e:
                logger.error(f"Unexpected error retrieving reports for user {user_id}: {e}", exc_info=True)
                raise