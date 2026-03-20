# atlassian-cli-skill

Skills and tools for AI coding agents (Claude Code, Cursor, etc.) to work with Atlassian products.

## What's here

| Component                                   | Description                                                                                                                                           |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| [atlassian-cli](atlassian-cli/)             | Open-source Python CLI for Jira and Confluence Cloud. Drop-in replacement for Atlassian's proprietary `acli`.                                         |
| [atlassian-cli-skill](atlassian-cli-skill/) | Agent skill that teaches AI agents how to use `atlassian-cli` for project management — JQL, decision patterns, workflows, Jira+Confluence philosophy. |

The CLI tool and the skill are designed to work together. The skill provides the knowledge; the CLI provides the tool.

## Quick start

### One-liner (CLI + Claude Code skill)

```bash
curl -fsSL https://raw.githubusercontent.com/ankitmundada/atlassian-cli-skill/main/install.sh | bash
```

### Or install separately

```bash
# CLI — pick one
brew install ankitmundada/tap/atlassian-cli
pip install cli-atlassian
pipx install cli-atlassian
```

Then authenticate:

```bash
atlassian-cli auth login
```

## License

MIT — see [LICENSE](LICENSE).
