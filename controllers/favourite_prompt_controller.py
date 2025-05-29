# controllers/favourite_prompt_controller.py
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Any
import logging

from managers.favourite_prompt_mgr import FavoritePromptManager # Adjust import path as needed
from models.favourite_prompt_models import FavouritePromptCreate, FavouritePromptResponse # Import Pydantic models
from utils.token_util import verify_token # Assuming you have this for authentication

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["Favorite Prompts"]
)

favourite_prompt_mgr = FavoritePromptManager()

@router.post("/favourites/prompts/", status_code=status.HTTP_201_CREATED)
async def add_favourite_prompt_endpoint(
    favourite_data: FavouritePromptCreate, # Use Pydantic model for request body
    token: dict = Depends(verify_token)
) -> Dict[str, str]:
    """
    Adds a prompt to a user's favourites.
    """
    try:
        # It's good practice to ensure user_id from token matches user_id in payload,
        # or even better, just use the user_id from the token and ignore the payload's user_id for security.
        # For simplicity, using payload's user_id for now.
        favourite_id = await favourite_prompt_mgr.add_prompt_to_favourites(
            user_id=favourite_data.user_id,
            prompt_id=favourite_data.prompt_id
        )
        return {"id": favourite_id, "message": "Prompt added to favourites successfully."}
    except ValueError as e: # Catch the specific error for duplicate
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # 409 Conflict for duplicate resource
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"API error adding favourite prompt: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add prompt to favourites: {str(e)}"
        )

@router.get("/users/{user_id}/favourites/prompts/", response_model=List[FavouritePromptResponse])
async def get_user_favourite_prompts_endpoint(
    user_id: str,
    token: dict = Depends(verify_token)
) -> List[FavouritePromptResponse]: # Adjust return type hint
    """
    Retrieves all favourite prompts for a specific user.
    """
    # Optional: Security check - ensure user_id from token matches path user_id
    # if token.get("user_id") != user_id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    try:
        favourites_data = await favourite_prompt_mgr.get_user_favourite_prompts(user_id)
        # Convert raw dictionaries from manager to Pydantic models
        return [FavouritePromptResponse(**fav) for fav in favourites_data]
    except Exception as e:
        logger.error(f"API error retrieving favourite prompts for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve favourite prompts: {str(e)}"
        )

@router.delete("/users/{user_id}/favourites/prompts/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favourite_prompt_endpoint(
    user_id: str,
    prompt_id: int,
    token: dict = Depends(verify_token)
) -> None:
    """
    Removes a prompt from a user's favourites.
    """
    # Optional: Security check - ensure user_id from token matches path user_id
    # if token.get("user_id") != user_id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    try:
        success = await favourite_prompt_mgr.remove_prompt_from_favourites(user_id, prompt_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Favorite prompt for user {user_id} and prompt {prompt_id} not found."
            )
        return None # No content for 204
    except Exception as e:
        logger.error(f"API error removing favourite prompt: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove favourite prompt: {str(e)}"
        )