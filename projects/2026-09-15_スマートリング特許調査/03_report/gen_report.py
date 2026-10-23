# -*- coding: utf-8 -*-
"""
final_report.docx 生成スクリプト（案件: 2026-09-15_スマートリング特許調査）
python-docx を用いて、調査観点・特許調査・市場調査・分析結果を1つのdocxにまとめる。
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

PROJECT_DIR = r"C:\Users\lemon\dev\013_PatentAnalyze\projects\2026-09-15_スマートリング特許調査"
PATENT_CHARTS = os.path.join(PROJECT_DIR, r"01_research\patent\charts")
MARKET_CHARTS = os.path.join(PROJECT_DIR, r"01_research\market\charts")
ANALYSIS_CHARTS = os.path.join(PROJECT_DIR, r"02_analysis\charts")
OUT_PATH = os.path.join(PROJECT_DIR, r"03_report\final_report.docx")

doc = Document()

# --- 既定フォントを日本語対応に -----------------------------------------
style = doc.styles["Normal"]
style.font.name = "Yu Gothic"
style.font.size = Pt(10.5)
rpr = style.element.get_or_add_rPr()
rFonts = rpr.find(qn("w:rFonts"))
if rFonts is None:
    from docx.oxml import OxmlElement
    rFonts = OxmlElement("w:rFonts")
    rpr.append(rFonts)
rFonts.set(qn("w:eastAsia"), "Yu Gothic")


def add_heading(text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.name = "Yu Gothic"
        run.font.color.rgb = RGBColor(0x1F, 0x1F, 0x1F)
        r = run._element.rPr.rFonts
        r.set(qn("w:eastAsia"), "Yu Gothic")
    return h


def add_para(text, bold=False, size=10.5):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = "Yu Gothic"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Yu Gothic")
    return p


def add_bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    run = p.add_run(text)
    run.font.name = "Yu Gothic"
    run.font.size = Pt(10.5)
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Yu Gothic")
    return p


def add_image(path, width_cm=15):
    if os.path.exists(path):
        doc.add_picture(path, width=Cm(width_cm))
        last = doc.paragraphs[-1]
        last.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        add_para(f"[画像が見つかりません: {path}]")


def add_table(headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = str(h)
        for p in hdr_cells[i].paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.size = Pt(9.5)
                r.font.name = "Yu Gothic"
                r._element.rPr.rFonts.set(qn("w:eastAsia"), "Yu Gothic")
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)
            for p in cells[i].paragraphs:
                for r in p.runs:
                    r.font.size = Pt(9)
                    r.font.name = "Yu Gothic"
                    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Yu Gothic")
    doc.add_paragraph()
    return table


# =========================================================================
# 表紙
# =========================================================================
title = doc.add_heading("スマートリング特許調査 最終レポート", level=0)
for run in title.runs:
    run.font.name = "Yu Gothic"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Yu Gothic")

add_para("案件ID: 2026-09-15_スマートリング特許調査")
add_para("作成日: 2026-09-15")
add_para("目的: 自社でのスマートリング分野への参入検討・特許性確認のための情報収集")
doc.add_page_break()

# =========================================================================
# 1. 調査概要
# =========================================================================
add_heading("1. 調査概要", level=1)
add_para(
    "本レポートは、スマートリング関連技術全般（生体センシング、通信、バッテリー・充電、装着感・"
    "フォームファクタ、UI/UXを含む）を対象に、特許調査・市場調査を実施し、その結果を突き合わせた"
    "分析結果をまとめたものである。"
)
add_para("特許調査観点", bold=True)
add_bullet("対象技術分野: スマートリング関連技術全般（技術分野を広く俯瞰）")
add_bullet("対象出願人・期間: 指定なし（調査の中で主要出願人・直近動向を把握）")
add_para("市場調査観点", bold=True)
add_bullet("対象市場: スマートリング（ワールドワイド）")
add_bullet("知りたいこと: 市場規模・成長率を中心に、主要プレイヤーの動向を把握")

# =========================================================================
# 2. 特許調査結果
# =========================================================================
add_heading("2. 特許調査結果", level=1)

add_heading("2.1 検索式・検索結果", level=2)
add_para("EPO Open Patent Services（OPS）を用い、以下のCQL検索式でワールドワイドの公開特許を検索した。")
p = doc.add_paragraph()
run = p.add_run('(ti="smart ring" OR ab="smart ring") AND pd within "2015-2026"')
run.font.name = "Consolas"
run.font.size = Pt(10)
add_bullet("総ヒット件数: 270件")
add_bullet(
    "書誌情報（公開年・出願人）取得のため、層化サンプリングにより67件の書誌データを取得し集計に使用（悉皆調査ではない）"
)

add_heading("2.2 出願推移", level=2)
add_image(os.path.join(PATENT_CHARTS, "filing_trend.png"))
add_para(
    "2023年以降にスマートリング関連特許の公開件数が明確に増加しており、Oura・Samsung・Huawei等の"
    "コンシューマー向け製品普及と時期が符合する。"
)

add_heading("2.3 出願人ランキング", level=2)
add_image(os.path.join(PATENT_CHARTS, "applicant_ranking.png"))
add_para(
    "Samsung Electronicsが最多（サンプル中3件）で、Oura Health・High Distinction Optics・Ceraart・"
    "Plume Designが2件で続く。個人・大学・中小スタートアップによる単発出願も多く、参入障壁が低い"
    "黎明期市場である様子がうかがえる。"
)

add_heading("2.4 対象特許リスト（技術分野横断で20件を深掘り）", level=2)
patent_rows = [
    ["WO2026106176 A1", "Sky Labs Inc（韓国）", "2025-10-27", "Smart Ring Device for Electrocardiography"],
    ["WO2026079901 A1 / KR20260050909 A", "Samsung Electronics", "2025-10-02", "Smart Ring Device for Identifying Posture of User"],
    ["KR102981847 B1", "韓林大学校産学協力団", "2025-07-25", "Smart Ring-Based Patient Monitoring System"],
    ["CN122161541 A", "Ultrahuman Health Pty Ltd", "2025-08-07", "Replaceable Sensor Assembly Intelligent Ring"],
    ["MA70860 A1", "Univ. Euro-Méditerranéenne de Fès", "2025-02-21", "AIによる急性冠症候群早期検知スマートリング"],
    ["WO2026172136 A1", "個人（イラン）", "2025-04-17", "UVセンサ搭載・皮膚がんリスク評価スマートウェアラブル"],
    ["US20260060604 A1", "Senbiosys（スイス）", "2025-09-03", "マイクロ流体式発汗コレクター搭載リング"],
    ["DE102024121837 A1", "BMW", "2024-07-31", "スマートリング経由の車両アクセス（デジタルキー）"],
    ["US20260023426 A1 / WO2026020042 A1", "Oura Health Oy", "2025-07-16", "複数ウェアラブル連携（スマートリング×ARグラス）"],
    ["KR20260112914 A", "Connected In Corp", "2025-10-31", "スマートリング基盤の糖尿病患者行動・アラーム管理"],
    ["KR102919103 B1", "Creativemut Co Ltd", "2025-06-04", "NFC搭載アーティストアルバム連携リング"],
    ["WO2026157625 A1", "華為技術（Huawei）", "2025-12-11", "形状記憶合金採用リングハウジング（サイズ可変）"],
    ["KR102941362 B1", "Remotesolution Co Ltd", "2025-07-18", "スペーサー式指囲調整スマートリング"],
    ["KR102909808 B1 / 102909809 B1", "Ceraart Co Ltd", "2024-10-30", "偏心輪による内径調整スマートリング（通気性改善）"],
    ["US20260090614 A1", "個人（インド）", "2025-10-08", "非導電性・指囲可変スマートリング（決済・安全解除機構）"],
    ["CA245659 S", "Shenzhen Shufang Innovation Tech", "2025-11-14", "スマートリング用充電ベース（意匠）"],
    ["KR20260042642 A", "LG Energy Solution", "2024-09-23", "ヒンジ構造バッテリー搭載スマートリング"],
    ["DE202025107600 U1", "Shenzhen Chenbei Technology", "2025-12-10", "リング周方向溝にバッテリーを収納する構造"],
    ["WO2026067894 A1", "Shenzhen Arcension Technology", "2025-11-20", "回転＋押下の二段階操作トリガー機構（UI/UX）"],
    ["CN122450282 A", "Lok Rocket Corp", "2025-01-22", "押下回数に応じた動作モード切替（UI/UX）"],
]
add_table(["特許番号", "出願人", "出願日", "タイトル"], patent_rows)

add_para(
    "各特許の詳細サマリは 01_research/patent/research_output.md を参照。技術的注目点として、"
    "電気的バイオシグナル計測（Sky Labs）、姿勢推定UI（Samsung）、交換可能センサー構造（Ultrahuman）、"
    "発汗バイオマーカー分析（Senbiosys）、車両アクセス連携（BMW）、形状記憶合金ハウジング（Huawei）等、"
    "各社が独自の切り口で差別化を図っている点が挙げられる。"
)

# =========================================================================
# 3. 市場調査結果
# =========================================================================
add_heading("3. 市場調査結果", level=1)

add_heading("3.1 市場規模", level=2)
market_rows = [
    ["GMI Insights", "USD 697.6百万", "USD 1,010百万", "USD 7,800百万（2035年）", "25.4%（2026-2035）"],
    ["Fortune Business Insights", "USD 416.9百万", "USD 518.9百万", "USD 3,772.4百万（2034年）", "29.30%（2026-2034）"],
    ["Grand View Research", "―", "USD 502.4百万", "USD 2,079.3百万（2033年）", "22.5%（2026-2033）"],
    ["Persistence Market Research", "―", "USD 502.7百万", "USD 2,506.5百万（2033年）", "25.8%（2026-2033）"],
    ["Future Market Insights", "USD 300百万（2025推計）", "―", "USD 2,800百万（2035年）", "24.1%（2025-2035）"],
]
add_table(["調査会社", "2025年実績", "2026年予測", "長期予測", "CAGR"], market_rows)
add_para(
    "調査会社ごとに金額水準は異なるが、いずれも年率20〜30%台の高成長で一致している。地域別では"
    "北米が最大市場、アジア太平洋（中国・インド・日本）が最速成長という傾向も各社共通している。"
)

add_heading("3.2 市場規模の推移・予測", level=2)
add_image(os.path.join(MARKET_CHARTS, "market_size_growth.png"))

add_heading("3.3 主要プレイヤー", level=2)
add_para(
    "市場シェア（2025年、GMI Insights推計）: Ouraが単独で約76.4%を占める市場リーダー。"
    "上位5社（Oura、Ultrahuman、Renpho US、Noise、boAt）で合計85.9%。"
)
player_rows = [
    ["Oura Health Oy（フィンランド）", "市場リーダー。2025年10月にUSD 900百万超調達（評価額約110億ドル）、2026年5月にIPO予備申請。Samsung・Zepp Health・Reebok・Noise・Nexxbaseを特許侵害で提訴。"],
    ["Samsung Electronics（韓国）", "Galaxy Ring 2は2027年早期に延期（バッテリー刷新とOura特許係争が要因）。Xealth買収で医療連携プラットフォームに布石。"],
    ["Ultrahuman（インド）", "2026年2月に新モデル「Ring Pro」発表。ITC裁定で一時輸入制限を受けたが2026年3月に再開。2026年9月にQualcomm等からUSD 70百万調達。"],
    ["RingConn（中国系）", "2026年1月に「Gen 3」発表（振動アラート・血管系トレンド分析追加）。サブスク不要モデルを訴求。"],
    ["Circular（フランス）", "2026年9月のIFAで「Ring 3 Pro」「Ring 3 Slim」を発表。過去にOuraから提訴された経緯あり。"],
    ["Zepp Health（Amazfit）／Reebok／Noise／Nexxbase（Luna）", "いずれもOura Healthから特許侵害訴訟（ITC・東テキサス地区連邦地裁）の対象となっている。"],
]
add_table(["プレイヤー", "近年の動向"], player_rows)

add_heading("3.4 主要トレンド", level=2)
add_bullet("ヘルスケア・予防医療シフトの加速（医療・臨床モニタリング用途はCAGR 40.7%と最高水準）")
add_bullet("特許係争の急拡大（Ouraが主要競合を相次いで提訴、業界の参入障壁・設計自由度に直結）")
add_bullet("保険・法人ウェルネス領域との連携拡大（Vida Health、Xealth買収等）")
add_bullet("AI統合・オンデバイスコンピューティングへの進化（Ultrahumanの「リングのコンピュータ化」構想）")
add_bullet("非接触決済（NFC）機能の標準化（Circular Ring 3、Galaxy Ring 2予定等）")
add_bullet("バッテリー・フォームファクタの継続的な進化（長寿命化・小型軽量化競争）")
add_bullet("資金調達の活発化・IPO機運（Oura、Ultrahuman）")
add_bullet("地域展開: 北米が最大市場、アジア太平洋が最速成長（CAGR 26.3%）")

# =========================================================================
# 4. 分析結果
# =========================================================================
add_heading("4. 分析結果", level=1)

add_heading("4.1 技術動向分類", level=2)
add_image(os.path.join(ANALYSIS_CHARTS, "tech_category_breakdown.png"))
tech_rows = [
    ["生体センシング", "7", "Sky Labs（ECG）、韓林大学校、Ultrahuman、Univ. Euro-Méd. Fès、個人・イラン（UV）、Senbiosys（発汗）、Connected In"],
    ["装着感・フォームファクタ", "4", "Huawei（形状記憶合金）、Remotesolution、Ceraart、個人・インド"],
    ["通信・連携", "3", "BMW（車両連携）、Oura（ARグラス連携）、Creativemut（NFC）"],
    ["バッテリー・充電", "3", "Shenzhen Shufang、LG Energy Solution、Shenzhen Chenbei"],
    ["UI/UX（限定操作系）", "3", "Samsung（姿勢推定）、Shenzhen Arcension、Lok Rocket"],
]
add_table(["カテゴリ", "件数", "代表的な出願"], tech_rows)
add_para(
    "生体センシングが最大カテゴリ（35%）だが、内訳は光学式PPGの精緻化ではなくECG・発汗・UV等の"
    "非典型モダリティへの多様化が中心。装着感・フォームファクタでは韓国系中小メーカーが独自方式で"
    "サイズ調整機構を競って特許化している。"
)

add_heading("4.2 競合マッピング", level=2)
add_image(os.path.join(ANALYSIS_CHARTS, "market_player_patent_mapping.png"))
mapping_rows = [
    ["Samsung", "Galaxy Ring展開中", "3", "被告（Ouraを逆提訴）"],
    ["Oura Health", "市場リーダー（シェア約76%）", "2", "原告（コア特許で提訴）"],
    ["Ultrahuman", "市場シェア上位、急成長", "1", "ITC裁定で一時輸入制限"],
    ["Huawei", "スマートウォッチ由来の量産技術", "1", "―"],
    ["RingConn／Circular／Renpho US／Noise／boAt／Zepp Health／Reebok／Nexxbase", "市場シェア上位〜新規参入", "0", "多くが被告（Noise・Zepp Health・Reebok・Nexxbase・Circular）"],
]
add_table(["市場プレイヤー", "市場での位置づけ", "特許サンプル67件中の件数", "Oura特許訴訟での立場"], mapping_rows)
add_para(
    "特許サンプル内で複数件を確保しているのはSamsung・Oura・Ultrahuman・Huaweiという、自社で研究開発"
    "機能を持つ大手のみ。市場シェア上位でも自社特許が確認できないブランドの多くがOuraの特許訴訟で"
    "被告側に回っており、「自社IPを持たずOEM調達等で製品展開しているブランドほど、他社特許の権利"
    "行使リスクに晒されやすい」という構図が読み取れる。"
)

add_heading("4.3 市場×特許の突き合わせ（ホワイトスペース分析）", level=2)
whitespace_rows = [
    ["ヘルスケア・医療モニタリング用途", "CAGR 39.3〜40.7%と最高水準", "生体センシング特許が最多（7/20）。大学・中小発が中心", "需要と特許件数はおおむね対応。大手による非典型モダリティの取り込み余地あり"],
    ["NFC非接触決済", "CAGR 36.3%。標準搭載化が進行", "サンプル中2件のみ", "ホワイトスペース：市場の重要性に対し特許蓄積が薄い"],
    ["バッテリー・駆動時間競争", "各社が駆動時間を訴求", "サンプル中3件。主要ブランド自身の電池技術特許は未確認", "ホワイトスペース：電池セル技術は外部依存の可能性。自社権利化・提携の余地"],
    ["UI/UX（限定操作系）", "「リングのコンピュータ化」で重要性増大", "中国系中小企業3件が中心。大手の厚みは薄い", "ホワイトスペース：独自UI特許で先行者優位を築ける可能性"],
    ["特許係争・基本特許の権利行使", "Oura対大手5社の訴訟が最重要トレンド", "Ouraの基本特許（'178特許等）を軸に訴訟が展開中", "リスク領域：新規参入時はOura基本特許との抵触リスク精査が必須"],
]
add_table(["市場側の注目領域", "市場側の成長性", "特許側の状況", "評価"], whitespace_rows)

add_heading("4.4 総括・示唆", level=2)
add_bullet(
    "市場は2025→2035年でCAGR20〜30%台の高成長が見込まれる一方、特許出願も2023年以降急増しており、"
    "技術開発と権利化が同時並行で進む黎明期にある。今が権利化のタイミングとして重要な局面。"
)
add_bullet(
    "Ouraは市場シェア（約76%）と基本特許の両輪で優位性を構築しており、自社が新規参入・製品開発する"
    "場合はOuraの基本特許との抵触リスク精査を最優先事項とすべき。"
)
add_bullet(
    "市場シェア上位でも自社特許を持たないブランドほどOuraの提訴対象になりやすい構図が見られる。"
    "自社開発時はOEM調達だけに頼らず、自社IPの確保（防御目的を含む）が重要。"
)
add_bullet(
    "ホワイトスペース候補は「NFC決済」「電池セル技術」「UI/UX（限定操作系）」の3領域。"
    "市場側の重要性が高い一方で特許の厚みが相対的に薄く、早期の権利化・技術提携が先行者優位につながる可能性がある。"
)
add_bullet(
    "生体センシングは光学式PPGでの精度競争が成熟しつつあり、ECG・発汗バイオマーカー・UV等の"
    "非典型モダリティへの展開が次の差別化軸になっている。"
)
add_bullet(
    "BMW（デジタルキー）、LG Energy Solution（電池構造）等、異業種・コンポーネントメーカーの参入が"
    "見られ、垂直統合だけでなく他業種との提携・コンポーネント調達戦略も選択肢になり得る。"
)
add_bullet(
    "次の調査への示唆: Ouraの基本特許のクレーム範囲の詳細調査、および出願人ファミリー名寄せによる"
    "悉皆的な出願人ランキングの精緻化が、自社の特許性判断・参入戦略検討の精度向上に有効。"
)

# =========================================================================
# 5. 出典・参考資料
# =========================================================================
add_heading("5. 出典・参考資料", level=1)
add_para("詳細な出典URL一覧は以下の調査結果ファイルを参照。", size=10)
add_bullet("特許調査: 01_research/patent/research_output.md")
add_bullet("市場調査: 01_research/market/market_research_output.md")
add_bullet("分析結果: 02_analysis/analysis_output.md")
add_bullet("前回調査（同一観点・2026-09-14実施）: projects/_archive/2026-09-14_スマートリング特許調査/")

doc.save(OUT_PATH)
print("saved:", OUT_PATH)
