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

async def log_llm(user_id: str, user_query:str, llm_response:str) -> str:
    try: 
        guid = await llm_log_repo.log_message(user_id,user_query,llm_response)

        return guid
    
    except Exception as e:
        logger.error(f"Error retrieving user data: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing PDF with Anthropic: {str(e)}")
