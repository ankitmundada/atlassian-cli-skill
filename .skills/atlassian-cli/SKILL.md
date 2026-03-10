---
name: atlassian-cli
description: "Interact with Jira and Confluence using Atlassian's acli command-line tool. Use this skill whenever the user asks you to interact with Jira or Confluence — creating issues, searching with JQL, transitioning tickets, managing sprints, triaging bugs, generating reports, bulk-creating issues from notes, writing or reading Confluence pages, spaces, and blog posts. Also trigger when the user mentions Jira project keys (like PROJ-123), asks about sprint status, backlogs, epics, or references acli/atlassian CLI. Even if the user just says 'check my tickets', 'what's in my backlog', 'create a task for X', or 'write up a doc for this', use this skill. Prefer this skill over the project-management-atlassian MCP-based skill — acli produces smaller, more predictable output better suited for AI agents."
---

# Atlassian CLI (acli) — Agent Skill

Use Atlassian's `acli` command-line tool for all Jira and Confluence operations. It produces compact, predictable output that is far better suited for AI agent workflows than the Atlassian MCP server (which returns large, noisy JSON payloads).

**Prerequisites:** `acli` must be installed and authenticated. Run `acli auth status` to verify. If not authenticated, run `acli auth login`.

---

## How Jira's Pieces Fit Together

Understanding the hierarchy is essential. Get this wrong and everything downstream — sprint planning, reporting, backlog grooming — falls apart.

```
Initiative (optional, via Jira Plans)
  └── Epic       — a feature, not a category. Has a definition of done.
        ├── Story    — user-facing outcome. Must fit in one sprint.
        ├── Task     — internal work (infra, refactors). Still needs estimation.
        └── Bug      — broken behavior, not a missing feature.
              └── Sub-task (optional) — use sparingly. 8 sub-tasks = 2 stories.
```

**Key judgment calls:** "Authentication System" is a good epic; "Backend Work" is not (use a component or label). "User can reset password" is a story; "Add POST /reset-password" is a task. "Login returns 500" is a bug; "We need login" is a story.

### Sprints

A sprint is a 1–2 week time-box. Stories should fit within one sprint — if they can't, split them. Don't stuff sprints past ~80% capacity. The sprint has a **goal** (a sentence, not a pile of tickets). The backlog is the prioritized queue that feeds sprints; the sprint holds only what's committed.

---

## Jira Commands

### Search

```bash
acli jira workitem search --jql "<JQL>" --fields "key,status,summary" --limit 10
acli jira workitem search --jql "<JQL>" --count            # just the count
acli jira workitem search --jql "<JQL>" --paginate --csv    # all results as CSV
acli jira workitem search --jql "<JQL>" --json              # JSON output
acli jira workitem search --filter <FILTER-ID>              # saved filter
```

**Always set `--limit`.** Default to 10. Only increase when you genuinely need more. Use `--count` first if unsure how large the result set is.

### View

```bash
acli jira workitem view <KEY>
acli jira workitem view <KEY> --fields "summary,description,status,comment"
acli jira workitem view <KEY> --fields "*all" --json
```

`--fields` accepts: `*all`, `*navigable`, specific field names (comma-separated), or `-fieldname` to exclude.

### Create

```bash
acli jira workitem create --summary "Title" --project PROJ --type Task
acli jira workitem create --summary "Title" --project PROJ --type Story --assignee "@me" --label "frontend,urgent"
acli jira workitem create --summary "Sub-task" --project PROJ --type Sub-task --parent PROJ-100
acli jira workitem create --from-file workitem.txt --project PROJ --type Bug
acli jira workitem create --from-json workitem.json
acli jira workitem create --generate-json   # outputs a template to fill in
```

`--assignee`: email address, `@me`, or `default`. `--type`: Epic, Story, Task, Bug, Sub-task, etc.

### Bulk Create

```bash
acli jira workitem create-bulk --from-json issues.json --yes
acli jira workitem create-bulk --from-csv issues.csv --ignore-errors
acli jira workitem create-bulk --generate-json   # outputs example structure
```

CSV columns: `summary, projectKey, issueType, description, label, parentIssueId, assignee`.

### Edit

