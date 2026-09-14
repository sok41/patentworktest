---
name: market-research
description: 案件の00_overview.mdにある市場調査観点をもとに、市場規模・主要プレイヤー・トレンドをWeb調査して整理する。「市場調査して」「market-research」「案件の市場調査を始めたい」といった依頼で使用する。
---

# market-research（市場調査スキル）

## 入力

- 案件フォルダ内 `00_overview.md` の「市場調査観点」セクション
  （対象市場・製品領域／知りたいこと（市場規模／プレイヤー／トレンド等）／その他の指定条件）

## 処理手順

1. `00_overview.md` の市場調査観点を読み取る。記入が不十分な場合はユーザーに確認する。
2. Web検索等により、市場規模・主要プレイヤー・トレンドを調査する。
3. 出典（参考URL）を必ず記録する。

## 出力

- `01_research/market/market_research_output.md`
  - 市場規模
  - 主要プレイヤー
  - トレンド
  - 出典・参考URL

出力時は `projects/_template/01_research/market/market_research_output.md` の見出し構成を維持すること（`post_tool_use_validate.sh` が必須見出しの有無をチェックする）。

## 完了時の処理

1. `status.yaml` の `phase.market_research` を `done` に更新する。
2. `projects/_index.md` の当該案件行を更新する。
3. `status.yaml` を確認し、`phase.patent_research` も `done` であれば `patent-analysis` スキルへの着手をユーザーに提案する。まだ `done` でなければ、特許調査の完了を待つ旨を伝えて待機する。

## 将来的な拡張候補

- 社内データソース（MCP経由）との連携（要件定義書10章参照）
