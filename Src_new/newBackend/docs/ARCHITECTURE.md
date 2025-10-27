# 多模态视频编辑系统 - 架构设计文档

## 📐 系统架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户界面层                                │
│  (Web前端 / API客户端 / 命令行工具)                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API服务层                                    │
│                  fastapi_server.py                               │
│  • /process-multimodal    - 多模态输入处理                        │
│  • /execute-operation-json - 执行JSON操作                        │
│  • /operation-history     - 操作历史查询                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌──────────────┐
│ 多模态处理器 │  │  NLP解析器   │  │ 操作执行器    │
│multimodal_  │  │qwen_nlp_    │  │video_       │
│processor.py │  │parser.py    │  │operation_   │
│             │  │             │  │executor.py  │
└─────────────┘  └─────────────┘  └──────────────┘
       │                │                 │
       │                ▼                 │
       │         ┌─────────────┐          │
       │         │  Qwen API   │          │
       │         │  (千问模型)  │          │
       │         └─────────────┘          │
       │                                  │
       └──────────────┬───────────────────┘
                      ▼
          ┌────────────────────────┐
          │    视频编辑引擎层        │
          │  • FFmpegVideoEditor   │
          │  • QwenVideoEditor     │
          └────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │      输出结果层          │
         │  • 处理后的视频文件      │
         │  • 操作JSON文件         │
         │  • 执行日志            │
         └────────────────────────┘
```

## 🏗️ 核心组件详解

### 1. 多模态输入处理器 (multimodal_processor.py)

**职责:**
- 处理多种类型的输入（文本、图片、视频、音频）
- 统一输入格式
- 转换为AI模型可理解的格式

**核心类:**

```python
class MultimodalProcessor:
    - process_input()           # 处理多模态输入
    - convert_to_qwen_format()  # 转换为千问API格式
    - _process_image()          # 处理图片
    - _process_video()          # 处理视频
    - _process_audio()          # 处理音频
```

**数据流:**
```
输入文件 → MediaInput → MultimodalInput → Qwen API格式
```

---

### 2. NLP解析器 (qwen_nlp_parser.py)

**职责:**
- 理解用户的自然语言指令
- 调用千问大模型进行语义解析
- 生成标准化的操作JSON
- 管理对话历史

**核心类和函数:**

```python
class DialogueManager:
    - process_user_input()         # 处理纯文本输入
    - process_multimodal_input()   # 处理多模态输入
    - process_instruction()        # 处理指令
    
def ask_qwen()                     # 调用千问API (文本)
def ask_qwen_multimodal()          # 调用千问API (多模态)
def classify_instruction_type()    # 分类指令类型
def generate_response_by_type()    # 生成响应
```

**指令分类:**

```
Type 1: 能匹配操作 + 能提取参数
  → 返回完整的操作JSON

Type 2: 能匹配操作 + 不能提取参数
  → 返回带None参数的JSON，等待用户补充

Type 3: 不能匹配操作
  → 返回空操作，需要进一步澄清
```

---

### 3. 视频操作执行器 (video_operation_executor.py)

**职责:**
- 解析操作JSON
- 调用底层视频编辑引擎
- 管理操作历史
- 处理批量操作

**核心类:**

```python
class VideoOperationExecutor:
    - execute_from_json()      # 从JSON执行操作
    - execute_operation()      # 执行单个操作
    - execute_batch()          # 批量执行操作
    - save_operation_json()    # 保存JSON
    - load_operation_json()    # 加载JSON
```

**操作映射机制:**

```
JSON操作名 → 方法名映射 → 编辑器实例方法 → 实际执行
    ↓             ↓                ↓              ↓
  "trim"    →  trim()    →  ffmpeg.trim()  →  视频处理
```

---

### 4. API服务层 (fastapi_server.py)

**职责:**
- 提供HTTP RESTful API
- 处理文件上传
- 协调各个组件
- 返回处理结果

**核心接口:**

| 接口                      | 方法 | 功能           |
| ------------------------- | ---- | -------------- |
| `/process-multimodal`     | POST | 多模态输入处理 |
| `/execute-operation-json` | POST | 执行JSON操作   |
| `/operation-history`      | GET  | 查询操作历史   |
| `/upload-video`           | POST | 上传视频文件   |
| `/process-video`          | POST | 处理视频       |

---

## 🔄 数据流程

### 完整工作流程

```
1. 用户输入
   ├─ 文本指令
   ├─ 图片文件 (可选)
   ├─ 视频文件 (可选)
   └─ 音频文件 (可选)
          ↓
2. 多模态处理
   ├─ 检查文件格式
   ├─ 提取元数据
   ├─ 转换为base64/URL
   └─ 构建MultimodalInput
          ↓
3. AI理解与解析
   ├─ 调用千问模型
   ├─ 语义理解
   ├─ 操作匹配
   └─ 生成操作JSON
          ↓
4. JSON验证
   ├─ 检查操作是否存在
   ├─ 验证参数完整性
   └─ 分类指令类型
          ↓
5. 操作执行
   ├─ 选择编辑器 (FFmpeg/Qwen)
   ├─ 准备输入输出路径
   ├─ 调用编辑器方法
   └─ 生成输出文件
          ↓
6. 结果返回
   ├─ 执行状态
   ├─ 输出文件路径
   ├─ 执行时间
   └─ 错误信息 (如有)
