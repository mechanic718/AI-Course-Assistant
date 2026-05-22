from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

API_KEY = "sk-DVBlunew3AML6wWLr2T7s09oVhJZpT851unNRgnT4OWITblk"

# ===== 通用请求函数（加稳定性）=====
def call_api(messages, max_tokens=500):
    url = "https://api.moonshot.cn/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json; charset=utf-8"
    }

    data = {
        "model": "moonshot-v1-8k",
        "messages": messages,
        "max_tokens": max_tokens
    }

    for _ in range(3):  # 重试3次
        try:
            import json

            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                timeout=60,
                verify=False
            )

            result = response.json()

            return result

        except Exception as e:
            last_error = str(e)

    return {"error": last_error}


# ===== 报告模板 =====
def chemistry_prompt(topic):
    return f"""
请生成一份化学实验报告：

实验题目：{topic}

【实验目的】
【实验原理】
【实验仪器与试剂】
【实验步骤】
【实验现象与数据】
【结果分析】
【注意事项】

请严格使用【标题】格式输出
"""

def cs_prompt(topic):
    return f"""
请生成一份计算机实验报告：

实验题目：{topic}

【实验目的】
【实验环境】
【实验原理】
【实验步骤】
【代码实现】
【运行结果】
【总结】

请严格使用【标题】格式输出
"""

def politics_prompt(topic):
    return f"""
请生成一份政治课程报告：

题目：{topic}

【背景分析】
【理论依据】
【现实意义】
【案例分析】
【总结】

请严格使用【标题】格式输出
"""


# ===== 聊天接口 =====
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return '', 200

    data_json = request.json
    user_input = data_json.get("message")
    subject = data_json.get("subject")
    mode = data_json.get("mode")

    if subject in ["化学", "政治"] and mode == "代码":
        return jsonify({"reply": "该学科暂不支持代码模式"})

    if mode == "学习":
        system_prompt = f"""
你是一个优秀的{subject}老师，请按结构讲解：

【知识点拆解】
【逐步讲解】
【示例】
【总结】
【选择题】
【解析】

请严格使用【标题】格式
"""

    elif mode == "出题":
        system_prompt = f"""
请根据{subject}知识：
- 出3道选择题
- 1道简答题
- 给详细解析
"""

    elif mode == "代码":
        system_prompt = """
你是编程助手：
- 解释代码
- 找bug
- 优化代码
"""
    else:
        system_prompt = "你是学习助手"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    result = call_api(messages)

    try:
        reply = result["choices"][0]["message"]["content"]
    except:
        reply = f"AI暂时不可用：{result}"

    return jsonify({"reply": reply})


# ===== 报告接口 =====
@app.route("/report", methods=["POST", "OPTIONS"])
def report():
    if request.method == "OPTIONS":
        return '', 200

    data_json = request.json
    topic = data_json.get("topic")
    subject = data_json.get("subject")

    if subject == "化学":
        prompt = chemistry_prompt(topic)
    elif subject == "计算机":
        prompt = cs_prompt(topic)
    elif subject == "政治":
        prompt = politics_prompt(topic)
    else:
        prompt = topic

    messages = [
        {"role": "system", "content": "你是专业报告生成助手"},
        {"role": "user", "content": prompt}
    ]

    result = call_api(messages, max_tokens=800)

    try:
        reply = result["choices"][0]["message"]["content"]
    except:
        reply = f"生成失败：{result}"

    return jsonify({"report": reply})


if __name__ == "__main__":
    app.run(debug=True)
