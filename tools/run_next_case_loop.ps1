<#
.SYNOPSIS
  External loop: process N Supply Code cases, each in a fresh Grok headless session.

.DESCRIPTION
  Each iteration:
    1. python tools/prepare_next_scj.py  (pick PDF, skip dups, extract text)
    2. grok -p                          (author lean JSON only — quality-critical)
    3. python tools/finalize_scj.py     (PDF, state, index, git) if the agent did not
  Fresh grok process each time (no -c / -r). Quality of the JSON is unchanged;
  Chrome/git/index no longer occupy model turns.

.PARAMETER Count
  Max cases to process (default 10).

.PARAMETER RepoRoot
  Repo path (default: parent of tools/).

.PARAMETER MaxTurns
  Max agent turns per case (default 50 — JSON-only runs need far fewer than 100).

.PARAMETER NoPush
  Finalize commits locally but does not git push (faster; push yourself at the end).

.PARAMETER DryRun
  Print commands only; do not extract or invoke grok.

.EXAMPLE
  cd C:\Users\HP\Downloads\Grok\Claude
  powershell -ExecutionPolicy Bypass -File tools\run_next_case_loop.ps1 -Count 100
#>
[CmdletBinding()]
param(
  [int]$Count = 10,
  [string]$RepoRoot = "",
  [int]$MaxTurns = 50,
  [switch]$NoPush,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
  $RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
}
$RepoRoot = (Resolve-Path $RepoRoot).Path
Set-Location $RepoRoot

$ScRoot = Join-Path $RepoRoot "supply-code"
if (-not (Test-Path $ScRoot)) {
  throw "Missing supply-code/ under $RepoRoot"
}

$promptFile = Join-Path $RepoRoot "tools\prompts\next_case_once.txt"
$preparePy = Join-Path $RepoRoot "tools\prepare_next_scj.py"
$finalizePy = Join-Path $RepoRoot "tools\finalize_scj.py"
$ticketPath = Join-Path $ScRoot "tmp\NEXT_TICKET.json"
if (-not (Test-Path $promptFile)) { throw "Missing prompt file: $promptFile" }

$grok = Get-Command grok -ErrorAction SilentlyContinue
if (-not $grok -and -not $DryRun) {
  $candidate = Join-Path $env:USERPROFILE ".grok\bin\grok.exe"
  if (Test-Path $candidate) { $grokPath = $candidate }
  else { throw "grok not found on PATH. Install Grok CLI or add %USERPROFILE%\.grok\bin to PATH." }
} else {
  $grokPath = if ($grok) { $grok.Source } else { "grok" }
}

$logDir = Join-Path $ScRoot "tmp\loop_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = Join-Path $logDir "next_case_loop_$stamp.log"
$py = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "python3" }

function Write-Log([string]$msg) {
  $line = "[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $msg
  Write-Host $line
  Add-Content -Path $logFile -Value $line -Encoding UTF8
}

function Get-NextSeq {
  $s = Get-Content (Join-Path $ScRoot "state\index.json") -Raw -Encoding UTF8 | ConvertFrom-Json
  return [int]$s.next_seq
}

function Get-Ticket {
  if (-not (Test-Path $ticketPath)) { return $null }
  return (Get-Content $ticketPath -Raw -Encoding UTF8 | ConvertFrom-Json)
}

Write-Log "Repo: $RepoRoot"
Write-Log "Grok: $grokPath"
Write-Log "Count: $Count | MaxTurns: $MaxTurns | NoPush: $NoPush | Log: $logFile"
Write-Log "Starting next_seq=$(Get-NextSeq)"

$ok = 0
$fail = 0
$skipped = 0

