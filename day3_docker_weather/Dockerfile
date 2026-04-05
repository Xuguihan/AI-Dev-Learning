# 1. 基础镜像：使用官方 Python 运行时作为基础
FROM python:3.10-slim

# 2. 设置工作目录：在容器里创建一个文件夹 /app
WORKDIR /app

# 3. 复制依赖文件：把 requirements.txt 复制进去
COPY requirements.txt .

# 4. 安装依赖：运行 pip install
RUN pip install --no-cache-dir -r requirements.txt

# 5. 复制代码：把当前目录所有文件复制到容器的 /app 目录
COPY . .

# 6. 运行命令：容器启动时运行 app.py
CMD ["python", "app.py"]