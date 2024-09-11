from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/get_tables')
def get_tables():
    tables = ['table1', 'table2', 'table3']  # Um exemplo de retorno de tabelas
    return jsonify(tables)

if __name__ == '__main__':
    app.run(debug=True)
