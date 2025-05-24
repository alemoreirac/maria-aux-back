# database/menu_repo.py
import logging
from typing import List, Dict, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from models.enums import TipoParametroEnum, TipoPromptEnum
from models.menu_models import MenuParameter, MenuPromptWithParams

load_dotenv()

DATABASE_URL = os.getenv("ASYNC_PG_CONN_STR", "postgresql+asyncpg://user:password@host:port/dbname")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_recycle=1800,
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

logger = logging.getLogger(__name__)



class MenuRepository:
    
    async def get_prompts_with_parameters(self) -> List[MenuPromptWithParams]:
        """
        Busca todos os prompts com seus parâmetros usando uma única query com JOIN.
        Retorna uma lista estruturada para montar o menu.
        """
        async with AsyncSessionLocal() as session:
            try:
                query = text("""
                    SELECT 
                        p.id as prompt_id,
                        p.titulo as prompt_titulo,
                        p.conteudo as prompt_conteudo,
                        p.tipo as prompt_tipo,
                        par.id as param_id,
                        par.titulo as param_titulo,
                        par.descricao as param_descricao,
                        par.tipo as param_tipo
                    FROM aux.prompts p
                    LEFT JOIN aux.parameters par ON p.id = par.prompt_id
                    ORDER BY p.id, par.id
                """)
                
                result = await session.execute(query)
                rows = result.fetchall()
                
                # Agrupar os resultados por prompt
                prompts_dict = {}
                
                for row in rows:
                    prompt_id = row[0]
                    
                    # Se é a primeira vez que vemos este prompt, criar entrada
                    if prompt_id not in prompts_dict:
                        prompts_dict[prompt_id] = {
                            'id': row[0],
                            'titulo': row[1],
                            'conteudo': row[2],
                            'tipo': TipoPromptEnum(int(row[3])),
                            'parameters': []
                        }
                    
                    # Se há parâmetro nesta linha (LEFT JOIN pode retornar None)
                    if row[4] is not None:  # param_id
                        parameter = MenuParameter(
                            id=row[4],
                            titulo=row[5],
                            descricao=row[6],
                            tipo=TipoParametroEnum(int(row[7]))
                        )
                        prompts_dict[prompt_id]['parameters'].append(parameter)
                
                # Converter o dicionário para lista de MenuPromptWithParams
                menu_prompts = []
                for prompt_data in prompts_dict.values():
                    menu_prompt = MenuPromptWithParams(
                        id=prompt_data['id'],
                        titulo=prompt_data['titulo'],
                        conteudo=prompt_data['conteudo'],
                        tipo=prompt_data['tipo'],
                        parameters=prompt_data['parameters']
                    )
                    menu_prompts.append(menu_prompt)
                
                logger.info(f"Carregados {len(menu_prompts)} prompts para o menu")
                return menu_prompts
                
            except SQLAlchemyError as e:
                logger.error(f"Erro SQLAlchemy ao buscar prompts para menu: {str(e)}")
                return []
            except Exception as e:
                logger.error(f"Erro inesperado ao buscar prompts para menu: {str(e)}")
                return []

    async def get_prompt_with_parameters(self, prompt_id: int) -> MenuPromptWithParams | None:
        """
        Busca um prompt específico com seus parâmetros.
        Útil quando você precisar dos detalhes de um prompt específico do menu.
        """
        async with AsyncSessionLocal() as session:
            try:
                query = text("""
                    SELECT 
                        p.id as prompt_id,
                        p.titulo as prompt_titulo,
                        p.conteudo as prompt_conteudo,
                        p.tipo as prompt_tipo,
                        par.id as param_id,
                        par.titulo as param_titulo,
                        par.descricao as param_descricao,
                        par.tipo as param_tipo
                    FROM aux.prompts p
                    LEFT JOIN aux.parameters par ON p.id = par.prompt_id
                    WHERE p.id = :prompt_id
                    ORDER BY par.id
                """)
                
                result = await session.execute(query, {"prompt_id": prompt_id})
                rows = result.fetchall()
                
                if not rows:
                    return None
                
                # Primeira linha tem os dados do prompt
                first_row = rows[0]
                parameters = []
                
                # Coletar todos os parâmetros
                for row in rows:
                    if row[4] is not None:  # param_id existe
                        parameter = MenuParameter(
                            id=row[4],
                            titulo=row[5],
                            descricao=row[6],
                            tipo=TipoParametroEnum(int(row[7]))
                        )
                        parameters.append(parameter)
                
                return MenuPromptWithParams(
                    id=first_row[0],
                    titulo=first_row[1],
                    conteudo=first_row[2],
                    tipo=TipoPromptEnum(int(first_row[3])),
                    parameters=parameters
                )
                
            except SQLAlchemyError as e:
                logger.error(f"Erro SQLAlchemy ao buscar prompt {prompt_id} para menu: {str(e)}")
                return None
            except Exception as e:
                logger.error(f"Erro inesperado ao buscar prompt {prompt_id} para menu: {str(e)}")
                return None
 