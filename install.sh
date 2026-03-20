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
  if command -v pipx &>/dev/null; then
    echo "Installing cli-atlassian via pipx..."
    pipx upgrade cli-atlassian 2>/dev/null || pipx install cli-atlassian
  elif command -v pip3 &>/dev/null; then
    echo "Installing cli-atlassian via pip3..."
    pip3 install --upgrade cli-atlassian
  elif command -v pip &>/dev/null; then
    echo "Installing cli-atlassian via pip..."
    pip install --upgrade cli-atlassian
  else
    echo "Error: need pipx or pip to install the CLI." >&2
    echo "Install pipx: https://pipx.pypa.io/stable/installation/" >&2
    exit 1
  fi
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
