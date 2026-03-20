# ADF (Atlassian Document Format) Reference

Jira Cloud uses ADF (JSON) for rich text. Plain `\n` newlines do **not** create paragraph breaks.

## atlassian-cli Limitations

Rejected or stripped by atlassian-cli: headings, bold/italic/code text marks, code block syntax highlighting.

Supported: paragraphs, bullet lists, ordered lists, code blocks (no language highlighting).

## ADF Examples

**Paragraph**
```json
{"version":1,"type":"doc","content":[{"type":"paragraph","content":[{"type":"text","text":"Your text here"}]}]}
```

**Bullet list**
```json
{"version":1,"type":"doc","content":[{"type":"bulletList","content":[{"type":"listItem","content":[{"type":"paragraph","content":[{"type":"text","text":"Item one"}]}]},{"type":"listItem","content":[{"type":"paragraph","content":[{"type":"text","text":"Item two"}]}]}]}]}
```

**Code block**
```json
{"version":1,"type":"doc","content":[{"type":"codeBlock","attrs":{},"content":[{"type":"text","text":"def hello():\n    print('Hello')"}]}]}
```

## Usage

```bash
# Inline ADF
atlassian-cli jira issue comment add <KEY> --body '{"version":1,"type":"doc","content":[...]}'

# From file
atlassian-cli jira issue comment add <KEY> --body-file comment.json
```
