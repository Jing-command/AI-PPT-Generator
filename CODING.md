# AI PPT Backend - 编程规范

本文档记录本项目的代码规范、最佳实践和经验总结。

---

## 📁 项目结构规范

```
ai-ppt-backend/
├── app/                    # 主应用代码
│   ├── models/            # SQLAlchemy 数据模型
│   ├── schemas/           # Pydantic 验证模型
│   ├── routers/           # FastAPI 路由（按模块拆分）
│   ├── services/          # 业务逻辑层
│   ├── core/              # 安全、配置、工具
│   ├── tasks/             # Celery 异步任务
│   └── main.py            # 应用入口
├── test/                  # 测试代码
│   ├── tests/             # pytest 单元测试
│   ├── test-core.py       # 核心功能测试
│   └── test-api.sh        # API 集成测试
├── docker/                # Docker 配置
├── scripts/               # 运维脚本
├── alembic/               # 数据库迁移
└── docs/                  # 文档（可选）
```

**分层原则：**
- **Router** 只处理 HTTP（路由、参数、响应）
- **Service** 处理业务逻辑（CRUD、计算、调用外部服务）
- **Model** 只定义数据结构（数据库表、关系）
- **Schema** 只定义验证规则（Pydantic 模型）

---

## 📝 代码风格规范

### 1. Python 代码风格

```python
# 使用 Black 格式化（行长度 100）
# 使用 isort 排序导入

# ✅ 正确：清晰的函数签名
def create_ppt(
    self,
    user_id: UUID,
    data: PresentationCreate,
    slides: Optional[List[dict]] = None
) -> Presentation:
    """
    创建 PPT
    
    Args:
        user_id: 用户 ID
        data: 创建数据
        slides: 初始幻灯片（可选）
        
    Returns:
        创建的 PPT 对象
        
    Raises:
        ValueError: 参数验证失败
    """
    pass

# ❌ 错误：缺少类型注解和文档
def create_ppt(user_id, data, slides=None):
    pass
```

### 2. 导入排序

```python
# 1. 标准库
import uuid
from datetime import datetime
from typing import List, Optional

# 2. 第三方库
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# 3. 本项目模块
from app.core import get_current_user
from app.database import get_db
from app.models.user import User
```

---

## 🗄️ 数据库规范

### 1. 模型定义

```python
class User(Base):
    """
    用户模型
    
    字段说明：
        id: UUID 主键
        email: 唯一邮箱
        password_hash: bcrypt 密码哈希
        is_active: 账户状态
    """
    
    __tablename__ = "users"
    
    # 主键（必用 UUID）
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # 业务字段（必须加注释）
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,           # 查询频繁的字段加索引
        comment="用户邮箱"
    )
    
    # 时间戳（必备）
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间"
    )
    
    # 关系（显式声明 cascade）
    presentations: Mapped[List["Presentation"]] = relationship(
        "Presentation",
        back_populates="user",
        cascade="all, delete-orphan",  # 用户删除时级联删除 PPT
        lazy="selectin"                # 异步推荐 selectin
    )
```

### 2. 外键规范

```python
# ✅ 正确：显式设置 ondelete
user_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("users.id", ondelete="CASCADE"),  # 或 SET NULL
    nullable=False,
    index=True
)

# ❌ 错误：不设置 ondelete
user_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("users.id")  # 默认 RESTRICT，可能阻塞删除
)
```

### 3. 查询规范

```python
# ✅ 正确：异步查询 + selectin
result = await db.execute(
    select(User)
    .where(User.id == user_id)
    .options(selectinload(User.presentations))  # 预加载关系
)

# ❌ 错误：同步查询
result = db.query(User).filter(User.id == user_id).first()

# ❌ 错误：N+1 查询
for ppt in user.presentations:  # 每次访问都会触发查询
    print(ppt.title)
```

---

## 🔐 安全规范

### 1. 密码处理

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 哈希密码（自动加盐）
hashed = pwd_context.hash(password)

# 验证密码
is_valid = pwd_context.verify(plain_password, hashed)
```

### 2. JWT Token

```python
# ✅ 正确：区分 token 类型
def decode_token(token: str, expected_type: str = "access"):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    token_type = payload.get("type")
    
    if token_type != expected_type:
        raise ValueError(f"Invalid token type: expected {expected_type}")
    
    return payload["sub"]

# 使用
user_id = decode_token(access_token, expected_type="access")
user_id = decode_token(refresh_token, expected_type="refresh")
```

### 3. API Key 加密

```python
from cryptography.fernet import Fernet

# 加密（存储到数据库前）
encrypted = cipher_suite.encrypt(api_key.encode())

# 解密（使用时）
decrypted = cipher_suite.decrypt(encrypted).decode()
```

**红线：**
- ❌ 绝不明文存储密码、API Key
- ❌ 绝不把 API Key 打印到日志
- ❌ 绝不在 URL 中传递敏感参数

---

## 🌐 API 设计规范

### 1. RESTful 路径

```
GET    /api/v1/ppt              # 列表（支持分页、筛选）
POST   /api/v1/ppt              # 创建
GET    /api/v1/ppt/{id}         # 详情
PATCH  /api/v1/ppt/{id}         # 部分更新
PUT    /api/v1/ppt/{id}         # 全量更新（少用）
DELETE /api/v1/ppt/{id}         # 删除

