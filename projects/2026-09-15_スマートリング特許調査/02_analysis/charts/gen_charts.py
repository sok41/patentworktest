import sys
sys.path.insert(0, r"C:\Users\lemon\dev\013_PatentAnalyze\scripts")
from chart_utils import save_pie_chart, save_bar_chart

OUT_DIR = r"C:\Users\lemon\dev\013_PatentAnalyze\projects\2026-09-15_スマートリング特許調査\02_analysis\charts"

# 技術動向分類（対象特許リスト20件を5カテゴリに分類）
labels = ["生体センシング", "装着感・フォームファクタ", "通信・連携", "バッテリー・充電", "UI/UX（限定操作系）"]
values = [7, 4, 3, 3, 3]

save_pie_chart(
    labels=labels,
    values=values,
    title="技術動向分類（対象特許リスト20件の内訳）",
    output_path=OUT_DIR + r"\tech_category_breakdown.png",
)

# 競合マッピング：市場側の主要プレイヤーが、特許サンプル67件中にどれだけ
# 自社出願を持つか（0件＝Ouraの特許訴訟で被告となっている企業が大半）
labels2 = [
    "Samsung",
    "Oura Health",
    "Ultrahuman",
    "Huawei",
    "RingConn",
    "Circular",
    "Renpho US",
    "Noise",
    "boAt",
    "Zepp Health(Amazfit)",
    "Reebok",
    "Nexxbase(Luna)",
]
values2 = [3, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]

save_bar_chart(
    labels=labels2,
    values=values2,
    title="市場主要プレイヤーの特許保有状況（特許サンプル67件中の出現件数）",
    category_label="市場プレイヤー",
    value_label="件数（サンプル）",
    output_path=OUT_DIR + r"\market_player_patent_mapping.png",
    horizontal=True,
)

print("done")
