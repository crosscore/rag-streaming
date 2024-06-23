# RAG Streamingプロジェクト概要

## 1. プロジェクト概要
プロジェクト名: RAG Streaming
目的: PDFドキュメントの目次（TOC）をベクトル化し、ユーザーの質問に基づいて関連する目次を検索・表示するシステム

## 2. アーキテクチャ
- Frontend: ユーザーインターフェース（FastAPI + Jinja2テンプレート）
- Backend: 検索ロジックと類似度計算を行い、WebSocketを通じて検索結果のリストを返却する（FastAPI）
- pgvector_toc: ベクトルデータベース（PostgreSQL + pgvector）
- s3_db: PDFファイルストレージ（カスタムFlaskアプリケーション）

## 3. docker-compose.yml

```yaml
services:
  frontend:
    build: ./frontend
    volumes:
      - ./frontend:/app
    depends_on:
      - backend
    environment:
      - BACKEND_URL=http://backend:8001
      - S3_DB_URL=http://s3_db:9000
    ports:
      - "8000:8000"
    networks:
      - app-network
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  backend:
    build: ./backend
    volumes:
      - ./backend:/app
    depends_on:
      - pgvector_toc
      - s3_db
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@pgvector_toc:5432/${POSTGRES_DB}
      - S3_DB_URL=http://s3_db:9000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_HOST=${POSTGRES_HOST}
      - POSTGRES_PORT=${POSTGRES_PORT}
    ports:
      - "8001:8001"
    networks:
      - app-network
    command: uvicorn main:app --host 0.0.0.0 --port 8001 --reload

  pgvector_toc:
    build: ./pgvector_toc
    volumes:
      - ./pgvector_toc/init_pgvector.sql:/docker-entrypoint-initdb.d/init_pgvector.sql
      - pgvector_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    networks:
      - app-network

  s3_db:
    build: ./s3_db
    volumes:
      - ./s3_db/data:/data
    ports:
      - "9000:9000"
    networks:
      - app-network
    command: python main.py

networks:
  app-network:
    driver: bridge

volumes:
  pgvector_data:
```

変更点の解説：
1. フロントエンドとバックエンドのcommandを`uvicorn`を使用するように変更しました。これにより、開発中のコード変更が即座に反映されます。
2. ポートマッピングから`127.0.0.1`を削除し、コンテナ間の通信を可能にしました。
3. 環境変数を使用してデータベースの認証情報を設定するように変更しました。これにより、セキュリティが向上します。
4. `S3_URL`を`S3_DB_URL`に統一しました。

## 4. Dockerfiles
（変更なし）

## 5. 動作仕様

a. フロントエンド (frontend):
- FastAPIとJinja2テンプレートを使用してユーザーインターフェースを提供
- WebSocketを使用してバックエンドと通信
- 検索結果を表示
- PDFリンクを生成し、クリック時にs3_dbからPDFを取得し、ストリーミングで表示する

b. バックエンド (backend):
- WebSocketを通じてフロントエンドからの検索クエリを受け取る
- OpenAI APIを使用してクエリをベクトル化
- pgvector_tocデータベースで類似度検索を実行
- 検索結果をWebSocketを通じてフロントエンドに返す

c. ベクトルデータベース (pgvector_toc):
- PDFの目次（TOC）データとそのベクトル表現を保存

d. PDFストレージ (s3_db):
- PDFファイルを保存
- フロントエンドでストリーミング表示する際にここからPDFを取得する

## 6. 主要な機能
（変更なし）

## 7. 環境変数
- OPENAI_API_KEY: OpenAI APIキー
- POSTGRES_DB: データベース名
- POSTGRES_USER: データベースユーザー名
- POSTGRES_PASSWORD: データベースパスワード
- その他のデータベース接続情報

## 8. 起動方法
```
docker compose up --build
```

## 9. アクセス方法
- フロントエンド: http://localhost:8000
- バックエンドAPI: http://localhost:8001
- PDFストレージ: http://localhost:9000

## 10. 今後の改善点
1. API ドキュメンテーション: Swagger UIなどを使用してAPIドキュメントを追加する
2. ログ管理: アプリケーション全体で適切なログ記録を実装する
3. 設定管理: 異なる環境（開発、本番など）を管理するための設定システムを導入する
4. テスト: ユニットテストと統合テストを追加する
5. コードコメント: 複雑なロジックに対して詳細なインラインコメントを追加する
6. エラーメッセージ: より分かりやすいエラーメッセージをフロントエンドに提供する
7. 入力バリデーション: フロントエンドとバックエンドの両方で入力検証を実装する
8. パフォーマンス最適化: 頻繁なクエリに対してキャッシュメカニズムを実装する
9. スケーラビリティ: 特にバックエンドとデータベースコンポーネントの水平スケーラビリティを計画する
10. モニタリング: システムの健全性とパフォーマンスのためのモニタリングとアラートを実装する
