import os
import mysql.connector
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configura as variáveis para conexão
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')

# Conectando ao banco de dados
try:
    connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database=db_name
    )

    if connection.is_connected():
        print("Conexão com o banco de dados foi bem-sucedida")
        # Aqui você pode executar suas queries

except mysql.connector.Error as err:
    print(f"Erro ao conectar ao banco de dados: {err}")

finally:
    if connection.is_connected():
        connection.close()
        print("Conexão encerrada")
