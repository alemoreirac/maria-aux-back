import logging
from typing import List, Dict, Any

# Assuming ReportRepository is in database.report_repo
from database.report_repo import ReportRepository

logger = logging.getLogger(__name__)

class ReportManager:
    def __init__(self):
        self.report_repo = ReportRepository()

    async def create_report(
        self,
        user_id: str,
        request_id: str,
        report_text: str,
    ) -> str: 
        try:
            report_id = await self.report_repo.insert_report(user_id, request_id, report_text)
            logger.info(f"Report created successfully for user {user_id} with ID: {report_id}")
            return report_id
        except Exception as e:
            logger.error(f"Failed to create report for user {user_id}: {e}", exc_info=True)
            raise # Re-raise for the controller to handle

    async def get_user_reports(self, user_id: str) -> List[Dict[str, Any]]:
        try:
            reports = await self.report_repo.get_all_reports_by_user_id(user_id)
            logger.info(f"Retrieved {len(reports)} reports for user {user_id}.")
            return reports
        except Exception as e:
            logger.error(f"Failed to retrieve reports for user {user_id}: {e}", exc_info=True)
            raise # Re-raise for the controller to handle