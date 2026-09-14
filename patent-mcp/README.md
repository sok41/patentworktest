# patent-mcp

EPO Open Patent Services（OPS。Espacenetの背後にあるAPI）を経由して特許を検索・取得するMCPサーバー。
親プロジェクト（`../`、patent-projects）の `patent-research` スキルが、`.mcp.json` の `patent-search-mcp` として利用する想定。

## セットアップ

1. [developers.epo.org](https://developers.epo.org/) でアカウントを作成し、アプリを登録してConsumer Key/Secretを発行する
   （無料利用枠あり。詳細は [OPS利用規約・ドキュメント](https://www.epo.org/en/searching-for-patents/data/web-services/ops) 参照）
2. `.env` を開き、`OPS_CONSUMER_KEY` / `OPS_CONSUMER_SECRET` に発行された値を記入する
   （`.env` はGit管理対象外。項目のテンプレートは `.env.example` を参照）
3. 依存関係をインストールする

   ```bash
   uv sync
   ```

4. 動作確認（MCPサーバーを直接起動してstdioで待受）

   ```bash
   uv run patent-mcp
   ```

   正常に起動すればstdioでJSON-RPCの入力待ちになる（フリーズしているように見えるのが正常）。Ctrl+Cで終了。

## 親プロジェクトからの接続

`../.mcp.json` の `patent-search-mcp` エントリのコマンドを、このプロジェクトを起動する内容に差し替える。例:

```json
{
  "mcpServers": {
    "patent-search-mcp": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "patent-mcp", "run", "patent-mcp"]
    }
  }
}
```

（`command`/`args` はOSやuvの配置場所により調整が必要な場合がある）

## 提供ツール

| ツール | 内容 |
|---|---|
| `search_patents(query, range_begin=1, range_end=25)` | OPSの `published-data search` をCQLクエリで実行し、ヒット結果をJSONで返す。例: `query='ti=drone AND pd within "2020-2026"'` |
| `get_bibliographic_data(patent_number, input_format="epodoc", constituents="biblio,abstract")` | 特許番号から書誌情報・要約を取得する。例: `patent_number='EP1000000A1'` |

CQLクエリの書き方は [OPS CQLシンタックス](https://www.epo.org/en/searching-for-patents/data/web-services/ops) や既存の `patsnap-search-formula` スキルを参照。

## 認証の仕組み

OAuth2 client_credentialsグラント。Consumer Key/Secretを使って `/auth/accesstoken` からアクセストークンを取得し、有効期限が切れる少し手前で自動的に再取得する（`src/patent_mcp/ops_client.py`）。APIキーは `.env` にのみ保持し、リポジトリにコミットしない。

## 今後の拡張候補

- ファミリー・法的状況（リーガルステータス）取得ツール
- 全文検索（fulltext）対応
- レート制限（OPSは1分あたりのリクエスト数に上限あり）へのリトライ・バックオフ
