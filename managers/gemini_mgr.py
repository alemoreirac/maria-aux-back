import os
import logging
import base64
from fastapi import HTTPException
import google.generativeai as genai
from managers.prompt_mgr import PromptManager
from models.prompt_models import PromptRequest
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    logger.warning("GEMINI_API_KEY not found in environment variables. Please set it.")
else:
    genai.configure(api_key=gemini_api_key)

prompt_mgr = PromptManager() # For text prompts if still used by 'process'

# Define models - Gemini 1.5 Flash is good for multimodal and speed
GEMINI_MODEL_TEXT = "gemini-1.5-flash-latest"
GEMINI_MODEL_MULTIMODAL = "gemini-1.5-flash-latest" # Can be the same model

# Initialize models only if API key is available
gemini_text_model = genai.GenerativeModel(GEMINI_MODEL_TEXT) if gemini_api_key else None
gemini_multimodal_model = genai.GenerativeModel(GEMINI_MODEL_MULTIMODAL) if gemini_api_key else None

async def process(req: PromptRequest) -> str:
    if not gemini_text_model:
        raise HTTPException(status_code=503, detail="Gemini API key não configurada.")
    try:
        prompt_content = await prompt_mgr.mount(req) # For text-based prompts
        
        logger.info(f"Enviando prompt de texto para Gemini ({GEMINI_MODEL_TEXT}): {prompt_content[:100]}...")

        response = await gemini_text_model.generate_content_async( # Use async version
            contents=[{"role": "user", "parts": [prompt_content]}],
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 2048
            }
        )
        
        result = response.text.strip()
        logger.info("Resposta do Gemini (texto) recebida com sucesso.")
        return result

    except Exception as e:
        logger.error(f"Erro ao processar prompt de texto com Gemini: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento de texto com Gemini: {str(e)}")

async def process_image_base64(image_base64: str, prompt_text: str, image_media_type: str = "image/jpeg") -> str:
    if not gemini_multimodal_model:
        raise HTTPException(status_code=503, detail="Gemini API key não configurada.")
    try:
        # Gemini expects raw bytes for Blob data, so decode base64
        image_bytes = base64.b64decode(image_base64)
        
        image_part = genai.types.Blob(mime_type=image_media_type, data=image_bytes)
        
        logger.info(f"Enviando imagem e prompt multimodal para Gemini ({GEMINI_MODEL_MULTIMODAL})...")

        response = await gemini_multimodal_model.generate_content_async( # Use async version
            contents=[{"role": "user", "parts": [image_part, prompt_text]}],
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 2048
            }
        )
        
        result = response.text.strip()
        logger.info("Resposta de imagem do Gemini recebida com sucesso.")
        return result
    except Exception as e:
        logger.error(f"Erro ao analisar imagem com Gemini: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao analisar imagem com Gemini: {str(e)}")

async def process_pdf_base64(pdf_base64: str, prompt_text: str) -> str:
    if not gemini_multimodal_model:
        raise HTTPException(status_code=503, detail="Gemini API key não configurada.")
    try:
        # Gemini expects raw bytes for Blob data
        pdf_bytes = base64.b64decode(pdf_base64)
        
        pdf_part = genai.types.Blob(mime_type="application/pdf", data=pdf_bytes)
        
        logger.info(f"Enviando PDF e prompt multimodal para Gemini ({GEMINI_MODEL_MULTIMODAL})...")

        response = await gemini_multimodal_model.generate_content_async( # Use async version
            contents=[{"role": "user", "parts": [pdf_part, prompt_text]}],
            generation_config={
                "max_output_tokens": 4096 # PDFs might need more tokens
            }
        )
        
        result = response.text.strip()
        logger.info("Resposta de PDF do Gemini recebida com sucesso.")
        return result
    
    except Exception as e:
        logger.error(f"Erro ao analisar PDF com Gemini: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao analisar PDF com Gemini: {str(e)}")