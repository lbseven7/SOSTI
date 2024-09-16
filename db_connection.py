import mysql.connector
import streamlit as st
from config import db_host, db_user, db_pass, db_name

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
