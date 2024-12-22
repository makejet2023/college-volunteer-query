from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def serve_index():
    return send_from_directory('', 'index.html')

def query_schools(rank, city=None, school_type=None):
    conn = sqlite3.connect('schools.db')
    cursor = conn.cursor()

    # 构建SQL查询
    query = "SELECT * FROM schools WHERE 1=1"
    params = []

    # 添加位次条件
    if rank < 1000:
        query += " AND ? - 200 <= 最低位次 AND 最低位次 <= ? + 200"
        params.extend([rank, rank])
    elif 1000 <= rank <= 10000:
        query += " AND ? * 0.9 <= 最低位次 AND 最低位次 <= ? * 1.2"
        params.extend([rank, rank])
    else:
        query += " AND ? * 0.95 <= 最低位次 AND 最低位次 <= ? * 1.05"
        params.extend([rank, rank])

    # 添加城市条件
    if city:
        query += " AND 城市 = ?"
        params.append(city)

    # 添加学校类型条件
    if school_type:
        query += " AND 学校类型 = ?"
        params.append(school_type)

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return results

@app.route('/search', methods=['GET'])
def search():
    rank = int(request.args.get('rank'))
    city = request.args.get('city')
    school_type = request.args.get('school_type')

    results = query_schools(rank, city, school_type)
    return jsonify(results)

@app.route('/table_info', methods=['GET'])
def table_info():
    conn = sqlite3.connect('schools.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(schools)")
    columns = cursor.fetchall()
    conn.close()
    return jsonify(columns)

if __name__ == '__main__':
    app.run(debug=True)

import sqlite3

# 连接到SQLite数据库
conn = sqlite3.connect('schools.db')
cursor = conn.cursor()

# 查询表结构
cursor.execute("PRAGMA table_info(schools)")
columns = cursor.fetchall()

# 打印表结构
for column in columns:
    print(column)

# 关闭数据库连接
conn.close() 