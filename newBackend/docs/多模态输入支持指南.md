# 📝 多模态输入支持指南

## 📋 概述

ClipPersona 系统支持多种输入模态组合，但不同的编辑器对输入模态有不同的要求。

## 🎯 支持的输入模态

### FFmpeg 编辑器

**设计目的**: 编辑现有视频

| 输入模态           | 支持 | 说明                            |
| ------------------ | ---- | ------------------------------- |
| 纯文本             | ❌    | FFmpeg 需要输入视频才能进行编辑 |
| 图片 + 文本        | ❌    | FFmpeg 不支持从图片生成视频     |
| **视频 + 文本**    | ✅    | **主要使用场景**                |
| 视频 + 图片 + 文本 | ❌    | 暂不支持                        |

**使用示例:**
```python
from core import DialogueManager

manager = DialogueManager()

# ✅ 正确：视频 + 文本
result = manager.process_multimodal_input(
    text="剪掉前5秒",
    video_paths=["input.mp4"]
)

# ❌ 错误：纯文本
result = manager.process_user_input("生成一个视频")  # FFmpeg 无法生成

# ❌ 错误：图片 + 文本
result = manager.process_multimodal_input(
    text="使用这张图片生成视频",
    image_paths=["image.png"]
)  # FFmpeg 不支持
```

### Qwen 编辑器

**设计目的**: AI驱动的视频生成

| 输入模态           | 支持 | 说明                          |
| ------------------ | ---- | ----------------------------- |
| **纯文本**         | ✅    | **文生视频 (T2V)**            |
| **图片 + 文本**    | ✅    | **图生视频 (I2V)、模板视频**  |
| 视频 + 文本        | ❌    | Qwen 用于生成，不编辑现有视频 |
| 视频 + 图片 + 文本 | ❌    | 暂不支持                      |

**使用示例:**
```python
from core import DialogueManager

manager = DialogueManager()

# ✅ 正确：纯文本（T2V）
result = manager.process_user_input(
    "生成一个猫咪在草地上奔跑的视频"
)

# ✅ 正确：图片 + 文本（I2V）
result = manager.process_multimodal_input(
    text="让这张图片动起来，猫咪向前奔跑",
    image_paths=["cat.png"]
)

# ❌ 错误：视频 + 文本
result = manager.process_multimodal_input(
    text="调整视频速度",
    video_paths=["input.mp4"]
)  # Qwen 不支持编辑
```

## 🔀 如何选择编辑器

### 决策流程图

```
用户输入
    │
    ├─→ 有现有视频需要编辑？
    │       ├─ 是 → 使用 FFmpeg
    │       │       输入：视频 + 文本指令
    │       │       操作：trim, adjust_speed, add_text 等
    │       │
    │       └─ 否 → 继续判断
    │
    └─→ 需要生成新视频？
            ├─ 从文本生成 → 使用 Qwen (T2V)
            │       输入：纯文本描述
            │       操作：make_video_by_text
            │
            └─ 从图片生成 → 使用 Qwen (I2V)
                    输入：图片 + 文本描述
                    操作：make_video_by_first_frame
```

## 📊 完整对照表

| 场景         | 输入         | 编辑器 | 操作                                 | 示例                     |
| ------------ | ------------ | ------ | ------------------------------------ | ------------------------ |
| 裁剪视频     | 视频+文本    | FFmpeg | `trim`                               | "剪掉前3秒"              |
| 添加字幕     | 视频+文本    | FFmpeg | `add_text`                           | "在第5秒添加字幕'Hello'" |
| 调整速度     | 视频+文本    | FFmpeg | `adjust_speed`                       | "加速2倍"                |
| 文本生成视频 | 纯文本       | Qwen   | `make_video_by_text`                 | "一只猫在奔跑"           |
| 图片生成视频 | 图片+文本    | Qwen   | `make_video_by_first_frame`          | "让这张图片动起来"       |
| 首尾帧生成   | 2张图片+文本 | Qwen   | `make_video_by_first_and_last_frame` | "从图A平滑过渡到图B"     |

## 💡 常见问题

### Q1: 我有一个视频和一张图片，想把图片做成水印加到视频上，用哪个编辑器？