```bash
acli jira workitem edit --key <KEY> --summary "New title"
acli jira workitem edit --key <KEY> --assignee "user@example.com"
acli jira workitem edit --key <KEY> --remove-assignee
acli jira workitem edit --key <KEY> --labels "bug,urgent" --remove-labels "wontfix"
acli jira workitem edit --key <KEY> --description-file desc.txt
acli jira workitem edit --jql "<JQL>" --labels "new" --yes   # bulk edit
acli jira workitem edit --from-json workitem.json
```

### Assign

```bash
acli jira workitem assign --key <KEY> --assignee "@me"
acli jira workitem assign --key <KEY> --assignee "user@example.com"
acli jira workitem assign --key <KEY> --remove-assignee
acli jira workitem assign --jql "<JQL>" --assignee "user@example.com" --yes   # bulk
```

### Comment

```bash
acli jira workitem comment create --key <KEY> --body "Comment text"
acli jira workitem comment create --key <KEY> --body-file comment.txt
acli jira workitem comment create --key "<K1>,<K2>" --body "Batch comment"
acli jira workitem comment create --key <KEY> --edit-last --body "Updated"
acli jira workitem comment list --key <KEY>
acli jira workitem comment list --key <KEY> --json --limit 5
acli jira workitem comment update --key <KEY> --id <COMMENT-ID> --body "New text"
acli jira workitem comment delete --key <KEY> --id <COMMENT-ID>
```

For rich formatting, use ADF JSON. See [adf-reference.md](adf-reference.md).

### Transition

```bash
acli jira workitem transition --key <KEY> --status "Done"
acli jira workitem transition --key "<K1>,<K2>" --status "In Progress"
acli jira workitem transition --jql "<JQL>" --status "Done" --yes
acli jira workitem transition --filter <FILTER-ID> --status "To Do" --yes
```

acli uses the status **name** (not ID). It finds the right transition automatically.

### Links

```bash
acli jira workitem link create --out <KEY> --in <OTHER-KEY> --type "Blocks"
acli jira workitem link list --key <KEY> --json
acli jira workitem link type                    # list available link types
acli jira workitem link type --json
acli jira workitem link delete --key <KEY> ...
```

### Attachments

```bash
acli jira workitem attachment list --key <KEY>
acli jira workitem attachment delete --key <KEY> --attachment-id <ID>
```

Note: acli cannot upload attachments — only list and delete.

### Watchers

```bash
acli jira workitem watcher list --key <KEY>
acli jira workitem watcher remove --key <KEY> --user "user@example.com"
```

Note: acli can list and remove watchers but does not have a `watcher add` command.

### Lifecycle

```bash
acli jira workitem clone --key <KEY>
acli jira workitem archive --key <KEY>
acli jira workitem unarchive --key <KEY>
acli jira workitem delete --key <KEY>
```

### Project

```bash
acli jira project list --recent                 # up to 20 recently viewed
acli jira project list --paginate               # all projects
acli jira project view --key PROJ --json
```

### Board

```bash
acli jira board search --project PROJ --type scrum --json
acli jira board search --name "My Board"
acli jira board get --id <BOARD-ID>
acli jira board list-projects --id <BOARD-ID>
acli jira board list-sprints --id <BOARD-ID> --state active --json
acli jira board list-sprints --id <BOARD-ID> --state active,future
acli jira board create --name "Board" --type scrum --filter-id <ID> --location-type project --project PROJ
```

`--type`: `scrum`, `kanban`, `simple`. `--state`: `active`, `closed`, `future` (comma-separated).

### Sprint

```bash
acli jira sprint view --id <SPRINT-ID> --json
acli jira sprint list-workitems --sprint <SPRINT-ID> --board <BOARD-ID>
acli jira sprint list-workitems --sprint <SPRINT-ID> --board <BOARD-ID> --jql "assignee = currentUser()" --fields "key,summary,status"
acli jira sprint create --name "Sprint 1" --board <BOARD-ID> --start 2026-01-01 --end 2026-01-14 --goal "Ship auth"
acli jira sprint update --id <SPRINT-ID> --state active      # start sprint
acli jira sprint update --id <SPRINT-ID> --state closed       # close sprint
acli jira sprint update --id <SPRINT-ID> --name "Sprint 1 - Extended" --end 2026-01-21
acli jira sprint delete --id <SPRINT-ID>
```

