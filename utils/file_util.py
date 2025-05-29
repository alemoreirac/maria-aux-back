
from models.enums import TipoParametro


def get_mime_type(tipo_arquivo: TipoParametro) -> str:
    """Retorna o MIME type para o tipo de arquivo"""
    mime_types = {
        TipoParametro.ARQUIVO_PDF: "application/pdf",
        TipoParametro.ARQUIVO_DOCX: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        TipoParametro.ARQUIVO_XLSX: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        TipoParametro.ARQUIVO_XLS: "application/vnd.ms-excel",
        TipoParametro.ARQUIVO_CSV: "text/csv",
        TipoParametro.ARQUIVO_TXT: "text/plain",
        TipoParametro.IMAGEM: "image/jpeg"
    }
    return mime_types.get(tipo_arquivo, "application/octet-stream")

def get_default_filename(tipo_arquivo: TipoParametro) -> str:
    """Retorna o nome de arquivo padrão para o tipo de arquivo"""
    filenames = {
        TipoParametro.ARQUIVO_PDF: "documento.pdf",
        TipoParametro.ARQUIVO_DOCX: "documento.docx",
        TipoParametro.ARQUIVO_XLSX: "planilha.xlsx",
        TipoParametro.ARQUIVO_XLS: "planilha.xls",
        TipoParametro.ARQUIVO_CSV: "dados.csv",
        TipoParametro.ARQUIVO_TXT: "arquivo.txt",
        TipoParametro.IMAGEM: "imagem.jpg"
    }
    return filenames.get(tipo_arquivo, None)