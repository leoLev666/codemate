import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not API_KEY:
    print("错误：未找到 DEEPSEEK_API_KEY，请在 .env 文件中设置或设置环境变量")
    sys.exit(1)

client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com/v1")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "你好！请介绍一下你自己。"}
    ],
    stream=False
)

print(response.choices[0].message.content)