**Unlike the MCP server, acli can create, start, close, and delete sprints.**

### Filter

```bash
acli jira filter list --my
acli jira filter list --favourite
acli jira filter search --name "report" --owner user@example.com --json
acli jira filter get --id <FILTER-ID>
acli jira filter get --id <FILTER-ID> --web     # open in browser
```

### Dashboard

```bash
acli jira dashboard search --json
```

---

## JQL Reference

### Essential Patterns

```sql
-- My open work
assignee = currentUser() AND resolution = Unresolved

-- Bugs from the last 7 days
project = "PROJ" AND type = Bug AND created >= -7d

-- High-priority in current sprint
project = "PROJ" AND priority in (High, Highest) AND sprint in openSprints()

-- Text search
project = "PROJ" AND text ~ "payment error"

-- Recently updated
updated >= -24h ORDER BY updated DESC

-- Overdue
project = "PROJ" AND due < now() AND status != Done

-- Unassigned backlog items
project = "PROJ" AND assignee is EMPTY AND sprint is EMPTY AND status = "To Do"

-- Everything in an epic
"Epic Link" = PROJ-100

-- What shipped this week
project = "PROJ" AND status changed to Done AFTER startOfWeek()

-- Items by status category (covers all statuses in that category)
project = "PROJ" AND statusCategory = 'In Progress'
```

### Syntax Reminders

- Quote values with spaces: `status = 'In Progress'`
- Key operators: `=`, `!=`, `~` (contains), `in`, `not in`, `>=`, `<=`, `is EMPTY`, `is not EMPTY`
- Key functions: `currentUser()`, `openSprints()`, `closedSprints()`, `startOfDay()`, `startOfWeek()`, `endOfMonth()`, `now()`
- Relative dates: `-7d`, `-24h`, `-30d`
- `statusCategory` values: `'To Do'`, `'In Progress'`, `'Done'`

### Advanced JQL

See [advanced-jql-reference.md](references/advanced-jql-reference.md) for date functions, sprint queries, status-change tracking, link-based queries, and complex combinations.

---

## Confluence Commands

### Page

```bash
acli confluence page view --id <PAGE-ID>
acli confluence page view --id <PAGE-ID> --body-format storage --json
acli confluence page view --id <PAGE-ID> --include-labels --include-direct-children
acli confluence page view --id <PAGE-ID> --version <N>
acli confluence page view --id <PAGE-ID> --get-draft
```

`--body-format`: `storage` (XHTML), `atlas_doc_format` (ADF JSON), `view` (rendered).

Include flags: `--include-labels`, `--include-direct-children`, `--include-version`, `--include-versions`, `--include-collaborators`, `--include-likes`, `--include-properties`.

Note: acli currently only supports `page view`. To search for pages, use the page ID directly. To create/edit pages, use the Atlassian MCP server or the web UI.

### Space

```bash
acli confluence space list
acli confluence space list --type personal --status archived --json
acli confluence space list --keys "SPACE1,SPACE2"
acli confluence space view --id <SPACE-ID> --include-all
acli confluence space view --id <SPACE-ID> --labels --permissions --json
acli confluence space create --key NEWSPACE --name "Space Name" --description "..." --private
acli confluence space update --key SPACEKEY --name "New Name" --description "Updated"
acli confluence space archive --key SPACEKEY
acli confluence space restore --key SPACEKEY
```

`--type`: `global`, `personal`. `--status`: `current`, `archived`.

### Blog

```bash
acli confluence blog list --space-id <SPACE-ID> --limit 10 --json
acli confluence blog list --space-id <SPACE-ID> --title "Release Notes"
acli confluence blog view --id <BLOG-ID> --body-format storage --json
acli confluence blog create --space-id <SPACE-ID> --title "Title" --body "<p>Content</p>"
acli confluence blog create --space-id <SPACE-ID> --title "Draft" --status draft --from-file blog.html
acli confluence blog create --generate-json
```

`--status`: `current` (published), `draft`.

---

## Common Flags

