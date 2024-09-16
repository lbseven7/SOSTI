import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração de conexão ao banco
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')

# Lista de tabelas disponíveis
tables = ["Contador", "Demanda", "Departamento", "Equipamento", "Escola", "Fornecedor", "Gestor", "Secretaria", "Suprimento", "telefone"]
