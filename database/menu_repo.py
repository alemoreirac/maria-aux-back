# database/menu_repo.py
import logging
from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from models.enums import TipoParametro, TipoPrompt, LLM 
from models.menu_models import MenuParameter, MenuPromptWithParams
from database.db_config import AsyncSessionLocal
load_dotenv()

logger = logging.getLogger(__name__)

class MenuRepository:
    async def get_prompts_with_parameters(self) -> List[MenuPromptWithParams]:
        async with AsyncSessionLocal() as session:
            try:
                query = text("""
                    SELECT
                        p.id as prompt_id, p.titulo as prompt_titulo,
                        p.tipo, p.llm_used as prompt_llm_used,
                        p.has_reasoning as prompt_has_reasoning, p.has_search as prompt_has_search,
                        p.has_files as prompt_has_files, p.has_photo as prompt_has_photo, p.descricao as prompt_descricao,
                        par.id as param_id, par.titulo as param_titulo,
                        par.descricao as param_descricao, par.tipo as param_tipo
                    FROM aux.prompts p
                    LEFT JOIN aux.parameters par ON p.id = par.prompt_id
                    ORDER BY p.id, par.id
                """)
                result = await session.execute(query)
                rows = result.fetchall() 

                prompts_map = {}
                for row in rows:
                    if row.prompt_id not in prompts_map:
                        prompts_map[row.prompt_id] = MenuPromptWithParams(
                            id=row.prompt_id,
                            titulo=row.prompt_titulo,
                            tipo=TipoPrompt(int(row.tipo)),
                            llm_used=LLM(int(row.prompt_llm_used)) if row.prompt_llm_used is not None else None,
                            has_reasoning=row.prompt_has_reasoning,
                            has_search=row.prompt_has_search,
                            has_files=row.prompt_has_files,
                            has_photo=row.prompt_has_photo,
                            descricao=row.prompt_descricao,
                            parameters=[]
                        )
                    if row.param_id is not None:
                        parameter = MenuParameter(
                            id=row.param_id,
                            titulo=row.param_titulo,
                            descricao=row.param_descricao,
                            tipo=TipoParametro(int(row.param_tipo))
                        )
                        prompts_map[row.prompt_id].parameters.append(parameter)
                
                menu_prompts = list(prompts_map.values())
                logger.info(f"Carregados {len(menu_prompts)} prompts para o menu")
                return menu_prompts
            except SQLAlchemyError as e:
                logger.error(f"Erro SQLAlchemy ao buscar prompts para menu: {str(e)}")
                return []
            except Exception as e:
                logger.error(f"Erro inesperado ao buscar prompts para menu: {str(e)}")
                return []

    async def get_prompt_with_parameters(self, prompt_id: int) -> Optional[MenuPromptWithParams]:
        async with AsyncSessionLocal() as session:
            try:
                query = text("""
                    SELECT
                        p.id as prompt_id, p.titulo as prompt_titulo,
                        p.tipo as prompt_tipo, p.llm_used as prompt_llm_used,
                        p.has_reasoning as prompt_has_reasoning, p.has_search as prompt_has_search,
                        p.has_files as prompt_has_files, p.has_photo as prompt_has_photo, p.descricao as prompt_descricao,
                        par.id as param_id, par.titulo as param_titulo,
                        par.descricao as param_descricao, par.tipo as param_tipo
                    FROM aux.prompts p
                    LEFT JOIN aux.parameters par ON p.id = par.prompt_id
                    WHERE p.id = :prompt_id
                    ORDER BY par.id
                """)
                result = await session.execute(query, {"prompt_id": prompt_id})
                rows = result.fetchall()

                if not rows:
                    return None

                first_row = rows[0]
                parameters = []
                for row_data in rows:
                    if row_data.param_id is not None:
                        parameter = MenuParameter(
                            id=row_data.param_id,
                            titulo=row_data.param_titulo,
                            descricao=row_data.param_descricao,
                            tipo=TipoParametro(int(row_data.param_tipo))
                        )
                        parameters.append(parameter)
                
                return MenuPromptWithParams(
                    id=first_row.prompt_id,
                    titulo=first_row.prompt_titulo,
                    tipo=TipoPrompt(int(first_row.prompt_tipo)),
                    llm_used=LLM(int(first_row.prompt_llm_used)) if first_row.prompt_llm_used is not None else None,
                    has_reasoning=first_row.prompt_has_reasoning,
                    has_search=first_row.prompt_has_search,
                    has_files=first_row.prompt_has_files,
                    has_photo=first_row.prompt_has_photo,
                    descricao = first_row.prompt_descricao,
                    parameters=parameters
                )
            except SQLAlchemyError as e:
                logger.error(f"Erro SQLAlchemy ao buscar prompt {prompt_id} para menu: {str(e)}")
                return None
            except Exception as e:
                logger.error(f"Erro inesperado ao buscar prompt {prompt_id} para menu: {str(e)}")
                return None