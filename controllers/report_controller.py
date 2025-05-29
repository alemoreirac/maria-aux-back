from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Any
import logging
from models.report_models import ReportCreate,ReportResponse
from pydantic import BaseModel

# Assuming ReportManager is in managers.report_mgr
from managers.report_mgr import ReportManager
from utils.token_util import verify_token # Assuming you have this for authentication

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["Reports"]
)

report_mgr = ReportManager()
  
@router.post("/reports/", status_code=status.HTTP_201_CREATED)
async def create_report_endpoint(
    report_data: ReportCreate,
    token: dict = Depends(verify_token) # Ensure the user is authenticated
) -> Dict[str, str]:
    """
    Creates a new report.
    """
    try:
        # In a real application, user_id would likely come from the token
        # For now, we'll use it directly from the payload.
        report_id = await report_mgr.create_report(
            user_id=report_data.user_id,
            request_id=report_data.request_id,
            report_text=report_data.report_text
        )
        return {"id": report_id, "message": "Report created successfully."}
    except Exception as e:
        logger.error(f"API error creating report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create report: {str(e)}"
        )

@router.get("/users/{user_id}/reports/", response_model=List[ReportResponse])
async def get_user_reports_endpoint(
    user_id: str,
    token: dict = Depends(verify_token) # Ensure the user is authenticated
) -> List[Dict[str, Any]]:
    """
    Retrieves all reports for a specific user.
    """
    # In a real application, you might want to check if the token's user_id matches
    # the user_id in the path to prevent users from accessing other users' reports.
    # if token["user_id"] != user_id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    try:
        reports = await report_mgr.get_user_reports(user_id)
        # Convert the raw dictionary output from manager to ReportResponse models
        return [
            ReportResponse(
                id=report["id"],
                user_id=report["user_id"],
                request_id=report["request_id"],
                report_text=report["report_text"],
                created_at=report["created_at"]
            ) for report in reports
        ]
    except Exception as e:
        logger.error(f"API error retrieving reports for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve reports: {str(e)}"
        )