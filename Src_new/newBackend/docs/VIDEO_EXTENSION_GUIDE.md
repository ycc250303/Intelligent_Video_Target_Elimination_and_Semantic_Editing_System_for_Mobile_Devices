# 📹 视频延展功能使用指南

## 🎯 功能概述

视频延展功能可以将短视频延长到 **5 秒**，基于输入的首段视频和提示词生成延续性内容。

> **注意**：延长后的视频总时长固定为 **5 秒**（这是最终输出视频的完整时长，而非在原视频基础上延长 5 秒）

## 🔑 核心参数

| 参数             | 类型   | 必填 | 说明                                                                                                                                                   |
| ---------------- | ------ | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `prompt`         | string | ✅ 是 | 提示词，描述生成视频中期望包含的元素和视觉特点<br>- 支持中英文<br>- 长度不超过 800 字符                                                                |
| `first_clip_url` | string | ✅ 是 | 首段视频的 URL 地址<br>- **必须是公网可访问的 HTTP/HTTPS URL**<br>- 视频格式：MP4<br>- 视频帧率：≥ 16 FPS<br>- 视频大小：≤ 50 MB<br>- 视频长度：≤ 3 秒 |
| `prompt_extend`  | bool   | ❌ 否 | 是否开启 prompt 智能改写<br>- `False`（默认，推荐）：关闭智能改写<br>- `True`：开启智能改写（会增加耗时）                                              |

## 📝 使用方法

### 方法 1：Python API 调用

```python
from VideoEditor.qwen_editor import QwenVideoEditor
from config import QWEN_API_KEY

# 初始化编辑器
editor = QwenVideoEditor(api_key=QWEN_API_KEY, base_dir="Results")

# 调用视频延展功能
result = editor.extend_video(
    prompt="一只戴着墨镜的狗在街道上滑滑板，3D卡通。",
    first_clip_url="http://wanx.alicdn.com/material/20250318/video_extension_1.mp4",
    prompt_extend=False  # 是否开启智能改写
)

if result:
    print(f"✅ 视频延展成功，生成文件: {result}")
else:
    print("❌ 视频延展失败")
```

### 方法 2：通过 JSON 配置

```json
{
  "operations": {
    "operation": "extend_video",
    "params": {
      "prompt": "一只戴着墨镜的狗在街道上滑滑板，3D卡通。",
      "first_clip_url": "http://wanx.alicdn.com/material/20250318/video_extension_1.mp4",
      "prompt_extend": false
    },
    "editor": "qwen"
  }
}
```

## ⚠️ 重要限制

### 1. 视频必须是公网 URL

视频延展功能要求 `first_clip_url` **必须是公网可访问的 HTTP/HTTPS URL**。

❌ **不支持**：
```python
# 本地文件路径（会报错）
first_clip_url = "C:/videos/my_video.mp4"
first_clip_url = "../videos/test.mp4"
```

✅ **支持**：
```python
# 公网 HTTP/HTTPS URL
first_clip_url = "http://example.com/video.mp4"
first_clip_url = "https://cdn.example.com/videos/sample.mp4"
```

### 2. 视频格式要求

| 要求项   | 限制                    |
| -------- | ----------------------- |
| 视频格式 | MP4                     |
| 视频帧率 | ≥ 16 FPS                |
| 视频大小 | ≤ 50 MB                 |
| 视频长度 | ≤ 3 秒（超过取前 3 秒） |
| 输出时长 | 固定 5 秒               |

### 3. 分辨率处理

- 输入视频分辨率 **≤ 720P**：输出保留原始分辨率
- 输入视频分辨率 **> 720P**：按比例缩放至不超过 720P（保持宽高比）

## 🌐 如何获取公网视频 URL

由于 API 要求视频必须是公网可访问的 URL，以下是几种获取方式：

### 方案 1：使用云存储服务（推荐）

#### 阿里云 OSS
```python
# 1. 上传视频到 OSS
# 2. 设置公共读权限或生成临时访问 URL
# 3. 获取公网 URL
first_clip_url = "https://your-bucket.oss-cn-beijing.aliyuncs.com/video.mp4"
```

#### 腾讯云 COS
```python
# 1. 上传视频到 COS
# 2. 设置公共读权限或生成预签名 URL
# 3. 获取公网 URL
first_clip_url = "https://your-bucket-12345.cos.ap-beijing.myqcloud.com/video.mp4"
```

#### 七牛云 Kodo
```python
# 1. 上传视频到七牛云
# 2. 获取公网访问 URL
first_clip_url = "https://your-domain.qiniucdn.com/video.mp4"
```

### 方案 2：使用临时文件上传服务

