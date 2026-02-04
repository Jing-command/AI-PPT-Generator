# 部署指南

## 1. GitHub 仓库设置

### 创建仓库

访问 https://github.com/new 创建新仓库：
- **Repository name**: `ai-ppt-backend`
- **Description**: AI PPT Generator Backend - FastAPI + PostgreSQL
- **Visibility**: Public 或 Private
- **Initialize**: 不要勾选任何初始化选项（已有代码）

### 推送代码

```bash
cd /root/projects/ai-ppt-backend

# 配置远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/ai-ppt-backend.git

# 推送代码
git push -u origin master
```

## 2. 服务器部署

### 方式一：Docker Compose（推荐）

```bash
# 克隆代码
git clone https://github.com/YOUR_USERNAME/ai-ppt-backend.git
cd ai-ppt-backend

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置数据库密码和密钥

# 启动服务
cd docker
docker-compose up -d

# 初始化数据库
docker-compose exec postgres psql -U postgres -d aippt -f /scripts/init_db.sql
```

### 方式二：手动部署

```bash
# 安装依赖
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置 PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE aippt;"
sudo -u postgres psql -c "CREATE USER aippt WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE aippt TO aippt;"

# 创建表
psql -U aippt -d aippt -f scripts/init_db.sql

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 3. Nginx 反向代理配置

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 4. 系统服务配置

创建 `/etc/systemd/system/aippt-api.service`：

```ini
[Unit]
Description=AI PPT Generator API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/ai-ppt-backend
Environment="PATH=/var/www/ai-ppt-backend/venv/bin"
EnvironmentFile=/var/www/ai-ppt-backend/.env
ExecStart=/var/www/ai-ppt-backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl enable aippt-api
sudo systemctl start aippt-api
sudo systemctl status aippt-api
```

## 5. 依赖安装

### LibreOffice（PDF 导出必需）

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y libreoffice

# CentOS/RHEL
sudo yum install -y libreoffice
```

### pdf2image（图片导出）

```bash
pip install pdf2image
# 同时需要 poppler
sudo apt-get install -y poppler-utils  # Ubuntu
```

## 6. 安全配置

### 防火墙

```bash
# 开放端口
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw allow 8000  # API (如果使用直接访问)
sudo ufw enable
```

### SSL 证书（Let's Encrypt）

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

## 7. 监控

### 日志查看

```bash
# 应用日志
tail -f /var/log/aippt-api.log

# Docker 日志
docker-compose logs -f api

# 系统日志
journalctl -u aippt-api -f
```

### 健康检查

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health
```

## 8. 备份

### 数据库备份

```bash
# 手动备份
pg_dump -U postgres aippt > backup_$(date +%Y%m%d).sql

# 自动备份脚本（添加到 crontab）
0 2 * * * pg_dump -U postgres aippt | gzip > /backups/aippt_$(date +\%Y\%m\%d).sql.gz
```

### 文件备份

```bash
# 备份导出文件
tar -czf exports_backup_$(date +%Y%m%d).tar.gz /var/www/ai-ppt-backend/storage/exports
```

## 9. 更新部署

```bash
cd /var/www/ai-ppt-backend

# 拉取最新代码
git pull origin master

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 执行数据库迁移
PYTHONPATH=/var/www/ai-ppt-backend alembic upgrade head

# 重启服务
sudo systemctl restart aippt-api
# 或使用 Docker:
# docker-compose restart api
```

## 10. 故障排除

### 常见问题

**1. 数据库连接失败**
- 检查 PostgreSQL 是否运行：`sudo systemctl status postgresql`
- 检查连接字符串：`echo $DATABASE_URL`
- 检查防火墙：确保端口 5432 可访问

**2. 导出失败**
- 检查 LibreOffice：`which soffice`
- 检查权限：`ls -la storage/exports/`

**3. 内存不足**
- 增加交换空间：`sudo fallocate -l 2G /swapfile`
- 调整 Docker 内存限制

**4. 端口占用**
```bash
# 查找占用 8000 端口的进程
sudo lsof -i :8000
# 结束进程
sudo kill -9 <PID>
```
