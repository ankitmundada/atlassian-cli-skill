---
name: atlassian-cli
version: 0.3.5
description: "Interact with Jira and Confluence using the open-source atlassian-cli tool. Use this skill whenever the user asks you to interact with Jira or Confluence — creating issues, searching with JQL, transitioning tickets, managing sprints, triaging bugs, generating reports, bulk-creating issues from notes, writing or reading Confluence pages, spaces, and blog posts. Also trigger when the user mentions Jira project keys (like PROJ-123), asks about sprint status, backlogs, epics, or references atlassian-cli. Even if the user just says 'check my tickets', 'what's in my backlog', 'create a task for X', or 'write up a doc for this', use this skill."
---

# atlassian-cli — Agent Skill

Use the open-source `atlassian-cli` tool for all Jira and Confluence operations.

**Install:** `pipx install cli-atlassian`

**Setup:** `atlassian-cli auth login` — prompts for site URL, email, and API token. Create a token at https://id.atlassian.com/manage/api-tokens.

**Verify:** `atlassian-cli auth status`

---

## Jira Commands

### Search

```bash
atlassian-cli jira issue search --jql "<JQL>" --limit 10
atlassian-cli jira issue search --jql "<JQL>" --fields "key,summary,status" --limit 10
atlassian-cli jira issue search --jql "<JQL>" --count   # just the count
```

**Always set `--limit`.** Default is 10. Use `--count` first if unsure how large the result set is.

### View

```bash
atlassian-cli jira issue view PROJ-123
atlassian-cli jira issue view PROJ-123 --output json
atlassian-cli jira issue view PROJ-123 --dev          # show linked commits, branches, PRs
```

### Create

```bash
atlassian-cli jira issue create --project PROJ --type Task --summary "Title"
atlassian-cli jira issue create --project PROJ --type Story --summary "Title" --description "Details" --assignee "@me" --priority "High"
atlassian-cli jira issue create --project PROJ --type Sub-task --summary "Sub-task" --parent PROJ-100
```

`--assignee`: email or `@me`. `--type`: Epic, Story, Task, Bug, Sub-task. `--priority`: Highest, High, Medium, Low, Lowest.

### Edit

```bash
atlassian-cli jira issue edit PROJ-123 --summary "New title"
atlassian-cli jira issue edit PROJ-123 --assignee "user@example.com" --priority "High" --labels "bug,urgent"
```

### Assign / Transition / Delete

```bash
atlassian-cli jira issue assign PROJ-123 --user "@me"
atlassian-cli jira issue assign PROJ-123 --unassign
atlassian-cli jira issue transition PROJ-123 --status "Done"
atlassian-cli jira issue delete PROJ-123 --yes
```

The transition tool finds the right transition from the status name. If invalid, it shows available options.

### Comment

```bash
atlassian-cli jira issue comment add PROJ-123 --body "Comment text"
atlassian-cli jira issue comment list PROJ-123 --limit 5
atlassian-cli jira issue comment edit PROJ-123 --id <COMMENT-ID> --body "Updated"
atlassian-cli jira issue comment delete PROJ-123 --id <COMMENT-ID>
```

For rich formatting, use ADF JSON in the body. See [adf-reference.md](adf-reference.md).

### Links

```bash
atlassian-cli jira issue link add PROJ-123 --target PROJ-456 --type "Blocks"
atlassian-cli jira issue link list PROJ-123
atlassian-cli jira issue link types
```

### Project / Board / Sprint

```bash
atlassian-cli jira project list --recent 5
atlassian-cli jira board list --project PROJ
atlassian-cli jira board sprints 42 --state active

atlassian-cli jira sprint view 100
atlassian-cli jira sprint issues 100 --limit 20
atlassian-cli jira sprint create --board 42 --name "Sprint 5" --start 2026-03-15 --end 2026-03-29 --goal "Ship auth"
atlassian-cli jira sprint update 100 --state active    # start
atlassian-cli jira sprint update 100 --state closed    # close
atlassian-cli jira sprint move 100 --keys "PROJ-1,PROJ-2,PROJ-3"
```

---

## JQL Reference

```sql
-- My open work
assignee = currentUser() AND resolution = Unresolved

-- Bugs from the last 7 days
project = "PROJ" AND type = Bug AND created >= -7d

-- High-priority in current sprint
project = "PROJ" AND priority in (High, Highest) AND sprint in openSprints()

-- Text search
project = "PROJ" AND text ~ "payment error"

-- Overdue
project = "PROJ" AND due < now() AND status != Done

-- Everything in an epic
"Epic Link" = PROJ-100

-- What shipped this week
project = "PROJ" AND status changed to Done AFTER startOfWeek()
```

**Syntax:** Quote values with spaces (`status = 'In Progress'`). Operators: `=`, `!=`, `~`, `in`, `is EMPTY`. Functions: `currentUser()`, `openSprints()`, `startOfDay()`, `now()`. Relative dates: `-7d`, `-24h`.

See [advanced-jql-reference.md](references/advanced-jql-reference.md) for date functions, sprint queries, status-change tracking, and complex combinations.

---

## Confluence Commands

### Page

```bash
atlassian-cli confluence page view <PAGE-ID>
atlassian-cli confluence page view <PAGE-ID> --version 3                      # view specific historical version
atlassian-cli confluence page versions <PAGE-ID>                              # list version history
atlassian-cli confluence page create --space <SPACE-ID> --title "Title" --body "# Heading\n\nContent here."
atlassian-cli confluence page create --space <SPACE-ID> --title "Title" --body-file page.md
atlassian-cli confluence page edit <PAGE-ID> --body "# Updated\n\nNew content."
atlassian-cli confluence page edit <PAGE-ID> --body "## New Section" --append  # append to existing content
atlassian-cli confluence page search --cql "space = 'ENG' AND title = 'Design Doc'" --limit 10
```

