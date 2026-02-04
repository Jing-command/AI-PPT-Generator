# 🤖 AI PPT Generator - Backend

AI 驱动的 PPT 生成服务后端

## ✨ 特性

- 🤖 **多 AI 提供商支持** - OpenAI, Claude, Kimi, 阿里通义, 腾讯混元
- 💬 **对话式编辑** - 左聊右编，实时预览
- 🎨 **丰富模板** - 多行业模板支持
- 📤 **多格式导出** - PPTX, PDF, 图片
- 📝 **操作历史** - 完整的撤销/重做支持
- 🔐 **安全认证** - JWT + API Key 管理

## 🛠️ 技术栈

- **框架**: FastAPI + Python 3.12
- **数据库**: PostgreSQL + SQLAlchemy 2.0 (异步)
- **缓存**: Redis
- **任务队列**: Celery
- **认证**: JWT + bcrypt
- **文档**: Swagger UI / ReDoc

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/Jing-command/ai-ppt-backend.git
cd ai-ppt-backend
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库和密钥
```

### 5. 启动服务

**方式一：本地开发**
```bash
uvicorn app.main:app --reload
```

**方式二：Docker**
```bash
cd docker
docker-compose up -d
```

### 6. 访问文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📁 项目结构

```
ai-ppt-backend/
├── app/                    # 应用代码
│   ├── models/            # 数据库模型
│   ├── schemas/           # Pydantic 模型
│   ├── routers/           # API 路由
│   ├── services/          # 业务逻辑
│   ├── core/              # 核心工具
│   ├── utils/             # 工具函数
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库连接
│   └── main.py            # 应用入口
├── tests/                 # 测试
├── alembic/               # 数据库迁移
├── docker/                # Docker 配置
├── requirements.txt       # 依赖
└── README.md             # 本文件
```

## 🧪 测试

```bash
# 运行测试
pytest

# 带覆盖率
pytest --cov=app --cov-report=html
```

## 📝 API 规范

所有接口遵循 RESTful 规范，统一响应格式：

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

### 主要端点

| 端点 | 描述 |
|------|------|
| `POST /api/v1/auth/register` | 用户注册 |
| `POST /api/v1/auth/login` | 用户登录 |
| `POST /api/v1/ppt/generate` | 生成 PPT |
| `GET /api/v1/ppt` | PPT 列表 |
| `GET /api/v1/ppt/{id}` | PPT 详情 |
| `PUT /api/v1/ppt/{id}/slides/{slide_id}` | 单页编辑 |
| `POST /api/v1/ppt/{id}/undo` | 撤销 |

## 🗺️ 路线图

- [x] Sprint 1: 基础架构 + 认证
- [ ] Sprint 2: API Key 管理
- [ ] Sprint 3: PPT 生成核心
- [ ] Sprint 4: PPT 管理 + 单页编辑
- [ ] Sprint 5: 操作历史 + 撤销
- [ ] Sprint 6: 导出系统
- [ ] Sprint 7: 模板系统
- [ ] Sprint 8: 优化与测试

## 📄 License

MIT License
