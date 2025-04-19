# ベースのイメージを指定
FROM python:3.13-slim-bookworm

# 標準出力・標準エラーのストリームのバッファリングを行わない
ENV PYTHONUNBUFFERED=1 

# コンテナのワークディレクトリを/backendに指定
WORKDIR /backend

# curlと、mysqlclientのビルドに必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Poetryをインストールしてパスを通す
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH /root/.local/bin:$PATH

# pyproject.toml、poetry.lock*をワークディレクトリにコピー
# COPY ./pyproject.toml* ./poetry.lock* ./
# 依存関係のみをインストール（ルートパッケージを除く）
# RUN poetry install --no-root

# ソースコードをコピー
# COPY . .

# entrypoint.shに実行権限を付与
# RUN chmod 755 entrypoint.sh