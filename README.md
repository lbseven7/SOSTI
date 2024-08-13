# SOSTI
Sistema de Organização do Setor de TI

Importações e Configuração:

import os, import mysql.connector, from dotenv import load_dotenv, import streamlit as st, import pandas as pd
Carrega variáveis de ambiente do arquivo .env e importa bibliotecas necessárias.
Função get_data:

Conexão com o Banco de Dados: Estabelece uma conexão com o banco de dados MySQL usando credenciais definidas no .env.
Consulta SQL: Executa uma query para selecionar todos os dados da tabela escola.
Criação do DataFrame: Converte os dados recuperados em um DataFrame do Pandas.
Configuração do Aplicativo Streamlit:

st.title('Dados da Tabela Escola'): Define o título da página.
st.write(data): Exibe os dados no formato de tabela interativa.

Executar o Aplicativo
Para iniciar o aplicativo, execute o seguinte comando no terminal:

bash
Copiar código
streamlit run app.py
O aplicativo será acessível no navegador padrão e exibirá os dados da tabela escola.