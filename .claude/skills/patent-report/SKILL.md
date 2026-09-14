---
name: patent-report
description: 分析結果（analysis_output.md）をもとに最終レポート（docx）を作成する。「レポート作成して」「patent-report」「最終レポートをまとめて」といった依頼で使用する。
---

# patent-report（レポート作成スキル）

## 前提条件

`status.yaml` の `phase.analysis` が `done` であること。

## 入力

- `02_analysis/analysis_output.md`（必要に応じて `01_research/` 配下の調査結果も参照する）

## 処理手順

1. 分析結果を読み込み、レポート構成案を作成する。
2. docxスキル（Claude Code標準のドキュメント生成機能）を用いてレポートを整形する。
3. 必要に応じて特許リストや出典を補足資料として添付する。

## 出力

- `03_report/final_report.docx`

## 完了時の処理

1. `status.yaml` の `phase.report` を `done` に更新する。
2. `projects/_index.md` の当該案件行を更新する。
3. レポート内容の要約をユーザーに提示し、承認を得る（レビューゲート方式）。
4. `report` が `done` になった時点で、案件をアーカイブしてよいかをユーザーに確認する（要件定義書7章）。承認後、案件フォルダを `projects/<案件ID>/` から `projects/_archive/<案件ID>/` にそのままの構造で移動し、`_index.md` の該当行のステータスを `archived` に更新する（行自体は削除しない）。
