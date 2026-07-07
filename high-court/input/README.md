# Drop High Court judgments here

Put a judgment file in this folder and the pipeline auto-processes it into a digest
(source is then moved to `../processed/`, so this folder always shows what's still pending).

**Accepted formats** — the parser sniffs the content, so a missing or odd file extension is fine:
- **HTML** — an Indian Kanoon page saved as HTML. *Richest input:* preserves the cited-case
  doc-ids, so the digest's Table of Authorities gets accurate links.
- **MHTML** — Chrome/Edge *Save page as → "Webpage, Single File"* (`.mhtml` / "Saved by Blink").
  Fully supported (decoded automatically).
- **PDF** — searchable / text-selectable PDFs. Scanned image-only PDFs need OCR first — flag those.

**A plain link does _not_ work.** Giving only an `indiankanoon.org/doc/...` URL can't be
processed: this cloud sandbox can't reach that domain, and Indian Kanoon blocks automated
fetching (HTTP 403). Save the page (Ctrl/Cmd-S) and upload the file instead.

- **Any filename works.** Prefix a number (`01-`, `02-`, …) to force processing order.
- You can upload several at once; each is processed and committed separately.
