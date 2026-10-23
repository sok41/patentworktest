# patent-projects 運用ルール

このリポジトリは、特許調査・市場調査・分析・レポート作成を一連のプロジェクトとしてClaude Code上で実行するためのものです。詳細な背景・設計意図は [特許調査プロジェクト_要件定義書.md](./特許調査プロジェクト_要件定義書.md) を参照してください。このファイルはその要件定義書に基づく「恒久的な運用ルール」を集約したものです。

## 1. 全体方針

- 調査（特許・市場）、分析、レポート作成はそれぞれ独立したスキル（`.claude/skills/`）として実装されている。
- 特許調査と市場調査は並行実行可能。分析スキルは**両方の結果が揃ってから**着手する。
- スキル自体は使い回し、案件ごとのデータは `projects/<案件ID>/` 単位で管理する。
- 案件の始め方には2通りある（どちらもClaudeが `projects/_template/` をもとに自動生成し、ユーザーが手動でフォルダ操作する必要はない）。
  1. ユーザーが調査観点の具体的な中身と共に依頼した場合: `00_overview.md` への記入まで一括で行う。
  2. ユーザーが案件名だけで「プロジェクトを作成して」と依頼した場合: `project-create` スキルで空の案件フォルダだけを作成し、`00_overview.md` はユーザーが後で手動記入する。
- 案件に対する調査の開始は `research-kickoff` スキルが担う。対象案件をユーザーに確認したうえで、`patent-research`/`market-research` を**並列のサブエージェントとして同時に**起動し、両方完了してから `patent-analysis` に引き継ぐ（詳細は4.1節）。

## 2. ディレクトリ構成

```
patent-projects/                         # このリポジトリのルート
├── CLAUDE.md                            # このファイル
├── .mcp.json                            # 特許データベースMCPサーバー接続設定
├── .claude/
│   ├── settings.json                    # hooksの登録
│   ├── skills/
│   │   ├── project-create/SKILL.md      # 案件フォルダの新規作成（概要なし）
│   │   ├── research-kickoff/SKILL.md    # 調査開始オーケストレーション（並列起動）
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
├── patent-mcp/                          # 特許MCPサーバー本体（Python, EPO OPS連携）
│   ├── README.md                        # セットアップ手順
│   ├── .env                             # OPS_CONSUMER_KEY/SECRET（Git管理外）
│   └── src/patent_mcp/                  # search_patents / get_bibliographic_data ツール
└── scripts/                             # グラフ生成ヘルパー（matplotlib、3.5節参照）
    ├── README.md
    ├── requirements.txt
    └── chart_utils.py
```

## 3. MCPサーバー接続について

- 特許データベースへの検索実行は、`patent-mcp/`（EPO Open Patent Services = OPS を利用、Espacenetの背後にあるAPI）経由で行う。接続設定は `.mcp.json` にプロジェクトスコープで記載している（サーバー名: `patent-search-mcp`、`patent-mcp/.venv/Scripts/python.exe -m patent_mcp` を起動）。
- 初回利用前に `patent-mcp/README.md` の手順に従い、`patent-mcp/.env` に developers.epo.org で発行したConsumer Key/Secretを記入し、`uv sync` で依存関係をインストールする必要がある。
- プロジェクトスコープのMCPサーバーは初回起動時に承認が必要。
- APIキー等の認証情報は `patent-mcp/.env`（Git管理外）にのみ保持し、`.mcp.json` や他のファイルに直接書かない。
- `patent-research` スキルはMCP未接続・未承認（`.env`未設定含む）の場合、エラーにせずユーザーに接続を促す（`search_patents`/`get_bibliographic_data`は `[MCP未接続]` というテキストを返す）。

## 4. 案件管理

- 案件ID命名規則: `YYYY-MM-DD_案件名スラッグ`（例: `2026-09-14_ドローン特許調査`）
- 新規案件は `projects/_template/` をコピーして作成する（1章の2通りの始め方を参照。`project-create` はフォルダ作成のみ、概要付き依頼は `status.yaml`/`00_overview.md` への記入まで一括で行う）。
- `projects/_index.md` に案件ID・案件名・現フェーズ・更新日を一覧管理する。各スキルは担当フェーズ完了時にここを追記更新する。

