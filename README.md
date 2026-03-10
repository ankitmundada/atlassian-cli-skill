# useful-skills

Skills and tools for AI coding agents (Claude Code, Cursor, etc.) to work with Atlassian products.

## What's here

| Component                                   | Description                                                                                                                                           |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| [atlassian-cli](atlassian-cli/)             | Open-source Python CLI for Jira and Confluence Cloud. Drop-in replacement for Atlassian's proprietary `acli`.                                         |
| [atlassian-cli-skill](atlassian-cli-skill/) | Agent skill that teaches AI agents how to use `atlassian-cli` for project management — JQL, decision patterns, workflows, Jira+Confluence philosophy. |

The CLI tool and the skill are designed to work together. The skill provides the knowledge; the CLI provides the tool.

## Quick start

### Install the CLI

```bash
# Homebrew (macOS/Linux)
brew install ankitmundada/tap/atlassian-cli

# or pip
pip install cli-atlassian

# or pipx
pipx install cli-atlassian
```

Then authenticate:

```bash
atlassian-cli auth login
```

### Install the skill (Claude Code)

```bash
claude skill add --from github:ankitmundada/useful-skills/atlassian-cli-skill
```

## License

MIT — see [LICENSE](LICENSE).
