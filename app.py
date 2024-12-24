from flask import Flask, render_template, request, jsonify
import pandas as pd

# 初始化 Flask 应用
app = Flask(__name__)

# 加载 Excel 数据
df = pd.read_excel('schools.xlsx')

# 查询函数
def query_schools(rank):
    result = []

    # 判断位次范围，选择查询范围
    if rank < 1000:
        # 位次小于1000，正负200名范围
        min_rank = rank - 200
        max_rank = rank + 200
    elif 1000 <= rank < 10000:
        # 位次在1000到10000之间，负10%到正20%
        min_rank = int(rank * 0.9)
        max_rank = int(rank * 1.2)
    else:
        # 位次大于10000，正负5%
        min_rank = int(rank * 0.95)
        max_rank = int(rank * 1.05)

    # 查询符合位次范围的学校
    query_result = df[(df['最低位次'] >= min_rank) & (df['最低位次'] <= max_rank)]

    return query_result

@app.route('/')
def index():
    return render_template('index.html')  # 返回前端页面

@app.route('/query', methods=['GET'])
def query():
    # 获取前端传递的参数
    rank = request.args.get('rank', type=int)
    city = request.args.get('city', type=str)
    school_type = request.args.get('school_type', type=str)

    if not rank:
        return jsonify({"error": "位次不能为空"}), 400

    # 查询学校
    query_result = query_schools(rank)

    # 根据用户选择的城市和学校类型进行过滤（如果有的话）
    if city:
        query_result = query_result[query_result['城市'].str.contains(city, case=False, na=False)]
    if school_type:
        query_result = query_result[query_result['学校类型'].str.contains(school_type, case=False, na=False)]

    # 转换为字典格式，方便传递给前端
    result = query_result[['学校名称', '城市', '专业名称', '最低位次', '学校类型']].to_dict(orient='records')

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
