import os
import json
import subprocess
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not API_KEY:
    raise ValueError("请在 .env 文件中设置 DEEPSEEK_API_KEY")

client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com/v1")

def execute_python(code: str) -> str:
    dangerous = ["__import__", "exec", "eval", "open", "file", "input", "raw_input"]
    for kw in dangerous:
        if kw in code:
            return f"错误：禁止使用关键字 '{kw}'"
    try:
        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True,
            text=True,
            timeout=5,
            encoding="utf-8"
        )
        if result.stderr:
            return f"执行错误：{result.stderr}"
        return result.stdout.strip() or "执行成功（无输出）"
    except subprocess.TimeoutExpired:
        return "错误：代码执行超时（>5秒）"
    except Exception as e:
        return f"错误：{str(e)}"

def run_agent(user_input: str, max_steps=3):
    messages = [
        {"role": "system", "content": """你是一个能够使用工具的助手。如果用户的问题需要执行Python代码（如计算、数据处理），请输出以下JSON格式：
{"tool": "execute_python", "args": {"code": "要执行的代码"}}
否则直接输出回答。"""},
        {"role": "user", "content": user_input}
    ]
    for _ in range(max_steps):
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0
        )
        assistant_msg = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_msg})
        try:
            parsed = json.loads(assistant_msg)
            if parsed.get("tool") == "execute_python":
                code = parsed["args"]["code"]
                print(f"[执行] {code}")
                result = execute_python(code)
                messages.append({"role": "user", "content": f"工具返回：{result}\n请根据结果回答用户问题。"})
                continue
        except json.JSONDecodeError:
            return assistant_msg
    return messages[-1]["content"]

if __name__ == "__main__":
    print("简易Agent（输入exit退出）")
    while True:
        user = input("你: ")
        if user.lower() == "exit":
            break
        answer = run_agent(user)
        print(f"Agent: {answer}")