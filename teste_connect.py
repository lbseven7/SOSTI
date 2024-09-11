import mysql.connector
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')

try:
    connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database=db_name
    )
    print("Conexão bem-sucedida!")
except mysql.connector.Error as err:
    print(f"Erro ao conectar ao banco de dados: {err}")
finally:
    if connection.is_connected():
        connection.close()
        print("Conexão fechada.")
