FROM python:3.11-slim

WORKDIR /app

# Switch to domestic mirror and install minimal nodejs runtime for pyexecjs
RUN (sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
     sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list 2>/dev/null || true) && \
    apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY src/ ./src/

EXPOSE 5000

CMD ["sh", "-c", "python src/init_db.py && python src/main.py"]
