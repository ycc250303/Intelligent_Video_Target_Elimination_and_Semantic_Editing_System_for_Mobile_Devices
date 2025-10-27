# 📖 ClipPersona 使用指南

## 🎯 快速开始

### 1. 启动服务器

```bash
cd D:\ClipPersona\Src\newBackend
python main.py
```

服务器将在 `http://localhost:8000` 启动。

## 📝 使用方式

系统支持两种使用方式：
1. **Python API** - 直接调用代码
2. **REST API** - 通过 HTTP 请求

---

## 🔧 方式一：Python API

### 场景 1: 编辑现有视频 (FFmpeg)

**适用输入**: 视频 + 文本

```python
from core import DialogueManager, VideoOperationExecutor

# 初始化
manager = DialogueManager()
executor = VideoOperationExecutor(output_dir="Results")

# 步骤1: 理解用户指令
result = manager.process_multimodal_input(
    text="剪掉前3秒，然后加速2倍",
    video_paths=["input.mp4"]
)

print(f"AI 理解: {result['response']}")
print(f"操作 JSON: {result['action']}")

# 步骤2: 执行操作
if result['success'] and result['action']:
    import json
    action_json = json.loads(result['action'].replace("action:", "").strip())
    
    exec_result = executor.execute_from_json(
        action_json,
        input_video="input.mp4"
    )
    
    if exec_result.success:
        print(f"✅ 完成！输出: {exec_result.output_path}")
        print(f"⏱️ 耗时: {exec_result.execution_time:.2f}秒")
    else:
        print(f"❌ 失败: {exec_result.error_message}")
```

**支持的编辑操作**:
- 裁剪视频: "剪掉前5秒"
- 调整速度: "加速2倍" / "慢放到0.5倍"
- 添加字幕: "在第3秒添加字幕'Hello World'"
- 调整音量: "音量增大1.5倍"
- 旋转视频: "旋转90度"
- 合并视频: "合并这两个视频"

### 场景 2: 从文本生成视频 (Qwen T2V)

**适用输入**: 纯文本

```python
from core import DialogueManager

manager = DialogueManager()

# 文本生成视频
result = manager.process_user_input(
    "生成一个5秒的视频：一只橘猫在绿色草地上快速奔跑，阳光明媚，蓝天白云"
)

print(f"AI 响应: {result['response']}")
print(f"操作 JSON: {result['action']}")

# 执行生成
if result['success']:
    import json
    from core import VideoOperationExecutor
    
    executor = VideoOperationExecutor(output_dir="Results")
    action_json = json.loads(result['action'].replace("action:", "").strip())
    
    exec_result = executor.execute_from_json(action_json)
    
    if exec_result.success:
        print(f"✅ 视频已生成: {exec_result.output_path}")
```

**提示词技巧**:
- ✅ 好的提示词: "城市夜景，车流穿梭，霓虹灯闪烁，雨后湿润的路面反射着灯光"
- ❌ 差的提示词: "一个视频" / "好看的场景"

### 场景 3: 从图片生成视频 (Qwen I2V)

**适用输入**: 图片 + 文本

```python
from core import DialogueManager

manager = DialogueManager()

# 图片生成视频
result = manager.process_multimodal_input(
    text="让这张图片动起来，添加微风吹动树叶的效果，持续5秒",
    image_paths=["landscape.jpg"]
)

print(f"AI 响应: {result['response']}")

# 执行生成
if result['success']:
    import json
    from core import VideoOperationExecutor
    
    executor = VideoOperationExecutor(output_dir="Results")
    action_json = json.loads(result['action'].replace("action:", "").strip())
    
    exec_result = executor.execute_from_json(action_json)
    
    if exec_result.success:
        print(f"✅ 视频已生成: {exec_result.output_path}")
```

### 场景 4: 生成后编辑（混合使用）

```python
from core import VideoOperationExecutor

executor = VideoOperationExecutor(output_dir="Results")

# 步骤1: 使用 Qwen 生成视频
print("🎬 步骤1: 生成视频...")
gen_result = executor.execute_operation(
    operation_name="make_video_by_text",
    params={
        "prompt": "海边日落，波浪轻轻拍打沙滩，天空渐变色",
        "model": "wan2.2-t2v-plus",
        "size": "832*480"
    },
    editor_type="qwen"
)

if gen_result.success:
    print(f"✅ 视频已生成: {gen_result.output_path}")
    
    # 步骤2: 使用 FFmpeg 编辑生成的视频
    print("\n✂️ 步骤2: 编辑视频...")
    edit_result = executor.execute_operation(
        operation_name="trim",
        params={
            "input_video": gen_result.output_path,
            "start": 0,
            "end": 3  # 保留前3秒
        },
        editor_type="ffmpeg"
    )
    
    if edit_result.success:
        print(f"✅ 编辑完成: {edit_result.output_path}")
```

### 场景 5: 批量操作