**A:** 目前系统不支持这个功能。可以考虑的替代方案：
- 使用 FFmpeg 的 `add_text` 添加文字标识
- 先用其他工具将图片和视频合成，再用 FFmpeg 编辑

### Q2: 我只有文本描述，想生成一个视频然后编辑它，怎么做？

**A:** 分两步操作：
```python
from core import VideoOperationExecutor

executor = VideoOperationExecutor()

# 步骤1: 使用 Qwen 生成视频
result1 = executor.execute_operation(
    operation_name="make_video_by_text",
    params={"prompt": "一只猫在草地上奔跑"},
    editor_type="qwen"
)

# 步骤2: 使用 FFmpeg 编辑生成的视频
if result1.success:
    result2 = executor.execute_operation(
        operation_name="trim",
        params={
            "input_video": result1.output_path,
            "start": 0,
            "end": 3
        },
        editor_type="ffmpeg"
    )
```

### Q3: 系统如何自动判断使用哪个编辑器？

**A:** 系统会根据操作类型自动选择：
- 如果操作是 `make_video_*` 开头，使用 Qwen
- 其他编辑操作使用 FFmpeg
- 也可以在 JSON 中显式指定 `"editor": "ffmpeg"` 或 `"editor": "qwen"`

### Q4: 为什么 FFmpeg 不支持图片输入？

**A:** FFmpeg 是视频编辑工具，设计用于处理已有的视频文件。虽然 FFmpeg 本身有从图片生成视频的能力，但在我们的系统中，这个功能由 Qwen AI 提供，效果更好。

### Q5: 未来会支持视频+图片+文本的组合吗？

**A:** 这是规划中的功能。可能的应用场景：
- 在视频特定位置插入图片
- 使用图片作为转场效果
- 图片作为视频片头/片尾

## 🚀 最佳实践

### 1. 明确输入类型

在调用 API 前，先确定你有什么输入：
```python
# 检查输入类型
has_video = len(video_paths) > 0
has_image = len(image_paths) > 0
has_text = text != ""

# 根据输入选择策略
if has_video and has_text and not has_image:
    # 使用 FFmpeg 编辑
    editor = "ffmpeg"
elif has_image and has_text and not has_video:
    # 使用 Qwen 图生视频
    editor = "qwen"
    operation = "make_video_by_first_frame"
elif has_text and not has_video and not has_image:
    # 使用 Qwen 文生视频
    editor = "qwen"
    operation = "make_video_by_text"
```

### 2. 提供清晰的文本指令

不同的编辑器需要不同风格的文本：

**FFmpeg (编辑指令):**
```python
# 好的例子 ✅
"剪掉前5秒"
"在第3秒添加字幕'Hello World'"
"将速度加快2倍"

# 不好的例子 ❌
"让视频更好看"  # 太模糊
"优化一下"  # 不明确
```

**Qwen (描述性文本):**
```python
# 好的例子 ✅
"一只橘猫在绿色的草地上快速奔跑，阳光明媚，蓝天白云"
"城市夜景，车流穿梭，霓虹灯闪烁"

# 不好的例子 ❌
"视频"  # 太简单
"剪掉前3秒"  # 这是编辑指令，不是生成描述
```

### 3. 处理错误情况

```python
from core import VideoOperationExecutor

executor = VideoOperationExecutor()

try:
    result = executor.execute_operation(
        operation_name="trim",
        params={
            "input_video": "input.mp4",
            "start": 1.0,
            "end": 5.0
        },
        editor_type="ffmpeg"
    )
    
    if not result.success:
        print(f"操作失败: {result.error_message}")
        
        # 检查是否是输入问题
        if "输入视频不存在" in result.error_message:
            print("提示: FFmpeg 需要已存在的视频文件")
            
except Exception as e:
    print(f"执行出错: {e}")
```

## 📚 相关文档

- [编辑器选择指南](EDITOR_GUIDE.md) - 详细的编辑器功能说明
- [系统架构文档](ARCHITECTURE.md) - 系统整体架构
- [API 使用文档](MULTIMODAL_SYSTEM_README.md) - API 接口说明

---

**总结**: 记住关键点
- FFmpeg = 视频编辑 = 需要视频输入
- Qwen = 视频生成 = 支持文本/图片输入
- 混合使用两者可以实现更复杂的工作流


