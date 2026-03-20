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

install_pipx() {
  if command -v pipx &>/dev/null; then
    return
  fi
  echo "pipx not found, installing..."
  if command -v brew &>/dev/null; then
    brew install pipx
  elif command -v apt-get &>/dev/null; then
    sudo apt-get update -qq && sudo apt-get install -y -qq pipx
  else
    python3 -m pip install --user pipx
  fi
  pipx ensurepath 2>/dev/null || true
  export PATH="$HOME/.local/bin:$PATH"
}

install_cli() {
  install_pipx
  echo "Installing cli-atlassian via pipx..."
  pipx upgrade cli-atlassian 2>/dev/null || pipx install cli-atlassian
}

# ── Skill ────────────────────────────────────────────────────────────────

install_skill() {
  # Clean up old install path
  rm -rf "$HOME/.claude/skills/atlassian-cli-skill"

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
