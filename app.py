from flask import Flask, request, jsonify, send_from_directory, render_template
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 提供静态页面
@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')  # 假设你的 index.html 在 static 目录下

# 查询学校的函数
def query_schools(rank, city=None, school_type=None):
    conn = sqlite3.connect('schools.db')
    cursor = conn.cursor()

    # 构建SQL查询
    query = "SELECT * FROM schools WHERE 1=1"
    params = []

    # 添加位次条件
    if rank < 1000:
        query += " AND `最低位次` BETWEEN ? - 200 AND ? + 200"
        params.extend([rank, rank])
    elif 1000 <= rank <= 10000:
        query += " AND `最低位次` BETWEEN ? * 0.9 AND ? * 1.2"
        params.extend([rank, rank])
    else:
        query += " AND `最低位次` BETWEEN ? * 0.95 AND ? * 1.05"
        params.extend([rank, rank])

    # 添加城市条件
    if city:
        query += " AND `城市` = ?"
        params.append(city)

    # 添加学校类型条件
    if school_type:
        query += " AND `学校类型` = ?"
        params.append(school_type)

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return results

# 搜索学校的API
@app.route('/search', methods=['GET'])
def search():
    try:
        rank = int(request.args.get('rank'))
        city = request.args.get('city')
        school_type = request.args.get('school_type')

        results = query_schools(rank, city, school_type)

        if not results:
            return jsonify({"message": "No data found"}), 404

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 获取表结构的API
@app.route('/table_info', methods=['GET'])
def table_info():
    try:
        conn = sqlite3.connect('schools.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(schools)")
        columns = cursor.fetchall()
        conn.close()

        # 格式化返回的列信息
        column_info = [{"column_name": column[1], "data_type": column[2]} for column in columns]
        return jsonify(column_info)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 错误处理
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
