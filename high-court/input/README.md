# Add High Court judgments here

Two ways to queue a case — either one auto-processes into a digest (the source is then moved to
`../processed/`, so this folder always shows what is still pending). Put it here for High Court
cases; use `supreme-court/input/` for Supreme Court.

## 1. Give an Indian Kanoon doc-id or link  ← least friction
Create a file here whose **content** is the doc-id or the IK link. The pipeline fetches the
judgment through the Indian Kanoon API and processes it. Valid content:

- `51255397`
- `https://indiankanoon.org/doc/51255397/`

Name the file anything — using the doc-id as the filename is handy, since re-adding the same id
is then skipped as a duplicate. (An empty file *named* `<docid>.ik` also works.)

*One-time setup this relies on:* `IK_API_TOKEN` set in the cloud environment's variables, and
network access to `indiankanoon.org` / `api.indiankanoon.org`.

## 2. Upload the saved judgment file
Save the IK page (Ctrl/Cmd-S) or download the PDF, and upload it here. Accepted formats — the
content is sniffed, so the file extension does not matter:

- **HTML** — an IK page saved as HTML (richest: preserves cited-case doc-ids).
- **MHTML** — Chrome/Edge *"Webpage, Single File"* (`.mhtml` / "Saved by Blink").
- **PDF** — searchable / text-selectable PDFs (scanned image-only PDFs need OCR first).

---
Prefix a number (`01-`, `02-`, …) to force processing order. You can add several at once.
