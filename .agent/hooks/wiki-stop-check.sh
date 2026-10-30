#!/usr/bin/env bash
# Stop-проверка (Claude Code: Stop; в opencode прямого аналога нет — заменяется
# периодическим прогоном скилла wiki-lint). Если за сессию менялся код подсистем,
# описанных вики, а docs/wiki — нет, один раз возвращает агента дописать вики.
# Второй Stop проходит всегда.
set -uo pipefail

input=$(cat)
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$root" || exit 0

sid=$(HOOK_INPUT="$input" python -c 'import json,os; d=json.loads(os.environ.get("HOOK_INPUT") or "{}"); print(d.get("session_id") or d.get("sessionID") or "default")' 2>/dev/null) || sid="default"
sentinel="/tmp/wiki-stopped-$sid"
[ -f "$sentinel" ] && exit 0

changed=$(git status --porcelain 2>/dev/null | awk '{print $NF}')
base=$(cat "/tmp/wiki-head-$sid" 2>/dev/null || true)
if [ -n "$base" ] && git cat-file -e "$base^{commit}" 2>/dev/null; then
  changed="$changed"$'\n'$(git diff --name-only "$base" HEAD 2>/dev/null || true)
fi
[ -z "${changed//[[:space:]]/}" ] && exit 0

CODE_RE='\.(py|js|ts|html|css|svelte)$'
code=$(printf '%s\n' "$changed" | grep -E "$CODE_RE" | sort -u)
[ -z "$code" ] && exit 0

wiki=$(printf '%s\n' "$changed" | grep -E '^docs/wiki/' | sort -u)
[ -n "$wiki" ] && exit 0

touch "$sentinel"
list=$(printf '%s\n' "$code" | head -8 | sed 's/^/  - /')

HOOK_REASON="За сессию менялся код, а docs/wiki — нет:
$list

Правило из AGENTS.md: обнови страницу вики для затронутой подсистемы — не создавай новый датированный документ. Страницы: архитектура, данные, ui-система, глоссарий.

Если обновление вики в этот раз не нужно (тривиальная правка, эксперимент, откат) — просто скажи это одной строкой и завершай. Повторно этот хук за сессию не сработает." \
python -c 'import json,os; print(json.dumps({"decision":"block","reason":os.environ["HOOK_REASON"]}, ensure_ascii=False))'
