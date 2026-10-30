#!/usr/bin/env bash
# Старт сессии (opencode: session.created — см. .opencode/plugins/wiki.js):
# впрыскивает компактное оглавление вики и запоминает HEAD сессии.
# Оглавление генерируется из docs/wiki/index.md, поэтому не устаревает.
set -uo pipefail

input=$(cat)
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
idx="$root/docs/wiki/index.md"
[ -f "$idx" ] || exit 0

sid=$(HOOK_INPUT="$input" python -c 'import json,os; d=json.loads(os.environ.get("HOOK_INPUT") or "{}"); print(d.get("session_id") or d.get("sessionID") or "default")' 2>/dev/null) || sid="default"
git -C "$root" rev-parse HEAD > "/tmp/wiki-head-$sid" 2>/dev/null || true
rm -f "/tmp/wiki-stopped-$sid" 2>/dev/null || true

HOOK_INDEX="$idx" python - <<'PY'
import json, os, re

rows = []
with open(os.environ["HOOK_INDEX"], encoding="utf-8") as handle:
    for line in handle:
        match = re.match(r"^\|\s*\[\[([^\]]+)\]\]\s*\|\s*(.+?)\s*\|\s*$", line)
        if match:
            rows.append(f"  {match.group(1)}.md — {match.group(2)}")

if not rows:
    raise SystemExit(0)

message = (
    "Вики проекта (docs/wiki/, живое состояние — читать вместо вывода из кода/прозы):\n"
    + "\n".join(rows)
    + "\nКаталог: docs/wiki/index.md"
)
print(json.dumps({
    "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": message},
    "suppressOutput": True,
}, ensure_ascii=False))
PY
