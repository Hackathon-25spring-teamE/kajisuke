#!/bin/sh

# DBのマイグレーション
poetry run python manage.py migrate --noinput

# poetry run python manage.py collectstatic --noinput

# サーバー起動の代わりに常駐プロセスとして待機
tail -f /dev/null

# 開発サーバーの起動
# poetry run python manage.py runserver 0.0.0.0:8000