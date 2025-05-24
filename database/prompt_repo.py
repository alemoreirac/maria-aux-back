# database/prompt_repo.py
import logging
from typing import List, Optional, Any, Dict
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from models.prompt_models import PromptResponse, PromptCreate, PromptUpdate # Atualizado
from models.enums import TipoParametroEnum

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

class PromptRepository:

    async def create_prompt(self, prompt_data: PromptCreate) -> Optional[PromptResponse]:
        async with AsyncSessionLocal() as session:
            try:
                print("teste@###########")
                print(str(prompt_data))
                
                query = text("""
                    INSERT INTO aux.prompts (titulo, conteudo, tipo)
                    VALUES (:titulo, :conteudo, :tipo)
                    RETURNING id, titulo, conteudo, tipo
                """)
                result = await session.execute(
                    query,
                    {
                        "titulo": prompt_data.titulo,
                        "conteudo": prompt_data.conteudo,
                        "tipo": prompt_data.tipo.value # Armazenar o valor do enum
                    }
                )
                created_prompt_row = result.fetchone()
                await session.commit()
                if created_prompt_row:
                    return PromptResponse(
                        id=created_prompt_row[0],
                        titulo=created_prompt_row[1],
                        conteudo=created_prompt_row[2],
                        tipo=TipoParametroEnum(int(created_prompt_row[3])) # Converter de volta para Enum
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
                    SELECT id, titulo, conteudo, tipo FROM aux.prompts
                    WHERE id = :prompt_id
                """)
                result = await session.execute(query, {"prompt_id": prompt_id})
                prompt_row = result.fetchone()
                if prompt_row:
                    return PromptResponse(
                        id=prompt_row[0],
                        titulo=prompt_row[1],
                        conteudo=prompt_row[2],
                        tipo=TipoParametroEnum(int(prompt_row[3]))
                    )
                return None
            except SQLAlchemyError as e:
                logger.error(f"Erro ao buscar prompt por ID: {e}")
                return None
            except Exception as e:
                logger.error(f"Erro inesperado ao buscar prompt por ID: {e}")
                return None

    async def get_prompts(self) -> List[PromptResponse]: # Alterado para retornar List[PromptResponse]
        async with AsyncSessionLocal() as session:
            try:
                query = text("""SELECT id, titulo, conteudo, tipo FROM aux.prompts""")
                result = await session.execute(query)
                prompt_rows = result.fetchall()
                return [
                    PromptResponse(
                        id=row[0],
                        titulo=row[1],
                        conteudo=row[2],
                        tipo=TipoParametroEnum(int(row[3]))
                    ) for row in prompt_rows
                ]
            except SQLAlchemyError as e:
                logger.error(f"Erro ao buscar prompts: {e}")
                return [] # Retornar lista vazia em caso de erro
            except Exception as e:
                logger.error(f"Erro inesperado ao buscar prompts: {e}")
                return [] # Retornar lista vazia em caso de erro

    async def update_prompt(self, prompt_id: int, prompt_update_data: PromptUpdate) -> Optional[PromptResponse]:
        async with AsyncSessionLocal() as session:
            try:
                # Buscar o prompt existente para garantir que ele exista
                select_query = text("SELECT id, titulo, conteudo, tipo FROM aux.prompts WHERE id = :prompt_id")
                current_prompt_result = await session.execute(select_query, {"prompt_id": prompt_id})
                current_prompt = current_prompt_result.fetchone()

                if not current_prompt:
                    return None

                update_fields = prompt_update_data.model_dump(exclude_unset=True)
                if not update_fields:
                    # Se nada for passado para atualizar, retorna o prompt atual
                    return PromptResponse(
                        id=current_prompt[0],
                        titulo=current_prompt[1],
                        conteudo=current_prompt[2],
                        tipo=TipoParametroEnum(int(current_prompt[3]))
                    )

                # Se 'tipo' estiver sendo atualizado, use seu valor numérico
                if 'tipo' in update_fields and isinstance(update_fields['tipo'], TipoParametroEnum):
                    update_fields['tipo'] = update_fields['tipo'].value

                set_clauses = [f"{key} = :{key}" for key in update_fields.keys()]
                query_str = f"""
                    UPDATE aux.prompts
                    SET {', '.join(set_clauses)}
                    WHERE id = :prompt_id
                    RETURNING id, titulo, conteudo, tipo
                """
                query = text(query_str)

                params = {"prompt_id": prompt_id, **update_fields}

                result = await session.execute(query, params)
                updated_prompt_row = result.fetchone()
                await session.commit()

                if updated_prompt_row:
                    return PromptResponse(
                        id=updated_prompt_row[0],
                        titulo=updated_prompt_row[1],
                        conteudo=updated_prompt_row[2],
                        tipo=TipoParametroEnum(int(updated_prompt_row[3]))
                    )
                return None
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Erro ao atualizar prompt: {e}")
                return None
            except Exception as e:
                await session.rollback()
                logger.error(f"Erro inesperado ao atualizar prompt: {e}")
                return None

    async def delete_prompt(self, prompt_id: int) -> bool:
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
            
async def get_prompts_with_params(self) -> List[Dict[str, Any]]:
    async with AsyncSessionLocal() as session:
        try:
            # Query com debug e campos corretos
            query = text("""
                SELECT
                    p.id,
                    p.titulo,
                    p.conteudo,
                    p.tipo as prompt_tipo,
                    CASE 
                        WHEN COUNT(par.id) = 0 THEN '[]'::json
                        ELSE JSON_AGG(
                            JSON_BUILD_OBJECT(
                                'id', par.id,
                                'titulo', par.titulo,
                                'descricao', par.descricao,
                                'tipo_param', par.tipo,
                                'valor', COALESCE(par.valor_padrao, '')
                            ) ORDER BY par.id
                        )
                    END as parameters
                FROM aux.prompts p
                LEFT JOIN aux.parameters par ON p.id = par.prompt_id
                GROUP BY p.id, p.titulo, p.conteudo, p.tipo
                ORDER BY p.id
            """)
            
            result = await session.execute(query)
            rows = result.fetchall()
            
            logger.info(f"Query retornou {len(rows)} prompts")
            
            response_data = []
            for row in rows:
                try:
                    parameters = row[4]
                    # Se parameters vier como string, converter para JSON
                    if isinstance(parameters, str):
                        import json
                        parameters = json.loads(parameters)
                    
                    response_data.append({
                        "id": row[0],
                        "titulo": row[1],
                        "conteudo": row[2],
                        "tipo": row[3],
                        "parameters": parameters
                    })
                    
                    # Debug: log do primeiro prompt para verificar estrutura
                    if len(response_data) == 1:
                        logger.info(f"Exemplo de prompt: {response_data[0]}")
                        
                except Exception as row_error:
                    logger.error(f"Erro ao processar linha do prompt {row[0]}: {row_error}")
                    response_data.append({
                        "id": row[0],
                        "titulo": row[1],
                        "conteudo": row[2],
                        "tipo": row[3],
                        "parameters": []
                    })
            
            return response_data
            
        except SQLAlchemyError as e:
            logger.error(f"Erro SQLAlchemy ao buscar prompts com parâmetros: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar prompts com parâmetros: {str(e)}")
            return []