for ($i = 1; $i -le $Count; $i++) {
  $seqBefore = Get-NextSeq
  Write-Log "===== CASE $i / $Count | next_seq=$seqBefore ====="

  if ($DryRun) {
    Write-Log "DRY-RUN: $py tools/prepare_next_scj.py"
    Write-Log "DRY-RUN: $grokPath --prompt-file $promptFile --max-turns $MaxTurns"
    Write-Log "DRY-RUN: $py tools/finalize_scj.py SCJ-NNN --source <file>"
    continue
  }

  & $py $preparePy
  $prepExit = $LASTEXITCODE
  if ($prepExit -eq 2) {
    Write-Log "STOP: prepare reported NO_INPUT (next_seq=$seqBefore)"
    $skipped = $Count - $i + 1
    break
  }
  if ($prepExit -ne 0) {
    Write-Log "FAIL case $i prepare exit=$prepExit"
    $fail++
    continue
  }

  $ticket = Get-Ticket
  if (-not $ticket -or $ticket.status -ne "READY") {
    Write-Log "FAIL case ${i}: bad ticket $ticketPath"
    $fail++
    continue
  }
  Write-Log "ticket $($ticket.case_id) source=$($ticket.source) words=$($ticket.word_count)"

  $caseLog = Join-Path $logDir ("case_{0:D2}_{1}_{2}.log" -f $i, $ticket.case_id, $stamp)
  $grokArgs = @(
    "--cwd", $RepoRoot,
    "--prompt-file", $promptFile,
    "--permission-mode", "bypassPermissions",
    "--always-approve",
    "--max-turns", "$MaxTurns",
    "--output-format", "plain",
    "--no-auto-update"
  )

  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  try {
    & $grokPath @grokArgs 2>&1 | Tee-Object -FilePath $caseLog
    $exit = $LASTEXITCODE
  } catch {
    Write-Log "ERROR invoking grok: $_"
    $exit = 1
  }
  $sw.Stop()

  $jsonPath = Join-Path $ScRoot "summaries\json\$($ticket.case_id).json"
  $seqMid = Get-NextSeq
  $tail = ""
  if (Test-Path $caseLog) {
    $tail = (Get-Content $caseLog -Tail 8 -ErrorAction SilentlyContinue) -join " | "
  }

  # Safety net: if the agent wrote JSON but skipped finalize, do it here.
  if ((Test-Path $jsonPath) -and ($seqMid -le $seqBefore)) {
    Write-Log "agent left JSON unfinalized; running finalize_scj.py"
    $finArgs = @($finalizePy, $ticket.case_id, "--source", $ticket.source)
    if ($NoPush) { $finArgs += "--no-push" }
    & $py @finArgs
    if ($LASTEXITCODE -ne 0) {
      Write-Log "FAIL case $i finalize exit=$LASTEXITCODE"
      Write-Log "  tail: $tail"
      $fail++
      continue
    }
  }

  $seqAfter = Get-NextSeq
  $elapsed = [int]$sw.Elapsed.TotalSeconds

  if ($seqAfter -gt $seqBefore) {
    Write-Log "OK case $i $($ticket.case_id) done → next_seq=$seqAfter elapsed=${elapsed}s"
    Write-Log "  tail: $tail"
    $ok++
  } elseif ($tail -match "NO_INPUT") {
    Write-Log "STOP: agent reported NO_INPUT"
    break
  } elseif ($exit -ne 0 -and $null -ne $exit) {
    Write-Log "FAIL case $i exit=$exit elapsed=${elapsed}s next_seq=$seqAfter"
    Write-Log "  tail: $tail"
    $fail++
  } elseif ($tail -match "FAILED") {
    Write-Log "FAIL case $i agent FAILED next_seq still $seqAfter"
    Write-Log "  tail: $tail"
    $fail++
  } else {
    Write-Log "WARN case $i exit=0 but next_seq unchanged ($seqBefore). Check $caseLog"
    Write-Log "  tail: $tail"
    $fail++
  }
}

Write-Log "===== DONE ok=$ok fail=$fail skipped_remaining~$skipped next_seq=$(Get-NextSeq) ====="
Write-Log "Full log: $logFile"
Write-Host ""
Write-Host "Summary: ok=$ok fail=$fail | next_seq=$(Get-NextSeq) | log=$logFile"
exit $(if ($fail -gt 0) { 1 } else { 0 })
