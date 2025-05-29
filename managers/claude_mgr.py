import anthropic
from fastapi import HTTPException
import logging
import os
from managers.menu_mgr import MenuManager 
from dotenv import load_dotenv
from models.enums import TipoParametro
from models.prompt_models import PromptRequest
from utils.file_util import get_default_filename, get_mime_type

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_api_key:
    logger.warning("Anthropic API key not found in environment variables")

client = anthropic.Anthropic(api_key=anthropic_api_key)
menu_mgr = MenuManager() 

#MODEL_NAME = "claude-3-sonnet-20240229" 
CLAUDE4='claude-sonnet-4-20250514'

async def process(req: PromptRequest) -> str:
    try:
        prompt_content = await menu_mgr.mount(req) # For text-based prompts
        
        response = client.messages.create(
            model=CLAUDE4,
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
 
async def process_file(file_base64: str, prompt_text: str, tipo_arquivo: TipoParametro) -> str:
    try:
        mime_type = get_mime_type(tipo_arquivo)
          
        response = client.messages.create(
            model=CLAUDE4,
            max_tokens=204,
            messages=[
              {
                "role":"user",
                "content":[
                    {
                        "type": "image",
                        "source": { 
                            "type": "base64",
                            "media_type": mime_type,
                            "data": file_base64
                                }                       
                    },
                    {"type": "text", "text": prompt_text},
                ],
              }
            ],
        )
        result = response.content[0].text.strip()
        return result
    except Exception as e:
        print(e)
        
async def process_web_search(req: PromptRequest):
    try:
        prompt_content = await menu_mgr.mount(req)
        
        response = client.messages.create(
            model=CLAUDE4,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": prompt_content
                }
            ],
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 1
            }]
        )
        return response
    
    except Exception as e:
        logger.error(f"Erro ao processar prompt com Claude (texto): {e}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento com Claude (texto): {str(e)}")
