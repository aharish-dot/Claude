<#
.SYNOPSIS
  External loop: process N Supply Code cases, each in a fresh Grok headless session.

.DESCRIPTION
  Each iteration:
    1. python tools/prepare_next_scj.py  (pick PDF, skip dups, extract text)
    2. grok -p                          (author lean JSON only -- quality-critical)
    3. python tools/finalize_scj.py     (PDF, state, index, git) if the agent did not
  Fresh grok process each time (no -c / -r), except stencil tickets: proved
  families (Clause 6.5 billing relegation; contempt of a 6.5 writ dismissed)
  are filled by tools/scj_stencil.py with no grok call. Chrome/git/index
  still run via finalize_scj.py.

.PARAMETER Count
  Max cases to process (default 10).

.PARAMETER RepoRoot
  Repo path (default: parent of tools/).

.PARAMETER MaxTurns
  Max agent turns per case (default 50 -- JSON-only runs need far fewer than 100).

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
$promptShort = Join-Path $RepoRoot "tools\prompts\next_case_short.txt"
$preparePy = Join-Path $RepoRoot "tools\prepare_next_scj.py"
$finalizePy = Join-Path $RepoRoot "tools\finalize_scj.py"
$ticketPath = Join-Path $ScRoot "tmp\NEXT_TICKET.json"
if (-not (Test-Path $promptFile)) { throw "Missing prompt file: $promptFile" }
if (-not (Test-Path $promptShort)) { throw "Missing prompt file: $promptShort" }
$maxTurnsUserSet = $PSBoundParameters.ContainsKey("MaxTurns")

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

function Write-ReviewMetric {
  param([hashtable]$Fields)
  $script = Join-Path $RepoRoot "tools\log_scj_review.py"
  if (-not (Test-Path $script)) { return }
  $argList = @($script)
  foreach ($k in $Fields.Keys) {
    $v = $Fields[$k]
    if ($null -eq $v -or $v -eq "") { continue }
    $argList += "--$k"
    $argList += [string]$v
  }
  try {
    & $py @argList 2>&1 | ForEach-Object { Write-Log $_ }
  } catch {
    Write-Log "review-log skipped: $_"
  }
}

Write-Log "Repo: $RepoRoot"
Write-Log "Grok: $grokPath"
Write-Log "Count: $Count | MaxTurns: $MaxTurns | NoPush: $NoPush | Log: $logFile"
Write-Log "Starting next_seq=$(Get-NextSeq)"
Write-Log "Review batch: SCJ-338 to SCJ-387 (50 cases). Metrics: supply-code/tmp/pipeline_review/metrics.jsonl"

$ok = 0
$fail = 0
$skipped = 0
$prepFailStreak = 0
$stencilFailStreak = 0

