#!/usr/bin/env bash
# Карта «файл → страницы вики». Подсказка приходит перед edit/write через
# .opencode/plugins/wiki.js. Ключ — имя файла; значение — страницы без .md.
# Пополнять по мере появления подсистем.
set -uo pipefail

input=$(cat)
path=$(HOOK_INPUT="$input" python -c 'import json,os; d=json.loads(os.environ.get("HOOK_INPUT") or "{}"); print(d.get("tool_input",{}).get("file_path",""))' 2>/dev/null)
[ -z "$path" ] && exit 0

b=$(basename "$path")
case "$b" in
  server.py|app.py|canon.py)
    pages="архитектура данные" ;;
  build_canon_db.py)
    pages="данные архитектура" ;;
  *.json)
    pages="данные" ;;
  *.svelte|app.css|*.js)
    pages="ui-система" ;;
  *)
    pages="" ;;
esac
[ -z "$pages" ] && exit 0

list=""
for page in $pages; do
  list="$list  - docs/wiki/$page.md"$'\n'
done

msg="Правишь $b. Сначала прочитай страницу(ы) вики, это живое описание текущего состояния:
$list"
HOOK_MSG="$msg" python -c 'import json,os; print(json.dumps({"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":os.environ["HOOK_MSG"]},"suppressOutput":True}, ensure_ascii=False))'
