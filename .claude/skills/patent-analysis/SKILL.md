---
name: patent-analysis
description: 特許調査結果と市場調査結果の両方が揃った案件について、技術動向分類・競合マッピング・ホワイトスペース分析等を行う。「分析して」「patent-analysis」「特許と市場の突き合わせをして」といった依頼で使用する。
metadata:
  version: "1.0.0"
  last_updated: "2026-09-25"
---

# patent-analysis（分析スキル）

## 前提条件

`status.yaml` の `phase.patent_research` と `phase.market_research` が**両方とも `done`** であること。
片方のみ完了している場合は分析に着手せず、未完了の工程を待つ旨をユーザーに伝えて待機する。

## 入力

- `01_research/patent/research_output.md`
- `01_research/market/market_research_output.md`

## 処理手順

1. 前提条件（両フェーズ `done`）を `status.yaml` で確認する。
2. 特許調査結果から技術動向を分類する。
3. 市場調査結果から得た主要プレイヤーと、特許出願人を突き合わせて競合マッピングを行う。
4. 市場の注目領域と特許出願状況を突き合わせ、ホワイトスペース（手薄な領域）を分析する。
5. 総括・示唆をまとめる。
6. **グラフ生成（推奨）**: 文章だけでなく視覚情報を積極的に補う。特に以下は可能な範囲で図・グラフ化する。
   - 技術動向分類: カテゴリ別の特許件数を `scripts/chart_utils.py` の `save_bar_chart` または `save_pie_chart` で構成比・件数比較にする。
   - 競合マッピング: 出願人（特許側）×主要プレイヤー（市場側）の件数を `save_bar_chart` 等で比較できる形にする（単純な表よりグラフの方が把握しやすい場合）。
   - `01_research/patent/charts/` にすでにある出願推移・出願人ランキングのグラフも、分析の文脈で再利用・参照してよい。
   - 生成したPNGは `02_analysis/charts/` に保存し、`analysis_output.md` から画像リンクで埋め込む。
   - 初回利用時は `pip install -r scripts/requirements.txt` が必要（詳細は [scripts/README.md](../../../scripts/README.md)）。

## 出力

- `02_analysis/analysis_output.md`
  - 技術動向分類（可能な範囲でグラフを含む）
  - 競合マッピング（可能な範囲でグラフを含む）
  - 市場×特許の突き合わせ（ホワイトスペース分析等）
  - 総括・示唆

出力時は `projects/_template/02_analysis/analysis_output.md` の見出し構成を維持すること（`post_tool_use_validate.sh` が必須見出しの有無をチェックする）。

## 完了時の処理

1. `status.yaml` の `phase.analysis` を `done` に更新する。
2. `projects/_index.md` の当該案件行を更新する。
3. 分析結果の要約をユーザーに提示し、承認を得てから `patent-report` スキルに進む（レビューゲート方式が基本。全自動連鎖にするかは案件ごとに調整可能）。
