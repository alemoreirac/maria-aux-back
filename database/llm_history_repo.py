from datetime import datetime, timezone, timedelta  
import logging 
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from typing import List, Any, Dict
import os
from dotenv import load_dotenv 
import asyncio 

load_dotenv()

logger = logging.getLogger(__name__)
 
engine = create_async_engine(
    os.getenv("ASYNC_PG_CONN_STR"),
    echo=False,
    pool_recycle=1800,
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False)
 
class LLMHistoryRepository:  
    async def log_message( 
            self,
            user_id: str,
            user_query: str,
            gpt_response: str,
        ) -> None: 

        async with AsyncSessionLocal() as session:
            try:
                create_table_sql = text("""
                    CREATE TABLE IF NOT EXISTS arq.llm_log (
                        user_id TEXT NOT NULL,
                        user_query TEXT,
                        gpt_response TEXT,
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                        PRIMARY KEY (user_id, timestamp)
                    );
                """)

                logger.debug("Executando CREATE TABLE IF NOT EXISTS...") # Use debug, info pode poluir o log
                await session.execute(create_table_sql)
               
                await session.commit()
                logger.debug("Commit após CREATE TABLE executado.")
 
                result = await session.execute(create_table_sql)
                print("Resultado de criar a tabela llm_log: "+ str(result))
 
                insert_sql = text("""
                    INSERT INTO arq.llm_log (user_id, user_query, gpt_response, timestamp)
                    VALUES (:user_id, :user_query, :gpt_response, :timestamp);
                """)
 
                await session.execute(
                    insert_sql,
                    {
                        "user_id": user_id,
                        "user_query": user_query,
                        "gpt_response": gpt_response,
                        "timestamp": datetime.now(timezone.utc),  
                    },
                )
                # --- Crucial Fix: Commit the INSERT operation ---
                await session.commit()
                logger.debug("Commit após INSERT executado.")
    
            except SQLAlchemyError as e: 
                logger.error(f"SQLAlchemy error during message logging: {e}", exc_info=True) 
            except Exception as e: 
                logger.error(f"Unexpected error during message logging: {e}", exc_info=True)

    async def get_recent_history(
            self, 
            user_id: str,
        ) -> List[Dict[str, Any]]: 
    
        async with AsyncSessionLocal() as session:
            try:   
                select_sql = text("""
                    SELECT user_id, user_query, gpt_response, timestamp
                    FROM arq.llm_log
                    WHERE user_id = :user_id 
                    ORDER BY timestamp DESC
                    LIMIT 20;
                """)

                result = await session.execute(
                    select_sql,
                    {
                        "user_id": user_id
                    },
                )

                messages = result.fetchall()

                history_list_of_dicts = [dict(row._mapping) for row in messages]

                return  history_list_of_dicts
            except SQLAlchemyError as e:
                # Log database-specific errors
                logger.error(f"SQLAlchemy error during llm log history for user:  {user_id}: {e}", exc_info=True)
                return [] # Return an empty list on error   
            except Exception as e:
                # Catch any other unexpected errors
                logger.error(f"Unexpected error during llm log history for user: {user_id}: {e}", exc_info=True)
                return [] # Return an empty list on error
 

async def test_log_message_and_retrieve():
    """
    Função assíncrona para testar os métodos log_message e get_recent_history.
    """
    print("Iniciando teste do LLMHistoryRepository...")

    repository = LLMHistoryRepository()

    # Dados de teste
    test_user_id = "E1yKeRwjOtWdTrhhNsvc8wiWTQu2"
    test_query_1 = "Qual a capital da França?"
    test_response_1 = "A capital da França é Paris."
    test_query_2 = "Qual o maior oceano?"
    test_response_2 = "O maior oceano é o Pacífico."

    # --- Testando log_message ---
    print(f"Testando log_message para user_id: {test_user_id}")
    try:
        await repository.log_message(test_user_id, test_query_1, test_response_1)
        print("Primeira mensagem logada com sucesso.")
        await repository.log_message(test_user_id, test_query_2, test_response_2)
        print("Segunda mensagem logada com sucesso.")
        result = await repository.get_recent_history(test_user_id)
        print(str(result))
    except Exception as e:
        logger.error(f"Erro durante o teste de log_message: {e}", exc_info=True)
        # Podemos sair ou continuar dependendo da severidade
 
    print("Teste do LLMHistoryRepository finalizado.")
    # O pool de conexões do engine será fechado automaticamente quando o script terminar.

# --- Ponto de Entrada para Execução Direta ---

if __name__ == "__main__":
    # Use asyncio.run() para executar a função assíncrona principal
    try:
        asyncio.run(test_log_message_and_retrieve())
    except KeyboardInterrupt:
        print("Execução interrompida pelo usuário.")
    except Exception as e:
        logger.error(f"Erro fatal durante a execução do teste: {e}", exc_info=True)