```python
from core import VideoOperationExecutor

executor = VideoOperationExecutor(output_dir="Results")

# 定义多个操作
operations = [
    {
        "operation": "trim",
        "params": {"start": 1.0, "end": 10.0},
        "editor": "ffmpeg"
    },
    {
        "operation": "adjust_speed",
        "params": {"factor": 1.5},
        "editor": "ffmpeg"
    },
    {
        "operation": "add_text",
        "params": {
            "text": "我的视频",
            "start_time": 0.5,
            "fontsize": 36
        },
        "editor": "ffmpeg"
    }
]

# 批量执行
results = executor.execute_batch(
    operations,
    input_video="input.mp4"
)

# 查看结果
for i, result in enumerate(results, 1):
    if result.success:
        print(f"✅ 操作 {i}: {result.operation_name} - {result.output_path}")
    else:
        print(f"❌ 操作 {i}: {result.operation_name} - {result.error_message}")
```

---

## 🌐 方式二：REST API

### 启动服务器

```bash
python main.py
```

服务器运行后，你会看到：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### API 端点

#### 1. `/process-multimodal` - 多模态输入处理

**场景 A: 编辑视频**

```bash
curl -X POST "http://localhost:8000/process-multimodal" \
  -F "text=剪掉前5秒并添加字幕'开始'" \
  -F "video=@input.mp4" \
  -F "execute_operation=true"
```

**场景 B: 文本生成视频**

```bash
curl -X POST "http://localhost:8000/process-multimodal" \
  -F "text=生成一个猫咪在草地上奔跑的视频" \
  -F "execute_operation=true"
```

**场景 C: 图片生成视频**

```bash
curl -X POST "http://localhost:8000/process-multimodal" \
  -F "text=让这张图片动起来" \
  -F "images=@photo.jpg" \
  -F "execute_operation=true"
```

**响应示例**:
```json
{
  "status": "success",
  "modal_type": "text+video",
  "response": "我理解了，您想剪掉前5秒并添加字幕",
  "success": true,
  "action": "{\"operations\": {...}}",
  "execution": {
    "success": true,
    "output_path": "Results/output_20251027_120000.mp4",
    "execution_time": 3.45
  }
}
```

#### 2. `/execute-operation-json` - 直接执行 JSON 操作

```bash
curl -X POST "http://localhost:8000/execute-operation-json" \
  -F 'operation_json={
    "operations": {
      "operation": "trim",
      "params": {"start": 1.0, "end": 5.0},
      "editor": "ffmpeg"
    }
  }' \
  -F "video=@input.mp4"
```

#### 3. `/generate-video-from-image` - 图片生成视频

```bash
curl -X POST "http://localhost:8000/generate-video-from-image" \
  -F "image=@photo.jpg" \
  -F "prompt=让这张图片动起来，添加微风效果"
```

#### 4. `/operation-history` - 查看操作历史

```bash
curl "http://localhost:8000/operation-history"
```

**响应**:
```json
{
  "total": 3,
  "operations": [
    {
      "operation": "trim",
      "success": true,
      "output_path": "Results/output_1.mp4",
      "execution_time": 2.3,
      "timestamp": "2025-10-27 12:00:00"
    }
  ]
}
```

---

## 📊 完整工作流示例

### Python 脚本示例

创建 `my_video_edit.py`:

```python
#!/usr/bin/env python3
"""
我的视频编辑脚本
"""
import sys
sys.path.insert(0, '/path/to/ClipPersona/Src/newBackend')

from core import DialogueManager, VideoOperationExecutor
import json

def main():
    # 1. 初始化
    manager = DialogueManager()
    executor = VideoOperationExecutor(output_dir="MyVideos")
    
    # 2. 场景选择
    print("请选择场景：")
    print("1. 编辑现有视频")
    print("2. 文本生成视频")
    print("3. 图片生成视频")
    
    choice = input("输入选择 (1-3): ")
    
    if choice == "1":
        # 编辑现有视频
        video_path = input("视频路径: ")
        instruction = input("编辑指令 (如'剪掉前3秒'): ")
        
        result = manager.process_multimodal_input(
            text=instruction,
            video_paths=[video_path]
        )
        
    elif choice == "2":
        # 文本生成视频
        prompt = input("描述你想要的视频: ")
        
        result = manager.process_user_input(prompt)
        
    elif choice == "3":
        # 图片生成视频
        image_path = input("图片路径: ")
        prompt = input("描述动态效果: ")
        
        result = manager.process_multimodal_input(
            text=prompt,
            image_paths=[image_path]
        )
    
    # 3. 显示 AI 理解
    print(f"\n🤖 AI 理解: {result['response']}")
    
    # 4. 执行操作
    if result['success'] and result['action']:
        print("\n⚙️ 执行中...")
        
        action_json = json.loads(result['action'].replace("action:", "").strip())
        
        # 根据场景传入 input_video
        if choice == "1":
            exec_result = executor.execute_from_json(action_json, input_video=video_path)
        else:
            exec_result = executor.execute_from_json(action_json)
        
        if exec_result.success:
            print(f"\n✅ 完成！")
            print(f"📁 输出文件: {exec_result.output_path}")
            print(f"⏱️ 耗时: {exec_result.execution_time:.2f}秒")
        else:
            print(f"\n❌ 失败: {exec_result.error_message}")
    else:
        print("\n❌ 理解失败，请重新描述")

if __name__ == "__main__":
    main()
```

