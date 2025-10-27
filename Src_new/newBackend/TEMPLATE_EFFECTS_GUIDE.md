# 🎨 图片特效模板使用指南

## 📋 概述

对于 **图片+文本** 的输入，系统会根据用户的描述自动选择合适的视频生成方式：

### 三种生成方式

1. **`make_video_by_first_frame`** - 普通图生视频
   - 使用场景：用户只有一张图片，没有提到特效
   - 示例：`"让这张图片动起来"`, `"给图片添加动态效果"`

2. **`make_video_by_first_and_last_frame`** - 首尾帧过渡
   - 使用场景：用户提供两张图片
   - 示例：`"从第一张图过渡到第二张图"`

3. **`make_video_by_first_frame_and_template`** - 特效模板生成
   - 使用场景：用户明确提到特定特效
   - 使用模型：`wanx2.1-i2v-plus`
   - 示例：`"给图片添加转圈圈特效"`, `"用解压捏捏效果"`

---

## 🎭 支持的特效列表

### 完整特效映射表

| 特效中文名 | Template 值 | 说明           |
| ---------- | ----------- | -------------- |
| 解压捏捏   | `squish`    | 挤压变形效果   |
| 转圈圈     | `rotation`  | 旋转效果       |
| 戳戳乐     | `poke`      | 戳动效果       |
| 气球膨胀   | `inflate`   | 膨胀效果       |
| 分子扩散   | `dissolve`  | 扩散消散效果   |
| 热浪融化   | `melt`      | 融化效果       |
| 冰淇淋星球 | `icecream`  | 冰淇淋风格特效 |

### 识别关键词

系统支持识别以下关键词（不区分顺序）：

- **解压捏捏**: "解压捏捏", "捏捏"
- **转圈圈**: "转圈圈", "转圈"
- **戳戳乐**: "戳戳乐", "戳戳"
- **气球膨胀**: "气球膨胀", "膨胀"
- **分子扩散**: "分子扩散", "扩散"
- **热浪融化**: "热浪融化", "融化"
- **冰淇淋星球**: "冰淇淋星球", "冰淇淋"

---

## 💡 使用示例

### 示例 1: 普通图生视频（无特效）

**用户输入:**
```
文本: "让这张图片动起来"
图片: photo.jpg
```

**系统行为:**
- 操作: `make_video_by_first_frame`
- 参数: 
  - `img_url`: `photo.jpg`
  - `prompt`: `"自然流畅的动画效果"`
  - `model`: `wan2.2-i2v-flash`
  - `resolution`: `1080P`

### 示例 2: 特效模板生成

**用户输入:**
```
文本: "给这张图片添加转圈圈特效"
图片: photo.jpg
```

**系统行为:**
- ✅ 识别关键词 "转圈圈"
- 操作: `make_video_by_first_frame_and_template`
- 参数:
  - `img_url`: `photo.jpg`
  - `template`: `rotation`
  - `model`: `wanx2.1-i2v-plus`
  - `resolution`: `720P`

### 示例 3: 多种特效关键词

**用户输入:**
```python
# 示例 3.1
tool.process(text="用捏捏效果处理这张图片", image_path="photo.jpg")
# → template: "squish"

# 示例 3.2
tool.process(text="让图片像气球一样膨胀", image_path="photo.jpg")
# → template: "inflate"

# 示例 3.3
tool.process(text="添加融化效果", image_path="photo.jpg")
# → template: "melt"

# 示例 3.4
tool.process(text="来个冰淇淋星球风格", image_path="photo.jpg")
# → template: "icecream"
```

---

## 🔍 自动参数填充逻辑

### 系统处理流程

```
用户输入: 文本 + 图片
    ↓
1. AI 解析指令
    ↓
2. _enhance_multimodal_params 增强参数
    ↓
3. 检测用户文本中是否包含特效关键词
    ↓
    ├─ 有特效关键词
    │   ↓
    │   确认操作: make_video_by_first_frame_and_template
    │   ↓
    │   自动填充:
    │   - img_url: 从 multimodal_input.images[0].content 获取
    │   - template: 从特效映射表转换（中文 → 英文）
    │   - model: 自动设置为 "wanx2.1-i2v-plus"
    │   - resolution: 默认 "720P"
    │
    └─ 无特效关键词
        ↓
        使用操作: make_video_by_first_frame
        ↓
        自动填充:
        - img_url: 从 multimodal_input.images[0].content 获取
        - prompt: 从用户文本获取（或默认"自然流畅的动画效果"）
        - model: 默认 "wan2.2-i2v-flash"
        - resolution: 默认 "1080P"
```

---

## 🎯 命令行使用示例

