#!/usr/bin/env bash
# Sync GitHub repo About (description, homepage, topics) and default issue labels.
# Requires: gh auth login
# Usage: ./scripts/github-repo-setup.sh
#        GITHUB_REPO=owner/repo ./scripts/github-repo-setup.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO="${GITHUB_REPO:-xwqiang/cursor-mem0}"
TOPICS_FILE="${ROOT}/.github/topics.txt"

if ! command -v gh >/dev/null 2>&1; then
  echo "Install GitHub CLI: https://cli.github.com/" >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "Run: gh auth login" >&2
  exit 1
fi

TOPICS=()
while IFS= read -r line; do
  TOPICS+=("$line")
done < <(grep -v '^[[:space:]]*$' "$TOPICS_FILE" | head -20)
if ((${#TOPICS[@]} == 0)); then
  echo "No topics in $TOPICS_FILE" >&2
  exit 1
fi

echo "Updating $REPO (description, homepage, ${#TOPICS[@]} topics)..."
gh repo edit "$REPO" \
  --description "mem0-compatible AI agent memory via Cursor SDK (CURSOR_API_KEY). Local embeddings, Qdrant, MCP for Cursor IDE." \
  --homepage "https://pypi.org/project/cursor-mem0/"

for topic in "${TOPICS[@]}"; do
  gh repo edit "$REPO" --add-topic "$topic" 2>/dev/null || true
done

echo "Syncing issue labels..."
declare -A LABELS=(
  ["bug"]="d73a4a|Something isn't working"
  ["enhancement"]="a2eeef|New feature or request"
  ["documentation"]="0075ca|Improvements or additions to docs"
  ["good first issue"]="7057ff|Good for newcomers"
  ["help wanted"]="008672|Extra attention is needed"
  ["question"]="d876e3|Further information is requested"
  ["mcp"]="1d76db|MCP server / Cursor integration"
  ["dependencies"]="0366d6|Dependency updates"
)

for name in "${!LABELS[@]}"; do
  IFS='|' read -r color description <<< "${LABELS[$name]}"
  if gh label list --repo "$REPO" --json name -q ".[].name" 2>/dev/null | grep -qx "$name"; then
    gh label edit "$name" --repo "$REPO" --color "$color" --description "$description" 2>/dev/null || true
  else
    gh label create "$name" --repo "$REPO" --color "$color" --description "$description" 2>/dev/null || true
  fi
done

echo "Done. Verify: https://github.com/${REPO}"
