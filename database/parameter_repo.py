    import logging
    from typing import List, Optional
    from sqlalchemy import text
    from sqlalchemy.exc import SQLAlchemyError
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker
    from models.parameter_models import ParameterCreate, ParameterUpdate, ParameterResponse
    from models.enums import TipoParametroEnum
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    DATABASE_URL = os.getenv("ASYNC_PG_CONN_STR")

    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_recycle=1800,
    )

    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )


    logger = logging.getLogger(__name__)

    class ParameterRepository:
        async def create_parameter(self, parameter_data: ParameterCreate) -> Optional[ParameterResponse]:
            async with AsyncSessionLocal() as session:
                try:
                    query = text("""
                        INSERT INTO aux.parameters (prompt_id, titulo, descricao, tipo)
                        VALUES (:prompt_id, :titulo, :descricao, :tipo)
                        RETURNING id, prompt_id, titulo, descricao, tipo
                    """)
                    result = await session.execute(
                        query,
                        {
                            "prompt_id": parameter_data.prompt_id,
                            "titulo": parameter_data.titulo,
                            "descricao": parameter_data.descricao,
                            "tipo": parameter_data.tipo.value # Armazena o valor numérico (e.g., 1)
                        }
                    )
                    created_row = result.fetchone()
                    await session.commit()
                    if created_row:
                        return ParameterResponse(
                            id=created_row[0],
                            prompt_id=created_row[1],
                            titulo=created_row[2],
                            descricao=created_row[3],
                            tipo=TipoParametroEnum(int(created_row[4])) # <-- CORRIGIDO
                        )
                    return None
                except SQLAlchemyError as e:
                    await session.rollback()
                    logger.error(f"Erro ao criar parâmetro: {e}")
                    return None
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Erro inesperado ao criar parâmetro: {e}")
                    return None

        async def get_parameter(self, parameter_id: int) -> Optional[ParameterResponse]:
            async with AsyncSessionLocal() as session:
                try:
                    query = text("""
                        SELECT id, prompt_id, titulo, descricao, tipo FROM aux.parameters
                        WHERE id = :parameter_id
                    """)
                    result = await session.execute(query, {"parameter_id": parameter_id})
                    row = result.fetchone()
                    if row:
                        return ParameterResponse(
                            id=row[0],
                            prompt_id=row[1],
                            titulo=row[2],
                            descricao=row[3],
                            tipo=TipoParametroEnum(int(row[4])) # <-- CORRIGIDO
                        )
                    return None
                except SQLAlchemyError as e:
                    logger.error(f"Erro ao buscar parâmetro por ID: {e}")
                    return None
                except Exception as e:
                    logger.error(f"Erro inesperado ao buscar parâmetro por ID: {e}")
                    return None

        async def get_parameters_for_prompt(self, prompt_id: int) -> List[ParameterResponse]:
            async with AsyncSessionLocal() as session:
                try:
                    query = text("""
                        SELECT id, prompt_id, titulo, descricao, tipo FROM aux.parameters
                        WHERE prompt_id = :prompt_id
                    """)
                    result = await session.execute(query, {"prompt_id": prompt_id})
                    rows = result.fetchall()
                    return [
                        ParameterResponse(
                            id=row[0],
                            prompt_id=row[1],
                            titulo=row[2],
                            descricao=row[3],
                            tipo=TipoParametroEnum(int(row[4])) # <-- CORRIGIDO
                        ) for row in rows
                    ]
                except SQLAlchemyError as e:
                    logger.error(f"Erro ao buscar parâmetros para o prompt {prompt_id}: {e}")
                    return []
                except Exception as e:
                    logger.error(f"Erro inesperado ao buscar parâmetros para o prompt {prompt_id}: {e}")
                    return []

        async def update_parameter(self, parameter_id: int, parameter_data: ParameterUpdate) -> Optional[ParameterResponse]:
            async with AsyncSessionLocal() as session:
                try:
                    # Primeiro, verificar se o parâmetro existe
                    select_query = text("SELECT id, prompt_id, titulo, descricao, tipo FROM aux.parameters WHERE id = :parameter_id")
                    current_param_result = await session.execute(select_query, {"parameter_id": parameter_id})
                    current_param = current_param_result.fetchone()
                    
                    if not current_param:
                        return None

                    # Obter apenas os campos que foram enviados (excluindo unset)
                    update_fields = parameter_data.model_dump(exclude_unset=True)
                    
                    if not update_fields:
                        # Se nenhum campo foi enviado para atualizar, retorna o registro atual
                        return ParameterResponse(
                            id=current_param[0], 
                            prompt_id=current_param[1], 
                            titulo=current_param[2],
                            descricao=current_param[3], 
                            tipo=TipoParametroEnum(int(current_param[4]))
                        )

                    # Converter enum para valor se necessário
                    if 'tipo' in update_fields and isinstance(update_fields['tipo'], TipoParametroEnum):
                        update_fields['tipo'] = update_fields['tipo'].value

                    # IMPORTANTE: Remover prompt_id dos campos de atualização se estiver presente
                    # Isso garante que a chave estrangeira não seja tocada
                    if 'prompt_id' in update_fields:
                        del update_fields['prompt_id']

                    # Se após remover prompt_id não há mais campos para atualizar
                    if not update_fields:
                        return ParameterResponse(
                            id=current_param[0], 
                            prompt_id=current_param[1], 
                            titulo=current_param[2],
                            descricao=current_param[3], 
                            tipo=TipoParametroEnum(int(current_param[4]))
                        )

                    # Construir a query de UPDATE apenas com os campos permitidos
                    set_clauses = [f"{key} = :{key}" for key in update_fields.keys()]
                    
                    query_str = f"""
                        UPDATE aux.parameters
                        SET {', '.join(set_clauses)}
                        WHERE id = :parameter_id
                        RETURNING id, prompt_id, titulo, descricao, tipo
                    """
                    
                    query = text(query_str)
                    params = {"parameter_id": parameter_id, **update_fields}
                    
                    result = await session.execute(query, params)
                    updated_row = result.fetchone()
                    
                    await session.commit()
                    
                    if updated_row:
                        return ParameterResponse(
                            id=updated_row[0], 
                            prompt_id=updated_row[1], 
                            titulo=updated_row[2],
                            descricao=updated_row[3], 
                            tipo=TipoParametroEnum(int(updated_row[4]))
                        )
                    
                    return None
                
                except SQLAlchemyError as e:
                    await session.rollback()
                    logger.error(f"Erro SQLAlchemy ao atualizar parâmetro {parameter_id}: {str(e)}")
                    logger.error(f"Query tentada: {query_str if 'query_str' in locals() else 'N/A'}")
                    logger.error(f"Parâmetros: {params if 'params' in locals() else 'N/A'}")
                    return None
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Erro inesperado ao atualizar parâmetro {parameter_id}: {str(e)}")
                    return None

        async def delete_parameter(self, parameter_id: int) -> bool:
            async with AsyncSessionLocal() as session:
                try:
                    query = text("""
                        DELETE FROM aux.parameters
                        WHERE id = :parameter_id
                        RETURNING id
                    """)
                    result = await session.execute(query, {"parameter_id": parameter_id})
                    deleted_id = result.fetchone()
                    await session.commit()
                    return deleted_id is not None
                except SQLAlchemyError as e:
                    await session.rollback()
                    logger.error(f"Erro ao deletar parâmetro: {e}")
                    return False
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Erro inesperado ao deletar parâmetro: {e}")
                    return False

        # --- Método de Teste CRUD ---
        async def run_crud_test(self, prompt_id_for_test: int):
            print(f"\n--- Iniciando Teste CRUD de Parâmetros para Prompt ID: {prompt_id_for_test} ---")

            # 1. Criar Parâmetro 1
            print("\n1. Criando Parâmetro 1 (TEXTO)...")
            param_data_1 = ParameterCreate(
                prompt_id=prompt_id_for_test,
                titulo="Nome do Usuário",
                descricao="Nome completo do usuário.",
                tipo=TipoParametroEnum.TEXTO
            )
            created_param_1 = await self.create_parameter(param_data_1)
            if created_param_1:
                print(f"Parâmetro 1 criado: {created_param_1.model_dump_json(indent=2)}")
            else:
                print("Falha ao criar Parâmetro 1.")
                return

            # 2. Criar Parâmetro 2
            print("\n2. Criando Parâmetro 2 (NUMERICO)...")
            param_data_2 = ParameterCreate(
                prompt_id=prompt_id_for_test,
                titulo="Idade do Usuário",
                descricao="Idade em anos.",
                tipo=TipoParametroEnum.NUMERICO
            )
            created_param_2 = await self.create_parameter(param_data_2)
            if created_param_2:
                print(f"Parâmetro 2 criado: {created_param_2.model_dump_json(indent=2)}")
            else:
                print("Falha ao criar Parâmetro 2.")
                return

            # 3. Ler todos os parâmetros para o prompt
            print(f"\n3. Lendo todos os parâmetros para o Prompt ID {prompt_id_for_test}...")
            params_for_prompt = await self.get_parameters_for_prompt(prompt_id_for_test)
            if params_for_prompt:
                print("Parâmetros encontrados:")
                for p in params_for_prompt:
                    print(f"- {p.model_dump_json(indent=2)}")
            else:
                print("Nenhum parâmetro encontrado para o prompt.")

            # 4. Ler um parâmetro específico (Parâmetro 1)
            print(f"\n4. Lendo Parâmetro 1 por ID ({created_param_1.id})...")
            fetched_param_1 = await self.get_parameter(created_param_1.id)
            if fetched_param_1:
                print(f"Parâmetro 1 lido: {fetched_param_1.model_dump_json(indent=2)}")
            else:
                print("Falha ao ler Parâmetro 1.")

            # 5. Atualizar Parâmetro 1
            print(f"\n5. Atualizando Parâmetro 1 (ID: {created_param_1.id})...")
            update_data = ParameterUpdate(
                titulo="Nome Completo",
                descricao="Nome completo do cliente/usuário.",
                tipo=TipoParametroEnum.ARQUIVO_PDF # Mudar o tipo
            )
            updated_param_1 = await self.update_parameter(created_param_1.id, update_data)
            if updated_param_1:
                print(f"Parâmetro 1 atualizado: {updated_param_1.model_dump_json(indent=2)}")
            else:
                print("Falha ao atualizar Parâmetro 1.")

            # 6. Ler novamente Parâmetro 1 para confirmar a atualização
            print(f"\n6. Lendo Parâmetro 1 novamente para confirmar atualização (ID: {created_param_1.id})...")
            fetched_param_1_updated = await self.get_parameter(created_param_1.id)
            if fetched_param_1_updated:
                print(f"Parâmetro 1 após atualização: {fetched_param_1_updated.model_dump_json(indent=2)}")

            # 7. Deletar Parâmetro 1
            print(f"\n7. Deletando Parâmetro 1 (ID: {created_param_1.id})...")
            deleted_1 = await self.delete_parameter(created_param_1.id)
            if deleted_1:
                print(f"Parâmetro 1 (ID: {created_param_1.id}) deletado com sucesso.")
            else:
                print(f"Falha ao deletar Parâmetro 1 (ID: {created_param_1.id}).")

            # 8. Tentar ler Parâmetro 1 (deve ser None)
            print(f"\n8. Tentando ler Parâmetro 1 (ID: {created_param_1.id}) após deleção...")
            fetched_param_1_after_delete = await self.get_parameter(created_param_1.id)
            if fetched_param_1_after_delete is None:
                print("Parâmetro 1 não encontrado, deleção confirmada.")
            else:
                print("Erro: Parâmetro 1 ainda existe após deleção.")

            # 9. Deletar Parâmetro 2
            print(f"\n9. Deletando Parâmetro 2 (ID: {created_param_2.id})...")
            deleted_2 = await self.delete_parameter(created_param_2.id)
            if deleted_2:
                print(f"Parâmetro 2 (ID: {created_param_2.id}) deletado com sucesso.")
            else:
                print(f"Falha ao deletar Parâmetro 2 (ID: {created_param_2.id}).")
            
            print("\n--- Teste CRUD de Parâmetros Concluído ---")


    # Para executar o teste:
    import asyncio

    async def main():
        # Crie uma instância do ParameterRepository
        repo = ParameterRepository()

        # IMPORTANTE: Você precisa garantir que um prompt com este ID exista no banco de dados.
        # Se não tiver um prompt criado, você pode criar um manualmente antes ou
        # adicionar um método create_prompt temporário aqui para fins de teste.
        # Para o teste, vamos assumir que o prompt_id=1 já existe.
        test_prompt_id = 1
        
        # Chama o método de teste CRUD
        await repo.run_crud_test(test_prompt_id)

    if __name__ == "__main__":
        # Configura o logger para exibir mensagens INFO e acima
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())