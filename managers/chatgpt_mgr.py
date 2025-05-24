import os
import logging
from fastapi import HTTPException
from models.prompt_models import PromptRequest
from dotenv import load_dotenv
from openai import OpenAI
from managers.menu_mgr import MenuManager # Assuming this is still needed for text-only part

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.warning("OpenAI API key not found in environment variables")

client = OpenAI(api_key=openai_api_key)
menu_mgr = MenuManager()  

# Model capable of multimodal input, e.g., gpt-4o or gpt-4-turbo
MULTIMODAL_MODEL = "gpt-4o" # Or "gpt-4-turbo"
TEXT_MODEL = "gpt-4.1" # Or your preferred text model, can be MULTIMODAL_MODEL too

async def process(req: PromptRequest) -> str:
    try:
        prompt_content = await menu_mgr.mount2(req)  
        print("####PROMPT CONTENT#######")
        print(prompt_content)
        
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": prompt_content}],
            temperature=0.3,
            max_tokens=2048
        )
        
        result = response.choices[0].message.content.strip()
        return result
    
    except Exception as e:
        logger.error(f"Erro ao processar com ChatGPT (texto): {e}")
        raise HTTPException(status_code=500, detail=f"Erro na categorização com ChatGPT: {str(e)}")

async def process_image_base64(image_base64: str, prompt_text: str, image_media_type: str = "image/jpeg") -> str:
    try:
        response = client.chat.completions.create(
            model=MULTIMODAL_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{image_media_type};base64,{image_base64}"},
                        },
                    ],
                }
            ],
            temperature=0.3,
            max_tokens=2048
        )
        result = response.choices[0].message.content.strip()
        return result
    except Exception as e:
        logger.error(f"Erro ao processar imagem com ChatGPT: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento de imagem com ChatGPT: {str(e)}")

async def process_pdf_base64(pdf_base64: str, prompt_text: str) -> str:
    try:
       
        response = client.chat.completions.create(
            model=MULTIMODAL_MODEL, 
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:application/pdf;base64,{pdf_base64}"}
                        }
                    ],
                }
            ],
            temperature=0.3,
            max_tokens=4096 
        )
        result = response.choices[0].message.content.strip()
        return result
    except Exception as e:
        logger.error(f"Erro ao processar PDF com ChatGPT: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento de PDF com ChatGPT: {str(e)}")