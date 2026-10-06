param(
  [ValidateSet("auto", "native", "playwright")]
  [string]$Browser = "auto",
  [ValidateSet("auto", "required", "skip")]
  [string]$Beats = "auto"
)

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillDir = Split-Path -Parent $ScriptDir
$Failed = $false

function Check-Command([string]$Name) {
  $Command = Get-Command $Name -ErrorAction SilentlyContinue
  if ($Command) { Write-Host "PASS  $Name`: $($Command.Source)"; return $true }
  Write-Host "MISS  $Name"
  $script:Failed = $true
  return $false
}

$HasNode = Check-Command "node"
$PythonExe = $null
$PythonPrefix = @()
$PythonCommand = Get-Command "python" -ErrorAction SilentlyContinue
if ($PythonCommand) {
  $PythonExe = $PythonCommand.Source
  Write-Host "PASS  python: $PythonExe"
}
else {
  $PyLauncher = Get-Command "py" -ErrorAction SilentlyContinue
  if ($PyLauncher) {
    $PythonExe = $PyLauncher.Source
    $PythonPrefix = @("-3")
    Write-Host "PASS  python: $PythonExe -3"
  }
  else {
    Write-Host "MISS  python or py -3"
    $Failed = $true
  }
}
$HasPython = $null -ne $PythonExe
Check-Command "pnpm" | Out-Null
Check-Command "ffmpeg" | Out-Null
Check-Command "ffprobe" | Out-Null

if ($HasNode) {
  $NodeMajor = [int](& node -p 'Number(process.versions.node.split(".")[0])')
  if ($NodeMajor -lt 20) {
    Write-Host "MISS  Node 20+ required (found $(& node -v))"
    $Failed = $true
  }
}

if ($Browser -eq "native") {
  Write-Host "PASS  Browser mode: host-native browser/computer tool"
}
elseif ($Browser -in @("auto", "playwright")) {
  $HasPlaywright = $false
  if ($HasNode) {
    Push-Location $ScriptDir
    & node -e "import('playwright')" *> $null
    $HasPlaywright = ($LASTEXITCODE -eq 0)
    Pop-Location
  }
  if ($HasPlaywright) {
    Write-Host "PASS  Browser mode: Playwright module"
  }
  elseif ($Browser -eq "playwright") {
    Write-Host "MISS  Playwright required. Setup: cd `"$ScriptDir`"; npm ci; npx playwright install chromium"
    $Failed = $true
  }
  else {
    Write-Host "WARN  No Playwright module; use a host-native browser or install it."
  }
}

if ($HasPython) {
  & $PythonExe @PythonPrefix -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
  if ($LASTEXITCODE -ne 0) {
    Write-Host "MISS  Python 3.10+ required (found $(& $PythonExe @PythonPrefix --version))"
    $Failed = $true
  }
  if ($Beats -eq "skip") {
    Write-Host "PASS  Beat analysis skipped by request"
  }
  else {
    & $PythonExe @PythonPrefix -c "import librosa, numpy, scipy" *> $null
    if ($LASTEXITCODE -eq 0) { Write-Host "PASS  Python beat-analysis packages" }
    elseif ($Beats -eq "required") {
      Write-Host "MISS  Beat packages required. Setup: python -m venv .venv; .venv\Scripts\pip install -r `"$ScriptDir\requirements.txt`""
      $Failed = $true
    }
    else { Write-Host "WARN  Beat-analysis packages are absent." }
  }
  & $PythonExe @PythonPrefix (Join-Path $ScriptDir "shotcraft_router.py") --help *> $null
  if ($LASTEXITCODE -eq 0) { Write-Host "PASS  Shotcraft recipe router" }
  else { Write-Host "MISS  Shotcraft recipe router cannot start"; $Failed = $true }
  & $PythonExe @PythonPrefix (Join-Path $ScriptDir "shotcraft_router.py") --source embedded --recipe tape-scroll-fixed-pointer --json *> $null
  if ($LASTEXITCODE -eq 0) { Write-Host "PASS  Embedded Shotcraft snapshot" }
  else { Write-Host "MISS  Embedded Shotcraft snapshot integrity/routing check"; $Failed = $true }
}

$Required = @(
  "SKILL.md",
  "agents/openai.yaml",
  "scripts/package-lock.json",
  "scripts/install_skill.sh",
  "scripts/shotcraft_router.py",
  "scripts/sync_shotcraft_snapshot.py",
  "references/platform-codex.md",
  "references/platform-claude-code.md",
  "references/platform-workbuddy.md",
  "references/shotcraft-router.md",
  "assets/remotion-starter/package.json",
  "assets/remotion-starter/pnpm-lock.yaml",
  "assets/media-license-manifest.json",
  "assets/shotcraft-snapshot/SNAPSHOT.json",
  "assets/shotcraft-snapshot/repo/LICENSE",
  "assets/shotcraft-snapshot/repo/gallery/api/library.json"
)
foreach ($Relative in $Required) {
  $Path = Join-Path $SkillDir $Relative
  if (Test-Path -LiteralPath $Path) { Write-Host "PASS  $Relative" }
  else { Write-Host "MISS  $Relative"; $Failed = $true }
}

Write-Host "INFO  Starter setup: cd `"$SkillDir\assets\remotion-starter`"; pnpm install --frozen-lockfile"
if ($Failed) { throw "Preflight incomplete. Resolve missing required items." }
Write-Host "Preflight passed: $SkillDir"
