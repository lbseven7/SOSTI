import streamlit as st
import pandas as pd
from db_operations import get_data, insert_data, update_data, soft_delete_data, activate_data
from config import tables

# Função para exibir a interface de cada tabela
def show_table_interface(table_name):
    st.title(f'Gerenciamento da Tabela {table_name}')
    
    # Exibição dos dados com filtros
    st.subheader(f'Dados da Tabela {table_name}')
    filters = {}
    df = get_data(table_name, filters)
    
    if not df.empty:
        st.dataframe(df)
    else:
        st.error('Nenhum dado encontrado.')
    
    # Botões de Inserir, Atualizar e Excluir (soft delete)
    st.sidebar.subheader(f'Inserir dados em {table_name}')
    
    columns = df.columns if not df.empty else []
    input_data = {col: st.sidebar.text_input(f'Insira o valor para {col}') for col in columns if col != 'status'}
    
    if st.sidebar.button(f'Inserir em {table_name}'):
        if all(input_data.values()):
            insert_data(table_name, input_data)
        else:
            st.sidebar.error("Por favor, preencha todos os campos.")

    st.sidebar.subheader(f'Atualizar dados em {table_name}')
    
    if not df.empty:
        id_column = st.sidebar.selectbox('Coluna de ID para atualizar', df.columns)
        id_value = st.sidebar.selectbox(f'Selecione o ID para atualizar', df[id_column])
        updated_data = {col: st.sidebar.text_input(f'Atualize o valor para {col}', df[df[id_column] == id_value][col].values[0]) for col in columns if col != 'status'}
        
        if st.sidebar.button(f'Atualizar em {table_name}'):
            update_data(table_name, id_column, id_value, updated_data)
    
    st.sidebar.subheader(f'Excluir dados em {table_name} (Marcar como INATIVO)')
    
    if not df.empty:
        id_value = st.sidebar.selectbox(f'Selecione o ID para marcar como INATIVO', df[id_column])
        
        if st.sidebar.button(f'Marcar como INATIVO em {table_name}'):
            soft_delete_data(table_name, id_column, id_value)

    st.sidebar.subheader(f'Reativar dados INATIVOS em {table_name}')
    
    # Exibir apenas os dados que estão como "INATIVO" para reativação
    df_inativos = get_data(table_name, filters, include_inactive=True)
    if not df_inativos.empty:
        inativo_ids = df_inativos[df_inativos['status'] == 'INATIVO'][id_column]
        if not inativo_ids.empty:
            id_value_inativo = st.sidebar.selectbox(f'Selecione o ID INATIVO para reativar', inativo_ids)
            if st.sidebar.button(f'Reativar em {table_name}'):
                activate_data(table_name, id_column, id_value_inativo)
        else:
            st.sidebar.write("Não há registros INATIVOS para reativar.")

# Menu lateral para escolher a tabela
st.sidebar.title("Menu de Tabelas")

# Tabelas disponíveis
selected_table = st.sidebar.selectbox("Escolha a tabela para gerenciar", tables)

# Mostrar a interface da tabela selecionada
if selected_table:
    show_table_interface(selected_table)
