<#
.SYNOPSIS
  External loop: process N Supply Code cases, each in a fresh Grok headless session.

.DESCRIPTION
  Each iteration starts a NEW `grok -p` process (fresh session, no chat history).
  Follows supply-code/NEXT.md via tools/prompts/next_case_once.txt.

.PARAMETER Count
  Max cases to process (default 10).

.PARAMETER RepoRoot
  Repo path (default: parent of tools/).

.PARAMETER MaxTurns
  Max agent turns per case (default 100).

.PARAMETER DryRun
  Print commands only; do not invoke grok.

.EXAMPLE
  cd C:\Users\HP\Downloads\Grok\Claude
  powershell -ExecutionPolicy Bypass -File tools\run_next_case_loop.ps1

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\run_next_case_loop.ps1 -Count 100
#>
[CmdletBinding()]
param(
  [int]$Count = 10,
  [string]$RepoRoot = "",
  [int]$MaxTurns = 100,
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
if (-not (Test-Path $promptFile)) {
  throw "Missing prompt file: $promptFile"
}

$grok = Get-Command grok -ErrorAction SilentlyContinue
if (-not $grok -and -not $DryRun) {
  $candidate = Join-Path $env:USERPROFILE ".grok\bin\grok.exe"
  if (Test-Path $candidate) {
    $grokPath = $candidate
  } else {
    throw "grok not found on PATH. Install Grok CLI or add %USERPROFILE%\.grok\bin to PATH."
  }
} else {
  $grokPath = if ($grok) { $grok.Source } else { "grok" }
}

$logDir = Join-Path $ScRoot "tmp\loop_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = Join-Path $logDir "next_case_loop_$stamp.log"

function Write-Log([string]$msg) {
  $line = "[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $msg
  Write-Host $line
  Add-Content -Path $logFile -Value $line -Encoding UTF8
}

function Get-NextSeq {
  $statePath = Join-Path $ScRoot "state\index.json"
  $s = Get-Content $statePath -Raw -Encoding UTF8 | ConvertFrom-Json
  return [int]$s.next_seq
}

function Get-PendingCount {
  $inputDir = Join-Path $ScRoot "input"
  $processedDir = Join-Path $ScRoot "processed"
  if (-not (Test-Path $inputDir)) { return 0 }
  $processed = @()
  if (Test-Path $processedDir) {
    $processed = @(Get-ChildItem -Path $processedDir -File | Select-Object -ExpandProperty Name)
  }
  $n = 0
  Get-ChildItem -Path $inputDir -File | ForEach-Object {
    if ($_.Name -eq ".gitkeep") { return }
    if ($_.Name -match ' \(1\)\.pdf$') { return }
    if ($_.Name -eq "WRIC(A)_20210_2012.pdf") { return }
    if ($processed -contains $_.Name) { return }
    $n++
  }
  return $n
}

Write-Log "Repo: $RepoRoot"
Write-Log "Grok: $grokPath"
Write-Log "Count: $Count | MaxTurns: $MaxTurns | Log: $logFile"
Write-Log "Starting next_seq=$(Get-NextSeq) | pending PDFs=$(Get-PendingCount)"

$ok = 0
$fail = 0
$skipped = 0

for ($i = 1; $i -le $Count; $i++) {
  $pdfs = Get-PendingCount
  $seqBefore = Get-NextSeq

  if ($pdfs -le 0) {
    Write-Log "STOP: supply-code/input/ has no unique pending PDF (next_seq=$seqBefore)"
    $skipped = $Count - $i + 1
    break
  }

  Write-Log "===== CASE $i / $Count | next_seq=$seqBefore | pending_pdfs=$pdfs ====="

  $caseLog = Join-Path $logDir ("case_{0:D2}_SCJ-{1:D3}_{2}.log" -f $i, $seqBefore, $stamp)

  # Fresh session: new process each iteration (no -c / -r).
  $grokArgs = @(
    "--cwd", $RepoRoot,
    "--prompt-file", $promptFile,
    "--permission-mode", "bypassPermissions",
    "--always-approve",
    "--max-turns", "$MaxTurns",
    "--output-format", "plain",
    "--no-auto-update"
  )

  if ($DryRun) {
    Write-Log "DRY-RUN: $grokPath $($grokArgs -join ' ')"
    continue
  }

  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  try {
    & $grokPath @grokArgs 2>&1 | Tee-Object -FilePath $caseLog
    $exit = $LASTEXITCODE
  } catch {
    Write-Log "ERROR invoking grok: $_"
    $exit = 1
  }
  $sw.Stop()

  $seqAfter = Get-NextSeq
  $tail = ""
  if (Test-Path $caseLog) {
    $tail = (Get-Content $caseLog -Tail 8 -ErrorAction SilentlyContinue) -join " | "
  }

  if ($exit -ne 0 -and $null -ne $exit) {
    Write-Log "FAIL case $i exit=$exit elapsed=$([int]$sw.Elapsed.TotalSeconds)s next_seq=$seqAfter"
    Write-Log "  tail: $tail"
    $fail++
    continue
  }

  if ($seqAfter -gt $seqBefore) {
    Write-Log "OK case $i SCJ-$seqBefore done → next_seq=$seqAfter elapsed=$([int]$sw.Elapsed.TotalSeconds)s"
    Write-Log "  tail: $tail"
    $ok++
  } elseif ($tail -match "NO_INPUT") {
    Write-Log "STOP: agent reported NO_INPUT"
    break
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

Write-Log "===== DONE ok=$ok fail=$fail skipped_remaining~$skipped next_seq=$(Get-NextSeq) pending_pdfs=$(Get-PendingCount) ====="
Write-Log "Full log: $logFile"
Write-Host ""
Write-Host "Summary: ok=$ok fail=$fail | next_seq=$(Get-NextSeq) | log=$logFile"
exit $(if ($fail -gt 0) { 1 } else { 0 })
