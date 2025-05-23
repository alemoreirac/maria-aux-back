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
 
genai.configure(api_key=gemini_api_key)
 
prompt_mgr = PromptManager()
 
GEMINI_MODEL_TEXT = "gemini-1.5-flash-latest"
GEMINI_MODEL_MULTIMODAL = "gemini-1.5-flash-latest" 


gemini_text_model = genai.GenerativeModel(GEMINI_MODEL_TEXT)

async def process(req: PromptRequest) -> str: 
    try:
        prompt_content = await prompt_mgr.mount(req)
        
        logger.info(f"Enviando prompt de texto para Gemini ({GEMINI_MODEL_TEXT}): {prompt_content}")

        response = await gemini_text_model.generate_content(
            contents=[{"role": "user", "parts": [prompt_content]}],
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 2048  
            }
        )
        
        # Acessa o conteúdo da resposta do Gemini
        categorized_items = response.text.strip()
        logger.info("Resposta do Gemini (texto) recebida com sucesso.")
        return categorized_items

    except Exception as e:
        logger.error(f"Erro ao processar prompt de texto com Gemini: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento de texto: {str(e)}")


async def process_pdf(pdf_path: str, prompt_id: int) -> str:
    try:

        gemini_multimodal_model = genai.GenerativeModel(GEMINI_MODEL_MULTIMODAL)

        with open(pdf_path, "rb") as pdf_file:
            pdf_data = base64.b64encode(pdf_file.read()).decode("utf-8")
        
        prompt_obj = await prompt_mgr.get_prompt(prompt_id)
        prompt_text = prompt_obj.titulo # O texto do prompt para o PDF

        logger.info(f"Enviando PDF e prompt multimodal para Gemini ({GEMINI_MODEL_MULTIMODAL})...")

        response = await gemini_multimodal_model.generate_content(
            contents=[
                {"role": "user", "parts": [
                    genai.types.Blob(
                        mime_type="application/pdf",
                        data=pdf_data
                    ),
                    prompt_text 
                ]}
            ],
            generation_config={
                "max_output_tokens": 4000 
            }
        )
        
        return response.text.strip()
    
    except Exception as e:
        logger.error(f"Erro ao analisar PDF com Gemini: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao analisar PDF com Gemini: {str(e)}")