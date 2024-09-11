from flask import Flask, jsonify, request
import mysql.connector
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Carrega as variáveis de ambiente
load_dotenv()

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')

def get_db_connection():
    """Função para conectar ao banco de dados."""
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database=db_name
    )

@app.route('/get_tables', methods=['GET'])
def get_tables():
    """Rota para obter a lista de tabelas no banco de dados."""
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    cursor.close()
    connection.close()
    return jsonify(tables)

@app.route('/get_data/<table_name>', methods=['GET'])
def get_data(table_name):
    """Rota para obter dados de uma tabela específica."""
    filters = request.args
    connection = get_db_connection()
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
    cursor.close()
    connection.close()
    
    return jsonify({'columns': columns, 'rows': rows})

@app.route('/insert_data/<table_name>', methods=['POST'])
def insert_data(table_name):
    """Rota para inserir dados em uma tabela."""
    data = request.json
    connection = get_db_connection()
    cursor = connection.cursor()
    
    placeholders = ', '.join(['%s'] * len(data))
    columns = ', '.join(data.keys())
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    
    cursor.execute(sql, list(data.values()))
    connection.commit()
    cursor.close()
    connection.close()
    
    return jsonify({'message': 'Dados inseridos com sucesso!'})

if __name__ == '__main__':
    app.run(debug=True)
