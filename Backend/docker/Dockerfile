FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt requirements-dev.txt ./

# 国内镜像源（可通过 build-arg 覆盖）
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ARG PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

# 设置 pip 使用镜像源
ENV PIP_INDEX_URL=${PIP_INDEX_URL}
ENV PIP_TRUSTED_HOST=${PIP_TRUSTED_HOST}

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt -i ${PIP_INDEX_URL} --trusted-host ${PIP_TRUSTED_HOST}

# 复制应用代码
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
