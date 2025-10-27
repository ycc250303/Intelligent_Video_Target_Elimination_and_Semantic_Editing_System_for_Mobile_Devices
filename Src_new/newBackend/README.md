# 多模态视频编辑系统

基于AI的智能视频编辑系统，支持文本、图片、视频等多模态输入。

> 📖 **[👉 完整使用指南 USER_GUIDE.md](USER_GUIDE.md)** - 新手从这里开始！  
> 🚀 **[快速参考卡片 QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - 常用代码速查  
> 包含详细的代码示例、API调用、场景演示等

## 📁 项目结构

```
newBackend/
├── core/                    # 核心功能模块
│   ├── multimodal_processor.py      # 多模态输入处理器
│   ├── video_operation_executor.py  # 视频操作执行器
│   ├── qwen_nlp_parser.py           # NLP解析器
│   └── video_comprehension.py       # 视频理解模块
│
├── api/                     # API服务
│   └── fastapi_server.py            # FastAPI服务器
│
├── config/                  # 配置文件
│   └── config.py                    # 系统配置
│
├── tests/                   # 测试文件
│   ├── test_multimodal_system.py    # 系统测试
│   ├── test_nlp_qwen_ops.py        # NLP测试
│   └── test_ffmpeg_editor.py       # 编辑器测试
│
├── examples/                # 示例代码
│   └── quick_start_example.py      # 快速入门示例
│
├── docs/                    # 文档
│   ├── MULTIMODAL_SYSTEM_README.md # 系统使用指南
│   ├── ARCHITECTURE.md             # 架构设计文档
│   └── IMPLEMENTATION_SUMMARY.md   # 实现总结
│
├── VideoEditor/             # 视频编辑器引擎
│   ├── ffmpeg_editor.py            # FFmpeg编辑器
│   └── qwen_editor.py              # Qwen视频生成
│
├── Results/                 # 输出结果目录
├── Images/                  # 图片资源目录
└── main.py                  # 主入口文件
```

## 🚀 快速开始

### 1. 配置

编辑 `config/config.py`，设置你的 Qwen API Key:

```python
QWEN_API_KEY = "your-api-key-here"
```

### 2. 使用命令行工具（最简单的方式）⭐

我们提供了易用的命令行工具 `multimodal_video_tool.py`：

**交互模式（推荐新手）：**
```bash
python multimodal_video_tool.py
```

**命令行模式：**
```bash
# 编辑视频
python multimodal_video_tool.py --text "剪掉前3秒" --video input.mp4

# 文本生成视频
python multimodal_video_tool.py --text "一只猫在草地上奔跑"

# 图片生成视频
python multimodal_video_tool.py --text "让这张图片动起来" --image photo.jpg

# 批量处理
python multimodal_video_tool.py --batch batch_tasks_example.json
```

**查看帮助：**
```bash
python multimodal_video_tool.py --help
```

**运行演示：**
```bash
python demo_multimodal_tool.py
```

### 3. 启动API服务器

```bash
python main.py
```

或者直接运行：

```bash
python api/fastapi_server.py
```

### 4. 运行示例

```bash
python examples/quick_start_example.py
```

### 5. 运行测试

```bash
python tests/test_multimodal_system.py
```

## 📖 文档

### 核心文档
- [完整使用指南](USER_GUIDE.md) - 详细的使用说明和示例
- [快速参考卡片](QUICK_REFERENCE.md) - 常用代码速查
- [工具使用说明](TOOL_USAGE.md) - 三种使用方式详解
- [图片特效模板指南](TEMPLATE_EFFECTS_GUIDE.md) - 特效模板使用说明 ⭐
- [视频延展功能指南](docs/VIDEO_EXTENSION_GUIDE.md) - 视频延展使用说明 ⭐ NEW
- [多模态输入指南](docs/MULTIMODAL_INPUT_GUIDE.md) - 输入模态支持详解
- [编辑器选择指南](docs/EDITOR_GUIDE.md) - FFmpeg vs Qwen 功能对比

### 技术文档
- [架构设计文档](docs/ARCHITECTURE.md) - 系统架构和设计
- [实现总结](docs/IMPLEMENTATION_SUMMARY.md) - 实现细节和总结
- [目录结构说明](docs/DIRECTORY_STRUCTURE.md) - 项目组织结构

## 🎯 核心功能

### 双引擎支持

系统支持两种编辑器：

1. **FFmpeg** - 用于传统视频编辑
   - 裁剪、合并、调速、滤镜等20+种操作
   - **输入要求**: 视频 + 文本
   
2. **Qwen** - 用于AI视频生成
   - 文本生成视频 (T2V) - **输入**: 纯文本
   - 图片生成视频 (I2V) - **输入**: 图片 + 文本
   - 首尾帧生成视频 (KF2V) - **输入**: 图片 + 文本
   - 视频延展 (Video Extension) - **输入**: 视频URL + 文本 ⭐ NEW

### 多模态输入

```python
from core import DialogueManager

manager = DialogueManager()

# 纯文本
result = manager.process_user_input("剪掉视频前3秒")

# 文本+图片+视频
result = manager.process_multimodal_input(
    text="使用这张图片作为首帧生成视频",
    image_paths=["image.png"],
    video_paths=["video.mp4"]
)
```

### 视频操作执行

```python
from core import VideoOperationExecutor

executor = VideoOperationExecutor()

# 从JSON执行操作
operation_json = {
    "operations": {
        "operation": "trim",
        "params": {"start": 1.0, "end": 5.0},
        "editor": "ffmpeg"
    }
}

result = executor.execute_from_json(operation_json, "input.mp4")
print(f"输出: {result.output_path}")
```

## 🛠️ 依赖

```bash
pip install openai fastapi uvicorn python-multipart
```

系统依赖：

- Python 3.8+
- FFmpeg

## 📡 API接口

启动服务器后，访问 http://localhost:8000/docs 查看完整的API文档。

主要接口：

- `POST /process-multimodal` - 多模态输入处理
- `POST /execute-operation-json` - 执行JSON操作
- `GET /operation-history` - 查询操作历史

## 🧪 测试

```bash
# 测试所有功能
python tests/test_multimodal_system.py

# 测试NLP解析
python tests/test_nlp_qwen_ops.py

# 测试视频编辑器
python tests/test_ffmpeg_editor.py
```
