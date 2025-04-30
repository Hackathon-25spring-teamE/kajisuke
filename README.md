# kajisuke

## 概要

このプロジェクトは Django を使ったアプリケーションです。Docker および Devcontainer を利用して開発を行います。

## 使用技術

- **Python (Poetry 管理)**: 開発言語
- **Poetry**: Python のパッケージ管理＋仮想環境作成ツール
- **Django**: Python 製のWebアプリケーションフレームワーク
- **MySQL**: RDBMS
- **phpMyAdmin**: MySQL を視覚的に操作できるWebツール
- **Docker**: コンテナ化技術
- **Devcontainer**: VS Code の Docker 利用開発環境

## ディレクトリ構成

```
/kajisuke
├─ .devcontainer  # devcontainer設定ファイル 
│  └─ devcontainer.json
├─ apps  # 自分たちのアプリケーションファイル
│  ├─ migrations
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ apps.py
│  ├─ models.py
│  ├─ tests.py
│  ├─ urls.py
│  └─ views.py
├─ kajisuke  # Djangoのプロジェクト管理ファイル
│  ├─ __init__.py
│  ├─ asgi.py
│  ├─ settings.py
│  ├─ urls.py
│  └─ wsgi.py
├─ templates  # HTMLファイル
├─ static  # 静的ファイル
│  ├─ css
│  ├─ js
│  └─ images
├─ .env  # 環境変数の設定（git管理からは除外）
├─ .gitignore  # git管理から除外するファイルを指定
├─ docker-compose.yaml  # 複数のコンテナを起動する時の設定
├─ Dockerfile  # Djangoコンテナのイメージ設定
├─ entrypoint.sh  # コンテナ起動時に実行するスクリプト
├─ manage.py  # Djangoの操作ツール
├─ poetry.lock  # Poetryによるパッケージのバージョン管理ファイル
├─ pyproject.toml  # Poetryによるパッケージの依存管理ファイル
└─ README.md
```

## 開発環境構築
＜初回＞
1. ローカルにこのリポジトリをgit cloneする
2. developブランチでdockerコンテナを起動する
3. 開発サーバーが自動で動くので、[http://localhost:8000](http://localhost:8000)にアクセスできるか確認する

### コンテナの起動方法

#### 1. Devcontainerを使用する場合

1. VS Code に [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) 拡張機能をインストール
2. プロジェクトフォルダを開く
3. 左下にある「><」をクリックするとリモートウィンドウの起動オプションが表示されるので、「Reopen in Container」を選択する
4. 自動で Docker コンテナが起動し、VS Code内のターミナルがDjangoコンテナ内にアタッチされます

#### 2. Devcontainerを使用しない場合

1. docker-compose.yamlがあるディレクトリで`docker compose up`を実行する

### Poetry の使い方

- DjangoアプリケーションはPoetryの仮想環境内にあるため、操作にはpoetryコマンドを使います
- 主な使用コマンド（Djangoコンテナ内で実行）
  ```bash
  poetry run <command>     # 仮想環境上でコマンドを実行
  
  # 以下はpyproject.tomlがあるディレクトリで実行
  poetry add <pkg>         # パッケージの追加
  poetry add -G dev <pkg>  # 開発用パッケージの追加
  poetry remove <pkg>      # パッケージの削除
  ```


### 開発用サーバーの起動

- 初期の状態では、コンテナ起動と同時に Django 開発サーバーが自動で動きます
- 開発サーバーを手動で動かしたい場合
    1. entrypoint.sh内のサーバー起動コマンドをコメントアウトしてからコンテナを起動
    2. コンテナ内のmanage.pyがあるディレクトリで、サーバー起動コマンドを実行する
- [http://localhost:8000](http://localhost:8000) で動作確認できます

### phpMyAdmin

- [http://localhost:3001](http://localhost:3001)で使用できます

### マイグレーション関連

- コンテナ起動時に `migrate` は自動実行されます
- `makemigrations` は必要時に手動で実行します

```bash
poetry run python manage.py makemigrations
poetry run python manage.py migrate
```

