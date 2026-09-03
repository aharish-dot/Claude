<#
.SYNOPSIS
  External loop: process N Supply Code cases with 1–4 parallel authoring workers.

.DESCRIPTION
  Claim (prepare_next_scj.py) and finalize (finalize_scj.py) stay serial under a
  directory lock so SCJ ids and git never collide. Authoring runs in parallel:
  stencil tickets skip grok; otherwise a fresh grok -p writes JSON only.
  Workers=1 is the old one-at-a-time loop with the same lock.

.PARAMETER Count
  Max cases to process (default 10).

.PARAMETER Workers
  Parallel authoring workers (default 2, max 4). Finalize is always serial.

.PARAMETER RepoRoot
  Repo path (default: parent of tools/).

.PARAMETER MaxTurns
  Max agent turns per case. If omitted, the ticket's max_turns is used
  (15 short / 50 full).

.PARAMETER NoPush
  Finalize commits locally but does not git push.

.PARAMETER DryRun
  Print the plan; do not extract or invoke grok.

.EXAMPLE
  cd C:\Users\HP\Downloads\Grok\Claude
  powershell -ExecutionPolicy Bypass -File tools\run_next_case_loop.ps1 -Count 50 -Workers 2

  Ubuntu (same orchestrator):
  ./tools/run_next_case_loop.sh --count 50 --workers 2
#>
[CmdletBinding()]
param(
  [int]$Count = 10,
  [int]$Workers = 2,
  [string]$RepoRoot = "",
  [int]$MaxTurns = 0,
  [switch]$NoPush,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false

if (-not $RepoRoot) {
  $RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
}
$RepoRoot = (Resolve-Path $RepoRoot).Path
Set-Location $RepoRoot

$workerPy = Join-Path $RepoRoot "tools\run_next_case_workers.py"
if (-not (Test-Path $workerPy)) { throw "Missing $workerPy" }

$py = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "python3" }
$env:PYTHONUTF8 = "1"

$argList = @(
  $workerPy,
  "--count", "$Count",
  "--workers", "$Workers",
  "--repo-root", $RepoRoot
)
if ($PSBoundParameters.ContainsKey("MaxTurns") -and $MaxTurns -gt 0) {
  $argList += "--max-turns"
  $argList += "$MaxTurns"
}
if ($NoPush) { $argList += "--no-push" }
if ($DryRun) { $argList += "--dry-run" }

& $py @argList
exit $(if ($null -eq $LASTEXITCODE) { 0 } else { $LASTEXITCODE })
