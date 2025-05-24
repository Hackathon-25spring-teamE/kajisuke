#!/bin/sh

# DBのマイグレーション
poetry run python manage.py migrate --noinput

# Nginxを使う時用
# poetry run python manage.py collectstatic --noinput

# 開発サーバーの起動
# 起動したくないときはコメントアウト→下のtail～が代わりに常駐プロセスとして待機する
# poetry run python manage.py runserver 0.0.0.0:8000

# サーバー起動の代わりに常駐プロセスとして待機
tail -f /dev/null