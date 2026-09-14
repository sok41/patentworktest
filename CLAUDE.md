# patent-projects 運用ルール

このリポジトリは、特許調査・市場調査・分析・レポート作成を一連のプロジェクトとしてClaude Code上で実行するためのものです。詳細な背景・設計意図は [特許調査プロジェクト_要件定義書.md](./特許調査プロジェクト_要件定義書.md) を参照してください。このファイルはその要件定義書に基づく「恒久的な運用ルール」を集約したものです。

## 1. 全体方針

- 調査（特許・市場）、分析、レポート作成はそれぞれ独立したスキル（`.claude/skills/`）として実装されている。
- 特許調査と市場調査は並行実行可能。分析スキルは**両方の結果が揃ってから**着手する。
- スキル自体は使い回し、案件ごとのデータは `projects/<案件ID>/` 単位で管理する。
- ユーザーが調査概要（`00_overview.md`）を投げることでプロジェクトが開始する。新規案件のフォルダ作成・テンプレートコピー・`status.yaml`/`00_overview.md`への記入はClaudeが `projects/_template/` をもとに自動生成する（ユーザーが手動で行う必要はない）。

## 2. ディレクトリ構成

```
patent-projects/                         # このリポジトリのルート
├── CLAUDE.md                            # このファイル
├── .mcp.json                            # 特許データベースMCPサーバー接続設定
├── .claude/
│   ├── settings.json                    # hooksの登録
│   ├── skills/
│   │   ├── patent-research/SKILL.md     # ①-a 特許調査スキル（MCP経由で検索実行）
│   │   ├── market-research/SKILL.md     # ①-b 市場調査スキル
│   │   ├── patent-analysis/SKILL.md     # ②分析スキル
│   │   └── patent-report/SKILL.md       # ③レポート作成スキル
│   └── hooks/                           # 自動検証ゲート（9章参照）
│       ├── post_tool_use_validate.sh
│       ├── pre_tool_use_guard.sh
│       └── stop_check_status.sh
├── docs/
│   └── LEARNINGS.md                     # 失敗と恒久対策の記録
├── projects/
│   ├── _index.md                        # 案件一覧・ステータス管理表
│   ├── _template/                       # 案件テンプレート（新規案件はこれをコピー）
│   ├── _archive/                        # 完了案件の格納先
│   └── <YYYY-MM-DD_案件名スラッグ>/       # 進行中の案件フォルダ
└── patent-mcp/                          # 特許MCPサーバー本体（Python, EPO OPS連携）
    ├── README.md                        # セットアップ手順
    ├── .env                             # OPS_CONSUMER_KEY/SECRET（Git管理外）
    └── src/patent_mcp/                  # search_patents / get_bibliographic_data ツール
```

## 3. MCPサーバー接続について

- 特許データベースへの検索実行は、`patent-mcp/`（EPO Open Patent Services = OPS を利用、Espacenetの背後にあるAPI）経由で行う。接続設定は `.mcp.json` にプロジェクトスコープで記載している（サーバー名: `patent-search-mcp`、`patent-mcp/.venv/Scripts/python.exe -m patent_mcp` を起動）。
- 初回利用前に `patent-mcp/README.md` の手順に従い、`patent-mcp/.env` に developers.epo.org で発行したConsumer Key/Secretを記入し、`uv sync` で依存関係をインストールする必要がある。
- プロジェクトスコープのMCPサーバーは初回起動時に承認が必要。
- APIキー等の認証情報は `patent-mcp/.env`（Git管理外）にのみ保持し、`.mcp.json` や他のファイルに直接書かない。
- `patent-research` スキルはMCP未接続・未承認（`.env`未設定含む）の場合、エラーにせずユーザーに接続を促す（`search_patents`/`get_bibliographic_data`は `[MCP未接続]` というテキストを返す）。

## 4. 案件管理

- 案件ID命名規則: `YYYY-MM-DD_案件名スラッグ`（例: `2026-09-14_ドローン特許調査`）
- 新規案件は `projects/_template/` をコピーして作成し、`status.yaml` と `00_overview.md` に記入する。
- `projects/_index.md` に案件ID・案件名・現フェーズ・更新日を一覧管理する。各スキルは担当フェーズ完了時にここを追記更新する。

## 5. フェーズ遷移ルール

- 調査系スキル（patent-research / market-research）は、自分の担当完了後 `status.yaml` を確認し、もう一方も `done` であれば `patent-analysis` に進める。まだであれば待機する。
- 分析・レポート完了時は、結果要約をユーザーに提示し、承認を得てから次工程に進む（レビューゲート方式が基本）。全自動連鎖にするかは案件ごと・運用状況に応じて調整可能。

## 6. 案件のアーカイブ

- `status.yaml` の `phase.report` が `done` になった時点で、Claudeはユーザーに「この案件をアーカイブしてよいか」を確認する。
- 承認後、案件フォルダをそのままの構造で `projects/<案件ID>/` から `projects/_archive/<案件ID>/` に移動する。
- `_index.md` の該当行は削除せず、ステータス欄を `archived` に更新する。
- アーカイブ後の案件への再依頼があれば `_archive/` 配下も検索・参照対象に含める。

## 7. ハーネスエンジニアリング（Hooks・LEARNINGS）

CLAUDE.mdやSkillsのプロンプトの工夫だけに頼らず、AIの振る舞いを仕組み（Hooks・検証・記録）側で制約・保証する。

### 7.1 Hooksによる自動検証ゲート（`.claude/settings.json` で登録済み）

| Hook | タイミング | 内容 |
|---|---|---|
| `post_tool_use_validate.sh` | 各出力ファイル書き込み直後 | 必須見出しが揃っているかをチェックし、欠けていればその場で差し戻す |
| `pre_tool_use_guard.sh` | ファイル削除・書き込みの実行前 | `_archive/`配下への削除・上書きや、案件フォルダ命名規則に反する書き込みを実行前に止める |
| `stop_check_status.sh` | セッション終了時 | `status.yaml`と`_index.md`の内容に食い違いがないかを確認する（非ブロッキングの注意喚起） |

これらのスクリプトはGit Bash（`bash`）で実行される想定。動作しない場合はPATHにGit Bashが通っているか確認する。

### 7.2 LEARNINGS.md

`docs/LEARNINGS.md` に運用中の問題と恒久対策を記録する。対策反映時は対応するCLAUDE.md/SKILL.md/Hooksの変更と紐づけて記載する。定期的に見返し、蓄積された対策をこのCLAUDE.mdの恒久ルールに昇格させること。

## 8. 非機能要件・運用ルール

- このフォルダはGitで管理し、構成変更時に差分を追跡・ロールバック可能にする。
- 構成変更を行う場合は、このCLAUDE.mdを必ず同時に更新し、次回セッション以降も新ルールが反映されるようにする。

## 9. 将来的な拡張候補

- market-research スキルへの社内データソース（MCP経由）連携
- 出力ファイルのフォーマットのテンプレート固定化（スキル間の受け渡し精度向上）
- 評価用サブエージェント、カスタムスラッシュコマンドによる定型エントリポイントの導入
