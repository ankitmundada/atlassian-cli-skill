---
name: smart-commits
version: 0.1.0
description: "Link git activity to Jira automatically. Use this skill whenever creating git commits, branches, or pull requests in a project that uses Jira. Ensures commit messages, branch names, and PR titles include Jira issue keys so they appear in Jira's development panel. Trigger when: committing code related to a Jira issue, creating branches for Jira work, opening PRs for Jira-tracked work, or when the user mentions a Jira issue key (like PROJ-123) in the context of git operations."
---

# Smart Commits — Agent Skill

Include Jira issue keys in git commits, branches, and PRs so Jira automatically links them. This skill covers the full workflow from picking up an issue to closing it via commit.

**Keys must be UPPERCASE** — `PROJ-123`, not `proj-123`.

---

## 1. Find the Issue Key

Before any git operation, determine the issue key. Try these in order:

```bash
# Check the current branch — it may already contain the key
git branch --show-current
# e.g., "PROJ-123-add-login" → key is PROJ-123

# Look up an issue by key
atlassian-cli jira issue view PROJ-123

# Search if you only know the topic
atlassian-cli jira issue search --jql "project = PROJ AND text ~ 'login'" --limit 5
```

---

## 2. Create a Branch

```bash
git checkout -b <ISSUE-KEY>-short-description
```

Examples:
```bash
git checkout -b PROJ-123-add-login-page
git checkout -b PROJ-456-fix-null-pointer
```

The key in the branch name links it to Jira's development panel automatically.

---

## 3. Commit with Smart Commands

Every commit message should start with the issue key. You can also embed commands that update the Jira issue directly.

### Basic commit

```bash
git commit -m "<ISSUE-KEY> <description>"
```

### Smart commit commands

| Command | Effect | Example |
|---------|--------|---------|
| `#comment <text>` | Adds a comment to the issue | `#comment Fixed the race condition in auth` |
| `#time <duration>` | Logs work time | `#time 2h`, `#time 30m`, `#time 1h 30m` |
| `#<transition>` | Transitions the issue | `#done`, `#in-progress`, `#in-review` |

### Practical examples

```bash
# Simple commit — just links to the issue
git commit -m "PROJ-123 Add login form component"

# Comment on the issue to document what was done
git commit -m "PROJ-123 #comment Added OAuth support with Google and GitHub providers"

# Log time spent
git commit -m "PROJ-123 #time 2h Add unit tests for login flow"

# Final commit — comment + close the issue in one step
git commit -m "PROJ-123 #comment Completed login feature with OAuth, tests passing #done"

# Multiple issues in one commit
git commit -m "PROJ-123 PROJ-456 #comment Fix shared auth module affecting both issues"
```

### When to use each command

- **`#comment`** — use on meaningful commits to leave a trail in Jira. Especially useful when finishing work, explaining a fix, or documenting a decision. Don't comment on every trivial commit.
- **`#time`** — use when the team tracks time in Jira.
- **`#done`** (or other transitions) — use on the final commit to auto-close the issue. Saves a manual status update.

---

## 4. Create a Pull Request

```bash
gh pr create --title "<ISSUE-KEY> <description>" --body "..."
```

Example:
```bash
gh pr create --title "PROJ-123 Add login page with OAuth" --body "Implements login with Google and GitHub OAuth providers."
```

The key in the PR title links it to the Jira issue.

---

## Workflow Summary

```
1. Pick up issue         →  atlassian-cli jira issue view PROJ-123
2. Create branch         →  git checkout -b PROJ-123-add-login
3. Work + commit         →  git commit -m "PROJ-123 Add login form"
4. Final commit + close  →  git commit -m "PROJ-123 #comment Login complete, tests passing #done"
5. Open PR               →  gh pr create --title "PROJ-123 Add login page"
```
