---
name: patent-research
description: 案件の00_overview.mdにある特許調査観点をもとに検索式を作成し、特許MCPサーバー経由で検索を実行して結果を整理する。「特許調査して」「patent-research」「案件の特許調査を始めたい」といった依頼で使用する。
---

# patent-research（特許調査スキル）

## 入力

- 案件フォルダ内 `00_overview.md` の「特許調査観点」セクション
  （対象技術分野／対象出願人・競合／対象期間／その他の指定条件）

## 処理手順

1. `00_overview.md` の特許調査観点を読み取る。記入が不十分な場合はユーザーに確認する。
2. 検索式を作成する。既存の **patsnap-search-formula** スキル（本プロジェクト外に存在する前提）を内部利用できる場合はそれを呼び出す。利用できない場合はその旨をユーザーに伝えた上で、簡易的な検索式を自分で組み立てる。
3. `.mcp.json` で接続された `patent-search-mcp` サーバー経由で検索を実行する。
   - MCPサーバーが未接続・未承認の場合はエラーで停止せず、「特許MCPサーバーが未接続/未承認です。接続を承認してください」とユーザーに伝えて処理を止める（`status.yaml` は更新しない）。
4. ヒットした特許をリスト化し、各特許のサマリ（概要・注目ポイント）を作成する。

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

- 認証情報（APIキー等）は個人で保持せず、MCPサーバー側で一元管理される方針に従う。ここでキーの直接入力を求めない。