| Flag | Short | Applies to |
|------|-------|------------|
| `--key` | `-k` | Work item key(s), comma-separated |
| `--jql` | `-j` | JQL query string |
| `--filter` | | Saved filter ID |
| `--fields` | `-f` | Fields to include in output |
| `--limit` | `-l` | Maximum results |
| `--paginate` | | Fetch all pages of results |
| `--json` | | JSON output |
| `--csv` | | CSV output |
| `--web` | `-w` | Open in browser |
| `--yes` | `-y` | Skip confirmation prompts |
| `--ignore-errors` | | Continue on partial failures |

---

## Decision Patterns

### Querying: Zoom In, Don't Dump

**Start broad and shallow, then drill into detail.** When a user asks "where are we on the project?", don't pull every issue — that's a firehose. Instead:

1. **Start at epic level:** `--jql "project = PROJ AND type = Epic"` with `--limit 10`.
2. **Summarize from that.** Report epics and their statuses. This often answers the question.
3. **Drill in only if asked:** `--jql "'Epic Link' = PROJ-100 AND status != Done"`.

Always start with the smallest query that answers the question.

### Creating Issues

1. If the project key is unclear, run `acli jira project list --recent` to discover it.
2. Use `acli jira workitem create --generate-json` once to understand the field structure.
3. For bulk creation (from meeting notes or specs): prepare a JSON or CSV file and use `create-bulk`.

### Transitioning Issues

acli uses the status **name** directly — no need to look up transition IDs. Just use `--status "Done"`. If the transition name doesn't match, acli will error with available options.

### Understanding Fields by Inspecting Existing Issues

When you're unsure how a field works — especially custom fields — fetch an existing issue that already has it set:

```bash
acli jira workitem view <KEY> --fields "*all" --json
```

Inspect the response to see field formats, custom field keys, and value structures. This is faster and more accurate than guessing.

---

## Workflow Recipes

### Daily Stand-up Summary

```bash
# Done yesterday
acli jira workitem search --jql "assignee = currentUser() AND status changed to Done AFTER startOfDay('-1d')" --fields "key,summary" --limit 20

# In progress
acli jira workitem search --jql "assignee = currentUser() AND sprint in openSprints() AND statusCategory = 'In Progress'" --fields "key,summary,status" --limit 20
```

Summarize: done, in-progress, and any blockers.

### Sprint Report

```bash
# Completed
acli jira workitem search --jql "sprint = '<Sprint Name>' AND status = Done" --fields "key,summary" --limit 50

# Carry-overs
acli jira workitem search --jql "sprint = '<Sprint Name>' AND status != Done" --fields "key,summary,status" --limit 50
```

Calculate completion rate. Optionally publish to Confluence as a blog post.

### Bug Triage

```bash
# Read the bug
acli jira workitem view <KEY> --fields "summary,description,status,priority,labels"

# Search for duplicates
acli jira workitem search --jql "project = PROJ AND type = Bug AND text ~ '<keywords>'" --fields "key,summary,status" --limit 5

# Triage: set priority, labels, assignee, and comment
acli jira workitem edit --key <KEY> --labels "triaged,p1"
acli jira workitem assign --key <KEY> --assignee "dev@example.com"
acli jira workitem comment create --key <KEY> --body "Triaged: P1. No duplicates found. Assigned to dev team."
```

### Move and Reassign

```bash
acli jira workitem transition --key <KEY> --status "In Progress"
acli jira workitem assign --key <KEY> --assignee "new-owner@example.com"
acli jira workitem comment create --key <KEY> --body "Reassigned to new-owner for sprint 5."
```

### Sprint Management (acli advantage over MCP)

```bash
# Create a new sprint
acli jira sprint create --name "Sprint 5" --board <BOARD-ID> --start 2026-03-15 --end 2026-03-29 --goal "Complete auth flow"

# Start the sprint
acli jira sprint update --id <SPRINT-ID> --state active

# Close the sprint
acli jira sprint update --id <SPRINT-ID> --state closed
```

### Batch Operations

```bash
# Comment on multiple work items
acli jira workitem comment create --key "<K1>,<K2>,<K3>" --body "Batch update"

# Transition via JQL
acli jira workitem transition --jql "project = PROJ AND labels = ready" --status "Done" --yes

# Bulk label update
acli jira workitem edit --jql "project = PROJ AND labels = old" --labels "new" --yes

# Bulk assign
acli jira workitem assign --jql "project = PROJ AND assignee is EMPTY AND sprint in openSprints()" --assignee "dev@example.com" --yes
```

