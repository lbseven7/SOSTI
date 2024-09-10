import os
import mysql.connector
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from io import BytesIO

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configura as variáveis para conexão
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')

# Função para obter as tabelas
def get_tables():
    """Retorna uma lista de tabelas no banco de dados."""
    connection = None
    cursor = None
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
        return []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Função para obter dados de uma tabela com filtros
def get_data(table_name, filters=None):
    """Obtém dados da tabela especificada e aplica filtros se fornecido."""
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_name
        )
        cursor = connection.cursor()
        query = f"SELECT * FROM {table_name}"
        if filters:
            filter_conditions = " AND ".join([f"{col} LIKE %s" for col in filters.keys()])
            query += f" WHERE {filter_conditions}"
            cursor.execute(query, [f"%{val}%" for val in filters.values()])
        else:
            cursor.execute(query)

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=columns)
        return df
    except mysql.connector.Error as err:
        st.error(f"Erro ao conectar ao banco de dados: {err}")
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Função para inserir dados
def insert_data(table_name, data):
    """Insere dados na tabela especificada."""
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_name
        )
        cursor = connection.cursor()

        # Montar o comando SQL para inserir os dados
        placeholders = ', '.join(['%s'] * len(data))
        columns = ', '.join(data.keys())
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        cursor.execute(sql, list(data.values()))
        connection.commit()
        st.success("Dados inseridos com sucesso!")
    except mysql.connector.Error as err:
        st.error(f"Erro ao inserir dados: {err}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Função para excluir dados
def delete_data(table_name, id_column, id_value):
    """Exclui um dado da tabela especificada com base no ID."""
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_name
        )
        cursor = connection.cursor()
        sql = f"DELETE FROM {table_name} WHERE {id_column} = %s"
        cursor.execute(sql, (id_value,))
        connection.commit()
        st.success("Dados excluídos com sucesso!")
    except mysql.connector.Error as err:
        st.error(f"Erro ao excluir dados: {err}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Função para gerar relatórios e salvar como PDF
def generate_pdf(df):
    """Gera um relatório em PDF a partir do DataFrame."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, "Relatório de Dados")

    # Definir largura da coluna
    col_width = width / len(df.columns)
    y_position = height - 100

    # Cabeçalho da tabela
    c.setFont("Helvetica-Bold", 12)
    for i, column in enumerate(df.columns):
        c.drawString(100 + i * col_width, y_position, column)
    
    y_position -= 20

    # Dados da tabela
    c.setFont("Helvetica", 10)
    for index, row in df.iterrows():
        for i, value in enumerate(row):
            c.drawString(100 + i * col_width, y_position, str(value))
        y_position -= 20
        if y_position < 100:
            c.showPage()
            c.setFont("Helvetica-Bold", 12)
            for i, column in enumerate(df.columns):
                c.drawString(100 + i * col_width, height - 50, column)
            y_position = height - 100

    c.save()
    buffer.seek(0)
    return buffer

# Configuração do aplicativo Streamlit
st.title('SOSTI')

# Seleção da tabela
tables = get_tables()
if tables:
    selected_table = st.selectbox('Escolha a tabela para visualizar, inserir ou excluir dados', tables)

    if selected_table:
        st.sidebar.header('Opções de Inserção e Exclusão')

        # Inserção de dados
        st.subheader(f'Inserir dados na tabela {selected_table}')
        columns = [col for col in get_data(selected_table).columns]
        input_data = {}
        for column in columns:
            input_data[column] = st.text_input(f'Insira o valor para {column}')

        if st.button('Inserir Dados'):
            insert_data(selected_table, input_data)

        # Exclusão de dados
        st.sidebar.subheader('Excluir dados')
        df = get_data(selected_table)
        if not df.empty:
            id_column = st.sidebar.selectbox('Selecione a coluna de ID', df.columns)
            ids = df[id_column].tolist()
            selected_id = st.sidebar.selectbox(f'Selecione o ID para exclusão', ids)
            if st.sidebar.button('Excluir Dados'):
                delete_data(selected_table, id_column, selected_id)

        # Filtros de Busca
        st.sidebar.subheader('Filtros de Busca')
        filters = {}
        for column in columns:
            filter_value = st.sidebar.text_input(f'Valor para {column}', key=column)
            if filter_value:
                filters[column] = filter_value

        # Obter dados com ou sem filtros
        df = get_data(selected_table, filters)

        # Exibir e gerar relatório
        if not df.empty:
            st.subheader('Relatório de Dados')
            st.dataframe(df)

            # Botão para gerar PDF
            if st.button('Gerar PDF do Relatório'):
                pdf_buffer = generate_pdf(df)
                st.download_button(
                    label="Baixar PDF",
                    data=pdf_buffer,
                    file_name="relatorio.pdf",
                    mime="application/pdf"
                )
        else:
            st.error('Nenhum dado encontrado com o filtro aplicado.')

else:
    st.error('Nenhuma tabela encontrada.')
