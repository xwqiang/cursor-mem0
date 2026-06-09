#!/usr/bin/env bash
# Verify cursor-mem0 MCP install (same as cursor.directory / mcp.json).
# Usage: ./scripts/verify_mcp_install.sh
# Optional: export CURSOR_API_KEY=...  then test in Cursor IDE.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PASS=0
FAIL=0
UVX=(uvx --python 3.12 --from "cursor-mem0[mcp]")

ok()   { echo "  ✓ $*"; PASS=$((PASS + 1)); }
fail() { echo "  ✗ $*"; FAIL=$((FAIL + 1)); }
section() { echo; echo "== $* =="; }

section "1. Prerequisites"
if command -v uvx >/dev/null 2>&1; then
  ok "uvx: $(command -v uvx)"
else
  fail "uvx not found — install: curl -LsSf https://astral.sh/uv/install.sh | sh"
  echo; echo "RESULT: FAIL"; exit 1
fi

section "2. PyPI package import (Python 3.12)"
if "${UVX[@]}" python -c "import cursor_mem; print('cursor_mem ok')" 2>/dev/null | grep -q "cursor_mem ok"; then
  ok "cursor-mem0[mcp] installs and imports on Python 3.12"
else
  fail "cannot import cursor_mem — run:"
  echo "    uvx --python 3.12 --from \"cursor-mem0[mcp]\" python -c \"import cursor_mem\""
fi

section "3. MCP protocol (initialize + tools/list)"
TOOLS_JSON="$(
  {
    printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"verify","version":"1.0"}}}'
    printf '%s\n' '{"jsonrpc":"2.0","method":"notifications/initialized"}'
    printf '%s\n' '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
  } | "${UVX[@]}" cursor-mem-mcp 2>/dev/null | tail -1
)"

if echo "$TOOLS_JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
tools = d.get('result', {}).get('tools', [])
names = {t['name'] for t in tools}
need = {'add_memory', 'search_memories', 'list_memories', 'get_memory'}
if need - names:
    sys.exit(1)
print(','.join(sorted(names)))
" 2>/dev/null; then
  ok "MCP tools: add_memory, search_memories, list_memories, get_memory"
else
  fail "tools/list failed"
  echo "    tip: first run downloads deps (~1–3 min); retry if network slow"
  echo "    response: ${TOOLS_JSON:0:180}"
fi

section "4. Repo mcp.json matches directory"
if [[ -f mcp.json ]] && grep -q '"3.12"' mcp.json && grep -q '"--python"' mcp.json; then
  ok "mcp.json has uvx --python 3.12"
else
  fail "mcp.json missing --python 3.12"
fi

section "5. pip install (Intel Mac / Python version)"
PY_VER="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo unknown)"
ARCH="$(uname -m 2>/dev/null || echo unknown)"
if [[ "$ARCH" == "x86_64" && "$PY_VER" == "3.13" ]]; then
  fail "python3 is 3.13 on Intel Mac — onnxruntime has no x86_64 wheel; use python3.12 or uvx --python 3.12"
  echo "    brew install python@3.12 && python3.12 -m pip install \"cursor-mem0[mcp]\""
elif [[ "$PY_VER" == "3.10" ]]; then
  fail "python3 is 3.10 — use 3.11+ (3.12 recommended) for fastembed/onnxruntime wheels"
else
  ok "python3 version/arch OK for install ($PY_VER, $ARCH)"
fi

section "6. CURSOR_API_KEY (for real use in Cursor)"
if [[ -n "${CURSOR_API_KEY:-}" ]]; then
  ok "CURSOR_API_KEY is set"
else
  echo "  · set in project .env: CURSOR_API_KEY=cursor_..."
  echo "  · get key: https://cursor.com/dashboard/integrations"
fi

echo
if [[ "$FAIL" -eq 0 ]]; then
  echo "RESULT: PASS ($PASS checks)"
  echo
  echo "Use in Cursor:"
  echo "  1. cp mcp.json → <your-project>/.cursor/mcp.json"
  echo "  2. echo 'CURSOR_API_KEY=cursor_...' >> <your-project>/.env"
  echo "  3. Cursor → Settings → MCP → enable cursor-mem → Reload Window"
  exit 0
else
  echo "RESULT: FAIL ($FAIL failed, $PASS passed)"
  exit 1
fi
