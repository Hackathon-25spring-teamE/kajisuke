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
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . /app/

# 静的ファイルを収集
RUN python manage.py collectstatic --noinput

# uWSGIの設定ファイルをコピー
COPY ./uwsgi.ini /app/uwsgi.ini
