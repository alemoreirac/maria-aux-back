import os
import logging
from fastapi import HTTPException
from models.prompt_models import PromptRequest
from dotenv import load_dotenv
from openai import OpenAI
from models.enums import TipoParametro
from managers.menu_mgr import MenuManager # Assuming this is still needed for text-only part
from utils.file_util import get_default_filename , get_mime_type
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.warning("OpenAI API key not found in environment variables")

client = OpenAI(api_key=openai_api_key)
menu_mgr = MenuManager()  

MULTIMODAL_MODEL = "gpt-4o"  
TEXT_MODEL = "gpt-4.1"  



async def process(req: PromptRequest) -> str:
    try:
        prompt_content = await menu_mgr.mount(req)  
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

async def process_file(file_base64: str, prompt_text: str, tipo_arquivo: TipoParametro) -> str:
    
    try:
        mime_type = get_mime_type(tipo_arquivo)
        
        filename = get_default_filename(tipo_arquivo)
        
        response = client.responses.create(
            model=MULTIMODAL_MODEL,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_file",
                            "filename": filename,
                            "file_data": f"data:{mime_type};base64,{file_base64}",
                        },
                        {
                            "type": "input_text",
                            "text": prompt_text,
                        },
                    ],
                }
            ]
        )
        
        result = response.output_text.strip()
        return result
        
    except Exception as e:
        logger.error(f"Erro ao processar arquivo {tipo_arquivo.name} com ChatGPT: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento de arquivo {tipo_arquivo.name} com ChatGPT: {str(e)}")
    
async def process_web_search(req: PromptRequest) -> str:
    try:
        prompt_content = await menu_mgr.mount(req)

        print("####WEB SEARCH PROMPT#######")
        print(prompt_content)

        response = client.chat.completions.create(
           model="gpt-4.1",
    tools=[{"type": "web_search_preview"}],  messages=[
                {
                    "role": "user",
                    "content": f"""Pesquise na internet informações reais e atualizadas sobre: {prompt_content}
Forneça links reais, confiáveis e recentes como parte da resposta."""
                }
            ],
            temperature=0.2,
            max_tokens=4096
        )

        result = response.choices[0].message.content.strip()
        return result

    except Exception as e:
        logger.error(f"Erro ao fazer busca web com ChatGPT: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento de busca web com ChatGPT: {str(e)}")
