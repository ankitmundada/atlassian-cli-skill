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

for dir in "$HOME/.claude/skills/atlassian-cli-skill" "$HOME/.claude/skills/atlassian-cli" "$HOME/.claude/skills/smart-commits"; do
  if [ -d "$dir" ]; then
    echo "Removing skill from ${dir}..."
    rm -rf "$dir"
  fi
done

echo ""
echo "Done."
