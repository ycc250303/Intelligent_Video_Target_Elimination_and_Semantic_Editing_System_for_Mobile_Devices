# 🛠️ 多模态视频工具使用说明

## 📚 三种使用方式

本系统提供三种使用方式，满足不同场景需求：

| 方式              | 适用场景     | 优点               | 缺点           |
| ----------------- | ------------ | ------------------ | -------------- |
| **1. 命令行工具** | 快速单次操作 | 简单直观，开箱即用 | 功能相对基础   |
| **2. Python API** | 程序集成     | 灵活强大，可编程   | 需要写代码     |
| **3. REST API**   | 远程调用     | 跨语言，Web集成    | 需要启动服务器 |

---

## 方式1: 命令行工具 ⭐ 推荐新手

### 工具文件
- `multimodal_video_tool.py` - 主工具
- `demo_multimodal_tool.py` - 完整演示
- `batch_tasks_example.json` - 批量处理示例配置

### 使用方法

#### A. 交互模式（最简单）

```bash
python multimodal_video_tool.py
```

按照提示选择操作类型，输入文件路径和指令即可。

#### B. 命令行模式

**基本语法：**
```bash
python multimodal_video_tool.py --text "指令" [--video 视频] [--image 图片] [--output 输出目录]
```

**常用示例：**

1. **编辑现有视频**
```bash
# 裁剪视频
python multimodal_video_tool.py --text "剪掉前3秒" --video input.mp4

# 调整速度
python multimodal_video_tool.py --text "加速2倍" --video input.mp4

# 添加字幕
python multimodal_video_tool.py --text "在第2秒添加字幕'Hello World'" --video input.mp4

# 调整音量
python multimodal_video_tool.py --text "音量增大1.5倍" --video input.mp4
```

2. **文本生成视频**
```bash
# 自然场景
python multimodal_video_tool.py --text "海边日落，波浪拍打沙滩"

# 城市场景
python multimodal_video_tool.py --text "城市夜景，车流穿梭，霓虹灯闪烁"

# 动物场景
python multimodal_video_tool.py --text "一只可爱的小猫在草地上奔跑"
```

3. **图片生成视频**
```bash
# 添加动态效果
python multimodal_video_tool.py --text "让这张图片动起来，添加微风效果" --image photo.jpg

# 镜头效果
python multimodal_video_tool.py --text "添加镜头推进效果" --image photo.jpg

# 生成5秒视频
python multimodal_video_tool.py --text "基于这张图片生成5秒视频" --image photo.jpg
```

4. **批量处理**
```bash
# 从配置文件批量处理
python multimodal_video_tool.py --batch batch_tasks_example.json

# 指定输出目录
python multimodal_video_tool.py --batch tasks.json --output MyResults
```

5. **高级选项**
```bash
# 只生成JSON，不执行
python multimodal_video_tool.py --text "剪掉前5秒" --video input.mp4 --no-execute

# 显示详细信息（调试）
python multimodal_video_tool.py --text "加速2倍" --video input.mp4 --verbose

# 查看帮助
python multimodal_video_tool.py --help
```

#### C. 批量处理配置文件

创建 `my_tasks.json`：

```json
[
  {
    "text": "生成海边日落视频",
    "auto_execute": true
  },
  {
    "text": "让图片动起来",
    "image_path": "photo.jpg",
    "auto_execute": true
  },
  {
    "text": "剪掉前3秒并加速1.5倍",
    "video_path": "input.mp4",
    "auto_execute": true
  }
]
```

然后运行：
```bash
python multimodal_video_tool.py --batch my_tasks.json
```

#### D. 运行演示

```bash
python demo_multimodal_tool.py
```

查看所有功能的完整演示。

---

## 方式2: Python API

### 快速开始

```python
from multimodal_video_tool import MultimodalVideoTool

# 初始化工具
tool = MultimodalVideoTool(output_dir="Results")

# 处理单个任务
result = tool.process(
    text="剪掉前3秒",
    video_path="input.mp4"
)

print(f"成功: {result['success']}")
print(f"输出: {result.get('output_path')}")
```

### 详细示例

#### 1. 编辑视频

```python
from multimodal_video_tool import MultimodalVideoTool

tool = MultimodalVideoTool()

# 裁剪
result = tool.process(
    text="剪掉前3秒",
    video_path="input.mp4"
)

# 调速
result = tool.process(
    text="加速2倍播放",
    video_path="input.mp4"
)

# 添加字幕
result = tool.process(
    text="在第1秒添加字幕'Hello World'",
    video_path="input.mp4"
)
```

#### 2. 生成视频

```python
# 文本生成视频
result = tool.process(
    text="生成一段海边日落的视频，波浪拍打沙滩"
)

# 图片生成视频
result = tool.process(
    text="让这张图片动起来，添加微风效果",
    image_path="photo.jpg"
)
```

#### 3. 批量处理

```python
tasks = [
    {
        "text": "剪掉前3秒",
        "video_path": "video1.mp4",
        "auto_execute": True
    },
    {
        "text": "生成城市夜景视频",
        "auto_execute": True
    },
    {
        "text": "让图片动起来",
        "image_path": "photo.jpg",
        "auto_execute": True
    }
]

results = tool.batch_process(tasks)

# 查看结果
for i, result in enumerate(results, 1):
    if result['success']:
        print(f"任务{i}: 成功 - {result.get('output_path')}")
    else:
        print(f"任务{i}: 失败 - {result.get('error')}")
```

#### 4. 高级用法