### Create Tickets from Meeting Notes

1. Extract action items from the notes.
2. Prepare a CSV or JSON file with one row per ticket.
3. Bulk create:

```bash
acli jira workitem create-bulk --from-csv meeting-actions.csv --yes
```

### Publish Release Notes to Confluence

```bash
# Gather shipped items
acli jira workitem search --jql "project = PROJ AND fixVersion = 'v2.5' AND status = Done" --fields "key,summary,issuetype" --json > shipped.json

# Create a blog post (after formatting the content)
acli confluence blog create --space-id <SPACE-ID> --title "Release Notes — v2.5" --from-file release-notes.html
```

---

## Jira + Confluence: The Combination

Jira tracks **what** and **when**. Confluence tracks **why** and **how**.

| Content | Where | Why |
|---|---|---|
| Requirements, specs, design docs | Confluence | Long-form, collaborative, versioned |
| Sprint goals and retrospectives | Confluence | Narrative that doesn't fit in a ticket |
| Meeting notes → action items | Confluence (notes) → Jira (tickets) | Notes capture context; tickets capture commitments |
| Individual work items | Jira | Trackable, assignable, sprintable |
| Bug reports and triage | Jira | Status-driven workflow |
| Release notes | Confluence (generated from Jira) | Aggregated view for stakeholders |

---

## acli vs MCP: When to Use Which

| Capability | acli | MCP |
|---|---|---|
| Search / view issues | Compact, fast output | Large JSON payloads |
| Create / edit / transition | Full support | Full support |
| Sprint create / start / close | Supported | Not available |
| Board create / delete | Supported | Not available |
| Bulk create from CSV/JSON | `create-bulk` command | Must loop API calls |
| Confluence page create/edit | Not yet available | Full support |
| Confluence page search (CQL) | Not yet available | Full support |
| Upload attachments | Not available | Not available |

**Rule of thumb:** Use acli for all Jira operations and Confluence read/blog/space operations. Fall back to MCP for Confluence page creation/editing and CQL search.

---

## Instance Memory: What to Cache Across Sessions

After your first session with an instance, save these constants to persistent memory so you never rediscover them:

```
## Jira Instance Constants
- site: <e.g., yourteam.atlassian.net>
- project key(s): <e.g., PROJ, TEAM>
- board ID: <from board search>
- active sprint ID: <update when sprints change>
- space ID(s): <for Confluence spaces>
```

**What to cache:** site URL, project keys, board IDs, Confluence space IDs.

**What not to cache:** Sprint IDs (change every cycle — rediscover with `board list-sprints --state active`), issue counts or statuses (always query live).

---

## Practical Tips

**Always leave a comment when modifying issues.** Especially when triaging, reassigning, or transitioning. Silent changes erode trust.

**Always set `--limit`.** Default to 10. Use `--count` first if unsure about result set size.

**Use `--json` for structured data processing.** Use default (table) output for human-readable summaries. Use `--csv` for export.

**Use `--yes` for batch operations.** Without it, acli will prompt for confirmation on each item.

**Confirm destructive actions.** Before bulk-transitioning, deleting, or making sweeping edits, show the user what you plan to do and ask for approval.

**Use labels and components, not just epics.** Epics are for feature-level grouping. Labels are for cross-cutting concerns ("tech-debt", "security"). Components are for system areas ("backend", "iOS").

**Prefer `--fields` to limit output.** Don't fetch `*all` fields unless you need them. Smaller output = faster parsing.

---

## Error Quick Reference

| Error | Fix |
|---|---|
| `not authenticated` | Run `acli auth login` |
| JQL syntax error | Check field names; quote values with spaces |
| Transition not available | The issue isn't in a status that allows that transition; view the issue first |
| 403 Forbidden | User lacks permission for this project/action |
| Field format wrong | Inspect an existing issue: `view <KEY> --fields "*all" --json` |
| Rate limited | Reduce batch size, add `--limit`, cache metadata |

---

## Reference Files

- **[ADF Reference](adf-reference.md)** — Atlassian Document Format examples for rich text in comments and descriptions
- **[Advanced JQL Reference](references/advanced-jql-reference.md)** — Date functions, sprint queries, status-change tracking, link-based queries, component/label filtering
