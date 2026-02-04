# AI PPT Backend - 测试文档

## 📁 测试文件说明

| 文件/目录 | 用途 | 运行方式 |
|-----------|------|----------|
| `test-core.py` | 核心功能测试（无需数据库） | `python test-core.py` |
| `test-api.sh` | API 接口测试脚本（需要服务启动） | `./test-api.sh` |
| `test-quick.py` | 快速功能测试（包含安全模块） | `python test-quick.py` |
| `tests/` | pytest 单元测试 | `pytest tests/ -v` |

---

## 🚀 快速开始

### 1. 核心功能测试（推荐）

无需启动任何服务，直接测试代码结构：

```bash
cd /root/projects/ai-ppt-backend
python test/test-core.py
```

**预期输出：**
```
✅ 通过: 38
❌ 失败: 0
📈 成功率: 100.0%
```

---

### 2. API 接口测试（需要服务启动）

**Step 1: 启动服务**
```bash
cd docker
docker-compose up -d
```

**Step 2: 运行测试脚本**
```bash
cd /root/projects/ai-ppt-backend
./test/test-api.sh
```

**测试内容：**
- 用户注册/登录
- API Key 管理
- PPT CRUD
- 添加幻灯片
- 撤销/重做
- 模板列表

---

### 3. Pytest 单元测试

```bash
cd /root/projects/ai-ppt-backend
pytest test/tests/ -v
```

---

## 📊 测试覆盖范围

### ✅ 已测试的功能

| 模块 | 测试内容 |
|------|----------|
| **模型导入** | User, APIKey, Presentation, OperationHistory, ExportTask, Template |
| **路由导入** | Auth, PPT, API Keys, Generation, Export, Templates |
| **服务导入** | UserService, PPTService, APIKeyService, AIProvider, Encryption, Export |
| **Schemas** | UserCreate, LoginRequest, Token, GenerateRequest, PresentationCreate, Slide, APIKeyCreate, ExportRequest |
| **业务逻辑** | API Key 加密/解密, AI Provider 工厂, Celery 任务配置 |

### ⚠️ 需要完整环境测试的功能

需要启动 PostgreSQL + Redis 才能测试：
- 数据库操作（CRUD）
- JWT 认证流程
- 异步任务执行
- 导出功能
- AI 生成功能

---

## 🔧 环境要求

### 核心测试（test-core.py）
- Python 3.12+
- 已安装项目依赖（requirements.txt）
- 无需数据库

### API 测试（test-api.sh）
- 服务已启动（docker-compose up）
- curl 命令
- PostgreSQL + Redis 运行中

### Pytest 测试（tests/）
- pytest
- pytest-asyncio
- aiosqlite（用于测试）

---

## 📝 添加新测试

### 添加 pytest 测试

在 `test/tests/` 目录下创建新文件：

```python
# test/tests/test_feature.py
import pytest

@pytest.mark.asyncio
async def test_new_feature(client: AsyncClient, auth_headers):
    response = await client.get(
        "/api/v1/feature",
        headers=auth_headers
    )
    assert response.status_code == 200
```

### 添加核心功能测试

在 `test/test-core.py` 中添加：

```python
def test_new_module():
    print("\n🆕 测试新模块...")
    # 测试代码
    print("  ✅ 新模块正常")
```

---

## 🐛 常见问题

### 1. 导入错误
```bash
# 确保在项目根目录运行
cd /root/projects/ai-ppt-backend
python test/test-core.py
```

### 2. bcrypt 版本警告
这是警告不影响测试，可以忽略。

### 3. SQLite UUID 错误
pytest 测试需要 PostgreSQL，SQLite 不支持 UUID 类型。

---

## 📈 测试状态

**最新测试结果：** 38/38 通过 ✅

- 模块导入: 24/24 ✅
- Pydantic Schemas: 8/8 ✅
- 加密服务: 1/1 ✅
- AI Provider: 1/1 ✅
- Celery 任务: 4/4 ✅
