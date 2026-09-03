# grok_chats

Grok CLI transcripts for this working copy. Each session is a folder named
**local date and time** when it started: `YYYY-MM-DD_HH-MM-SS`.

| File | What |
|---|---|
| `INDEX.md` | Chronological list |
| `<date-time>/summary.json` | Title, timestamps, message counts |
| `<date-time>/chat_history.jsonl` | Raw messages |
| `prompt_history.jsonl` | Prompts typed in this working copy |

New sessions are copied here when a Grok session in this folder ends
(`tools/sync_grok_chats.py`, hooked on `SessionEnd`). If the case loop is not
holding git, that copy is committed and pushed to GitHub in the background.

On a new clone, trust project hooks once: `/hooks-trust` inside Grok.
