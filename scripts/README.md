# scripts/（グラフ生成ヘルパー）

`patent-research` / `market-research` / `patent-analysis` の各スキルが出力ファイルにグラフ（PNG画像）を埋め込むための共通ヘルパー。

## セットアップ（初回のみ）

```
pip install -r scripts/requirements.txt
```

matplotlibをインストールする。Pythonは `patent-mcp` とは独立しており、venvを分けずシステムのPython（3.10+推奨）にインストールする想定。

## 使い方

各スキルは案件ごとの実データを持って `chart_utils.py` の関数を呼ぶ短いPythonスクリプトをその場で作成・実行する（データは案件ごとに異なるため、このディレクトリ自体には案件固有のデータを置かない）。

```python
import sys
sys.path.insert(0, "scripts")
from chart_utils import save_line_chart, save_bar_chart, save_pie_chart

save_line_chart(
    x=["2019", "2020", "2021", "2022", "2023"],
    series={"出願件数": [12, 18, 25, 31, 40]},
    title="出願推移",
    xlabel="出願年",
    ylabel="件数",
    output_path="projects/<案件ID>/01_research/patent/charts/filing_trend.png",
)
```

## 提供する関数（`chart_utils.py`）

| 関数 | 用途の例 |
|---|---|
| `save_line_chart` | 出願推移（年次件数）、市場規模の成長推移 |
| `save_bar_chart` | 出願人ランキング、カテゴリ別件数比較（`horizontal=True`で横棒） |
| `save_pie_chart` | 技術分類の構成比など |

## 出力先の規約

生成したPNGは各フェーズの出力ファイルと同じ階層の `charts/` サブフォルダに保存し、出力Markdownからは相対パスの画像リンク（例: `![出願推移](charts/filing_trend.png)`）で参照する。

- `projects/<案件ID>/01_research/patent/charts/`
- `projects/<案件ID>/01_research/market/charts/`
- `projects/<案件ID>/02_analysis/charts/`

この規約に従うことで、`patent-report` スキルがdocxレポート作成時に `charts/` 配下の画像をまとめて埋め込める。

## 日本語フォントについて

`chart_utils.py` の `setup_japanese_font()` が、Windows標準搭載の日本語フォント（Yu Gothic → Meiryo → MS ゴシックの優先順）を自動検出してmatplotlibに登録する。フォントが1つも見つからない環境では日本語ラベルが文字化けする可能性があるため、その場合は先にフォントの存在を確認すること。
