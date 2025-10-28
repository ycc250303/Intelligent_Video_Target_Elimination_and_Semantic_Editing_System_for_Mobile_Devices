import json
import os
import sys
import dashscope
from dashscope import MultiModalConversation

# 添加父目录到Python路径，以便导入config模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import QWEN_API_KEY, QWEN_BASE_GENERATE_MEDIA_URL

# 以下为北京地域url，若使用新加坡地域的模型，需将url替换为：https://dashscope-intl.aliyuncs.com/api/v1
dashscope.base_http_api_url = QWEN_BASE_GENERATE_MEDIA_URL

messages = [
    {
        "role": "user",
        "content": [
            {"text": "一朵玉兰花，背景为纯白色"}
        ]
    }
]


response = MultiModalConversation.call(
    api_key=QWEN_API_KEY,
    model="qwen-image-plus",
    messages=messages,
    result_format='message',
    stream=False,
    watermark=True,
    prompt_extend=True,
    negative_prompt='',
    size='1328*1328'
)

if response.status_code == 200:
    print(json.dumps(response, ensure_ascii=False))
else:
    print(f"HTTP返回码：{response.status_code}")
    print(f"错误码：{response.code}")
    print(f"错误信息：{response.message}")
    print("请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code")