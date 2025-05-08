FROM nginx:latest

# 設定ファイルをコピー
COPY default.conf /etc/nginx/conf.d/default.conf

# 静的ファイル用ディレクトリを作成
RUN mkdir -p /app/static

# 権限設定
RUN chmod -R 755 /app/static

# Nginxをフォアグラウンドで実行
CMD ["nginx", "-g", "daemon off;"]