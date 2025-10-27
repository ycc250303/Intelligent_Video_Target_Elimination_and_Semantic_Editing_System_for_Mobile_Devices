# 🚀 快速参考卡片

## ⚡ 一分钟快速开始

### 1. 启动服务
```bash
cd D:\ClipPersona\Src\newBackend
python main.py
```

### 2. 选择你的场景

| 你想做什么？   | 你有什么？  | 使用代码                       |
| -------------- | ----------- | ------------------------------ |
| **编辑视频**   | 视频 + 指令 | [👉 场景1](#场景1-编辑视频)     |
| **生成视频**   | 文字描述    | [👉 场景2](#场景2-文本生成视频) |
| **图片动起来** | 图片 + 描述 | [👉 场景3](#场景3-图片生成视频) |

---

## 场景1: 编辑视频

```python
from core import DialogueManager, VideoOperationExecutor
import json

manager = DialogueManager()
executor = VideoOperationExecutor()

# 理解指令
result = manager.process_multimodal_input(
    text="剪掉前3秒",
    video_paths=["input.mp4"]
)

# 执行
action = json.loads(result['action'].replace("action:", "").strip())
exec_result = executor.execute_from_json(action, "input.mp4")

print(f"输出: {exec_result.output_path}")
```

**常用指令**:
- "剪掉前5秒"
- "加速2倍"
- "在第3秒添加字幕'Hello'"
- "音量增大1.5倍"

---

## 场景2: 文本生成视频

```python
from core import DialogueManager, VideoOperationExecutor
import json

manager = DialogueManager()
executor = VideoOperationExecutor()

# 生成
result = manager.process_user_input(
    "生成一个猫咪在草地上奔跑的视频"
)

# 执行
action = json.loads(result['action'].replace("action:", "").strip())
exec_result = executor.execute_from_json(action)

print(f"视频: {exec_result.output_path}")
```

**提示词示例**:
- "城市夜景，车流穿梭，霓虹灯闪烁"
- "海边日落，波浪拍打沙滩，天空橙红色"
- "森林小径，阳光透过树叶，鸟儿鸣叫"

---

## 场景3: 图片生成视频

```python
from core import DialogueManager, VideoOperationExecutor
import json

manager = DialogueManager()
executor = VideoOperationExecutor()

# 生成
result = manager.process_multimodal_input(
    text="让这张图片动起来，添加微风效果",
    image_paths=["photo.jpg"]
)

# 执行
action = json.loads(result['action'].replace("action:", "").strip())
exec_result = executor.execute_from_json(action)

print(f"视频: {exec_result.output_path}")
```

---

## 🌐 REST API 快速调用

### 编辑视频
```bash
curl -X POST "http://localhost:8000/process-multimodal" \
  -F "text=剪掉前3秒" \
  -F "video=@input.mp4" \
  -F "execute_operation=true"
```

### 生成视频
```bash
curl -X POST "http://localhost:8000/process-multimodal" \
  -F "text=生成一个猫咪奔跑的视频" \
  -F "execute_operation=true"
```

### 图片生成视频
```bash
curl -X POST "http://localhost:8000/process-multimodal" \
  -F "text=让这张图片动起来" \
  -F "images=@photo.jpg" \
  -F "execute_operation=true"
```

---

## 🔧 常用操作代码

### 裁剪视频
```python
executor.execute_operation(
    operation_name="trim",
    params={"input_video": "input.mp4", "start": 1.0, "end": 5.0},
    editor_type="ffmpeg"
)
```

### 调整速度
```python
executor.execute_operation(
    operation_name="adjust_speed",
    params={"input_video": "input.mp4", "factor": 2.0},
    editor_type="ffmpeg"
)
```

### 添加字幕
```python
executor.execute_operation(
    operation_name="add_text",
    params={
        "input_video": "input.mp4",
        "text": "Hello World",
        "start_time": 1.0,
        "fontsize": 36
    },
    editor_type="ffmpeg"
)
```

### 调整音量
```python
executor.execute_operation(
    operation_name="adjust_volume",
    params={"input_video": "input.mp4", "factor": 1.5},
    editor_type="ffmpeg"
)
```

### 批量操作
```python
operations = [
    {"operation": "trim", "params": {"start": 0, "end": 5}, "editor": "ffmpeg"},
    {"operation": "adjust_speed", "params": {"factor": 1.5}, "editor": "ffmpeg"}
]

results = executor.execute_batch(operations, "input.mp4")
```

---

## 📊 输入模态速查表

| 输入      | FFmpeg | Qwen | 说明           |
| --------- | ------ | ---- | -------------- |
| 纯文本    | ❌      | ✅    | 文生视频 (T2V) |
| 图片+文本 | ❌      | ✅    | 图生视频 (I2V) |
| 视频+文本 | ✅      | ❌    | 编辑现有视频   |

---

## 🎯 决策树

```
我有什么输入？
    │
    ├─ 只有文字 → 用 Qwen 生成视频
    │
    ├─ 有图片 + 文字 → 用 Qwen 图生视频
    │
    └─ 有视频 + 指令 → 用 FFmpeg 编辑
```

---

## 💡 最佳实践

### ✅ DO
- 使用清晰具体的指令
- 检查操作结果的 `success` 字段
- 使用批量操作提高效率
- 生成后可以再编辑

### ❌ DON'T  
- 不要混淆编辑器类型
- 不要忘记传入 input_video（FFmpeg）
- 不要使用太模糊的提示词

---

## 🔍 调试命令

### 查看支持的操作
```python
from config.config import OPERATIONS
for name in OPERATIONS.keys():
    print(name)
```

### 查看操作历史
```python
for op in executor.operation_history:
    print(f"{op.operation_name}: {op.success}")
```

### 启用详细日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📚 更多资源

- 📖 [完整使用指南](USER_GUIDE.md)
- 🎯 [多模态输入指南](docs/MULTIMODAL_INPUT_GUIDE.md)
- 🔧 [编辑器选择指南](docs/EDITOR_GUIDE.md)
- 🏗️ [系统架构文档](docs/ARCHITECTURE.md)

---

## ❓ 遇到问题？

1. **找不到模块** → 检查是否在正确的目录运行
2. **视频不存在** → 使用绝对路径或检查路径拼写
3. **操作失败** → 查看 `error_message` 了解原因
4. **API 无响应** → 确认服务器已启动 (`python main.py`)

---

**提示**: 这是快速参考，详细内容请查看 [USER_GUIDE.md](USER_GUIDE.md) 📖


