# Advanced JQL Reference

Supplementary reference for the atlassian-cli skill. Load this file when you need deeper JQL patterns, multi-step workflow recipes, or complex query combinations.

---

## 1. Relative Date Functions

```sql
-- Issues created this week
created >= startOfWeek()

-- Issues updated in the last 3 days
updated >= -3d

-- Issues due before end of month
due <= endOfMonth()

-- Issues resolved between specific dates
resolved >= "2026-01-01" AND resolved <= "2026-03-31"

-- Issues created in the last 2 hours
created >= -2h

-- Issues due next week
due >= startOfWeek("+1w") AND due <= endOfWeek("+1w")
```

Available functions: `startOfDay()`, `endOfDay()`, `startOfWeek()`, `endOfWeek()`, `startOfMonth()`, `endOfMonth()`, `startOfYear()`, `endOfYear()`, `now()`. All accept relative offsets like `("-1d")`, `("+1w")`.

---

## 2. Sprint-Based Queries

```sql
-- All issues in any open sprint
sprint in openSprints()

-- Issues in a specific sprint by name
sprint = "Sprint 2026-Q1-3"

-- Carry-over: unresolved issues from closed sprints
sprint in closedSprints() AND resolution = Unresolved

-- Issues not yet in any sprint (backlog)
sprint is EMPTY AND status = "To Do"

-- Issues in future sprints
sprint in futureSprints()
```

---

## 3. Status Change Queries

```sql
-- Issues that moved to "In Review" today
status changed to "In Review" AFTER startOfDay()

-- Issues that were "In Progress" at some point in the last week
status was "In Progress" DURING (startOfWeek(), now())

-- Issues stuck in current status for more than 5 days
status changed BEFORE -5d AND status != Done

-- Issues transitioned by a specific user
status changed BY "user@example.com"

-- Issues that have ever been in "Blocked" status
status was "Blocked"
```

---

## 4. Component and Label Filtering

```sql
-- Issues with a specific component
component = "Backend API"

-- Issues with multiple labels (AND — must have both)
labels = "performance" AND labels = "p0"

-- Issues with any of these labels (OR)
labels in ("critical", "security", "data-loss")

-- Issues without any label
labels is EMPTY

-- Issues without a component
component is EMPTY
```

---

## 5. Link-Based Queries

```sql
-- Issues that block other issues
issueLinkType = "blocks"

-- Issues linked to a specific epic
"Epic Link" = PROJ-100

-- Parent issue (for sub-tasks)
parent = PROJ-50
```

Note: `issueFunction` queries (like `hasSubtasks()`, `epicsOf()`) require ScriptRunner or similar plugin. Not available by default.

---

## 6. Group and Team Queries

```sql
-- Issues assigned to members of a group
assignee in membersOf("engineering-team")

-- Issues reported by current user
reporter = currentUser()

-- Issues watched by current user
watcher = currentUser()

-- Unassigned issues
assignee is EMPTY
```

---

## 7. Complex Combinations

```sql
-- High-priority bugs in active sprint, unresolved, created in last 30 days
project = "PROJ"
  AND type = Bug
  AND priority in (High, Highest)
  AND sprint in openSprints()
  AND resolution = Unresolved
  AND created >= -30d
  ORDER BY priority DESC, created ASC

-- Stale items: in "To Do" and not updated in 90 days
project = "PROJ" AND status = "To Do" AND updated <= -90d
  ORDER BY updated ASC

-- Items at risk: in progress but not updated in 5+ days
project = "PROJ" AND statusCategory = 'In Progress' AND updated <= -5d
  ORDER BY updated ASC

-- Cross-sprint carry-overs
project = "PROJ" AND sprint in closedSprints() AND resolution = Unresolved
  ORDER BY priority DESC
```

---

## 8. Using JQL with acli

```bash
# Basic search
acli jira workitem search --jql "project = PROJ AND type = Bug AND created >= -7d" --limit 10

# Count only
acli jira workitem search --jql "project = PROJ AND sprint in openSprints()" --count

# Select specific fields
acli jira workitem search --jql "assignee = currentUser() AND status != Done" --fields "key,summary,status,priority"

# JSON output for structured processing
acli jira workitem search --jql "project = PROJ AND fixVersion = 'v2.5'" --json --limit 50

# CSV export
acli jira workitem search --jql "project = PROJ" --csv --paginate

# Filter sprint work items via sprint command (supports JQL filter)
acli jira sprint list-workitems --sprint <ID> --board <ID> --jql "assignee = currentUser()"
```

---

## 9. Common Jira Field Names

| Field | JQL Name | Notes |
|---|---|---|
| Summary | `summary` | |
| Description | `description` | |
| Status | `status` | |
| Status Category | `statusCategory` | `'To Do'`, `'In Progress'`, `'Done'` |
| Assignee | `assignee` | |
| Reporter | `reporter` | |
| Priority | `priority` | |
| Issue Type | `type` or `issuetype` | |
| Project | `project` | |
| Labels | `labels` | |
| Components | `component` | |
| Fix Version | `fixVersion` | |
| Sprint | `sprint` | |
| Epic Link | `"Epic Link"` | Custom field, varies by instance |
| Story Points | `"Story Points"` | Custom field, varies by instance |
| Created | `created` | |
| Updated | `updated` | |
| Resolved | `resolved` | |
| Due Date | `due` | |
| Resolution | `resolution` | |