运行：
```bash
python my_video_edit.py
```

---

## 🎨 高级用法

### 1. 自定义输出目录

```python
from core import VideoOperationExecutor

# 按日期组织
from datetime import datetime
today = datetime.now().strftime("%Y%m%d")
executor = VideoOperationExecutor(output_dir=f"Results/{today}")
```

### 2. 查看操作历史

```python
from core import VideoOperationExecutor

executor = VideoOperationExecutor()

# 执行一些操作...

# 查看历史
for op in executor.operation_history:
    print(f"{op.operation_name}: {op.success}")
    if op.success:
        print(f"  输出: {op.output_path}")
        print(f"  耗时: {op.execution_time:.2f}秒")
```

### 3. 错误处理

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
        
        # 根据错误类型处理
        if "不存在" in result.error_message:
            print("提示: 请检查文件路径")
        elif "参数" in result.error_message:
            print("提示: 请检查参数设置")
            
except Exception as e:
    print(f"系统错误: {e}")
```

### 4. 进度监控（批量操作）

```python
from core import VideoOperationExecutor

executor = VideoOperationExecutor()

operations = [...]  # 多个操作

print(f"准备执行 {len(operations)} 个操作")

results = executor.execute_batch(operations, "input.mp4")

# 统计
success_count = sum(1 for r in results if r.success)
print(f"\n完成: {success_count}/{len(operations)}")

# 详细结果
for i, result in enumerate(results, 1):
    status = "✅" if result.success else "❌"
    print(f"{status} 操作 {i}: {result.operation_name}")
```

---

## 🔍 调试技巧

### 1. 查看生成的 JSON

```python
result = manager.process_user_input("剪掉前3秒")

import json
action = json.loads(result['action'].replace("action:", "").strip())
print(json.dumps(action, indent=2, ensure_ascii=False))
```

输出：
```json
{
  "operations": {
    "operation": "trim",
    "params": {
      "start": 3.0,
      "end": null
    },
    "editor": "ffmpeg"
  }
}
```

### 2. 测试单个操作

```python
from core import VideoOperationExecutor

executor = VideoOperationExecutor(output_dir="Test")

# 直接测试操作
result = executor.execute_operation(
    operation_name="trim",
    params={
        "input_video": "test.mp4",
        "start": 0,
        "end": 3
    },
    editor_type="ffmpeg"
)

print(f"成功: {result.success}")
if result.success:
    print(f"输出: {result.output_path}")
else:
    print(f"错误: {result.error_message}")
```

### 3. 日志输出

```python
import logging

# 启用详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 然后执行操作，会看到详细的处理过程
```

---

## 📚 参考文档

- [多模态输入指南](docs/MULTIMODAL_INPUT_GUIDE.md) - 输入类型详解
- [编辑器选择指南](docs/EDITOR_GUIDE.md) - FFmpeg vs Qwen
- [系统架构文档](docs/ARCHITECTURE.md) - 系统设计
- [API 文档](docs/MULTIMODAL_SYSTEM_README.md) - 完整 API 说明

---

## ❓ 常见问题

### Q: 如何知道支持哪些操作？

```python
from config.config import OPERATIONS

# 查看所有操作
for op_name, op_info in OPERATIONS.items():
    print(f"{op_name}: {op_info['description']}")
    print(f"  编辑器: {op_info['supported_editors']}")
    print(f"  参数: {list(op_info['params'].keys())}")
```

### Q: 视频处理很慢怎么办？

- FFmpeg 操作通常很快（几秒）
- Qwen 视频生成需要等待（1-3分钟）
- 批量操作按顺序执行，会比较耗时

### Q: 生成的视频质量如何控制？

```python
# Qwen T2V - 控制尺寸
params = {
    "prompt": "...",
    "model": "wan2.2-t2v-plus",
    "size": "1280*720"  # 或 "832*480"
}

# Qwen I2V - 控制分辨率
params = {
    "img_url": "...",
    "prompt": "...",
    "resolution": "1080P"  # 或 "720P"
}
```

### Q: 如何处理多个视频？

```python
import glob
from core import VideoOperationExecutor

executor = VideoOperationExecutor()

# 批量处理
for video in glob.glob("*.mp4"):
    print(f"处理: {video}")
    result = executor.execute_operation(
        operation_name="trim",
        params={
            "input_video": video,
            "start": 0,
            "end": 5
        },
        editor_type="ffmpeg"
    )
    if result.success:
        print(f"✅ {result.output_path}")
```

---

## 🎉 开始使用吧！

选择你的使用方式：
- 🐍 **Python**: 灵活控制，适合自动化脚本
- 🌐 **REST API**: 跨语言调用，适合集成到其他应用

**下一步**:
1. 启动服务器: `python main.py`
2. 准备你的素材（视频/图片）
3. 尝试上面的示例代码
4. 查阅文档了解更多功能

有问题？查看 [完整文档](docs/) 或运行测试脚本了解更多示例！


