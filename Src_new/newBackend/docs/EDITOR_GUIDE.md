# 编辑器选择指南

## 📋 概述

ClipPersona 系统支持两种视频处理引擎，分别适用于不同的场景：

## 🔧 FFmpeg 编辑器

### 用途
传统的视频编辑操作

### 多模态输入支持
- ✅ **视频 + 文本**（主要模式）
- ❌ 不支持纯文本输入（需要已有视频）
- ❌ 不支持图片输入（FFmpeg 用于编辑，不生成）

### 适用场景
- ✂️ 裁剪、合并视频
- ⏱️ 调整视频速度
- 🎵 音频处理（提取、混合、音量调节）
- 📝 添加字幕文字
- 🎨 应用滤镜效果
- 🔄 格式转换
- 📐 分辨率调整

### 支持的操作
```
trim, concatenate, adjust_speed, rotate, crop,
add_text, adjust_volume, add_background_music,
add_transition
```

### 使用示例

```json
{
  "operations": {
    "operation": "trim",
    "params": {
      "start": 1.0,
      "end": 5.0
    },
    "editor": "ffmpeg"
  }
}
```

```python
from core import VideoOperationExecutor

executor = VideoOperationExecutor()
result = executor.execute_operation(
    operation_name="trim",
    params={
        "input_video": "input.mp4",
        "start": 1.0,
        "end": 5.0
    },
    editor_type="ffmpeg"
)
```

---

## 🤖 Qwen 编辑器

### 用途
AI驱动的视频生成

### 多模态输入支持
- ✅ **纯文本**（文生视频 T2V）
- ✅ **图片 + 文本**（图生视频 I2V、模板视频）
- ❌ 不支持视频输入（Qwen 用于生成，不编辑）

### 适用场景
- 📝 文本描述生成视频
- 🖼️ 单张图片生成视频
- 🎬 首尾帧生成视频
- 📋 模板驱动生成视频

### 支持的操作
```
make_video_by_text                      # 文本生成视频 (T2V)
make_video_by_first_frame               # 单图生成视频 (I2V)
make_video_by_first_and_last_frame      # 首尾帧生成视频 (KF2V)
make_video_by_first_frame_and_template  # 图片+模板生成视频
```

### 使用示例

#### 1. 文本生成视频 (T2V)

```json
{
  "operations": {
    "operation": "make_video_by_text",
    "params": {
      "prompt": "一只可爱的猫咪在草地上奔跑",
      "model": "wan2.2-t2v-plus",
      "size": "832*480"
    },
    "editor": "qwen"
  }
}
```

```python
from core import VideoOperationExecutor

executor = VideoOperationExecutor()
result = executor.execute_operation(
    operation_name="make_video_by_text",
    params={
        "prompt": "一只可爱的猫咪在草地上奔跑",
        "model": "wan2.2-t2v-plus",
        "size": "832*480"
    },
    editor_type="qwen"
)
```

#### 2. 图片生成视频 (I2V)

```json
{
  "operations": {
    "operation": "make_video_by_first_frame",
    "params": {
      "img_url": "https://example.com/image.jpg",
      "prompt": "让这张图片动起来",
      "model": "wan2.2-i2v-flash",
      "resolution": "1080P"
    },
    "editor": "qwen"
  }
}
```

#### 3. 首尾帧生成视频 (KF2V)

```json
{
  "operations": {
    "operation": "make_video_by_first_and_last_frame",
    "params": {
      "first_img_url": "https://example.com/start.jpg",
      "last_img_url": "https://example.com/end.jpg",
      "prompt": "平滑过渡",
      "model": "wanx2.2-kf2v-flash",
      "resolution": "720P"
    },
    "editor": "qwen"
  }
}
```

---

## 🔀 选择指南

### 按需求选择

| 需求           | 推荐编辑器 | 原因               |
| -------------- | ---------- | ------------------ |
| 剪辑现有视频   | FFmpeg     | 快速、稳定、精确   |
| 添加特效/滤镜  | FFmpeg     | 丰富的滤镜支持     |
| 音频处理       | FFmpeg     | 专业的音频处理能力 |
| 从文本创建视频 | Qwen       | AI生成能力         |
| 图片转视频     | Qwen       | AI驱动的动态效果   |
| 格式转换       | FFmpeg     | 支持多种格式       |

### 按输入模态选择

| 输入模态           | FFmpeg | Qwen | 说明                 |
| ------------------ | ------ | ---- | -------------------- |
| 纯文本             | ❌      | ✅    | Qwen 文生视频（T2V） |
| 图片 + 文本        | ❌      | ✅    | Qwen 图生视频（I2V） |
| 视频 + 文本        | ✅      | ❌    | FFmpeg 编辑现有视频  |
| 视频 + 图片 + 文本 | ❌      | ❌    | 暂不支持             |

## 🔧 混合使用

可以在同一个工作流中混合使用两种编辑器：

```python
from core import VideoOperationExecutor

executor = VideoOperationExecutor()

# 1. 使用Qwen生成视频
gen_result = executor.execute_operation(
    operation_name="make_video_by_text",
    params={
        "prompt": "一只猫在奔跑",
        "model": "wan2.2-t2v-plus"
    },
    editor_type="qwen"
)

# 2. 使用FFmpeg编辑生成的视频
if gen_result.success:
    edit_result = executor.execute_operation(
        operation_name="trim",
        params={
            "input_video": gen_result.output_path,
            "start": 0,
            "end": 3
        },
        editor_type="ffmpeg"
    )
```

## ⚡ 性能对比

| 特性     | FFmpeg       | Qwen                   |
| -------- | ------------ | ---------------------- |
| 处理速度 | 🚀 极快       | ⏳ 需要等待（生成时间） |
| 资源消耗 | 💻 低         | ☁️ API调用              |
| 输出质量 | 📹 保持原画质 | 🎨 AI生成质量           |
| 成本     | 💵 免费       | 💰 API计费              |
| 离线使用 | ✅ 支持       | ❌ 需要网络             |

## 📝 常见问题

### Q: 如何知道某个操作支持哪个编辑器？

A: 查看 `config/config.py` 中的 `OPERATIONS` 字典，每个操作都有 `supported_editors` 字段。

```python
from config.config import OPERATIONS

# 查看trim操作支持的编辑器
print(OPERATIONS['trim']['supported_editors'])  # 'ffmpeg'

# 查看视频生成操作支持的编辑器
print(OPERATIONS['make_video_by_text']['supported_editors'])  # 'qwen'
```

### Q: 可以用FFmpeg进行视频生成吗？

A: 不可以。视频生成需要AI能力，必须使用Qwen编辑器。

### Q: 可以用Qwen进行视频编辑吗？

A: 不可以。Qwen仅用于视频生成，编辑操作请使用FFmpeg。

### Q: 如果不指定editor字段会怎样？

A: 系统会使用默认值 `"ffmpeg"`。对于视频生成操作，必须显式指定 `"editor": "qwen"`。

---

## 📚 更多资源

- [FFmpeg官方文档](https://ffmpeg.org/documentation.html)
- [Qwen视频生成API文档](https://help.aliyun.com/zh/dashscope/)
- [操作配置文件](../config/config.py)
- [系统架构文档](ARCHITECTURE.md)