### 4.1 調査開始のオーケストレーション（並列実行）

- 「〇〇についての調査・分析を開始して」のように調査開始を指示されたら `research-kickoff` スキルを使う。
- `research-kickoff` は、まず `projects/` 配下から対象案件を名前で特定し、複数/0件の場合はユーザーに確認・選択させる。一致が1件なら「`<案件ID>` プロジェクトでよいか」をユーザーに確認してから着手する。無断で複数案件から1つを決め打ちしない。
- 確認が取れたら、`patent-research` と `market-research` をAgentツールで**同一レスポンス内で同時に**サブエージェント起動する（`subagent_type: general-purpose`。それぞれのSKILL.mdを読んで従うよう指示する）。両方が完了するのを待ってから、メインセッション側で `status.yaml` を確認し `patent-analysis` に引き継ぐ。
- 各調査スキル自身が「もう一方が完了していれば分析に進める」と提案してくることがあるが、実際に次工程を呼び出す判断は常にメインセッション（オーケストレーション側）が行う。並列実行中に分析が二重起動するのを防ぐため。

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

- `Notification`（ユーザーへの確認待ち発生時）・`Stop`（セッション終了時）のタイミングでWindowsの通知音を再生するHookも`.claude/settings.json`に登録している（`stop_check_status.sh`の実行後、追加で音を鳴らす）。VSCode拡張機能利用時はWindows環境で`Notification`フックが発火しない既知の不具合があるため、本運用はターミナル（CLI）利用を前提とする。

### 7.2 LEARNINGS.md

`docs/LEARNINGS.md` に運用中の問題と恒久対策を記録する。対策反映時は対応するCLAUDE.md/SKILL.md/Hooksの変更と紐づけて記載する。定期的に見返し、蓄積された対策をこのCLAUDE.mdの恒久ルールに昇格させること。

### 7.3 スキルのバージョン管理

- 各スキルのSKILL.mdフロントマターに `metadata.version`（セマンティックバージョニング `major.minor.patch`）と `metadata.last_updated` を記載する。SKILL.mdの内容を変更した際は必ずこの2項目を更新する。
- 記載例:

```yaml
---
name: patent-research
description: ...
metadata:
  version: "1.0.0"
  last_updated: "2026-09-25"
---
```

- 各スキルフォルダに `CHANGELOG.md` を置き、バージョンごとの変更内容を記録する（`docs/LEARNINGS.md` の恒久対策と紐づけて記載する）。
- `patent-report` は最終レポート（docx）の末尾に、実際に使用した各スキル（`patent-research`/`market-research`/`patent-analysis`/`patent-report`自身）の`name`と`metadata.version`を「使用スキル」一覧として記載する。これにより、どのバージョンのスキルで作成されたレポートかを事後的に追跡できる。

### 7.4 スクリプトの同梱とPython実行環境

- ダウンロードしたデータの整形・重複除去・グラフ生成など「毎回同じ処理であるべきもの」は、その都度コードを書かせるのではなく、スキル配下（または`scripts/`共通フォルダ）にPythonスクリプトとして同梱し、SKILL.mdからそのスクリプトを実行するよう指示する。これにより実行のたびの処理のブレを防ぎ、再現性を担保する。
- スクリプト実行前に`python --version`（またはそれに準ずるコマンド）でPythonがインストール済みか確認する。未インストールの場合、無言でインストールを進めず、ユーザーに「Pythonがインストールされていないためインストールします。よろしいですか」と確認したうえで進める（システムへの変更を伴うため実行前の確認を必須とする）。必要なライブラリ（pandas、matplotlib等）が不足している場合も同様に、インストール前にユーザーへ確認する。

## 8. 非機能要件・運用ルール

