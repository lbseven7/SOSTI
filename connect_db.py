import os
import mysql.connector
from dotenv import load_dotenv
import streamlit as st
import pandas as pd

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configura as variáveis para conexão
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')

# Função para obter dados do banco de dados
def get_data():
    try:
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_name
        )

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM escola")
            
            # Recuperando os nomes das colunas
            colunas = [desc[0] for desc in cursor.description]
            
            # Recuperando todos os registros retornados pela query
            rows = cursor.fetchall()

            # Criando um DataFrame com os dados
            df = pd.DataFrame(rows, columns=colunas)
            
            return df

    except mysql.connector.Error as err:
        st.error(f"Erro ao conectar ao banco de dados: {err}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Configuração do aplicativo Streamlit
st.title('Dados da Tabela Escola')

# Obtendo e exibindo os dados
data = get_data()
if data is not None:
    st.write(data)
