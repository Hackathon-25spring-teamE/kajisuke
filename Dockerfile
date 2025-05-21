# ベースのイメージを指定
FROM python:3.13-slim-bookworm

# 標準出力・標準エラーのストリームのバッファリングを行わない
ENV PYTHONUNBUFFERED=1 

# コンテナのワークディレクトリを/appに指定
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    python3-dev \
    mysql-client \
    jq \
    curl \
    unzip && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf /var/lib/apt/lists/* awscliv2.zip ./aws

COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . /app/

# entrypoint.sh をコピーして実行権限を付与
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# uWSGIの設定ファイルをコピー
COPY ./uwsgi.ini /app/uwsgi.ini
