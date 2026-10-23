#!/usr/bin/env bash
# post_tool_use_validate.sh
#
# タイミング: PostToolUse（Write/Edit実行直後）
# 内容: research_output.md / market_research_output.md / analysis_output.md への
#       書き込み直後に、必須見出しが揃っているかを機械的にチェックする。
#       欠けていれば exit 2 でエージェントに差し戻す（status.yamlをdoneにする前の品質ゲート）。
#
# 参照: 特許調査プロジェクト_要件定義書.md 9.2節

set -u

input="$(cat)"

get_json_field() {
  # 簡易JSONパーサ（"field": "value" 形式の文字列値のみ対応）
  local field="$1"
  echo "$input" | sed -n "s/.*\"$field\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p" | head -1
}

tool_name="$(get_json_field tool_name)"
file_path="$(get_json_field file_path)"

# Write/Edit以外、またはfile_pathが取れない場合は何もしない
if [[ "$tool_name" != "Write" && "$tool_name" != "Edit" ]] || [[ -z "$file_path" ]]; then
  exit 0
fi

# 正規化（バックスラッシュ→スラッシュ）
norm_path="${file_path//\\//}"

check_headings() {
  local file="$1"
  shift
  local missing=()
  for heading in "$@"; do
    if ! grep -qF "$heading" "$file" 2>/dev/null; then
      missing+=("$heading")
    fi
  done
  if [[ ${#missing[@]} -gt 0 ]]; then
    echo "post_tool_use_validate: $file に必須見出しが不足しています: ${missing[*]}" >&2
    echo "不足している見出しを追記してから、再度書き込み・status.yaml更新を行ってください。" >&2
    exit 2
  fi
}

# charts/配下への画像リンク（Markdown形式）が最低min_count件埋め込まれているかを確認する。
# グラフ画像の生成自体を機械的に検証することはできないが、見出しだけ用意して
# 画像埋め込みを省略する事態を防ぐためのゲート。
check_chart_images() {
  local file="$1"
  local min_count="$2"
  local count
  count="$(grep -oF '](charts/' "$file" 2>/dev/null | wc -l)"
  if [[ "$count" -lt "$min_count" ]]; then
    echo "post_tool_use_validate: $file にグラフ画像の埋め込み（例: ![出願推移](charts/filing_trend.png)）が不足しています（${count}件 / 必要${min_count}件）。" >&2
    echo "scripts/chart_utils.py でグラフを生成し、charts/配下に保存のうえ画像リンクを埋め込んでください。" >&2
    exit 2
  fi
}

case "$norm_path" in
  */01_research/patent/research_output.md)
    check_headings "$file_path" "## 使用した検索式" "## 対象特許リスト" "## 出願推移" "## 出願人ランキング" "## 各特許のサマリ" "## 出典・参考URL"
    check_chart_images "$file_path" 2
    ;;
  */01_research/market/market_research_output.md)
    check_headings "$file_path" "## 市場規模" "## 主要プレイヤー" "## トレンド" "## 出典・参考URL"
    ;;
  */02_analysis/analysis_output.md)
    check_headings "$file_path" "## 技術動向分類" "## 競合マッピング" "## 市場×特許の突き合わせ" "## 総括・示唆"
    ;;
  *)
    # 対象外ファイルはチェックしない
    exit 0
    ;;
esac

exit 0
