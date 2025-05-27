#!/bin/bash
set -euo pipefail

read DB_HOST DB_PORT DB_PASSWORD DB_USER < <(
  aws --region ap-northeast-1 secretsmanager get-secret-value \
  --secret-id kajisuke-db/credentials \
  | jq -r '.SecretString | fromjson | "\(.host) \(.port) \(.password) \(.username)"'
)
export DB_HOST DB_PORT DB_PASSWORD DB_USER

echo "Waiting for MySQL at $DB_HOST:$DB_PORT..."

until mysqladmin ping -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" --silent; do
  sleep 2
done

echo "MySQL is ready."

# Djangoマイグレーション & 静的ファイル
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# uWSGI起動（プロセスを置き換える）
exec uwsgi --ini /app/uwsgi.ini