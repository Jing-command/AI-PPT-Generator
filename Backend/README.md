# AI PPT Generator Backend

基于 FastAPI 的 AI PPT 生成器后端服务。

## 🚀 功能特性

- **用户管理**: JWT 认证 + 刷新令牌
- **多 AI 提供商**: OpenAI, Anthropic, Kimi, Aliyun, Tencent
- **API Key 管理**: AES-256 加密存储，自动识别提供商
- **PPT 生成**: AI 驱动的智能内容生成
- **单页编辑**: 支持独立幻灯片更新
- **撤销/重做**: 50 步操作历史
- **导出系统**: PPTX, PDF, PNG, JPG
- **模板系统**: 4套预设模板

## 🛠 技术栈

- **框架**: FastAPI + Python 3.12
- **数据库**: PostgreSQL + SQLAlchemy 2.0 (异步)
- **缓存**: Redis
- **任务队列**: Celery
- **文件存储**: MinIO (S3 兼容)
- **导出**: python-pptx, LibreOffice

## 📦 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/Jing-command/ai-ppt-backend.git
cd ai-ppt-backend
```

### 2. 环境配置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 环境变量

创建 `.env` 文件：

```env
# 应用配置
APP_NAME=AI PPT Generator
APP_ENV=development
DEBUG=true

# 数据库
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/aippt
DATABASE_URL_SYNC=postgresql://postgres:password@localhost:5432/aippt

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# MinIO (文件存储)
STORAGE_TYPE=minio
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=aippt
MINIO_SECURE=false

# 可选：用于测试的本地存储
STORAGE_LOCAL_PATH=./storage
```

### 4. 启动服务

```bash
# 使用 Docker Compose 启动依赖服务
cd docker
docker-compose up -d

# 返回项目根目录
cd ..

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🐳 Docker 部署

```bash
# 一键启动所有服务
docker-compose -f docker/docker-compose.yml up -d

# 查看日志
docker-compose -f docker/docker-compose.yml logs -f

# 停止服务
docker-compose -f docker/docker-compose.yml down
```

## 📚 API 文档

启动服务后访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔑 主要 API

### 认证
```
POST /api/v1/auth/register          # 用户注册
POST /api/v1/auth/login             # 用户登录
POST /api/v1/auth/refresh           # 刷新令牌
```

### API Key 管理
```
POST   /api/v1/api-keys             # 添加 API Key
GET    /api/v1/api-keys             # 获取列表
PATCH  /api/v1/api-keys/{id}        # 更新
DELETE /api/v1/api-keys/{id}        # 删除
```

### PPT 生成
```
POST /api/v1/ppt/generate           # AI 生成 PPT
GET  /api/v1/ppt/{id}               # 获取 PPT
PUT  /api/v1/ppt/{id}               # 更新 PPT
```

### 单页编辑
```
GET    /api/v1/ppt/{id}/slides/{id}    # 获取单页
PATCH  /api/v1/ppt/{id}/slides/{id}    # 更新单页
POST   /api/v1/ppt/{id}/slides         # 添加页面
DELETE /api/v1/ppt/{id}/slides/{id}    # 删除页面
```

### 撤销/重做
```
POST /api/v1/ppt/{id}/undo          # 撤销
POST /api/v1/ppt/{id}/redo          # 重做
GET  /api/v1/ppt/{id}/history       # 操作历史
```

### 导出
```
POST /api/v1/ppt/{id}/export        # 提交导出任务
GET  /api/v1/ppt/{id}/export/{tid}/status  # 查询状态
```

### 模板
```
GET  /api/v1/templates              # 模板列表
GET  /api/v1/templates/categories   # 模板分类
GET  /api/v1/templates/{id}         # 模板详情
```

## 🧪 测试

```bash
# 运行测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_auth.py -v

# 覆盖率报告
pytest --cov=app tests/
```

## 📁 项目结构

```
ai-ppt-backend/
├── app/
│   ├── main.py              # 应用入口
│   ├── config.py            # 配置
│   ├── database.py          # 数据库连接
│   ├── models/              # SQLAlchemy 模型
│   ├── schemas/             # Pydantic 模型
│   ├── routers/             # API 路由
│   ├── services/            # 业务逻辑
│   └── core/                # 核心工具
├── alembic/                 # 数据库迁移
├── docker/                  # Docker 配置
├── tests/                   # 测试
├── requirements.txt         # 生产依赖
└── requirements-dev.txt     # 开发依赖
```

## ⚠️ 注意事项

1. **API Key 加密**: 用户 API Key 使用 AES-256-CBC 加密存储，密钥从 `JWT_SECRET_KEY` 派生
2. **文件导出**: PDF 导出需要安装 LibreOffice
3. **测试环境**: 建议使用 PostgreSQL 进行测试（SQLite UUID 类型兼容性有限）

## 📄 许可证

MIT License
