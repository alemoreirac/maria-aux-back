from fastapi import  HTTPException 
import logging 
from dotenv import load_dotenv 
from database.llm_history_repo import LLMHistoryRepository
from database.credits_repo import UserCreditRepository
load_dotenv()
    
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm_log_repo = LLMHistoryRepository()
credits_repo = UserCreditRepository()

async def get_user_data(user_id: str):
    try: 
        log_history = await llm_log_repo.get_recent_history(user_id)
        credits = await credits_repo.get_credits(user_id)

        user_info = {
        "log_history":log_history,
        "credits":credits
        }

        return user_info
    
    except Exception as e:
        logger.error(f"Error retrieving user data: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing PDF with Anthropic: {str(e)}")

async def set_credits(user_id:str, credits:int):
    try:
        result = credits_repo.add_credits(user_id,credits)
        return result
    
    except Exception as e:
        logger.error(f"Error retrieving user data: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing PDF with Anthropic: {str(e)}")
    