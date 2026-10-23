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

## 2026-09-14: 調査結果に視覚情報（グラフ）が不足していた

- 発生日: 2026-09-14
- 何が起きたか: 一通り運用テストしたところ、`patent-research`/`market-research`の出力が文章と表のみで、出願推移・出願人ランキング・市場規模の成長推移などをグラフ化する仕組みがなかった。また主要プレイヤーの近年の開発動向・トピックス情報も出力フォーマット上必須になっていなかった。
- 原因: 出力フォーマット（テンプレート・必須見出し）にグラフ生成のステップや画像埋め込みの規約が最初から組み込まれておらず、SKILL.mdの指示にも「グラフ化する」という明示的な指示がなかった。
- 恒久対策:
  - グラフ生成の共通ヘルパー [scripts/chart_utils.py](../scripts/chart_utils.py)（matplotlib、日本語フォント自動設定）を新設。セットアップ手順は [scripts/README.md](../scripts/README.md)。
  - [.claude/skills/patent-research/SKILL.md](../.claude/skills/patent-research/SKILL.md) に出願推移・出願人ランキングのグラフ生成を必須ステップとして追加し、[projects/_template/01_research/patent/research_output.md](../projects/_template/01_research/patent/research_output.md) に対応する見出し・画像リンクを追加。
  - [.claude/skills/market-research/SKILL.md](../.claude/skills/market-research/SKILL.md) に市場規模の成長推移グラフ生成と、主要プレイヤーごとの近年の開発動向・トピックス記載を追加。
  - [.claude/skills/patent-analysis/SKILL.md](../.claude/skills/patent-analysis/SKILL.md)・[.claude/skills/patent-report/SKILL.md](../.claude/skills/patent-report/SKILL.md) にもグラフ生成・埋め込みの指示を追加。
  - [.claude/hooks/post_tool_use_validate.sh](../.claude/hooks/post_tool_use_validate.sh) を拡張し、`research_output.md`について出願推移・出願人ランキングの見出しに加え、`charts/`への画像埋め込みが実際にあるか（`](charts/`の出現数）を機械的にチェックするようにした（見出しだけ用意してグラフを省略する事態を防ぐ）。市場規模グラフは単一時点しかない場合に省略が正当なため、こちらは必須チェックの対象外とした。
  - 恒久ルールとして [CLAUDE.md](../CLAUDE.md) 8.1節「グラフ・視覚情報について」に昇格。

## 2026-09-25: 要件定義書とCLAUDE.md/実装が部分的にずれていた（ドキュメントドリフト）

- 発生日: 2026-09-25
- 何が起きたか: [特許調査プロジェクト_要件定義書.md](../特許調査プロジェクト_要件定義書.md) の更新（複数業務プロジェクトへの拡張を前提とした構成）を確認したところ、(1) 既に廃止済みの`patsnap-search-formula`/`common-patsnap-search`スキルへの言及が要件定義書に残っていた、(2) スキルのバージョン管理（`metadata.version`/`CHANGELOG.md`）・通知Hooks・業務追加手順など、要件定義書に記載済みの恒久ルールがCLAUDE.mdに未反映だった。
- 原因: 要件定義書側の更新（複数業務対応の設計）と、実際のリポジトリ側の変更（patent-mcp直接利用への切替）が別々のタイミングで進み、両者間の同期チェックの仕組みがなかった。
- 恒久対策:
  - 要件定義書の該当箇所（3.2図・4.1節）を実装（patent-mcp直接利用）に合わせて修正。
  - [CLAUDE.md](../CLAUDE.md) 7.3節「スキルのバージョン管理」・7.4節「スクリプトの同梱とPython実行環境」・9章「将来的な拡張候補」を新設・拡充し、要件定義書の恒久ルールをCLAUDE.mdに反映。
  - 6スキル（`market-research`/`patent-analysis`/`patent-report`/`patent-research`/`project-create`/`research-kickoff`）のSKILL.mdフロントマターに`metadata.version`/`last_updated`を追加し、各スキルフォルダに`CHANGELOG.md`を新設（初版1.0.0）。
  - `.claude/settings.json`に`Notification`/`Stop`時の通知音Hookを追加。
  - 大規模な構造変更（`projects/`の業務ライン別ネスト化・スキルの`analysis-*`プレフィックス化・`patent-mcp`の独立リポジトリ化）は影響範囲が大きいため、今回はCLAUDE.mdへのロードマップ記載のみとし、実施はフェーズを分けて別作業とする判断をユーザーと合意。
