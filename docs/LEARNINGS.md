# LEARNINGS.md（失敗と恒久対策の記録）

運用中に発生した問題とその恒久対策を記録する。対策を反映した際は、対応する `CLAUDE.md` や `SKILL.md` の変更と紐づけて記載し、同じミスが再発しない状態を積み上げていく。定期的に見返し、蓄積された対策を `CLAUDE.md` の恒久ルールに昇格させること。

参照: 特許調査プロジェクト_要件定義書.md 9.3節

## 記録フォーマット

```
## YYYY-MM-DD: 見出し（何が起きたか）

- 発生日:
- 何が起きたか:
- 原因:
- 恒久対策: （CLAUDE.md / Hooks / SKILL.md のどれをどう変更したか。変更したファイルへのリンクを含める）
```

---

## 2026-09-14: patent-mcpのget_bibliographic_dataが常に404になっていた

- 発生日: 2026-09-14
- 何が起きたか: `patent-mcp`実装直後の動作テストで、`get_bibliographic_data`（書誌・要約取得ツール）がどの特許番号を渡しても404/EntityNotFoundになった。
- 原因:
  1. OPSのURLパステンプレートに `published-data/publication/{reference_type}/...` と書いており、`reference_type`のデフォルト値も`"publication"`だったため `published-data/publication/publication/...` と `publication` が二重になっていた。
  2. 二重を直した後も、epodoc形式でkindコード（例: `EP4803425A1`）を付けて渡すと`SERVER.EntityNotFound`になるケースがあった。`search_patents`の結果に含まれるcountry/doc-number/kindをそのまま`.`区切りで渡すdocdb形式（例: `EP.4803425.A1`）は安定して成功した。
- 恒久対策:
  - [patent-mcp/src/patent_mcp/ops_client.py](../patent-mcp/src/patent_mcp/ops_client.py) のURLテンプレートから重複した`publication`リテラルを削除。
  - `get_bibliographic_data`の`input_format`デフォルトを`epodoc`から`docdb`に変更し、[patent-mcp/README.md](../patent-mcp/README.md)にdocdb形式を推奨する旨と具体例を明記。
  - 実際にAPIキーを使って`search_patents`→`get_bibliographic_data`を通しで叩く動作確認を、実装直後に必ず行うことをルール化（コード上のURL構築ミスは単体テストだけでは気づきにくいため）。
