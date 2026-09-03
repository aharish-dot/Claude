# Supply Code Jurisprudence

Indian High Court / Supreme Court judgments on electricity Supply Codes, folded into
lean per-case digests (JSON + PDF) and a provision-keyed index.

Branch: `claude/supply-code-jurisprudence-design-yiwgen`  
Status: **SCJ-001 … SCJ-536** done. Treatise on hold until the `input/` queue is empty.

## Run the unattended loop (Windows or Ubuntu)

The same Python orchestrator runs on both. GitHub is the queue (`supply-code/input/`)
and the archive (`processed/` + JSON + digest PDFs). **One machine at a time** — do not
start the loop on Ubuntu while it is still running on Windows, or the reverse.

### Windows (this checkout)

```powershell
git pull
powershell -ExecutionPolicy Bypass -File tools\run_next_case_loop.ps1 -Count 50 -Workers 2
```

### Ubuntu (a separate clone — do not copy the Windows folder)

```bash
git pull
./tools/run_next_case_loop.sh --count 50 --workers 2
```

Both call `tools/run_next_case_workers.py`. `--workers 2` authors two cases at once;
claim (id + PDF) and finalize (Chrome/git/index) stay serial. `--workers 1` is serial
authoring. Max 4.

Verify the machine before a live run:

```bash
./tools/run_next_case_loop.sh --dry-run --count 1    # Ubuntu
# Windows: add -DryRun to the powershell command
```

That must print a **Grok** path and a **Chrome/Chromium** path.

Switch PCs only after the loop has stopped and `git status` is clean (ignore gitignored
`supply-code/tmp/` and `supply-code/extracts/`). Then `git pull` on the other machine.

## Ubuntu one-time setup

```bash
git clone -b claude/supply-code-jurisprudence-design-yiwgen https://github.com/aharish-dot/Claude.git
cd Claude
sudo apt update
sudo apt install -y python3 python3-pip git chromium-browser
python3 -m pip install pymupdf
```

Install the Grok CLI, log in, and put `~/.grok/bin` on `PATH`. Prefer apt Chromium or
Google Chrome over snap. If the browser is not on `PATH`:

```bash
export CHROME=/usr/bin/chromium   # or google-chrome-stable
```

Git push access to this branch is required (the loop commits and pushes each case).

## What the loop does

Each case: extract PDF → stencil or Grok writes lean JSON → Chrome/Chromium digest PDF →
move `input/` → `processed/` in git → commit + push.

Details: [`supply-code/NEXT.md`](supply-code/NEXT.md) (trigger card),
[`supply-code/HANDOFF.md`](supply-code/HANDOFF.md) (resume + gotchas).

## Layout

| Path | What |
|---|---|
| `supply-code/input/` | Live PDF queue (on GitHub) |
| `supply-code/processed/` | Sources after a case is finalized |
| `supply-code/summaries/json/` | Lean digest JSON |
| `supply-code/summaries/pdf/` | Digest PDFs |
| `supply-code/jurisprudence/` | Provision- and principle-keyed spine |
| `tools/run_next_case_loop.ps1` | Windows launcher |
| `tools/run_next_case_loop.sh` | Ubuntu launcher |
| `grok_chats/` | Grok session transcripts for this repo |

## Grok chats

[`grok_chats/`](grok_chats/) archives every Grok CLI session for this working copy.
Folders are named `YYYY-MM-DD_HH-MM-SS` (local time). Index: [`grok_chats/INDEX.md`](grok_chats/INDEX.md).

A `SessionEnd` hook runs `python tools/sync_grok_chats.py --hook`: it copies the
new transcript into `grok_chats/` and, if the case loop is not using git, commits
and pushes only that folder. First time in a clone, run `/hooks-trust` in Grok so
the project hook is allowed. Manual: `python tools/sync_grok_chats.py --push`.
