# RAG Streamingプロジェクト概要

## 1. プロジェクト概要
プロジェクト名: RAG Streaming
目的: PDFドキュメントの目次（TOC）をベクトル化し、ユーザーの質問に基づいて関連する目次を検索・表示するシステム

## 2. アーキテクチャ
- Frontend: ユーザーインターフェース（FastAPI + Jinja2テンプレート）
- Backend: 検索ロジックと類似度計算を行い、WebSocketを通じて検索結果のリストを返却する（FastAPI）
- pgvector_toc: ベクトルデータベース（PostgreSQL + pgvector）
- s3_db: PDFファイルストレージ（FastAPI）

注: 全てのサービスでFastAPIを採用し、一貫性と高パフォーマンスを実現。

## 3. docker-compose.yml
添付ファイル参照。主な特徴：
- 全サービスでUvicornを使用し、開発環境では`--reload`フラグを有効化
- ポートマッピングを`127.0.0.1`にバインドしてセキュリティを強化
- 環境変数を活用してサービス間の接続情報を管理

## 4. Dockerfiles
添付ファイル参照。各サービスに最適化されたDockerfile構成。

## 5. 動作仕様

a. フロントエンド (frontend):
- FastAPIとJinja2テンプレートを使用してユーザーインターフェースを提供
- WebSocketを使用してbackendと通信
- 検索結果を表示
- PDFリンクを生成し、クリック時にs3_dbからPDFを取得し、Streamingで表示する

b. バックエンド (backend):
- WebSocketを通じてfrontendからの検索クエリを受け取る
- OpenAI APIを使用してクエリをベクトル化
- pgvector_tocデータベースで類似度検索を実行
- 検索結果をWebSocketを通じてフロントエンドに返す

c. ベクトルデータベース (pgvector_toc):
- PDFの目次（TOC）データとそのベクトル表現を保存

d. PDFストレージ (s3_db):
- PDFファイルを保存
- frontendでStreaming表示する際にここからPDFを取得する
- 特定のページのみを抽出して返す機能を提供

## 6. 主要な機能
（変更なし）

## 7. 環境変数
- OPENAI_API_KEY: OpenAI APIキー
- S3_DB_URL: PDFストレージサービスのURL
- POSTGRES_URL: PostgreSQLデータベースの接続URL
- POSTGRES_DB: データベース名
- POSTGRES_USER: データベースユーザー名
- POSTGRES_PASSWORD: データベースパスワード
- POSTGRES_HOST: データベースホスト
- POSTGRES_PORT: データベースポート

注: セキュリティ向上のため、機密情報は環境変数として管理。

## 8. 起動方法
開発環境:
```
docker compose up --build
```

本番環境:
```
docker compose -f docker-compose.prod.yml up --build
```
注: 本番環境用の`docker-compose.prod.yml`ファイルは別途作成が必要。

## 9. アクセス方法
- フロントエンド: http://localhost:8000
- バックエンドAPI: http://localhost:8001
- PDFストレージ: http://localhost:9000

## 10. 今後の改善点
1. API ドキュメンテーション: FastAPIの自動生成されるSwagger UIを活用し、さらに詳細なAPIドキュメントを追加
2. ログ管理: 構造化ログを導入し、集中ログ管理システムと連携
3. 設定管理: 環境変数と設定ファイルを組み合わせた柔軟な設定システムの導入
4. テスト: ユニットテスト、統合テスト、エンドツーエンドテストの追加
5. コードコメント: 複雑なロジックに対する詳細なインラインコメントの追加
6. エラーハンドリング: グローバルな例外ハンドラーの実装と、ユーザーフレンドリーなエラーメッセージの提供
7. 入力バリデーション: Pydanticモデルを活用した厳密な入力検証の実装
8. パフォーマンス最適化: キャッシュメカニズムの導入と非同期処理の最適化
9. スケーラビリティ: コンテナオーケストレーションツール（例：Kubernetes）の導入検討
10. モニタリング: Prometheus、Grafana等を使用したシステムの健全性とパフォーマンスのモニタリング導入
11. セキュリティ強化: TLS/SSL導入、定期的なセキュリティ監査の実施
12. CI/CD: 自動テスト、ビルド、デプロイのパイプライン構築

注: FastAPIの採用により、API文書化、バリデーション、非同期処理などの実装が容易になりました。
