import anthropic
from fastapi import  HTTPException
import logging
import os
from managers.prompt_mgr import PromptManager
from dotenv import load_dotenv 
from models.prompt_models import PromptRequest
load_dotenv()
 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_api_key:
    logger.warning("Anthropic API key not found in environment variables")

prompt_mgr = PromptManager()
client = anthropic.Anthropic(api_key=anthropic_api_key)

async def process(req: PromptRequest) -> str:
    
    try:
        prompt = await prompt_mgr.mount(req)
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229", 
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2048 
        )

        categorized_items = response.content[0].text.strip()
        logger.info("Resposta do Claude recebida com sucesso.")
        return categorized_items

    except Exception as e:
        logger.error(f"Erro ao processar prompt com Claude: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento com Claude: {str(e)}")



# async def process_pdf(pdf_path: str, prompt_id:int) -> str:
#     """Send the PDF directly to Anthropic Claude for analysis."""
#     try:
#         # Encode the PDF to base64
#         with open(pdf_path, "rb") as pdf_file:
#             pdf_data = base64.b64encode(pdf_file.read()).decode("utf-8")
        
#         # Prepare the prompt
#         prompt = await prompt_mgr.get_prompt(prompt_id) 
#         prompt_text = prompt.titulo
 
        
#         # Call the Anthropic API with the PDF
#         response = anthropic_client.messages.create(
#             #model="claude-3-7-sonnet-20250219",
#             model="claude-sonnet-4-20250514",
#             max_tokens=4000,
#             messages=[
#                 {
#                     "role": "user",
#                     "content": [
#                         {
#                             "type": "document",
#                             "source": {
#                                 "type": "base64",
#                                 "media_type": "application/pdf",
#                                 "data": pdf_data
#                             }
#                         },
#                         {
#                             "type": "text",
#                             "text": prompt_text
#                         }
#                     ]
#                 }
#             ],
#         )
        
#         return response.content[0].text
    
#     except Exception as e:
#         logger.error(f"Error analyzing PDF with Anthropic: {e}")
#         raise HTTPException(status_code=500, detail=f"Error analyzing PDF with Anthropic: {str(e)}")

  