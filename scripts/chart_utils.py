"""
chart_utils.py

patent-research / market-research / patent-analysis 各スキルが出力する
グラフ画像（PNG）を生成するための共通ヘルパー。

セットアップ（初回のみ）:
    pip install -r scripts/requirements.txt

使い方の例（各スキルはこのモジュールをimportし、そのつど短いスクリプトで
実データを渡してグラフを生成する。データはスキルごとに異なるため、
このファイル自体に案件固有のデータは持たせない）:

    from chart_utils import save_bar_chart, save_line_chart

    save_line_chart(
        x=["2019", "2020", "2021", "2022", "2023"],
        series={"出願件数": [12, 18, 25, 31, 40]},
        title="出願推移",
        xlabel="出願年",
        ylabel="件数",
        output_path="projects/2026-09-14_xxx/01_research/patent/charts/filing_trend.png",
    )

    save_bar_chart(
        labels=["A社", "B社", "C社"],
        values=[40, 25, 18],
        title="出願人ランキング（上位10社）",
        category_label="出願人",
        value_label="件数",
        output_path="projects/2026-09-14_xxx/01_research/patent/charts/applicant_ranking.png",
        horizontal=True,
    )
"""

from __future__ import annotations

import os
from typing import Iterable, Mapping, Sequence

import matplotlib

matplotlib.use("Agg")  # 画面なし環境でも動くよう非対話バックエンドを固定

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

# --- 日本語フォント設定 -------------------------------------------------
# Windows標準搭載の日本語フォントを明示的に登録する。
# .ttc（フォントコレクション）はmatplotlibが自動検出しないことがあるため、
# 存在するものを直接 addfont() で読み込んでからファミリー名を指定する。
_JP_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\YuGothR.ttc",
    r"C:\Windows\Fonts\meiryo.ttc",
    r"C:\Windows\Fonts\msgothic.ttc",
]


def setup_japanese_font() -> None:
    """matplotlibが日本語ラベルを豆腐（□□□）にせず描画できるようにする。"""
    for path in _JP_FONT_CANDIDATES:
        if os.path.exists(path):
            fm.fontManager.addfont(path)
            family = fm.FontProperties(fname=path).get_name()
            plt.rcParams["font.family"] = family
            break
    else:
        # 候補が1つも見つからない場合は既定フォントのまま
        # （日本語が文字化けする可能性がある旨、呼び出し側で認識しておくこと）
        pass
    plt.rcParams["axes.unicode_minus"] = False


setup_japanese_font()

# 落ち着いた配色（brand-neutralなプレースホルダパレット）
_PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2", "#937860"]


def _ensure_dir(output_path: str) -> None:
    d = os.path.dirname(output_path)
    if d:
        os.makedirs(d, exist_ok=True)


def save_line_chart(
    x: Sequence[str],
    series: Mapping[str, Sequence[float]],
    title: str,
    xlabel: str,
    ylabel: str,
    output_path: str,
    figsize: tuple[float, float] = (8, 4.5),
) -> str:
    """折れ線グラフ（出願推移・市場規模成長率などの時系列に使用）。"""
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    for i, (label, values) in enumerate(series.items()):
        ax.plot(
            x, values, marker="o", linewidth=2,
            color=_PALETTE[i % len(_PALETTE)], label=label,
        )
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if len(series) > 1:
        ax.legend(frameon=False)
    fig.tight_layout()
    _ensure_dir(output_path)
    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def save_bar_chart(
    labels: Sequence[str],
    values: Sequence[float],
    title: str,
    category_label: str,
    value_label: str,
    output_path: str,
    horizontal: bool = False,
    figsize: tuple[float, float] | None = None,
) -> str:
    """棒グラフ（出願人ランキングなどのカテゴリ比較に使用）。

    category_label: カテゴリ軸（出願人名など）のラベル
    value_label: 数値軸（件数など）のラベル
    horizontalの向きに関わらず、この2つの意味は変わらない
    （内部で軸の割り当てを調整する）。
    """
    n = len(labels)
    if figsize is None:
        figsize = (8, max(3.5, 0.45 * n)) if horizontal else (max(6, 0.7 * n), 4.5)
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    color = _PALETTE[0]
    if horizontal:
        ax.barh(labels, values, color=color)
        ax.invert_yaxis()  # 1位を上に
        ax.set_xlabel(value_label)
        ax.set_ylabel(category_label)
    else:
        ax.bar(labels, values, color=color)
        ax.set_xlabel(category_label)
        ax.set_ylabel(value_label)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x" if horizontal else "y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    _ensure_dir(output_path)
    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def save_pie_chart(
    labels: Sequence[str],
    values: Sequence[float],
    title: str,
    output_path: str,
    figsize: tuple[float, float] = (6, 6),
) -> str:
    """円グラフ（技術分類の構成比などに使用）。"""
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    ax.pie(
        values, labels=labels, autopct="%1.0f%%",
        colors=_PALETTE * (len(labels) // len(_PALETTE) + 1),
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
    )
    ax.set_title(title, fontsize=13, fontweight="bold")
    fig.tight_layout()
    _ensure_dir(output_path)
    fig.savefig(output_path)
    plt.close(fig)
    return output_path