- このフォルダはGitで管理し、構成変更時に差分を追跡・ロールバック可能にする。
- 構成変更を行う場合は、このCLAUDE.mdを必ず同時に更新し、次回セッション以降も新ルールが反映されるようにする。
- 将来的に特許調査・分析以外の業務（出願前調査・中間処理対応等）を追加する場合、業務固有の詳細ルールは`projects/<業務名>/README.md`に記載し、CLAUDE.mdからは参照のみ行う方針とする（業務追加によるCLAUDE.mdの肥大化を防ぐ。詳細は9章）。現時点は本業務（特許調査・分析）のみのため、詳細ルールは引き続きこのCLAUDE.mdに集約している。

### 8.1 グラフ・視覚情報について

- 調査・分析結果は文章だけでなく、可能な限りグラフ（画像）で視覚化する。特に以下は必須／推奨とする。
  - `patent-research`: 出願推移（年次）、出願人ランキングのグラフ化は**必須**（`post_tool_use_validate.sh` が画像埋め込みの有無を機械的にチェックする）。
  - `market-research`: 市場規模の成長推移が複数時点で得られた場合はグラフ化する（単一時点しかない場合は省略可、その旨を明記）。主要プレイヤーには近年の開発動向・トピックスを必ず添える。
  - `patent-analysis`: 技術動向分類・競合マッピング等を推奨でグラフ化する。
  - `patent-report`: 各フェーズで生成済みのグラフ画像をdocxレポートに埋め込む。
- グラフ生成は `scripts/chart_utils.py`（matplotlib）の共通ヘルパーを使う。初回のみ `pip install -r scripts/requirements.txt` が必要（詳細は [scripts/README.md](./scripts/README.md)）。日本語ラベルはWindows標準の日本語フォントを自動検出して描画する。
- 生成した画像は各フェーズ配下の `charts/` サブフォルダに保存し、出力Markdownからは相対パスの画像リンクで参照する（規約の詳細は `scripts/README.md`）。

## 9. 将来的な拡張候補（複数業務プロジェクトへの拡張ロードマップ）

[特許調査プロジェクト_要件定義書.md](./特許調査プロジェクト_要件定義書.md) 3章では、特許権利化業務には本プロジェクト（特許調査・分析）以外にも「出願前調査」「中間処理対応」等があるため、それらを将来追加できる構成への拡張を計画している。**以下は計画段階であり、まだ未実施**（現状は単一業務・フラット構成のまま）。着手する際はこのCLAUDE.mdと合わせて段階的に反映する。

- `projects/`を業務ライン別に分割し、現行の`projects/_index.md`・`_template/`・`_archive/`・案件フォルダを`projects/analysis/`配下にネストする。`projects/prefiling-search/`・`projects/office-action/`等を業務追加時に新設する。
- スキル名に業務プレフィックスを付ける（例: `patent-research`→`analysis-patent-research`）。オーケストレーション系スキル（`project-create`/`research-kickoff`）は業務横断で使うため、プレフィックスなしの共通スキルとして維持する方針。
- `patent-mcp`（特許MCPサーバー本体）は将来的に本リポジトリ外の独立リポジトリとして管理し、`.mcp.json`から絶対パス／インストール済みコマンドで参照する（現状はリポジトリ内`patent-mcp/`に同梱・相対パス参照）。
- 新しい業務プロジェクトを追加する手順（着手時の参考。詳細は要件定義書12章）:
  1. `projects/<業務名>/`フォルダを作成し、`_index.md`・`_template/`・`_archive/`を用意する。
  2. `.claude/skills/`直下に当該業務のプレフィックスを付けたスキルフォルダを追加する。
  3. `projects/<業務名>/README.md`に業務固有のルールを記載する。
  4. CLAUDE.mdには業務追加の旨と当該README.mdへの参照のみ追記する。
  5. 1案件でテスト運用し、必要に応じてHooksの検証ルールやLEARNINGS.mdに知見を反映する。
- market-research スキルへの社内データソース（MCP経由）連携
- 出力ファイルのフォーマットのテンプレート固定化（スキル間の受け渡し精度向上）
- 評価用サブエージェント、カスタムスラッシュコマンドによる定型エントリポイントの導入
