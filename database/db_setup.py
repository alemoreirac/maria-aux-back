import psycopg2
import os
from dotenv import load_dotenv
import sys

load_dotenv()

class DatabaseSetup:
    def __init__(self):
        self.conn = self._get_db_connection()
        
    def _get_db_connection(self): 
        conn_string =  os.getenv("PG_CONN_STR")
  
        # Establish the connection
        conn = psycopg2.connect(conn_string) 
        
        return conn

    def setup_database(self):
        """Configura o banco de dados com todas as tabelas necessárias"""
        print("Iniciando configuração do banco de dados...")
        
        try:
            # Primeiro, testar permissões com tabela temporária
            self._test_permissions()
            
            # Criar schema aux
            self._create_schema()
            
            # Verificar se a extensão pgvector está disponível
            has_pgvector = self._check_pgvector_extension()
            
            # Criar tabelas necessárias
            self._create_functions_ia_table()
            
            if has_pgvector:
                self._create_embeddings_table_with_vector()
            else:
                self._create_embeddings_table_without_vector()
            
            print("Configuração do banco de dados concluída com sucesso!")
            return True
            
        except Exception as e:
            print(f"Erro na configuração do banco de dados: {e}")
            return False
        finally:
            self.conn.close()
    
    def _test_permissions(self):
        """Testa as permissões do banco de dados"""
        print("Testando permissões do banco de dados...")
        cur = self.conn.cursor()
        
        try:
            cur.execute("""
                CREATE TEMPORARY TABLE test_permissions (
                    id SERIAL PRIMARY KEY,
                    data TEXT
                );
            """)
            cur.execute("INSERT INTO test_permissions (data) VALUES ('test_data');")
            self.conn.commit()
            print("Teste de permissões bem-sucedido!")
        except Exception as e:
            self.conn.rollback()
            print(f"Erro no teste de permissões: {e}")
            raise
        finally:
            cur.close()
    
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
    
    def _check_pgvector_extension(self):
        """Verifica se a extensão pgvector está disponível"""
        print("Verificando extensão pgvector...")
        cur = self.conn.cursor()
        
        try:
            # Verificar se a extensão está disponível para instalação
            cur.execute("SELECT 1 FROM pg_available_extensions WHERE name = 'vector';")
            extension_available = cur.fetchone() is not None
            
            if extension_available:
                try:
                    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                    self.conn.commit()
                    print("Extensão pgvector ativada com sucesso.")
                    return True
                except Exception as e:
                    self.conn.rollback()
                    print(f"Aviso: Não foi possível criar a extensão vector: {e}")
                    return False
            else:
                print("Extensão pgvector não está disponível no servidor.")
                print("Para suporte a embeddings vetoriais, instale a extensão pgvector:")
                print("  1. Baixe em: https://github.com/pgvector/pgvector")
                print("  2. Siga as instruções de instalação para seu sistema")
                return False
                
        except Exception as e:
            print(f"Erro ao verificar extensão pgvector: {e}")
            return False
        finally:
            cur.close()
    
    def _create_functions_ia_table(self): 
        """Cria a tabela aux.functions_ia"""
        print("Criando tabela aux.functions_ia...")
        cur = self.conn.cursor()
        
        try:
            # Verificar se a tabela já existe
            cur.execute("SELECT to_regclass('aux.functions_ia');")
            table_exists = cur.fetchone()[0] is not None
            
            if table_exists:
                print("Tabela aux.functions_ia já existe, pulando criação.")
                return
                
            # Tentar criar com schema aux
            try:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS aux.aux.functions_ia (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        prompt_template TEXT NOT NULL
                    );
                """)
                self.conn.commit()
                print("Tabela aux.aux.functions_ia criada com sucesso.")
            except Exception as e:
                self.conn.rollback()
                print(f"Erro ao criar tabela aux.aux.functions_ia: {e}")
                
                # Tentar sem o schema
                print("Tentando criar tabela aux.functions_ia sem schema...")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS aux.functions_ia (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        prompt_template TEXT NOT NULL
                    );
                """)
                self.conn.commit()
                print("Tabela aux.functions_ia criada sem schema.")
        except Exception as e:
            self.conn.rollback()
            print(f"Erro ao verificar/criar tabela aux.functions_ia: {e}")
        finally:
            cur.close()
    
    def _create_embeddings_table_with_vector(self):
        """Cria a tabela embeddings com suporte a vetores (pgvector)"""
        print("Criando tabela embeddings com suporte a pgvector...")
        cur = self.conn.cursor()
        
        try:
            # Tentar criar com schema aux
            try:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS aux.embeddings (
                        id SERIAL PRIMARY KEY,
                        text TEXT NOT NULL,
                        embedding vector(1536),
                        metadata JSONB
                    );
                """)
                self.conn.commit()
                print("Tabela aux.embeddings criada com sucesso (com vetores).")
            except Exception as e:
                self.conn.rollback()
                print(f"Erro ao criar tabela aux.embeddings: {e}")
                
                # Tentar sem o schema
                print("Tentando criar tabela embeddings sem schema...")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS embeddings (
                        id SERIAL PRIMARY KEY,
                        text TEXT NOT NULL,
                        embedding vector(1536),
                        metadata JSONB
                    );
                """)
                self.conn.commit()
                print("Tabela embeddings criada sem schema (com vetores).")
        except Exception as e:
            self.conn.rollback()
            print(f"Erro ao criar tabela embeddings: {e}")
        finally:
            cur.close()
    
    def _create_embeddings_table_without_vector(self):
        """Cria a tabela embeddings sem suporte a vetores (fallback)"""
        print("Criando tabela embeddings sem suporte a pgvector (modo alternativo)...")
        cur = self.conn.cursor()
        
        try:
            # Tentar criar com schema aux
            try:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS aux.embeddings (
                        id SERIAL PRIMARY KEY,
                        text TEXT NOT NULL,
                        embedding JSONB,
                        metadata JSONB
                    );
                """)
                self.conn.commit()
                print("Tabela aux.embeddings criada sem suporte a vetores.")
                print("AVISO: Os embeddings serão armazenados como JSON e não terão suporte a operações vetoriais eficientes.")
            except Exception as e:
                self.conn.rollback()
                print(f"Erro ao criar tabela aux.embeddings: {e}")
                
                # Tentar sem o schema
                print("Tentando criar tabela embeddings sem schema...")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS embeddings (
                        id SERIAL PRIMARY KEY,
                        text TEXT NOT NULL,
                        embedding vector(1536),
                        metadata JSONB
                    );
                """)
                self.conn.commit()
                print("Tabela embeddings criada sem schema (sem suporte a vetores).")
                print("AVISO: Os embeddings serão armazenados como JSON e não terão suporte a operações vetoriais eficientes.")
        except Exception as e:
            self.conn.rollback()
            print(f"Erro ao criar tabela embeddings: {e}")
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