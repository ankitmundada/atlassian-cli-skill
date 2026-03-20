#!/usr/bin/env bash
set -euo pipefail

REPO="ankitmundada/atlassian-cli-skill"
BRANCH="main"
SKILL_DIR="atlassian-cli-skill"
RAW="https://raw.githubusercontent.com/${REPO}/${BRANCH}/${SKILL_DIR}"

SKILL_FILES=(
  "SKILL.md"
  "adf-reference.md"
  "references/advanced-jql-reference.md"
)

TARGET="$HOME/.claude/skills/atlassian-cli"

# ── CLI ──────────────────────────────────────────────────────────────────

install_cli() {
  if ! command -v pipx &>/dev/null; then
    echo "Error: pipx is required to install atlassian-cli." >&2
    echo "Install pipx: https://pipx.pypa.io/stable/installation/" >&2
    exit 1
  fi
  echo "Installing cli-atlassian via pipx..."
  pipx upgrade cli-atlassian 2>/dev/null || pipx install cli-atlassian
}

# ── Skill ────────────────────────────────────────────────────────────────

install_skill() {
  echo "Installing Claude Code skill to ${TARGET}..."
  mkdir -p "${TARGET}/references"
  for file in "${SKILL_FILES[@]}"; do
    curl -fsSL "${RAW}/${file}" -o "${TARGET}/${file}"
  done
}

# ── Main ─────────────────────────────────────────────────────────────────

echo "==> atlassian-cli installer"
install_cli
install_skill
echo ""
echo "Done. Verify with:  atlassian-cli --help"