### Blog

```bash
atlassian-cli confluence blog list --space <SPACE-ID> --limit 10
atlassian-cli confluence blog view <BLOG-ID>
atlassian-cli confluence blog create --space <SPACE-ID> --title "Title" --body "# Post\n\nContent." --status draft
```

### Space

```bash
atlassian-cli confluence space list
atlassian-cli confluence space view <SPACE-ID>
atlassian-cli confluence space create --key NEWSPACE --name "Space Name"
```

**Body format:** Reads and writes default to markdown. Write body content in standard markdown — it is converted to HTML automatically. Other write formats (`--format`): `wiki`, `storage`, `atlas_doc_format`. Other read formats (`--body-format`): `storage`, `view`, `atlas_doc_format`.

---

## Common Options

| Option      | Short | Purpose                                      |
| ----------- | ----- | -------------------------------------------- |
| `--output`  | `-o`  | `table` (default), `json`, or `csv`          |
| `--profile` | `-p`  | Select auth profile (default: `default`)     |
| `--limit`   | `-l`  | Max results (for list/search commands)       |
| `--yes`     | `-y`  | Skip confirmation (for destructive commands) |

---

## Decision Patterns

**Use `--append` when adding to a doc.** When iteratively building up a Confluence page, always use `--append` to add new sections. Use plain `edit` only when replacing the full content.

**Zoom in, don't dump.** Start broad (epics, `--limit 10`), summarize, drill in only if asked. Don't pull every issue.

**Always leave a comment when modifying issues.** Especially when triaging, reassigning, or transitioning. Silent changes erode trust.

**Confirm destructive actions.** Before bulk-transitioning, deleting, or making sweeping edits, show the user what you plan to do and ask for approval.

**Inspect before guessing.** When unsure about fields (especially custom fields), fetch an existing issue with `--output json` to see the structure.

---

## Writing Tickets

### Issue Types

| Type | When | Content |
|------|------|---------|
| **Epic** | Feature/initiative spanning sprints | Goal + scope. No implementation detail |
| **Story** | User-facing capability | "As a [who], I want [what] so that [why]". AC = user behavior, not internals. Can't phrase it as a user need? It's a Task |
| **Task** | Engineering work (infra, refactors, tooling, migrations) | Tech, approach, done state. Implementation detail belongs here |
| **Bug** | Something broken | Steps to reproduce, expected vs actual |
| **Sub-task** | One-person slice of a Story/Task | Implementation-specific OK — parent provides context |

### Stories vs Tasks

**Stories** describe what the user needs — not how to build it. No technology choices, no component names, no architecture. A Story should survive a framework swap. AC describes what the user observes, not what the code does. Tech suggestions go in a separate "Technical Notes" section if needed.

**Tasks** describe engineering work. Tech choices, libraries, and approach ARE the content. The audience is the engineer.

---

## Workflow Recipes

### Daily Stand-up

```bash
# Done yesterday
atlassian-cli jira issue search --jql "assignee = currentUser() AND status changed to Done AFTER startOfDay('-1d')" --limit 20

# In progress
atlassian-cli jira issue search --jql "assignee = currentUser() AND sprint in openSprints() AND statusCategory = 'In Progress'" --limit 20
```

### Bug Triage

```bash
atlassian-cli jira issue view PROJ-456
atlassian-cli jira issue search --jql "project = PROJ AND type = Bug AND text ~ '<keywords>'" --limit 5
atlassian-cli jira issue edit PROJ-456 --priority "High" --labels "triaged"
atlassian-cli jira issue assign PROJ-456 --user "dev@example.com"
atlassian-cli jira issue comment add PROJ-456 --body "Triaged: P1. No duplicates found."
```

### Publish Release Notes

```bash
atlassian-cli jira issue search --jql "project = PROJ AND fixVersion = 'v2.5' AND status = Done" --output json > shipped.json
atlassian-cli confluence blog create --space <SPACE-ID> --title "Release Notes — v2.5" --body-file release-notes.md
```

---

## Auth & Profiles

```bash
atlassian-cli auth login --profile prod --site https://team.atlassian.net --email you@company.com --token <TOKEN>
atlassian-cli auth status
atlassian-cli jira issue search --jql "..." --profile prod
```

Config: `~/.config/atlassian-cli/config.json`. Env var `ATLASSIAN_API_TOKEN` overrides stored tokens.

---

## Instance Memory

After first use, cache these constants so you don't rediscover them each session:

- Site URL, project key(s), board ID(s), Confluence space ID(s)

**Don't cache:** sprint IDs (change every cycle — use `board sprints --state active`), issue counts or statuses (always query live).

---

## Error Reference

| Error                    | Fix                                                   |
| ------------------------ | ----------------------------------------------------- |
| `No profiles configured` | Run `atlassian-cli auth login`                         |
| `No API token`           | Set `ATLASSIAN_API_TOKEN` or re-login                  |
| JQL syntax error         | Check field names; quote values with spaces            |
| Transition not available | Issue isn't in a valid status; view it first           |
| 403 Forbidden            | User lacks permission                                  |
| 404 Not Found            | Check issue key or page/space ID                       |

---

## Reference Files

- **[ADF Reference](adf-reference.md)** — Atlassian Document Format for rich text
- **[Advanced JQL](references/advanced-jql-reference.md)** — Date functions, sprint queries, complex combinations
