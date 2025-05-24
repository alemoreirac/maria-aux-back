import psycopg2
import os
from dotenv import load_dotenv
import sys

load_dotenv()

class DatabaseSetup:
    def __init__(self):
        self.conn = self._get_db_connection()
        
    def _get_db_connection(self): 
        conn_string = os.getenv("PG_CONN_STR")
        conn = psycopg2.connect(conn_string) 
        return conn

    def setup_database(self):
        """Configura o banco de dados com todas as tabelas necessárias"""
        print("Iniciando configuração do banco de dados...")
        
        try:
            # Criar schema aux
            self._create_schema()
            
            # Criar tabelas dos repositórios
            self._create_user_credits_table()
            self._create_llm_log_table()
            self._create_prompts_table()
            self._create_parameters_table()
            
            print("Configuração do banco de dados concluída com sucesso!")
            return True
            
        except Exception as e:
            print(f"Erro na configuração do banco de dados: {e}")
            return False
        finally:
            self.conn.close()
    
    def _create_schema(self):
        """Cria o schema aux"""
        print("Criando schema aux...")
        cur = self.conn.cursor()
        
        try:
            cur.execute("CREATE SCHEMA IF NOT EXISTS aux;")
            self.conn.commit()
            print("Schema aux criado ou já existente.")
        except Exception as e:
            self.conn.rollback()
            print(f"Erro ao criar schema aux: {e}")
            print("Tentando continuar com o schema padrão...")
        finally:
            cur.close()
    
    def _create_user_credits_table(self):
        """Cria a tabela aux.user_credits"""
        print("Criando tabela aux.user_credits...")
        cur = self.conn.cursor()
        
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS aux.user_credits (
                    user_id TEXT PRIMARY KEY,
                    credits INTEGER NOT NULL DEFAULT 0
                );
            """)
            self.conn.commit()
            print("Tabela aux.user_credits criada com sucesso.")
        except Exception as e:
            self.conn.rollback()
            print(f"Erro ao criar tabela aux.user_credits: {e}")
            raise
        finally:
            cur.close()
    
    def _create_llm_log_table(self):
        """Cria a tabela aux.llm_log"""
        print("Criando tabela aux.llm_log...")
        cur = self.conn.cursor()
        
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS aux.llm_log (
                    user_id TEXT NOT NULL,
                    user_query TEXT,
                    gpt_response TEXT,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    PRIMARY KEY (user_id, timestamp)
                );
            """)
            self.conn.commit()
            print("Tabela aux.llm_log criada com sucesso.")
        except Exception as e:
            self.conn.rollback()
            print(f"Erro ao criar tabela aux.llm_log: {e}")
            raise
        finally:
            cur.close()
    
    def _create_prompts_table(self):
        """Cria a tabela aux.prompts"""
        print("Criando tabela aux.prompts...")
        cur = self.conn.cursor()
        
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS aux.prompts (
                    id SERIAL PRIMARY KEY,
                    titulo TEXT NOT NULL,
                    conteudo TEXT NOT NULL,
                    tipo TEXT NOT NULL
                );
            """)
            self.conn.commit()
            print("Tabela aux.prompts criada com sucesso.")
        except Exception as e:
            self.conn.rollback()
            print(f"Erro ao criar tabela aux.prompts: {e}")
            raise
        finally:
            cur.close()
    
    def _create_parameters_table(self):
        """Cria a tabela aux.parameters"""
        print("Criando tabela aux.parameters...")
        cur = self.conn.cursor()
        
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS aux.parameters (
                    id SERIAL PRIMARY KEY,
                    prompt_id INTEGER NOT NULL,
                    titulo TEXT NOT NULL,
                    descricao TEXT,
                    tipo TEXT NOT NULL,
                    FOREIGN KEY (prompt_id) REFERENCES aux.prompts(id) ON DELETE CASCADE
                );
            """)
            self.conn.commit()
            print("Tabela aux.parameters criada com sucesso.")
        except Exception as e:
            self.conn.rollback()
            print(f"Erro ao criar tabela aux.parameters: {e}")
            raise
        finally:
            cur.close()

def main():
    db_setup = DatabaseSetup()
    success = db_setup.setup_database()
    if success:
        print("Banco de dados configurado com sucesso!")
    else:
        print("Falha na configuração do banco de dados.")
        sys.exit(1)

if __name__ == "__main__":
    main()