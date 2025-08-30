import os
from openai import OpenAI

# 获取API密钥，如果环境变量不存在则使用默认值或提示错误
api_key = "sk-20b4e293dc524e6ca819d9b37e2cadd2"
if not api_key:
    print("错误：未设置 DASHSCOPE_API_KEY 环境变量")
    print("请设置环境变量或直接在代码中配置API密钥")

    exit(1)

client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def get_response(messages):
    try:
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=messages
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"API调用失败: {e}")
        return f"错误: {str(e)}"

# 初始化 messages
messages = []

# 第 1 轮
messages.append({"role": "user", "content": "推荐一部关于太空探索的科幻电影。"})
print("第1轮")
print(f"用户：{messages[0]['content']}")
assistant_output = get_response(messages)
messages.append({"role": "assistant", "content": assistant_output})
print(f"模型：{assistant_output}\n")

# 第 2 轮
messages.append({"role": "user", "content": "这部电影的导演是谁？"})
print("第2轮")
print(f"用户：{messages[-1]['content']}")
assistant_output = get_response(messages)
messages.append({"role": "assistant", "content": assistant_output})
print(f"模型：{assistant_output}\n")