# 子资源
GET    /api/v1/ppt/{id}/slides
POST   /api/v1/ppt/{id}/slides
PATCH  /api/v1/ppt/{id}/slides/{slide_id}
```

### 2. 统一响应格式

```python
# 成功响应
{
    "code": "SUCCESS",
    "data": {
        "id": "uuid",
        "title": "PPT标题"
    }
}

# 错误响应
{
    "code": "NOT_FOUND",
    "message": "PPT 不存在",
    "details": {
        "resource": "ppt",
        "id": "uuid"
    }
}

# 列表响应
{
    "code": "SUCCESS",
    "data": [...],
    "pagination": {
        "page": 1,
        "size": 20,
        "total": 100
    }
}
```

### 3. HTTP 状态码

| 状态码 | 使用场景 |
|--------|----------|
| 200 | GET/PUT/PATCH 成功 |
| 201 | POST 创建成功 |
| 202 | 异步任务已接受 |
| 204 | DELETE 成功 |
| 400 | 参数验证失败 |
| 401 | 未认证（Token 无效） |
| 403 | 无权限（Token 有效但无权访问） |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

---

## 🧪 测试规范

### 1. 测试金字塔

```
       /\
      /  \     E2E 测试（少量，覆盖核心流程）
     /____\    
    /      \   集成测试（中等，覆盖 API）
   /________\  
  /          \ 单元测试（大量，覆盖函数）
 /____________\
```

### 2. 测试文件命名

```
test_module.py           # 对应模块测试
test_feature.py          # 功能测试
conftest.py              # 共享 fixture
```

### 3. 测试数据

```python
# ✅ 正确：动态生成，避免冲突
import uuid

email = f"test_{uuid.uuid4().hex[:8]}@example.com"

# ❌ 错误：固定数据，重复运行会失败
email = "test@example.com"
```

### 4. 异步测试

```python
import pytest

@pytest.mark.asyncio
async def test_create_ppt(client, auth_headers):
    response = await client.post(
        "/api/v1/ppt",
        json={"title": "测试"},
        headers=auth_headers
    )
    assert response.status_code == 201
```

---

## 🐛 Bug 修复经验

### 1. 修复流程

```
1. 复现 Bug → 2. 定位根因 → 3. 编写测试 → 4. 修复 → 5. 验证
```

### 2. 常见 Bug 模式

| 类型 | 示例 | 修复方案 |
|------|------|----------|
| **逻辑错误** | redo 栈未清空 | 用 `delete` 替代 `update` |
| **状态不一致** | undo 不恢复数据 | 添加自动状态恢复 |
| **异步问题** | 任务不执行 | 确保调用 `.delay()` |
| **边界条件** | 密码长度超限 | 添加验证和截断 |
| **类型错误** | UUID 与 SQLite 不兼容 | 使用兼容类型或 PostgreSQL |

### 3. Code Review Checklist

- [ ] 异常是否全部处理？
- [ ] 数据库事务是否正确提交/回滚？
- [ ] 异步函数是否都用 `await`？
- [ ] 是否有 N+1 查询？
- [ ] 敏感数据是否加密？
- [ ] 输入参数是否验证？
- [ ] 返回数据是否脱敏？
- [ ] 是否有适当的日志？

---

## 🚀 性能优化

### 1. 数据库优化

```python
# 连接池配置
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,           # 常驻连接数
    max_overflow=20,        # 临时连接数
    pool_pre_ping=True      # 自动检测断开的连接
)
```

### 2. 缓存策略

```python
# Redis 缓存热点数据
@cache(expire=300)  # 5分钟
def get_user_by_id(user_id: UUID):
    return db.get(User, user_id)
```

### 3. 异步处理

```python
# 大文件导出必须异步
@router.post("/export")
async def submit_export(...):
    task = await create_task(...)
    process_export.delay(task.id)  # 异步执行
    return {"task_id": task.id}
```

---

## 📝 Git 提交规范（Conventional Commits）

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 分类：**

| 类型 | 用途 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: add PPT generation API` |
| `fix` | Bug修复 | `fix: undo/redo logic error` |
| `chore` | 杂项 | `chore: update .gitignore` |
| `docs` | 文档 | `docs: add deployment guide` |
| `test` | 测试 | `test: add auth unit tests` |
| `refactor` | 重构 | `refactor: extract service layer` |
| `security` | 安全 | `security: add rate limiting` |
| `perf` | 性能 | `perf: optimize query with index` |

**示例：**
```
feat(ppt): implement undo/redo functionality

- Add OperationHistory model
- Implement undo/redo service methods
- Add API endpoints for undo/redo

Fixes #123
```

---

## 📚 文档规范

### 1. README.md 必备章节

```markdown
## 功能特性
## 技术栈
## 快速开始
## 安装部署
## API 文档
## 测试方法
## 目录结构
## 贡献指南
```

### 2. 代码注释

```python
def complex_function(param: str) -> dict:
    """
    简要描述函数功能
    
    Args:
        param: 参数说明
        
    Returns:
        返回值说明
        
    Raises:
        ValueError: 什么情况下抛出
        
    Example:
        >>> complex_function("test")
        {"result": "ok"}
    """
```

### 3. DEPLOY.md 必备内容

- 环境变量清单
- 依赖安装步骤
- 数据库迁移命令
- 启动/停止命令
- 日志查看方法
- 常见问题排查

---

## 🎯 核心口诀

> **"三分写代码，七分测和审"**
> 
> **"好代码是改出来的，不是写出来的"**
>
> **"今天偷懒不写注释，明天加班看不懂"**
>
> **"安全无小事，数据加密不商量"**

---

## 📖 参考资源

- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