for ($i = 1; $i -le $Count; $i++) {
  $seqBefore = Get-NextSeq
  Write-Log "===== CASE $i / $Count | next_seq=$seqBefore ====="

  if ($DryRun) {
    Write-Log "DRY-RUN: $py tools/prepare_next_scj.py"
    Write-Log "DRY-RUN: if ticket.authoring=stencil -> $py tools/scj_stencil.py --write ; else grok --prompt-file <full|short>"
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
    $prepFailStreak++
    if ($prepFailStreak -ge 3) {
      Write-Log "STOP: prepare failed $prepFailStreak times in a row (next_seq=$seqBefore). Fix extract then re-run."
      break
    }
    continue
  }
  $prepFailStreak = 0

  $ticket = Get-Ticket
  if (-not $ticket -or $ticket.status -ne "READY") {
    Write-Log "FAIL case ${i}: bad ticket $ticketPath"
    $fail++
    continue
  }
  $authoring = [string]$ticket.authoring
  if (-not $authoring) { $authoring = "full" }
  $caseLog = Join-Path $logDir ("case_{0:D2}_{1}_{2}.log" -f $i, $ticket.case_id, $stamp)
  $jsonPath = Join-Path $ScRoot "summaries\json\$($ticket.case_id).json"
  $stencilPy = Join-Path $RepoRoot "tools\scj_stencil.py"
  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  $exit = 0
  $tail = ""
  $safetyFinalize = 0

  if ($authoring -eq "stencil") {
    $fam = [string]$ticket.stencil_family
    Write-Log "ticket $($ticket.case_id) authoring=stencil family=$fam source=$($ticket.source) pages=$($ticket.page_count) words=$($ticket.word_count) -- no grok"
    try {
      & $py $stencilPy --write 2>&1 | Tee-Object -FilePath $caseLog
      $exit = $LASTEXITCODE
    } catch {
      Write-Log "ERROR stencil write: $_"
      $exit = 1
    }
    if ($exit -ne 0 -or -not (Test-Path $jsonPath)) {
      $sw.Stop()
      if (Test-Path $caseLog) {
        $tail = (Get-Content $caseLog -Tail 8 -ErrorAction SilentlyContinue) -join ' | '
      }
      Write-Log "FAIL case $i stencil write exit=$exit"
      Write-Log "  tail: $tail"
      $fail++
      $stencilFailStreak++
      if ($stencilFailStreak -ge 3) {
        Write-Log "STOP: stencil write failed $stencilFailStreak times in a row on $($ticket.case_id). Fix tools/scj_stencil.py then re-run."
        break
      }
      continue
    }
    $stencilFailStreak = 0
    $finArgs = @($finalizePy, $ticket.case_id, "--source", $ticket.source)
    if ($NoPush) { $finArgs += "--no-push" }
    & $py @finArgs 2>&1 | Tee-Object -FilePath $caseLog -Append
    if ($LASTEXITCODE -ne 0) {
      $sw.Stop()
      Write-Log "FAIL case $i stencil finalize exit=$LASTEXITCODE"
      $fail++
      continue
    }
  } else {
    $casePrompt = if ($authoring -eq "short") { $promptShort } else { $promptFile }
    $caseTurns = $MaxTurns
    if (-not $maxTurnsUserSet -and $ticket.max_turns) {
      $caseTurns = [int]$ticket.max_turns
    }
    Write-Log "ticket $($ticket.case_id) authoring=$authoring source=$($ticket.source) pages=$($ticket.page_count) words=$($ticket.word_count) turns=$caseTurns"
    $grokArgs = @(
      "--cwd", $RepoRoot,
      "--prompt-file", $casePrompt,
      "--permission-mode", "bypassPermissions",
      "--always-approve",
      "--max-turns", "$caseTurns",
      "--output-format", "plain",
      "--no-auto-update"
    )
    try {
      & $grokPath @grokArgs 2>&1 | Tee-Object -FilePath $caseLog
      $exit = $LASTEXITCODE
    } catch {
      Write-Log "ERROR invoking grok: $_"
      $exit = 1
    }
  }
  $sw.Stop()

  $seqMid = Get-NextSeq
  if (Test-Path $caseLog) {
    $tail = (Get-Content $caseLog -Tail 8 -ErrorAction SilentlyContinue) -join ' | '
  }

  # Safety net: JSON exists but finalize did not bump next_seq.
  if ((Test-Path $jsonPath) -and ($seqMid -le $seqBefore)) {
    $safetyFinalize = 1
    Write-Log "JSON unfinalized; running finalize_scj.py"
    $finArgs = @($finalizePy, $ticket.case_id, "--source", $ticket.source)
    if ($NoPush) { $finArgs += "--no-push" }
    & $py @finArgs
    if ($LASTEXITCODE -ne 0) {
      Write-Log "FAIL case $i finalize exit=$LASTEXITCODE"
      Write-Log "  tail: $tail"
      $fail++
      Write-ReviewMetric @{
        event = "loop"; cid = $ticket.case_id; authoring = $authoring
        family = [string]$ticket.stencil_family; source = [string]$ticket.source
        pages = [string]$ticket.page_count; words = [string]$ticket.word_count
        citations = [string]$ticket.citation_count; gate = [string]$ticket.gate
        elapsed = [string][int]$sw.Elapsed.TotalSeconds; ok = "0"
        safety_finalize = "1"
        grok = $(if ($authoring -eq "stencil") { "0" } else { "1" })
      }
      continue
    }
  }

  $seqAfter = Get-NextSeq
  $elapsed = [int]$sw.Elapsed.TotalSeconds
  $okFlag = 0

  if ($seqAfter -gt $seqBefore) {
    Write-Log "OK case $i $($ticket.case_id) done -> next_seq=$seqAfter elapsed=${elapsed}s"
    Write-Log "  tail: $tail"
    $ok++
    $okFlag = 1
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

  Write-ReviewMetric @{
    event = "loop"; cid = $ticket.case_id; authoring = $authoring
    family = [string]$ticket.stencil_family; source = [string]$ticket.source
    pages = [string]$ticket.page_count; words = [string]$ticket.word_count
    citations = [string]$ticket.citation_count; gate = [string]$ticket.gate
    elapsed = [string]$elapsed; ok = [string]$okFlag
    safety_finalize = [string]$safetyFinalize
    grok = $(if ($authoring -eq "stencil") { "0" } else { "1" })
  }
}

Write-Log "===== DONE ok=$ok fail=$fail skipped_remaining~$skipped next_seq=$(Get-NextSeq) ====="
Write-Log "Full log: $logFile"
try {
  & $py (Join-Path $RepoRoot "tools\log_scj_review.py") --summary 2>&1 | ForEach-Object { Write-Log $_ }
} catch { }
Write-Host ""
Write-Host "Summary: ok=$ok fail=$fail | next_seq=$(Get-NextSeq) | log=$logFile"
exit $(if ($fail -gt 0) { 1 } else { 0 })
