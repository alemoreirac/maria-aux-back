# database/prompt_repo.py
import logging
from typing import List, Optional, Any, Dict
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from models.prompt_models import PromptResponse, PromptCreate, PromptUpdate
from models.enums import TipoPrompt, LLM, CategoriaPrompt
from database.db_config import AsyncSessionLocal

load_dotenv()
 
logger = logging.getLogger(__name__)

class PromptRepository:

    async def create_prompt(self, prompt_data: PromptCreate) -> Optional[PromptResponse]:
        async with AsyncSessionLocal() as session:
            try:
                query = text("""
                    INSERT INTO aux.prompts (
                        titulo, conteudo, tipo, llm_used,
                        has_reasoning, has_search, has_files, has_photo,categoria,descricao
                    )
                    VALUES (:titulo, :conteudo, :tipo, :llm_used,
                            :has_reasoning, :has_search, :has_files, :has_photo, :categoria, :descricao)
                    RETURNING id, titulo, conteudo, tipo, llm_used,
                              has_reasoning, has_search, has_files, has_photo, categoria, descricao
                """)
                result = await session.execute(
                    query,
                    {
                        "titulo": prompt_data.titulo,
                        "conteudo": prompt_data.conteudo,
                        "tipo": prompt_data.tipo.value,
                        "llm_used": prompt_data.llm_used.value if prompt_data.llm_used else None,
                        "has_reasoning": prompt_data.has_reasoning,
                        "has_search": prompt_data.has_search,
                        "has_files": prompt_data.has_files,
                        "has_photo": prompt_data.has_photo,
                        "categoria": prompt_data.categoria,
                        "descricao": prompt_data.descricao
                    }
                )
                created_row = result.fetchone()
                await session.commit()
                if created_row:
                    return PromptResponse(
                        id=created_row[0],
                        titulo=created_row[1],
                        conteudo=created_row[2],
                        tipo=TipoPrompt(int(created_row[3])), # Corrected Enum
                        llm_used=LLM(int(created_row[4])) if created_row[4] is not None else None,
                        has_reasoning=created_row[5],
                        has_search=created_row[6],
                        has_files=created_row[7],
                        has_photo=created_row[8],
                        categoria=created_row[9],
                        descricao=created_row[10]
                    )
                return None
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Erro ao criar prompt: {e}")
                return None
            except Exception as e:
                await session.rollback()
                logger.error(f"Erro inesperado ao criar prompt: {e}")
                return None

    async def get_prompt(self, prompt_id: int) -> Optional[PromptResponse]:
        async with AsyncSessionLocal() as session:
            try:
                query = text("""
                    SELECT id, titulo, conteudo, tipo, llm_used,
                           has_reasoning, has_search, has_files, has_photo, categoria, descricao
                    FROM aux.prompts
                    WHERE id = :prompt_id
                """)
                result = await session.execute(query, {"prompt_id": prompt_id})
                prompt_row = result.fetchone()
                if prompt_row:
                    return PromptResponse(
                        id=prompt_row[0],
                        titulo=prompt_row[1],
                        conteudo=prompt_row[2],
                        tipo=TipoPrompt(int(prompt_row[3])), # Corrected Enum
                        llm_used=LLM(int(prompt_row[4])) if prompt_row[4] is not None else None,
                        has_reasoning=prompt_row[5],
                        has_search=prompt_row[6],
                        has_files=prompt_row[7],
                        has_photo=prompt_row[8],
                        categoria=prompt_row[9],
                        descricao=prompt_row[10]
                    )
                return None
            except SQLAlchemyError as e:
                logger.error(f"Erro ao buscar prompt por ID: {e}")
                return None
            except Exception as e:
                logger.error(f"Erro inesperado ao buscar prompt por ID: {e}")
                return None

    async def get_prompts(self) -> List[PromptResponse]:
        async with AsyncSessionLocal() as session:
            try:
                query = text("""
                    SELECT id, titulo, conteudo, tipo, llm_used,
                           has_reasoning, has_search, has_files, has_photo, categoria, descricao
                    FROM aux.prompts ORDER BY id
                """) # Added ORDER BY for consistency
                result = await session.execute(query)
                prompt_rows = result.fetchall()
                return [
                    PromptResponse(
                        id=row[0],
                        titulo=row[1],
                        conteudo=row[2],
                        tipo=TipoPrompt(int(row[3])), # Corrected Enum
                        llm_used=LLM(int(row[4])) if row[4] is not None else None,
                        has_reasoning=row[5],
                        has_search=row[6],
                        has_files=row[7],
                        has_photo=row[8],
                        categoria=row[9],
                        descricao=row[10]
                    ) for row in prompt_rows
                ]
            except SQLAlchemyError as e:
                logger.error(f"Erro ao buscar prompts: {e}")
                return []
            except Exception as e:
                logger.error(f"Erro inesperado ao buscar prompts: {e}")
                return []

    async def update_prompt(self, prompt_id: int, prompt_update_data: PromptUpdate) -> Optional[PromptResponse]:
        async with AsyncSessionLocal() as session:
            try:
                select_query = text("""
                    SELECT id, titulo, conteudo, tipo, llm_used,
                           has_reasoning, has_search, has_files, has_photo, descricao,categoria
                    FROM aux.prompts WHERE id = :prompt_id
                """)
                current_prompt_result = await session.execute(select_query, {"prompt_id": prompt_id})
                current_prompt = current_prompt_result.fetchone()

                if not current_prompt:
                    return None

                update_fields = prompt_update_data.model_dump(exclude_unset=True)
                if not update_fields: # Nothing to update
                    return PromptResponse.from_orm(current_prompt) # Use from_orm if row matches model

                # Convert enums to their values for SQL query
                if 'tipo' in update_fields and isinstance(update_fields['tipo'], TipoPrompt):
                    update_fields['tipo'] = update_fields['tipo'].value
                if 'llm_used' in update_fields: # Handles LLM enum or None
                    if isinstance(update_fields['llm_used'], LLM):
                        update_fields['llm_used'] = update_fields['llm_used'].value
                    # If None, it's already suitable for SQL

                set_clauses = [f"{key} = :{key}" for key in update_fields.keys()]
                query_str = f"""
                    UPDATE aux.prompts
                    SET {', '.join(set_clauses)}
                    WHERE id = :prompt_id
                    RETURNING id, titulo, conteudo, tipo, llm_used,
                              has_reasoning, has_search, has_files, has_photo,categoria,descricao
                """
                query = text(query_str)
                params = {"prompt_id": prompt_id, **update_fields}

                result = await session.execute(query, params)
                updated_row = result.fetchone()
                await session.commit()

                if updated_row:
                    return PromptResponse(
                        id=updated_row[0],
                        titulo=updated_row[1],
                        conteudo=updated_row[2],
                        tipo=TipoPrompt(int(updated_row[3])),
                        llm_used=LLM(int(updated_row[4])) if updated_row[4] is not None else None,
                        has_reasoning=updated_row[5],
                        has_search=updated_row[6],
                        has_files=updated_row[7],
                        has_photo=updated_row[8],
                        categoria=CategoriaPrompt(int(updated_row[9])),
                        descricao=updated_row[10]
                    )
                return None # Should not happen if update was successful and returned data
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Erro ao atualizar prompt: {e}")
                return None
            except Exception as e:
                await session.rollback()
                logger.error(f"Erro inesperado ao atualizar prompt: {e}")
                return None

    async def delete_prompt(self, prompt_id: int) -> bool: # No changes needed here
        async with AsyncSessionLocal() as session:
            try:
                query = text("""
                    DELETE FROM aux.prompts
                    WHERE id = :prompt_id
                    RETURNING id
                """)
                result = await session.execute(query, {"prompt_id": prompt_id})
                deleted_id = result.fetchone()
                await session.commit()
                return deleted_id is not None
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Erro ao deletar prompt: {e}")
                return False
            except Exception as e:
                await session.rollback()
                logger.error(f"Erro inesperado ao deletar prompt: {e}")
                return False
 
    async def get_prompts_with_parameters_dict(self) -> List[Dict[str, Any]]:
        async with AsyncSessionLocal() as session:
            try:
                query = text("""
                    SELECT
                        p.id, p.titulo, p.conteudo, p.tipo,
                        p.llm_used, p.has_reasoning, p.has_search, p.has_files, p.has_photo,p.categoria,p.descricao,
                        CASE
                            WHEN COUNT(par.id) = 0 THEN '[]'::json
                            ELSE JSON_AGG(
                                JSON_BUILD_OBJECT(
                                    'id', par.id,
                                    'titulo', par.titulo,
                                    'descricao', par.descricao,
                                    'tipo_param', par.tipo
                                ) ORDER BY par.id
                            )
                        END as parameters
                    FROM aux.prompts p
                    LEFT JOIN aux.parameters par ON p.id = par.prompt_id
                    GROUP BY p.id, p.titulo, p.conteudo, p.tipo, p.llm_used,
                             p.has_reasoning, p.has_search, p.has_files, p.has_photo, p.categoria, p.descricao
                    ORDER BY p.id
                """)
                result = await session.execute(query)
                rows = result.fetchall() # These are Row objects

                response_data = []
                for row in rows:
                    parameters_json = row.parameters
                    parameters_list = []
                    if isinstance(parameters_json, str): # Should be list of dicts from JSON_AGG
                        import json
                        parameters_list = json.loads(parameters_json)
                    elif isinstance(parameters_json, list):
                         parameters_list = parameters_json


                    prompt_dict = {
                        "id": row.id,
                        "titulo": row.titulo,
                        "conteudo": row.conteudo,
                        "tipo": TipoPrompt(int(row.tipo)).value, # Keep as value
                        "llm_used": LLM(int(row.llm_used)).value if row.llm_used is not None else None, # Keep as value
                        "has_reasoning": row.has_reasoning,
                        "has_search": row.has_search,
                        "has_files": row.has_files,
                        "has_photo": row.has_photo,
                        "parameters": parameters_list,
                        "descricao": row.descricao,
                        "categoria": row.categoria
                    }
                    response_data.append(prompt_dict)
                return response_data
            except SQLAlchemyError as e:
                logger.error(f"Erro SQLAlchemy ao buscar prompts com parâmetros (dict): {str(e)}")
                return []
            except Exception as e:
                logger.error(f"Erro inesperado ao buscar prompts com parâmetros (dict): {str(e)}")
                return []