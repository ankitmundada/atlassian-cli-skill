---
name: smart-commits
version: 0.1.0
description: "Link git activity to Jira automatically. Use this skill whenever creating git commits, branches, or pull requests in a project that uses Jira. Ensures commit messages, branch names, and PR titles include Jira issue keys so they appear in Jira's development panel. Trigger when: committing code related to a Jira issue, creating branches for Jira work, opening PRs for Jira-tracked work, or when the user mentions a Jira issue key (like PROJ-123) in the context of git operations."
---

# Smart Commits — Agent Skill

Link git commits, branches, and PRs to Jira issues automatically by including the issue key in the right places. Jira's integration picks up these references and shows them in the issue's Development panel.

**Requirement:** The Jira instance must be connected to the git host (GitHub, Bitbucket, GitLab). No agent-side setup needed — just format names correctly.

---

## Rules

1. **Issue keys must be UPPERCASE.** `PROJ-123`, not `proj-123`.
2. **Ask for the issue key if you don't have one.** Don't commit without linking when the user is working on a tracked issue.
3. **One key minimum, multiple allowed.** `PROJ-123 PROJ-456 Fix auth and session bugs` links to both issues.

---

## Branches

Include the issue key in the branch name:

```bash
git checkout -b PROJ-123-add-login-page
```

If the user already told you the issue key, use it. If not, ask — or check the current branch name (it may already contain a key).

---

## Commits

Include the issue key at the start of the commit message:

```bash
git commit -m "PROJ-123 Add login page with OAuth support"
```

**Multi-issue commits:**

```bash
git commit -m "PROJ-123 PROJ-456 Fix shared auth module"
```

The key can appear anywhere in the message, but leading with it is conventional and easiest to scan.

---

## Pull Requests

Include the issue key in the PR title:

```bash
gh pr create --title "PROJ-123 Add login page" --body "..."
```

Alternatively, if the source branch contains the key, the PR is linked automatically — but including it in the title is more explicit and always works.

---

## Finding the Issue Key

If the user hasn't provided a key:

1. **Check the branch name** — it may already contain one (e.g., `PROJ-123-feature`).
2. **Ask the user** — "Which Jira issue should this commit link to?"
3. **Search Jira** — if you have the atlassian-cli skill, use `atlassian-cli jira issue search --jql "..." --limit 5` to find the relevant issue.

---

## Smart Commit Commands (Optional)

If the Jira admin has enabled smart commits, you can add time tracking and transitions directly in commit messages:

```bash
# Log time
git commit -m "PROJ-123 #time 2h Fix pagination bug"

# Transition issue
git commit -m "PROJ-123 #done Fix pagination bug"

# Add comment
git commit -m "PROJ-123 #comment Fixed by updating the query logic"

# Combined
git commit -m "PROJ-123 #time 1h #comment Refactored auth flow #done"
```

**Only use smart commit commands when the user explicitly asks** to log time, transition, or comment via commit. Don't add them by default.