参考阿里云文档：[上传文件获取临时URL](https://help.aliyun.com/zh/dashscope/)

### 方案 3：自建文件服务器

如果您有自己的服务器，可以：
1. 将视频上传到服务器的公开目录
2. 确保服务器有公网 IP 和域名
3. 使用 HTTP/HTTPS 访问该视频

## 💡 使用场景

### 场景 1：延长短视频片段
```python
# 将 2 秒的视频片段延展到 5 秒
result = editor.extend_video(
    prompt="继续展现海浪拍打沙滩的场景，夕阳西下",
    first_clip_url="https://cdn.example.com/beach_2s.mp4",
    prompt_extend=False
)
```

### 场景 2：生成视频延续内容
```python
# 基于开头片段，生成后续内容
result = editor.extend_video(
    prompt="小狗继续滑滑板，加速前进，最后完成一个完美的停止动作",
    first_clip_url="https://cdn.example.com/dog_skateboard.mp4",
    prompt_extend=True  # 开启智能改写
)
```

### 场景 3：扩展动画片段
```python
# 延展 3D 动画片段
result = editor.extend_video(
    prompt="机器人继续行走在未来城市街道，背景有飞行汽车经过",
    first_clip_url="https://cdn.example.com/robot_walk.mp4",
    prompt_extend=False
)
```

## 🎨 Prompt 编写技巧

### ✅ 好的 Prompt

```python
# 详细、具体、与输入视频一致
prompt = "一只戴着墨镜的橘猫继续在公园的人行道上滑滑板，保持平衡，背景有绿色草坪和蓝天白云"
```

### ❌ 不好的 Prompt

```python
# 太简短、模糊
prompt = "滑滑板"

# 与输入视频内容不一致
prompt = "猫咪在游泳"  # 但输入视频是狗滑滑板
```

### 💡 建议

1. **保持一致性**：Prompt 描述应与输入视频的内容、风格、色调保持一致
2. **具体描述**：包含主体、动作、场景、氛围等元素
3. **关闭智能扩写**：当 Prompt 已经足够详细时，建议设置 `prompt_extend=False`（推荐）
4. **长度适中**：不超过 800 字符，但也不要过于简短

## 🔧 错误处理

### 常见错误及解决方案

| 错误信息                               | 原因               | 解决方案                                     |
| -------------------------------------- | ------------------ | -------------------------------------------- |
| "first_clip_url 是本地文件路径"        | 传入了本地文件路径 | 将视频上传到云存储，使用公网 URL             |
| "first_clip_url 必须是 HTTP/HTTPS URL" | URL 格式不正确     | 检查 URL 是否以 `http://` 或 `https://` 开头 |
| "prompt 参数不能为空"                  | 未提供 prompt      | 提供有效的提示词                             |
| "视频大小超过限制"                     | 视频文件 > 50 MB   | 压缩视频或截取前 3 秒                        |
| "视频格式不支持"                       | 不是 MP4 格式      | 转换为 MP4 格式                              |

## 📊 性能说明

- **处理时间**：通常需要 30-90 秒（取决于服务器负载）
- **输出时长**：固定 5 秒
- **输出格式**：MP4
- **智能改写**：开启 `prompt_extend=True` 会增加 5-10 秒处理时间

## 🔗 相关链接

- [Qwen 视频生成 API 文档](https://help.aliyun.com/zh/dashscope/)
- [视频延展功能详细说明](https://help.aliyun.com/zh/dashscope/developer-reference/video-generation-api)
- [阿里云 OSS 文档](https://help.aliyun.com/product/31815.html)
- [Prompt 编写指南](https://help.aliyun.com/zh/dashscope/prompt-engineering)

## ⚙️ 技术参数

```python
# API 调用参数（内部实现）
{
    "model": "wanx2.1-vace-plus",
    "input": {
        "function": "video_extension",
        "prompt": "提示词",
        "first_clip_url": "视频URL"
    },
    "parameters": {
        "duration": 5,              # 固定为 5 秒
        "prompt_extend": False,     # 是否智能改写
        "watermark": False          # 不添加水印
    }
}
```

## ❓ 常见问题

### Q1：能否延展超过 5 秒？
**A**：不能。当前版本固定输出 5 秒视频。

### Q2：输入视频长度有什么要求？
**A**：输入视频长度 ≤ 3 秒，超过部分会自动截取前 3 秒。

### Q3：为什么必须使用公网 URL？
**A**：这是 Qwen API 的技术限制，服务器需要能够访问视频文件。

### Q4：可以使用本地临时服务器吗？
**A**：理论上可以，但需要确保 Qwen 服务器能够访问您的本地服务器（需要公网 IP 和端口映射）。

### Q5：Prompt 改写建议开启吗？
**A**：**不建议**。当文本描述与输入视频内容不一致时，模型可能产生误解。建议关闭智能扩写，并在 prompt 中提供清晰、具体的画面描述。

---

**更新时间**：2025-10-27  
**版本**：v1.0


