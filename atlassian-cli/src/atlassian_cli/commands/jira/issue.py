"""Jira issue commands: search, view, create, edit, delete, transition, assign."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer

from atlassian_cli.client import get_client, jira_get, jira_post, jira_put, jira_delete, dev_status_get
from atlassian_cli.output import render, render_single, render_message

app = typer.Typer(help="Issue commands.")


# ── helpers ──────────────────────────────────────────────────────────────


def _extract_issue_row(issue: dict) -> dict:
    f = issue.get("fields", {})
    return {
        "key": issue.get("key", ""),
        "summary": f.get("summary", ""),
        "status": (f.get("status") or {}).get("name", ""),
        "assignee": (f.get("assignee") or {}).get("displayName", "Unassigned"),
        "priority": (f.get("priority") or {}).get("name", ""),
        "type": (f.get("issuetype") or {}).get("name", ""),
    }


ISSUE_COLUMNS = ["key", "type", "status", "priority", "assignee", "summary"]


def _extract_issue_detail(issue: dict) -> dict:
    f = issue.get("fields", {})
    desc = f.get("description")
    # ADF description — extract text content
    if isinstance(desc, dict):
        desc = _adf_to_text(desc)
    return {
        "Key": issue.get("key", ""),
        "Summary": f.get("summary", ""),
        "Status": (f.get("status") or {}).get("name", ""),
        "Type": (f.get("issuetype") or {}).get("name", ""),
        "Priority": (f.get("priority") or {}).get("name", ""),
        "Assignee": (f.get("assignee") or {}).get("displayName", "Unassigned"),
        "Reporter": (f.get("reporter") or {}).get("displayName", ""),
        "Labels": ", ".join(f.get("labels", [])),
        "Created": f.get("created", ""),
        "Updated": f.get("updated", ""),
        "Description": desc or "",
    }


DEV_LABELS = {
    "repository": "commits",
    "branch": "branches",
    "pullrequest": "pull requests",
    "build": "builds",
    "review": "reviews",
    "deployment-environment": "deployments",
}


def _get_dev_summary(client, issue_id: str) -> dict:
    """Fetch dev-status summary for an issue. Returns empty dict on failure."""
    try:
        data = dev_status_get(client, "issue/summary", issueId=issue_id)
        summary = data.get("summary", {})
        result = {}
        for category, info in summary.items():
            overall = info.get("overall", {}) if isinstance(info, dict) else {}
            count = overall.get("count", 0)
            if count > 0:
                label = DEV_LABELS.get(category, category)
                result[label] = count
        return result
    except Exception:
        return {}


def _get_dev_detail(client, issue_id: str) -> dict:
    """Fetch detailed dev info (commits, branches, PRs) for an issue."""
    result: dict = {"commits": [], "branches": [], "pull_requests": []}
    try:
        summary_data = dev_status_get(client, "issue/summary", issueId=issue_id)
        summary = summary_data.get("summary", {})
    except Exception:
        return result

    # Fetch detail for each category that has data
    detail_types = [
        ("repository", "commits"),
        ("branch", "branches"),
        ("pullrequest", "pull_requests"),
    ]
    for data_type, result_key in detail_types:
        cat = summary.get(data_type, {})
        overall = cat.get("overall", {})
        if overall.get("count", 0) == 0:
            continue
        # Get instance types (e.g. GitHub, Bitbucket)
        for instance_name in cat.get("byInstanceType", {}):
            try:
                detail = dev_status_get(
                    client, "issue/detail",
                    issueId=issue_id,
                    applicationType=instance_name,
                    dataType=data_type,
                )
                for entry in detail.get("detail", []):
                    if result_key == "commits":
                        for repo in entry.get("repositories", []):
                            for commit in repo.get("commits", []):
                                result["commits"].append({
                                    "id": commit.get("displayId", ""),
                                    "message": commit.get("message", "").split("\n")[0],
                                    "author": commit.get("author", {}).get("name", ""),
                                    "url": commit.get("url", ""),
                                })
                    elif result_key == "branches":
                        for repo in entry.get("repositories", []):
                            for branch in repo.get("branches", []):
                                result["branches"].append({
                                    "name": branch.get("name", ""),
                                    "url": branch.get("url", ""),
                                })
                    elif result_key == "pull_requests":
                        for pr in entry.get("pullRequests", []):
                            result["pull_requests"].append({
                                "id": pr.get("id", ""),
                                "title": pr.get("name", ""),
                                "state": pr.get("status", ""),
                                "url": pr.get("url", ""),
                                "author": pr.get("author", {}).get("name", ""),
                            })
            except Exception:
                continue
    return result


def _format_dev_markdown(key: str, dev: dict) -> str:
    """Format dev detail dict as markdown."""
    lines = [f"# Development — {key}", ""]
    if dev["commits"]:
        lines.append("## Commits")
        for c in dev["commits"]:
            lines.append(f"- `{c['id']}` {c['message']} — {c['author']}")
        lines.append("")
    if dev["branches"]:
        lines.append("## Branches")
        for b in dev["branches"]:
            lines.append(f"- `{b['name']}`")
        lines.append("")
    if dev["pull_requests"]:
        lines.append("## Pull Requests")
        for pr in dev["pull_requests"]:
            state = f"[{pr['state']}]" if pr["state"] else ""
            lines.append(f"- {pr['title']} {state} — {pr['author']}")
        lines.append("")
    if not dev["commits"] and not dev["branches"] and not dev["pull_requests"]:
        lines.append("No linked development activity.")
        lines.append("")
    return "\n".join(lines)


def _adf_to_text(adf: dict) -> str:
    """Recursively extract plain text from ADF JSON."""
    if adf.get("type") == "text":
        return adf.get("text", "")
    parts = []
    for child in adf.get("content", []):
        parts.append(_adf_to_text(child))
    return "\n".join(filter(None, parts))


# ── commands ─────────────────────────────────────────────────────────────


@app.command()
def search(
    jql: str = typer.Option(..., "--jql", "-j", help="JQL query string"),
    fields: str = typer.Option("key,summary,status,assignee,priority,issuetype", "--fields", "-f", help="Comma-separated fields"),
    limit: int = typer.Option(10, "--limit", "-l", help="Max results"),
    count: bool = typer.Option(False, "--count", help="Only print the count"),
    output: str = typer.Option("table", "--output", "-o", help="table, json, or csv"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Auth profile"),
) -> None:
    """Search issues with JQL."""
    client = get_client(profile)
    data = jira_post(client, "search/jql", json={
        "jql": jql,
        "fields": [f.strip() for f in fields.split(",")],
        "maxResults": limit,
    })
    if count:
        print(data.get("total", 0))
        return

    issues = data.get("issues", [])
    rows = [_extract_issue_row(i) for i in issues]
    total = data.get("total", len(rows))
    title = f"Results ({len(rows)} of {total})"
    render(rows, ISSUE_COLUMNS, output=output, title=title)


@app.command()
def view(
    key: str = typer.Argument(help="Issue key (e.g. PROJ-123)"),
    fields: str = typer.Option("*navigable", "--fields", "-f", help="Fields to fetch"),
    dev: bool = typer.Option(False, "--dev", help="Show linked commits, branches, and PRs"),
    output: str = typer.Option("table", "--output", "-o", help="table, json, or csv"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p"),
) -> None:
    """View an issue by key."""
    client = get_client(profile)
    params = {}
    if fields != "*all":
        params["fields"] = fields
    issue = jira_get(client, f"issue/{key}", **params)
    issue_id = issue.get("id", "")

    if dev:
        dev_detail = _get_dev_detail(client, issue_id)
        if output == "json":
            print(json.dumps(dev_detail, indent=2))
        else:
            print(_format_dev_markdown(key, dev_detail))
        return

    if output == "json":
        dev_summary = _get_dev_summary(client, issue_id)
        if dev_summary:
            issue["devSummary"] = dev_summary
        print(json.dumps(issue, indent=2))
    else:
        detail = _extract_issue_detail(issue)
        dev_summary = _get_dev_summary(client, issue_id)
        if dev_summary:
            parts = [f"{k}: {v}" for k, v in dev_summary.items()]
            detail["Development"] = ", ".join(parts)
        render_single(detail, output=output)


@app.command()
def create(
    project: str = typer.Option(..., "--project", "-P", help="Project key"),
    type: str = typer.Option("Task", "--type", "-t", help="Issue type"),
    summary: str = typer.Option(..., "--summary", "-s", help="Issue summary"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Plain text description"),
    assignee: Optional[str] = typer.Option(None, "--assignee", "-a", help="Assignee email or @me"),
    labels: Optional[str] = typer.Option(None, "--labels", help="Comma-separated labels"),
    priority: Optional[str] = typer.Option(None, "--priority", help="Priority name"),
    parent: Optional[str] = typer.Option(None, "--parent", help="Parent issue key (for sub-tasks)"),
    from_json: Optional[Path] = typer.Option(None, "--from-json", help="Create from JSON file"),
    output: str = typer.Option("table", "--output", "-o"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p"),
) -> None:
    """Create a new issue."""
    client = get_client(profile)

    if from_json:
        payload = json.loads(from_json.read_text())
    else:
        fields_dict: dict = {
            "project": {"key": project},
            "issuetype": {"name": type},
            "summary": summary,
        }
        if description:
            fields_dict["description"] = _text_to_adf(description)
        if assignee:
            if assignee == "@me":
                fields_dict["assignee"] = {"id": _get_myself(client)}
            else:
                fields_dict["assignee"] = {"id": _find_user(client, assignee)}
        if labels:
            fields_dict["labels"] = [l.strip() for l in labels.split(",")]
        if priority:
            fields_dict["priority"] = {"name": priority}
        if parent:
            fields_dict["parent"] = {"key": parent}
        payload = {"fields": fields_dict}

    result = jira_post(client, "issue", json=payload)
    key = result.get("key", "")
    render_message(f"[green]Created {key}[/green]")


@app.command()
def edit(
    key: str = typer.Argument(help="Issue key"),
    summary: Optional[str] = typer.Option(None, "--summary", "-s"),
    description: Optional[str] = typer.Option(None, "--description", "-d"),
    assignee: Optional[str] = typer.Option(None, "--assignee", "-a"),
    unassign: bool = typer.Option(False, "--unassign", help="Remove assignee"),
    labels: Optional[str] = typer.Option(None, "--labels", help="Set labels (comma-separated)"),
    priority: Optional[str] = typer.Option(None, "--priority"),
    from_json: Optional[Path] = typer.Option(None, "--from-json"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p"),
) -> None:
    """Edit an existing issue."""
    client = get_client(profile)

    if from_json:
        payload = json.loads(from_json.read_text())
    else:
        fields_dict: dict = {}
        if summary:
            fields_dict["summary"] = summary
        if description:
            fields_dict["description"] = _text_to_adf(description)
        if unassign:
            fields_dict["assignee"] = None
        elif assignee:
            if assignee == "@me":
                fields_dict["assignee"] = {"id": _get_myself(client)}
            else:
                fields_dict["assignee"] = {"id": _find_user(client, assignee)}
        if labels:
            fields_dict["labels"] = [l.strip() for l in labels.split(",")]
        if priority:
            fields_dict["priority"] = {"name": priority}
        if not fields_dict:
            print("Nothing to update. Specify at least one field.", file=sys.stderr)
            raise SystemExit(1)
        payload = {"fields": fields_dict}

    jira_put(client, f"issue/{key}", json=payload)
    render_message(f"[green]Updated {key}[/green]")


@app.command()
def delete(
    key: str = typer.Argument(help="Issue key"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p"),
) -> None:
    """Delete an issue."""
    if not yes:
        typer.confirm(f"Delete {key}?", abort=True)
    client = get_client(profile)
    jira_delete(client, f"issue/{key}")
    render_message(f"[yellow]Deleted {key}[/yellow]")


@app.command()
def transition(
    key: str = typer.Argument(help="Issue key"),
    status: str = typer.Option(..., "--status", "-s", help="Target status name"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p"),
) -> None:
    """Transition an issue to a new status."""
    client = get_client(profile)

    # Get available transitions
    data = jira_get(client, f"issue/{key}/transitions")
    transitions = data.get("transitions", [])

    # Find matching transition (case-insensitive)
    match = None
    for t in transitions:
        if t["name"].lower() == status.lower() or t.get("to", {}).get("name", "").lower() == status.lower():
            match = t
            break

    if not match:
        available = ", ".join(
            f"{t['name']} → {t.get('to', {}).get('name', '?')}" for t in transitions
        )
        print(f"No transition to '{status}'. Available: {available}", file=sys.stderr)
        raise SystemExit(1)

    jira_post(client, f"issue/{key}/transitions", json={"transition": {"id": match["id"]}})
    render_message(f"[green]{key} → {match.get('to', {}).get('name', status)}[/green]")


@app.command()
def assign(
    key: str = typer.Argument(help="Issue key"),
    user: str = typer.Option(None, "--user", "-u", help="Assignee email or @me"),
    unassign: bool = typer.Option(False, "--unassign", help="Remove assignee"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p"),
) -> None:
    """Assign or unassign an issue."""
    client = get_client(profile)

    if unassign:
        jira_put(client, f"issue/{key}/assignee", json={"accountId": None})
        render_message(f"[green]Unassigned {key}[/green]")
        return

    if not user:
        print("Specify --user or --unassign.", file=sys.stderr)
        raise SystemExit(1)

    if user == "@me":
        account_id = _get_myself(client)
    else:
        account_id = _find_user(client, user)

    jira_put(client, f"issue/{key}/assignee", json={"accountId": account_id})
    render_message(f"[green]Assigned {key} to {user}[/green]")


# ── user lookup helpers ──────────────────────────────────────────────────


def _get_myself(client) -> str:
    data = jira_get(client, "myself")
    return data["accountId"]


def _find_user(client, query: str) -> str:
    users = jira_get(client, "user/search", query=query)
    if not users:
        print(f"No user found for '{query}'", file=sys.stderr)
        raise SystemExit(1)
    return users[0]["accountId"]


def _text_to_adf(text: str) -> dict:
    """Convert plain text to minimal ADF JSON."""
    paragraphs = []
    for line in text.split("\n"):
        paragraphs.append({
            "type": "paragraph",
            "content": [{"type": "text", "text": line}] if line else [],
        })
    return {"version": 1, "type": "doc", "content": paragraphs}
