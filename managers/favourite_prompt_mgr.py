# managers/favourite_prompt_mgr.py
import logging
from typing import List, Dict, Any

from database.favourite_prompt_repo import FavoritePromptRepository # Adjust import path as needed

logger = logging.getLogger(__name__)

class FavoritePromptManager:
    def __init__(self):
        self.favourite_prompt_repo = FavoritePromptRepository()

    async def add_prompt_to_favourites(self, user_id: str, prompt_id: int) -> str:
        """
        Business logic to add a prompt to a user's favourites.
        Checks for existing favourite before adding.

        Args:
            user_id (str): The ID of the user.
            prompt_id (int): The ID of the prompt.

        Returns:
            str: The ID of the new favourite record.

        Raises:
            ValueError: If the prompt is already favourited by the user.
            Exception: For other underlying issues.
        """
        try:
            # You could add a check here if you want to explicitly verify
            # if the prompt exists before adding, by calling another repository.
            # For simplicity, we'll rely on the UNIQUE constraint in the DB.
            favourite_id = await self.favourite_prompt_repo.add_favourite_prompt(user_id, prompt_id)
            return favourite_id
        except ValueError as e:
            logger.warning(f"Attempted to re-favourite: {e}")
            raise # Re-raise for controller to handle as 409 Conflict
        except Exception as e:
            logger.error(f"Failed to add prompt {prompt_id} to favourites for user {user_id}: {e}", exc_info=True)
            raise

    async def get_user_favourite_prompts(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Business logic to retrieve all favourite prompts for a user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            List[Dict[str, Any]]: A list of favourite prompt data.
        """
        try:
            favourites = await self.favourite_prompt_repo.get_favourite_prompts_by_user_id(user_id)
            return favourites
        except Exception as e:
            logger.error(f"Failed to retrieve favourite prompts for user {user_id}: {e}", exc_info=True)
            raise

    async def remove_prompt_from_favourites(self, user_id: str, prompt_id: int) -> bool:
        """
        Business logic to remove a prompt from a user's favourites.

        Args:
            user_id (str): The ID of the user.
            prompt_id (int): The ID of the prompt to remove.

        Returns:
            bool: True if removed, False if not found.
        """
        try:
            success = await self.favourite_prompt_repo.remove_favourite_prompt(user_id, prompt_id)
            return success
        except Exception as e:
            logger.error(f"Failed to remove prompt {prompt_id} from favourites for user {user_id}: {e}", exc_info=True)
            raise