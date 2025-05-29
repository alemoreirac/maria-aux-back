from enum import IntEnum

class TipoParametro(IntEnum):
    TEXTO = 1
    NUMERICO = 2
    ARQUIVO_PDF = 3
    ARQUIVO_DOCX = 4
    ARQUIVO_XLSX = 5
    ARQUIVO_TXT = 6
    IMAGEM = 7
    ARQUIVO_XLS=8
    ARQUIVO_CSV=9
    

class TipoPrompt(IntEnum):
    TEXTO = 1
    ARQUIVO= 2
    BUSCA = 3
    
class LLM(IntEnum):
    CHAT_GPT = 1
    CLAUDE = 2
    GEMINI = 3
    
class CategoriaPrompt(IntEnum):
    TESTE = 1