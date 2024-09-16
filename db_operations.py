import pandas as pd
from db_connection import connect_db
import streamlit as st

def get_data(table_name, filters=None, include_inactive=False):
    connection = connect_db()
    if connection is None:
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro
    
    cursor = connection.cursor()
    query = f"SELECT * FROM {table_name}"

    # Incluir status "INATIVO" ou não
    if not include_inactive:
        query += " WHERE status = 'ATIVO'"

    if filters:
        filter_conditions = " AND ".join([f"{col} LIKE %s" for col in filters.keys()])
        query += f" AND {filter_conditions}"
        cursor.execute(query, [f"%{val}%" for val in filters.values()])
    else:
        cursor.execute(query)
    
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    df = pd.DataFrame(rows, columns=columns)
    cursor.close()
    connection.close()
    return df

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

def activate_data(table_name, id_column, id_value):
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
