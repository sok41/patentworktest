---
name: patent-research
description: 案件の00_overview.mdにある特許調査観点をもとにCQL検索式を作成し、patent-mcp（EPO OPS経由の特許MCPサーバー）で検索を実行して結果を整理する。「特許調査して」「patent-research」「案件の特許調査を始めたい」といった依頼で使用する。
---

# patent-research（特許調査スキル）

## 入力

- 案件フォルダ内 `00_overview.md` の「特許調査観点」セクション
  （対象技術分野／対象出願人・競合／対象期間／その他の指定条件）

## 使用するMCPサーバー

`patent-mcp`（`.mcp.json` の `patent-search-mcp`。EPO Open Patent Services = OPS 経由）を使う。提供されるツールは以下の2つ（詳細は `patent-mcp/README.md` 参照）。

| ツール | 用途 |
|---|---|
| `search_patents(query, range_begin=1, range_end=25)` | OPSのCQL検索式で特許を検索する |
| `get_bibliographic_data(patent_number, input_format="docdb", constituents="biblio,abstract")` | 特許番号から書誌情報・要約を取得する |

MCPサーバーが未接続・未承認、または `patent-mcp/.env` にキー未設定の場合、ツールはエラーで落ちずに `[MCP未接続] ...` というテキストを返す。その場合は処理を止め、接続・設定を促す旨をユーザーに伝える（`status.yaml` は更新しない）。

## 処理手順

1. `00_overview.md` の特許調査観点を読み取る。記入が不十分な場合はユーザーに確認する。
2. 特許調査観点をもとに、OPSのCQL検索式を自分で組み立てる。主なフィールドコード:
   - `ti=` タイトル / `ab=` 要約 / `ti,ab=` 両方
   - `pa=` 出願人・権利者（例: `pa="ACME Corp"`）
   - `in=` 発明者
   - `ic=` / `cpc=` IPC・CPC分類
   - `pd within "YYYY-YYYY"` 公開日の範囲
   - `AND` `OR` `NOT` で組み合わせ可能（例: `ti=drone AND pd within "2020-2026"`）
   詳細な構文は [OPS CQLシンタックス](https://www.epo.org/en/searching-for-patents/data/web-services/ops) を参照。
3. `search_patents` で検索を実行する。ヒット件数が多すぎる／少なすぎる場合は検索式を調整して再実行する。
4. ヒットした特許の中から調査観点に合致するものを選び、`get_bibliographic_data` で書誌・要約を取得する。
   - `patent_number` は `search_patents` の結果に含まれる `country`/`doc-number`/`kind` を `.` で連結した docdb 形式（例: `EP.4803425.A1`）で渡すこと。epodoc形式にkindコードを付けると見つからない場合があるため使わない。
5. ヒットした特許をリスト化し、各特許のサマリ（概要・注目ポイント）を作成する。

## 出力

- `01_research/patent/research_output.md`
  - 使用した検索式
  - 対象特許リスト（特許番号／出願人／出願日／タイトル）
  - 各特許のサマリ
  - 出典・参考URL

出力時は `projects/_template/01_research/patent/research_output.md` の見出し構成を維持すること（`post_tool_use_validate.sh` が必須見出しの有無をチェックする）。

## 完了時の処理

1. `status.yaml` の `phase.patent_research` を `done` に更新する。
2. `projects/_index.md` の当該案件行を更新する。
3. `status.yaml` を確認し、`phase.market_research` も `done` であれば `patent-analysis` スキルへの着手をユーザーに提案する。まだ `done` でなければ、市場調査の完了を待つ旨を伝えて待機する。

## 備考

- 認証情報（APIキー等）は個人で保持せず、`patent-mcp/.env` にのみ保持する方針に従う。ここでキーの直接入力を求めない。
