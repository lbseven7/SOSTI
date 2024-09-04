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

def get_tables():
    """Retorna uma lista de tabelas no banco de dados."""
    try:
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_name
        )
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        return tables
    except mysql.connector.Error as err:
        st.error(f"Erro ao conectar ao banco de dados: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_data(table_name, filter_column=None, filter_value=None):
    """Obtém dados da tabela especificada e aplica um filtro se fornecido."""
    try:
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_name
        )
        cursor = connection.cursor()
        query = f"SELECT * FROM {table_name}"
        if filter_column and filter_value:
            query += f" WHERE {filter_column} = %s"
            cursor.execute(query, (filter_value,))
        else:
            cursor.execute(query)
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=columns)
        return df
    except mysql.connector.Error as err:
        st.error(f"Erro ao conectar ao banco de dados: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Configuração do aplicativo Streamlit
st.title('SOSTI - Visualização de Dados ')

# Seleção da tabela
tables = get_tables()
selected_table = st.selectbox('Escolha a tabela', tables)

# Exibição de dados da tabela selecionada
if selected_table:
    # Filtros opcionais
    st.sidebar.header('Filtros')
    filter_column = st.sidebar.selectbox('Escolha a coluna para filtro', options=[None] + [col for col in pd.DataFrame(get_data(selected_table)).columns])
    filter_value = st.sidebar.text_input('Valor do filtro', '')

    if filter_column and filter_value:
        data = get_data(selected_table, filter_column, filter_value)
    else:
        data = get_data(selected_table)
    
    st.write(data)
