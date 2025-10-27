# CoEdit 后端测试指南

本文档说明如何运行后端测试套件。

---

## 🚀 快速开始

### 1. 启动后端服务器

```bash
cd newBackend
python run_server.py
```

服务器将在 `http://localhost:8000` 上启动。

### 2. 运行测试

#### 选项A: 基础集成测试（推荐）
```bash
python tests/test_single_user_integration.py
```

**测试内容**:
- 创建会话
- 获取会话列表
- 添加消息
- 更新会话
- 删除会话
- 数据格式验证

**预期结果**: ✅ 7/7 测试通过

#### 选项B: 完整后端测试
```bash
python tests/test_complete_backend.py
```

**测试内容**:
- 健康检查 (3项)
- 会话管理 (10项)
- 数据格式验证 (6项)
- 错误处理 (4项)
- 并发测试 (2项)

**预期结果**: ✅ 23/25 测试通过 (92%)

---

## 📁 测试文件说明

| 文件 | 说明 | 测试数量 |
|------|------|---------|
| `tests/test_single_user_integration.py` | 单用户模式集成测试 | 7 |
| `tests/test_complete_backend.py` | 完整后端功能测试 | 25 |
| `tests/test_session_system.py` | 会话系统压力测试 | N/A |

---

## 🔧 测试前准备

### 依赖检查
```bash
pip install requests
```

### 环境变量（可选）
```bash
# 修改API基础URL
export BASE_URL="http://localhost:8000"
```

---

## 📊 测试覆盖范围

### API v2 (会话管理)
- [x] 创建会话 `POST /api/v2/sessions/create`
- [x] 获取所有会话 `GET /api/v2/sessions`
- [x] 获取单个会话 `GET /api/v2/sessions/{id}`
- [x] 更新会话 `PUT /api/v2/sessions/update`
- [x] 删除会话 `DELETE /api/v2/sessions/{id}`
- [x] 添加消息 `POST /api/v2/sessions/add_message`
- [x] 删除所有会话 `DELETE /api/v2/sessions/all`

### 健康检查
- [x] 根路径 `GET /`
- [x] 健康检查 `GET /health`
- [x] API文档 `GET /docs`

### 数据验证
- [x] 字段完整性
- [x] 单用户模式（无user_id）
- [x] ID格式
- [x] 时间格式
- [x] 状态枚举

### 错误处理
- [x] 404错误（不存在的资源）
- [x] 422错误（验证失败）
- [x] 500错误（服务器错误）

### 并发性能
- [x] 并发创建（5个线程）
- [x] 并发读取（10个线程）

---

## 🐛 故障排查

### 问题1: 无法连接到服务器
**错误**: `ConnectionError: No connection could be made`

**解决**:
```bash
# 检查服务器是否运行
curl http://localhost:8000/health

# 如果未运行，启动服务器
cd newBackend
python run_server.py
```

### 问题2: 测试失败
**错误**: 部分测试显示 ✗

**解决**:
1. 检查服务器日志
2. 清理测试数据：删除 `newBackend/data/sessions/` 下的旧会话
3. 重启服务器
4. 重新运行测试

### 问题3: 编码错误（Windows）
**错误**: `UnicodeEncodeError: 'gbk' codec can't encode...`

**解决**: 测试脚本已自动处理UTF-8编码，无需额外配置

---

## 📈 测试报告

运行测试后，查看详细报告：
```bash
cat docs/测试报告.md
```

或在浏览器中查看API文档：
```
http://localhost:8000/docs
```

---

## 🎯 持续集成

### 自动化测试脚本
```bash
#!/bin/bash
# test_all.sh

# 启动服务器
python run_server.py &
SERVER_PID=$!

# 等待服务器启动
sleep 3

# 运行测试
python tests/test_single_user_integration.py
TEST_RESULT_1=$?

python tests/test_complete_backend.py
TEST_RESULT_2=$?

# 关闭服务器
kill $SERVER_PID

# 返回结果
if [ $TEST_RESULT_1 -eq 0 ] && [ $TEST_RESULT_2 -eq 0 ]; then
    echo "✅ 所有测试通过"
    exit 0
else
    echo "✗ 部分测试失败"
    exit 1
fi
```

---

## 📚 参考文档

- [测试报告](docs/测试报告.md) - 详细的测试结果和分析
- [单用户模式简化方案](docs/单用户模式简化方案.md) - 设计文档
- [前后端对接快速参考](docs/前后端对接快速参考.md) - API对接指南

---

**最后更新**: 2025-10-27  
**状态**: ✅ Ready for Testing