### 使用 `multimodal_video_tool.py`

```bash
# 普通图生视频
python multimodal_video_tool.py --text "让这张图片动起来" --image photo.jpg

# 转圈圈特效
python multimodal_video_tool.py --text "添加转圈圈特效" --image photo.jpg

# 解压捏捏特效
python multimodal_video_tool.py --text "用捏捏效果" --image photo.jpg

# 气球膨胀特效
python multimodal_video_tool.py --text "让图片像气球一样膨胀" --image photo.jpg

# 融化特效
python multimodal_video_tool.py --text "添加热浪融化效果" --image photo.jpg
```

---

## 🐍 Python API 使用示例

```python
from multimodal_video_tool import MultimodalVideoTool

tool = MultimodalVideoTool(output_dir="Results")

# 示例 1: 普通图生视频
result1 = tool.process(
    text="让这张图片动起来",
    image_path="photo.jpg"
)
# → 使用 make_video_by_first_frame

# 示例 2: 转圈圈特效
result2 = tool.process(
    text="给这张图片添加转圈圈特效",
    image_path="photo.jpg"
)
# → 使用 make_video_by_first_frame_and_template，template="rotation"

# 示例 3: 解压捏捏特效
result3 = tool.process(
    text="用解压捏捏效果处理图片",
    image_path="photo.jpg"
)
# → 使用 make_video_by_first_frame_and_template，template="squish"

# 示例 4: 冰淇淋星球特效
result4 = tool.process(
    text="来个冰淇淋风格的视频",
    image_path="photo.jpg"
)
# → 使用 make_video_by_first_frame_and_template，template="icecream"
```

---

## ⚙️ 技术实现细节

### 代码位置

**文件:** `core/qwen_nlp_parser.py`

**函数:** `_enhance_multimodal_params()`

**特效映射表:**
```python
TEMPLATE_EFFECTS = {
    "解压捏捏": "squish",
    "捏捏": "squish",
    "转圈圈": "rotation",
    "转圈": "rotation",
    "戳戳乐": "poke",
    "戳戳": "poke",
    "气球膨胀": "inflate",
    "膨胀": "inflate",
    "分子扩散": "dissolve",
    "扩散": "dissolve",
    "热浪融化": "melt",
    "融化": "melt",
    "冰淇淋星球": "icecream",
    "冰淇淋": "icecream"
}
```

### 关键逻辑

1. **特效识别:**
   - 遍历用户输入文本
   - 检查是否包含特效关键词
   - 找到第一个匹配的特效

2. **参数填充优先级:**
   - 图片路径: 始终从 `multimodal_input.images[0].content` 获取
   - Template: 优先使用识别到的特效，其次使用 AI 返回值
   - Model: 对于 template 操作，强制使用 `wanx2.1-i2v-plus`

3. **日志输出:**
   - 识别到特效时会记录: `识别到特效: 转圈圈 -> rotation`
   - 填充参数时会记录: `自动填充 template: rotation`

---

## 📝 注意事项

1. **特效优先级**: 如果用户文本中包含多个特效关键词，系统会使用第一个识别到的特效

2. **模型限制**: 特效模板只能使用 `wanx2.1-i2v-plus` 模型

3. **关键词匹配**: 关键词匹配是包含匹配，不需要完全一致
   - ✅ "给图片添加转圈圈特效" → 识别到 "转圈圈"
   - ✅ "用捏捏效果" → 识别到 "捏捏"
   - ✅ "让图片融化" → 识别到 "融化"

4. **未识别到特效**: 如果用户使用了 `make_video_by_first_frame_and_template` 但没有识别到特效，系统会保持 AI 返回的 template 值

---

## 🧪 测试建议

```python
# 测试特效识别
test_cases = [
    ("转圈圈特效", "rotation"),
    ("解压捏捏效果", "squish"),
    ("气球膨胀动画", "inflate"),
    ("融化特效", "melt"),
    ("冰淇淋风格", "icecream"),
    ("戳戳乐效果", "poke"),
    ("分子扩散", "dissolve"),
]

for text, expected_template in test_cases:
    result = tool.process(
        text=f"给图片添加{text}",
        image_path="test.jpg",
        verbose=True
    )
    # 检查日志输出，确认 template 是否为 expected_template
```

---

## 📚 相关文档

- [多模态输入指南](docs/MULTIMODAL_INPUT_GUIDE.md)
- [编辑器选择指南](docs/EDITOR_GUIDE.md)
- [工具使用说明](TOOL_USAGE.md)
- [快速参考](QUICK_REFERENCE.md)

---

**更新日期:** 2025-10-27  
**版本:** 1.0


