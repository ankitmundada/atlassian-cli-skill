# atlassian-cli-skill

Skills and tools for AI coding agents (Claude Code, Cursor, etc.) to work with Atlassian products.

## What's here

| Component                                   | Description                                                                                                       |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| [atlassian-cli](atlassian-cli/)             | Open-source Python CLI for Jira and Confluence Cloud. Drop-in replacement for Atlassian's proprietary `acli`.     |
| [atlassian-cli-skill](atlassian-cli-skill/) | Agent skill for Jira and Confluence — JQL, decision patterns, workflows, reading/writing Confluence pages.         |
| [smart-commits](smart-commits/)             | Agent skill that links git commits, branches, and PRs to Jira issues automatically via Jira smart commits.        |

## Quick start

### One-liner (CLI + Claude Code skill)

```bash
curl -fsSL https://raw.githubusercontent.com/ankitmundada/atlassian-cli-skill/main/install.sh | bash
```

### Or install separately

```bash
pipx install cli-atlassian
```

Then authenticate:

```bash
atlassian-cli auth login
```

## License

MIT — see [LICENSE](LICENSE).
