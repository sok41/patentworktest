#!/usr/bin/env bash
# pre_tool_use_guard.sh
#
# タイミング: PreToolUse（ファイル削除・書き込みの実行前）
# 内容: _archive/ 配下への削除・上書きや、案件フォルダ名の誤り（YYYY-MM-DD_スラッグ以外）
#       への書き込みを検知し、実行前に exit 2 で止める。
#
# 参照: 特許調査プロジェクト_要件定義書.md 9.2節

set -u

input="$(cat)"

get_json_field() {
  local field="$1"
  echo "$input" | sed -n "s/.*\"$field\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p" | head -1
}

tool_name="$(get_json_field tool_name)"

block() {
  echo "pre_tool_use_guard: $1" >&2
  exit 2
}

# --- Bash経由の削除コマンドをチェック ---
if [[ "$tool_name" == "Bash" ]]; then
  command="$(get_json_field command)"
  norm_cmd="${command//\\//}"
  if [[ "$norm_cmd" =~ (rm|del|Remove-Item)[^\|]*_archive/ ]]; then
    block "_archive/ 配下を削除するコマンドが検出されました。完了案件の削除は原則禁止です。本当に必要な場合はユーザーに明示的な承認を得てください。"
  fi
  exit 0
fi

# --- Write/Editの書き込み先をチェック ---
if [[ "$tool_name" == "Write" || "$tool_name" == "Edit" ]]; then
  file_path="$(get_json_field file_path)"
  norm_path="${file_path//\\//}"

  if [[ -z "$norm_path" ]]; then
    exit 0
  fi

  # _archive/ 配下への書き込み・上書きは禁止（アーカイブは読み取り専用の想定）
  if [[ "$norm_path" == *"/projects/_archive/"* ]]; then
    block "_archive/ 配下（完了案件）への書き込みが検出されました: $file_path 。アーカイブ後の案件を編集する場合は、先にユーザーへ確認してください。"
  fi

  # projects/ 配下だが、_template でも _archive でもない、YYYY-MM-DD_ 形式でもないフォルダへの書き込みを警告
  if [[ "$norm_path" =~ /projects/([^/]+)/ ]]; then
    project_dir="${BASH_REMATCH[1]}"
    if [[ "$project_dir" != "_template" && "$project_dir" != "_archive" && "$project_dir" != "_index.md" ]]; then
      if ! [[ "$project_dir" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}_.+ ]]; then
        block "案件フォルダ名の命名規則（YYYY-MM-DD_案件名スラッグ）に一致しないフォルダへの書き込みです: projects/$project_dir/ 。フォルダ名を確認してください。"
      fi
    fi
  fi
fi

exit 0
