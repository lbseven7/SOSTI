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

# Função para conectar ao banco de dados
def connect_db():
    try:
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_name
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"Erro ao conectar ao banco de dados: {err}")
        return None

# Função para obter dados da tabela com filtros
def get_data(table_name, status_filter='ATIVO'):
    connection = connect_db()
    if connection is None:
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro
    
    cursor = connection.cursor()
    query = f"SELECT * FROM {table_name} WHERE status = %s"
    cursor.execute(query, (status_filter,))
    
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    df = pd.DataFrame(rows, columns=columns)
    cursor.close()
    connection.close()
    return df

# Função para inserir dados na tabela
def insert_data(table_name, data):
    connection = connect_db()
    if connection is None:
        return
    
    cursor = connection.cursor()
    placeholders = ', '.join(['%s'] * len(data))
    columns = ', '.join(data.keys())
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    
    cursor.execute(sql, list(data.values()))
    connection.commit()
    st.success("Dados inseridos com sucesso!")
    cursor.close()
    connection.close()

# Função para atualizar dados
def update_data(table_name, id_column, id_value, updated_data):
    connection = connect_db()
    if connection is None:
        return
    
    cursor = connection.cursor()
    set_clause = ", ".join([f"{col} = %s" for col in updated_data.keys()])
    sql = f"UPDATE {table_name} SET {set_clause} WHERE {id_column} = %s"
    
    cursor.execute(sql, list(updated_data.values()) + [id_value])
    connection.commit()
    st.success("Dados atualizados com sucesso!")
    cursor.close()
    connection.close()

# Função para marcar registro como inativo (soft delete)
def soft_delete_data(table_name, id_column, id_value):
    connection = connect_db()
    if connection is None:
        return
    
    cursor = connection.cursor()
    sql = f"UPDATE {table_name} SET status = 'INATIVO' WHERE {id_column} = %s"
    cursor.execute(sql, (id_value,))
    connection.commit()
    st.success("Registro marcado como INATIVO!")
    cursor.close()
    connection.close()

# Função para reativar registro
def reactivate_data(table_name, id_column, id_value):
    connection = connect_db()
    if connection is None:
        return
    
    cursor = connection.cursor()
    sql = f"UPDATE {table_name} SET status = 'ATIVO' WHERE {id_column} = %s"
    cursor.execute(sql, (id_value,))
    connection.commit()
    st.success("Registro reativado com sucesso!")
    cursor.close()
    connection.close()

# Função para exibir a interface de cada tabela
def show_table_interface(table_name):
    st.title(f'Gerenciamento da Tabela {table_name}')
    
    # Exibição dos dados ATIVOS com filtros
    st.subheader(f'Dados ATIVOS da Tabela {table_name}')
    df_ativos = get_data(table_name, status_filter='ATIVO')
    
    if not df_ativos.empty:
        st.dataframe(df_ativos)
    else:
        st.error('Nenhum dado ATIVO encontrado.')
    
    # Exibição dos dados INATIVOS (exclusões)
    st.subheader(f'Dados INATIVOS da Tabela {table_name}')
    df_inativos = get_data(table_name, status_filter='INATIVO')
    
    if not df_inativos.empty:
        st.dataframe(df_inativos)
    else:
        st.info('Nenhum dado INATIVO encontrado.')

    # Botões de Inserir, Atualizar e Excluir (soft delete)
    st.sidebar.subheader(f'Inserir dados em {table_name}')
    
    columns = df_ativos.columns if not df_ativos.empty else []
    input_data = {col: st.sidebar.text_input(f'Insira o valor para {col}') for col in columns if col != 'status'}
    
    if st.sidebar.button(f'Inserir em {table_name}'):
        if all(input_data.values()):
            insert_data(table_name, input_data)
        else:
            st.sidebar.error("Por favor, preencha todos os campos.")

    st.sidebar.subheader(f'Atualizar dados em {table_name}')
    
    if not df_ativos.empty:
        id_column = st.sidebar.selectbox('Coluna de ID para atualizar', df_ativos.columns)
        id_value = st.sidebar.selectbox(f'Selecione o ID para atualizar', df_ativos[id_column])
        updated_data = {col: st.sidebar.text_input(f'Atualize o valor para {col}', df_ativos[df_ativos[id_column] == id_value][col].values[0]) for col in columns if col != 'status'}
        
        if st.sidebar.button(f'Atualizar em {table_name}'):
            update_data(table_name, id_column, id_value, updated_data)
    
    st.sidebar.subheader(f'Excluir dados em {table_name} (Marcar como INATIVO)')
    
    if not df_ativos.empty:
        id_value = st.sidebar.selectbox(f'Selecione o ID para marcar como INATIVO', df_ativos[id_column])
        
        if st.sidebar.button(f'Marcar como INATIVO em {table_name}'):
            soft_delete_data(table_name, id_column, id_value)

    # Função para reativar dados INATIVOS
    st.sidebar.subheader(f'Reativar dados INATIVOS em {table_name}')
    
    if not df_inativos.empty:
        id_value = st.sidebar.selectbox(f'Selecione o ID para reativar', df_inativos[id_column])
        
        if st.sidebar.button(f'Reativar em {table_name}'):
            reactivate_data(table_name, id_column, id_value)

# Menu lateral para escolher a tabela
st.sidebar.title("Menu de Tabelas")

# Tabelas disponíveis
tables = ["contador", "demanda", "departamento", "equipamento", "escola", "fornecedor", "gestor", "secretaria", "suprimento", "telefone"]

selected_table = st.sidebar.selectbox("Escolha a tabela para gerenciar", tables)

# Mostrar a interface da tabela selecionada
if selected_table:
    show_table_interface(selected_table)