```

---

## 📊 JSON操作格式标准

### 基本结构

```json
{
  "operations": {
    "operation": "操作名称",
    "params": {
      "参数名1": "值1",
      "参数名2": "值2"
    },
    "editor": "编辑器类型"
  }
}
```

### 示例

**1. 视频裁剪:**
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

**2. 速度调整:**
```json
{
  "operations": {
    "operation": "adjust_speed",
    "params": {
      "factor": 2.0
    },
    "editor": "ffmpeg"
  }
}
```

**3. 添加字幕:**
```json
{
  "operations": {
    "operation": "add_text",
    "params": {
      "text": "Hello World",
      "start_time": 0.0,
      "duration": 3.0,
      "fontsize": 48
    },
    "editor": "ffmpeg"
  }
}
```

---

## 🔌 可扩展性设计

### 1. 添加新的模态类型

**步骤:**
1. 在 `MediaType` 枚举中添加类型
2. 在 `MultimodalProcessor` 中实现处理方法
3. 更新 `convert_to_qwen_format()` 方法

**示例 - 添加音频支持:**
```python
# 1. 添加枚举
class MediaType(Enum):
    AUDIO = "audio"

# 2. 实现处理
def _process_audio(self, audio_path: str):
    # 处理逻辑
    pass

# 3. 更新转换
def convert_to_qwen_format(self, multimodal_input):
    # 添加音频处理
    for audio in multimodal_input.audios:
        content.append(self._convert_audio_to_qwen(audio))
```

---

### 2. 添加新的视频操作

**步骤:**
1. 在 `config.py` 的 `OPERATIONS` 中定义
2. 在编辑器中实现方法
3. 在 `video_operation_executor.py` 中添加映射

**示例 - 添加"模糊"操作:**
```python
# 1. 定义操作 (config.py)
OPERATIONS = {
    'blur': {
        'params': {
            'strength': {'type': float, 'default': 5.0, 'required': True}
        },
        'description': '模糊视频',
        'supported_editors': 'ffmpeg'
    }
}

# 2. 实现方法 (ffmpeg_editor.py)
def blur(self, input_video, output_video, strength=5.0):
    # 实现模糊逻辑
    pass

# 3. 添加映射 (video_operation_executor.py)
method_mapping = {
    'blur': 'blur',
    # ...
}
```

---

### 3. 支持新的AI模型

**步骤:**
1. 实现新的客户端初始化函数
2. 适配消息格式
3. 更新配置文件

**示例 - 添加GPT-4支持:**
```python
def init_gpt4_client():
    return OpenAI(
        api_key=GPT4_API_KEY,
        base_url=GPT4_BASE_URL
    )

def ask_gpt4(user_input, history):
    client = init_gpt4_client()
    # 调用逻辑
    pass
```

---

## 🔐 安全性考虑

### 1. 文件上传
- 验证文件类型
- 限制文件大小
- 隔离存储目录
- 定期清理临时文件

### 2. API安全
- 添加认证机制 (JWT/OAuth)
- 限流保护
- 输入验证
- 错误信息脱敏

### 3. 视频处理
- 超时控制
- 资源限制
- 进程隔离
- 错误恢复

---

## 📈 性能优化

### 1. 缓存策略
- 操作结果缓存
- AI响应缓存
- 文件内容缓存

### 2. 并发处理
- 异步任务队列
- 多进程视频处理
- 批量操作优化

### 3. 资源管理
- 临时文件清理
- 内存使用监控
- GPU加速支持

---

## 🧪 测试策略

### 1. 单元测试
- 各组件独立测试
- Mock外部依赖
- 边界条件测试

### 2. 集成测试
- 组件间交互测试
- 端到端流程测试
- 错误处理测试

### 3. 性能测试
- 负载测试
- 压力测试
- 并发测试

---

## 📝 配置管理

### 主要配置项 (config.py)

```python
# AI模型配置
QWEN_API_KEY = "your-api-key"
QWEN_BASE_CHAT_URL = "https://..."
QWEN_BASE_CHAT_MODEL = "qwen-vl-plus"

# 操作定义
OPERATIONS = {...}

# 系统提示词
SYSTEM_PROMPT_JSON = """..."""

# 指令类型枚举
class InstructionType(Enum):
    MATCH_OPERATION_AND_PARAMS = 1
    MATCH_OPERATION_BUT_NO_PARAMS = 2
    NO_MATCH_OPERATION = 3
```

---

## 🎯 未来改进方向

### 短期目标
- [ ] 添加更多视频操作
- [ ] 优化AI提示词
- [ ] 完善错误处理
- [ ] 添加操作预览

### 中期目标
- [ ] 支持实时视频流处理
- [ ] 添加视频质量评估
- [ ] 实现自动剪辑建议
- [ ] 支持多语言

### 长期目标
- [ ] 分布式处理架构
- [ ] AI模型微调
- [ ] 智能场景识别
- [ ] 自动内容生成

---

## 📚 相关文档

- [快速开始指南](MULTIMODAL_SYSTEM_README.md)
- [API接口文档](API_DOCUMENTATION.md)
- [操作参数说明](config.py)
- [测试文档](test_multimodal_system.py)

---

**文档版本:** 1.0
**最后更新:** 2025-10-27

