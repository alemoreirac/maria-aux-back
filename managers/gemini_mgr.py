import os
import logging
import base64
from fastapi import HTTPException
import google.generativeai as genai
from managers.menu_mgr import MenuManager
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

menu_mgr = MenuManager() # For text prompts if still used by 'process'

# Updated models - Gemini 2.0 Flash
#GEMINI_MODEL = "gemini-2.0-flash" 
GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"

gemini_text_model = genai.GenerativeModel(GEMINI_MODEL) if gemini_api_key else None
gemini_multimodal_model = genai.GenerativeModel(GEMINI_MODEL) if gemini_api_key else None

# Web search model - try different approaches
try:
    # First attempt: use tools as dict
    gemini_web_search_model = genai.GenerativeModel(
        GEMINI_MODEL,
        tools=[{"google_search": {}}]
    ) if gemini_api_key else None
except Exception as e1:
    try:
        # Second attempt: use system instruction approach
        gemini_web_search_model = genai.GenerativeModel(
            GEMINI_MODEL,
            system_instruction="You have access to Google Search. When answering questions, search for current information when needed."
        ) if gemini_api_key else None
        logger.info("Using system instruction approach for web search")
    except Exception as e2:
        # Fallback: use regular model and handle search in the method
        gemini_web_search_model = genai.GenerativeModel(GEMINI_MODEL) if gemini_api_key else None
        logger.warning(f"Could not configure web search tools. Using fallback approach. Errors: {e1}, {e2}")

async def process(req: PromptRequest) -> str:
    if not gemini_text_model:
        raise HTTPException(status_code=503, detail="Gemini API key não configurada.")
    try:
        prompt_content = await menu_mgr.mount(req) # For text-based prompts
        
        logger.info(f"Enviando prompt de texto para Gemini ({GEMINI_MODEL}): {prompt_content[:100]}...")

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

async def process_web_search(req: PromptRequest) -> str:
    if not gemini_web_search_model:
        raise HTTPException(status_code=503, detail="Gemini API key não configurada.")
    
    try:
        prompt = await menu_mgr.mount(req) # For text-based prompts
         
        logger.info(f"Enviando busca web para Gemini ({GEMINI_MODEL}): {prompt[:100]}...")

        # Enhanced prompt to encourage web search behavior
        enhanced_prompt = f"""Please search for current, up-to-date information to answer this request: {prompt}

Use real-time web search to find the most current and accurate information available. Provide detailed, factual responses based on your search results."""

        # Use the model (may have search tools or system instruction)
        response = await gemini_web_search_model.generate_content_async(
            contents=[{"role": "user", "parts": [enhanced_prompt]}],
            generation_config={
                "temperature": 0.1,  # Lower temperature for more factual responses
                "max_output_tokens": 4096
            }
        )
        
        result = response.text.strip()
        
        # Try to get grounding metadata if available
        try:
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    logger.info("Grounding metadata disponível na resposta")
                    # You could extract and use this metadata for source information
        except Exception as grounding_error:
            logger.warning(f"Erro ao acessar grounding metadata: {grounding_error}")
        
        logger.info("Resposta de busca web do Gemini recebida com sucesso.")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao realizar busca web com Gemini: {e}")
        # Fallback to regular text processing if web search fails
        logger.info("Tentando fallback para processamento de texto regular...")
        try:
            return await process(req)
        except Exception as fallback_error:
            logger.error(f"Erro no fallback: {fallback_error}")
            raise HTTPException(status_code=500, detail=f"Erro na busca web com Gemini: {str(e)}")

async def process_image_base64(image_base64: str, prompt_text: str, image_media_type: str = "image/jpeg") -> str:
    if not gemini_multimodal_model:
        raise HTTPException(status_code=503, detail="Gemini API key não configurada.")
    try:
        # Gemini expects raw bytes for Blob data, so decode base64
        image_bytes = base64.b64decode(image_base64)
        
        image_part = genai.types.Blob(mime_type=image_media_type, data=image_bytes)
        
        logger.info(f"Enviando imagem e prompt multimodal para Gemini ({GEMINI_MODEL})...")

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
        
        logger.info(f"Enviando PDF e prompt multimodal para Gemini ({GEMINI_MODEL})...")

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