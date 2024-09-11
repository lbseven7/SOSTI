from flask import Flask, request, jsonify
import mysql.connector
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configura as variáveis para conexão
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')

# Função para obter conexão com o banco de dados
def get_db_connection():
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database=db_name
    )

@app.route('/get_tables', methods=['GET'])
def get_tables():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        return jsonify(tables)
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/get_data/<table_name>', methods=['GET'])
def get_data(table_name):
    filters = request.args.to_dict()
    try:
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
        data = [dict(zip(columns, row)) for row in rows]
        return jsonify(data)
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/insert_data/<table_name>', methods=['POST'])
def insert_data(table_name):
    data = request.json
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        placeholders = ', '.join(['%s'] * len(data))
        columns = ', '.join(data.keys())
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, list(data.values()))
        connection.commit()
        return jsonify({'message': 'Dados inseridos com sucesso!'}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/delete_data/<table_name>', methods=['DELETE'])
def delete_data(table_name):
    id_column = request.args.get('id_column')
    id_value = request.args.get('id_value')
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        sql = f"DELETE FROM {table_name} WHERE {id_column} = %s"
        cursor.execute(sql, (id_value,))
        connection.commit()
        return jsonify({'message': 'Dados excluídos com sucesso!'}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