```python
# 只生成JSON，不执行
result = tool.process(
    text="剪掉前5秒",
    video_path="input.mp4",
    auto_execute=False  # 不执行
)

action_json = result['action_json']
print(action_json)

# 稍后手动执行
from core import VideoOperationExecutor
executor = VideoOperationExecutor()
exec_result = executor.execute_from_json(action_json, "input.mp4")
```

### 底层API（更灵活）

```python
from core import DialogueManager, VideoOperationExecutor
import json

# 1. 初始化
manager = DialogueManager()
executor = VideoOperationExecutor()

# 2. 解析指令
result = manager.process_multimodal_input(
    text="剪掉前3秒",
    video_paths=["input.mp4"]
)

# 3. 提取操作JSON
action = result['action'].replace("action:", "").strip()
action_json = json.loads(action)

# 4. 执行操作
exec_result = executor.execute_from_json(action_json, "input.mp4")

# 5. 查看结果
print(f"成功: {exec_result.success}")
print(f"输出: {exec_result.output_path}")
print(f"耗时: {exec_result.execution_time:.2f}秒")
```

---

## 方式3: REST API

### 启动服务器

```bash
python main.py
```

或

```bash
python api/fastapi_server.py
```

服务器启动后访问: http://localhost:8000/docs 查看API文档

### API端点

#### 1. 多模态输入处理

**端点:** `POST /process-multimodal`

**示例（curl）:**

```bash
# 编辑视频
curl -X POST "http://localhost:8000/process-multimodal" \
  -F "text=剪掉前3秒" \
  -F "video=@input.mp4" \
  -F "execute_operation=true"

# 生成视频
curl -X POST "http://localhost:8000/process-multimodal" \
  -F "text=生成一个猫咪奔跑的视频" \
  -F "execute_operation=true"

# 图片生成视频
curl -X POST "http://localhost:8000/process-multimodal" \
  -F "text=让这张图片动起来" \
  -F "images=@photo.jpg" \
  -F "execute_operation=true"
```

**示例（Python requests）:**

```python
import requests

# 编辑视频
with open('input.mp4', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/process-multimodal',
        data={'text': '剪掉前3秒', 'execute_operation': 'true'},
        files={'video': f}
    )

result = response.json()
print(result)
```

#### 2. 直接执行JSON操作

**端点:** `POST /execute-operation-json`

```bash
curl -X POST "http://localhost:8000/execute-operation-json" \
  -F "video=@input.mp4" \
  -F 'operation_json={"operations": {"operation": "trim", "params": {"start": 1.0, "end": 5.0}, "editor": "ffmpeg"}}'
```

#### 3. 查询操作历史

**端点:** `GET /operation-history`

```bash
curl "http://localhost:8000/operation-history"
```

---

## 🎯 使用场景决策树

```
我想做什么？
│
├─ 快速单次操作 
│  └─ 用命令行工具 (multimodal_video_tool.py)
│
├─ 集成到Python程序
│  └─ 用Python API (MultimodalVideoTool类 或 底层API)
│
├─ Web应用/远程调用
│  └─ 用REST API (启动main.py)
│
└─ 学习和测试
   └─ 运行demo (demo_multimodal_tool.py)
```

---

## 💡 最佳实践

### ✅ DO
1. **命令行工具**：适合快速测试和单次操作
2. **Python API**：适合批量处理和程序集成
3. **REST API**：适合Web应用和跨语言调用
4. 使用详细的文本描述以获得更好的结果
5. 检查返回的 `success` 字段确认操作是否成功

### ❌ DON'T
1. 不要在高并发场景使用命令行工具（改用API）
2. 不要忘记检查输入文件是否存在
3. 不要混淆不同编辑器的功能（FFmpeg编辑，Qwen生成）

---

## 📊 快速对比

| 特性       | 命令行工具 | Python API | REST API |
| ---------- | ---------- | ---------- | -------- |
| 易用性     | ⭐⭐⭐⭐⭐      | ⭐⭐⭐        | ⭐⭐⭐⭐     |
| 灵活性     | ⭐⭐⭐        | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐     |
| 批量处理   | ⭐⭐⭐⭐       | ⭐⭐⭐⭐⭐      | ⭐⭐⭐      |
| 集成性     | ⭐⭐         | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐⭐    |
| 跨语言     | ❌          | ❌          | ✅        |
| 需要服务器 | ❌          | ❌          | ✅        |

---

## 📚 相关文档

- [完整使用指南](USER_GUIDE.md) - 详细的使用说明
- [快速参考卡片](QUICK_REFERENCE.md) - 常用代码速查
- [多模态输入指南](docs/MULTIMODAL_INPUT_GUIDE.md) - 输入模态详解
- [编辑器选择指南](docs/EDITOR_GUIDE.md) - FFmpeg vs Qwen

---

## ❓ 常见问题

**Q: 我应该用哪种方式？**
A: 
- 新手或快速测试 → 命令行工具交互模式
- 批量处理 → 命令行工具批量模式 或 Python API
- 程序集成 → Python API
- Web应用 → REST API

**Q: 如何查看所有支持的操作？**
A: 
```python
from config.config import OPERATIONS
print(list(OPERATIONS.keys()))
```

**Q: 输出文件保存在哪里？**
A: 默认在 `Results/` 目录，可以通过 `--output` 参数自定义

**Q: 如何调试？**
A: 添加 `--verbose` 参数查看详细信息

---

**提示**: 如果你是新手，强烈建议先运行 `python demo_multimodal_tool.py` 查看完整演示！


