import anthropic
from fastapi import HTTPException
import logging
import os
from managers.menu_mgr import MenuManager 
from dotenv import load_dotenv
from models.prompt_models import PromptRequest

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_api_key:
    logger.warning("Anthropic API key not found in environment variables")

client = anthropic.Anthropic(api_key=anthropic_api_key)
menu_mgr = MenuManager() 

MODEL_NAME = "claude-3-sonnet-20240229" 

async def process(req: PromptRequest) -> str:
    try:
        prompt_content = await menu_mgr.mount(req) # For text-based prompts
        
        response = client.messages.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt_content}],
            temperature=0.3,
            max_tokens=2048
        )

        result = response.content[0].text.strip()
        logger.info("Resposta do Claude (texto) recebida com sucesso.")
        return result

    except Exception as e:
        logger.error(f"Erro ao processar prompt com Claude (texto): {e}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento com Claude (texto): {str(e)}")

async def process_image_base64(image_base64: str, prompt_text: str, image_media_type: str = "image/jpeg") -> str:
    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=2048,
            temperature=0.3,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": image_media_type,
                                "data": image_base64,
                            },
                        },
                        {"type": "text", "text": prompt_text},
                    ],
                }
            ],
        )
        result = response.content[0].text.strip()
        logger.info("Resposta de imagem do Claude recebida com sucesso.")
        return result
    except Exception as e:
        logger.error(f"Erro ao processar imagem com Claude: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento de imagem com Claude: {str(e)}")

async def process_pdf_base64(pdf_base64: str, prompt_text: str) -> str:
    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=4096, 
            temperature=0.3,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": { 
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_base64,
                            },
                        },
                        {"type": "text", "text": prompt_text},
                    ],
                }
            ],
        )
        result = response.content[0].text.strip() # Access the text content
        logger.info("Resposta de PDF do Claude recebida com sucesso.")
        return result
    except Exception as e:
        logger.error(f"Erro ao processar PDF com Claude: {e}")
        # Check for specific Anthropic errors if possible, e.g., e.status_code
        if isinstance(e, anthropic.APIError):
            logger.error(f"Anthropic API Error: {e.status_code} - {e.message}")
            raise HTTPException(status_code=e.status_code or 500, detail=f"Erro da API Claude ao processar PDF: {e.message}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento de PDF com Claude: {str(e)}")