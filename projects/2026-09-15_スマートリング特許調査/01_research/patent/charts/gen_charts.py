import sys
sys.path.insert(0, r"C:\Users\lemon\dev\013_PatentAnalyze\scripts")
from chart_utils import save_line_chart, save_bar_chart

OUT_DIR = r"C:\Users\lemon\dev\013_PatentAnalyze\projects\2026-09-15_スマートリング特許調査\01_research\patent\charts"

# 出願推移（公開年ベース、サンプル67件の集計。2026年は1-8月分のみ）
years = ["2015", "2016", "2017", "2018", "2019", "2020-2021", "2022", "2023", "2024", "2025", "2026(1-8月)"]
counts = [4, 2, 1, 2, 1, 0, 1, 6, 6, 1, 43]

save_line_chart(
    x=years,
    series={"サンプル件数": counts},
    title="スマートリング関連特許の公開件数推移（サンプル67件、母集団270件）",
    xlabel="公開年",
    ylabel="件数（サンプル）",
    output_path=OUT_DIR + r"\filing_trend.png",
)

# 出願人ランキング（上位10、サンプル内の出現件数）
labels = [
    "Samsung Electronics",
    "Oura Health Oy",
    "High Distinction Optics(TW)",
    "Ceraart(KR)",
    "Plume Design",
    "Huawei Technologies",
    "Sky Labs(KR)",
    "LG Energy Solution",
    "BMW",
    "Senbiosys(CH)",
]
values = [3, 2, 2, 2, 2, 1, 1, 1, 1, 1]

save_bar_chart(
    labels=labels,
    values=values,
    title="出願人ランキング（サンプル67件中の上位、同数は代表例を掲載）",
    category_label="出願人",
    value_label="件数（サンプル）",
    output_path=OUT_DIR + r"\applicant_ranking.png",
    horizontal=True,
)

print("done")
