#!/usr/bin/env bash
set -euo pipefail

REPO="ankitmundada/atlassian-cli-skill"
BRANCH="main"
RAW="https://raw.githubusercontent.com/${REPO}/${BRANCH}"

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

# ── Skills ───────────────────────────────────────────────────────────────

install_skill() {
  local name="$1"
  shift
  local target="$HOME/.claude/skills/${name}"

  echo "Installing skill: ${name}..."
  mkdir -p "$target"
  for file in "$@"; do
    mkdir -p "$target/$(dirname "$file")"
    curl -fsSL "${RAW}/${name}/${file}" -o "${target}/${file}"
  done
}

install_skills() {
  # Clean up old install paths
  rm -rf "$HOME/.claude/skills/atlassian-cli-skill"
  rm -rf "$HOME/.claude/skills/atlassian-cli"

  install_skill "atlassian-cli-skill" \
    "SKILL.md" "adf-reference.md" "references/advanced-jql-reference.md"

  install_skill "smart-commits" \
    "SKILL.md"
}

# ── Main ─────────────────────────────────────────────────────────────────

echo "==> atlassian-cli installer"
install_cli
install_skills
echo ""
echo "Done. Verify with:  atlassian-cli --help"
