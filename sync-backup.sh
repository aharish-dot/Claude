#!/usr/bin/env bash
# Mirror all branches of origin (aharish-dot/Claude) into the private backup repo
# (aharish-dot/Claude-backup). Safe to run repeatedly: it is a no-op when the
# backup is already up to date, and it never fails the caller — if the backup
# repo is not reachable in this session's git scope it just reports and exits 0.
#
# Usage:  bash sync-backup.sh [path-to-repo]
REPO="${1:-$(git rev-parse --show-toplevel 2>/dev/null || echo /home/user/Claude)}"

ORIGIN="$(git -C "$REPO" remote get-url origin 2>/dev/null)" || { echo "backup: no origin remote"; exit 0; }
BACKUP_URL="${ORIGIN%/*}/Claude-backup"

# Refresh every origin branch locally, then mirror them (with prune) to the backup.
if ! git -C "$REPO" fetch --prune origin '+refs/heads/*:refs/remotes/origin/*' 2>/dev/null; then
  echo "backup: could not fetch origin; skipped"; exit 0
fi

if git -C "$REPO" push --prune "$BACKUP_URL" 'refs/remotes/origin/*:refs/heads/*' 2>/dev/null; then
  echo "backup: synced all branches -> aharish-dot/Claude-backup"
else
  echo "backup: Claude-backup not reachable in this session's scope; skipped"
fi
exit 0
