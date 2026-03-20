#!/usr/bin/env bash
set -euo pipefail

echo "==> atlassian-cli uninstaller"

# ── CLI ──────────────────────────────────────────────────────────────────

if command -v pipx &>/dev/null && pipx list 2>/dev/null | grep -q cli-atlassian; then
  echo "Removing cli-atlassian via pipx..."
  pipx uninstall cli-atlassian
else
  echo "CLI not found (or not installed via pipx), skipping."
fi

# ── Skill ────────────────────────────────────────────────────────────────

TARGET="$HOME/.claude/skills/atlassian-cli"

if [ -d "$TARGET" ]; then
  echo "Removing Claude Code skill from ${TARGET}..."
  rm -rf "$TARGET"
else
  echo "Skill not found, skipping."
fi

echo ""
echo "Done."
