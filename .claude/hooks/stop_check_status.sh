#!/usr/bin/env bash
# stop_check_status.sh
#
# タイミング: Stop（セッション終了時）
# 内容: 各案件の status.yaml と projects/_index.md の内容に食い違いがないかを確認する。
#       ・_index.md に記載のない案件IDがないか
#       ・report が done なのに archived: false のまま放置されていないか
#       あくまで注意喚起（非ブロッキング）。食い違いがあれば標準出力に警告を出す。
#
# 参照: 特許調査プロジェクト_要件定義書.md 9.2節

set -u

# フック入力からcwdを取得（取得できなければカレントディレクトリを使用）
input="$(cat)"
cwd="$(echo "$input" | sed -n 's/.*"cwd"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
root="${cwd:-.}"

index_file="$root/projects/_index.md"
warnings=()

if [[ ! -f "$index_file" ]]; then
  # _index.md自体が無ければチェック対象なし
  exit 0
fi

for status_file in "$root"/projects/*/status.yaml; do
  [[ -e "$status_file" ]] || continue

  project_dir="$(basename "$(dirname "$status_file")")"
  [[ "$project_dir" == "_template" ]] && continue

  project_id="$(sed -n 's/^project_id:[[:space:]]*"\{0,1\}\([^"]*\)"\{0,1\}[[:space:]]*$/\1/p' "$status_file" | head -1)"
  [[ -z "$project_id" ]] && project_id="$project_dir"

  # _index.mdに案件IDの記載があるか
  if ! grep -qF "$project_id" "$index_file"; then
    warnings+=("案件 $project_id が projects/_index.md に記載されていません。")
  fi

  report_status="$(sed -n 's/^[[:space:]]*report:[[:space:]]*\([a-z_]*\).*/\1/p' "$status_file" | head -1)"
  archived="$(sed -n 's/^archived:[[:space:]]*\(true\|false\).*/\1/p' "$status_file" | head -1)"

  if [[ "$report_status" == "done" && "$archived" == "false" ]]; then
    warnings+=("案件 $project_id はreportが完了していますが、まだアーカイブされていません（ユーザーにアーカイブ可否の確認を）。")
  fi
done

if [[ ${#warnings[@]} -gt 0 ]]; then
  echo "stop_check_status: status.yaml と _index.md の間に以下の食い違い・確認事項があります:"
  for w in "${warnings[@]}"; do
    echo "  - $w"
  done
fi

exit 0
