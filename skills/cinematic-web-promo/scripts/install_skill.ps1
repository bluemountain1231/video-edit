param(
  [Parameter(Position = 0, Mandatory = $true)]
  [string]$Target,
  [Parameter(Position = 1)]
  [string]$Destination,
  [switch]$Force
)

$ErrorActionPreference = "Stop"
$SkillName = "cinematic-web-promo"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceDir = Split-Path -Parent $ScriptDir

function Backup-Existing([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) { return }
  if (-not $Force) {
    throw "Destination exists: $Path (pass -Force to back it up and replace it)"
  }
  $Stamp = Get-Date -Format "yyyyMMddHHmmss"
  $Backup = "$Path.backup.$Stamp"
  Move-Item -LiteralPath $Path -Destination $Backup
  Write-Host "Backed up existing destination to: $Backup"
}

function Install-ToRoot([string]$Root) {
  $Root = [IO.Path]::GetFullPath($Root)
  $TargetPath = Join-Path $Root $SkillName
  if ([IO.Path]::GetFullPath($TargetPath) -eq [IO.Path]::GetFullPath($SourceDir)) {
    throw "Source and destination are the same skill directory."
  }
  New-Item -ItemType Directory -Force -Path $Root | Out-Null
  Backup-Existing $TargetPath
  Copy-Item -LiteralPath $SourceDir -Destination $TargetPath -Recurse
  $CopiedGitDir = Join-Path $TargetPath ".git"
  if (Test-Path -LiteralPath $CopiedGitDir) { Remove-Item -LiteralPath $CopiedGitDir -Recurse -Force }
  Write-Host "Installed: $TargetPath"
}

function Package-Skill([string]$Output) {
  if ([string]::IsNullOrWhiteSpace($Output)) {
    $Output = Join-Path (Get-Location) "$SkillName-workbuddy.zip"
  }
  $Output = [IO.Path]::GetFullPath($Output)
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Output) | Out-Null
  Backup-Existing $Output
  $TempRoot = Join-Path ([IO.Path]::GetTempPath()) ("cwp-package-" + [guid]::NewGuid().ToString("N"))
  try {
    New-Item -ItemType Directory -Force -Path $TempRoot | Out-Null
    Copy-Item -LiteralPath $SourceDir -Destination (Join-Path $TempRoot $SkillName) -Recurse
    $PackagedGitDir = Join-Path (Join-Path $TempRoot $SkillName) ".git"
    if (Test-Path -LiteralPath $PackagedGitDir) { Remove-Item -LiteralPath $PackagedGitDir -Recurse -Force }
    Get-ChildItem -LiteralPath $TempRoot -Filter ".DS_Store" -Recurse -Force | Remove-Item -Force
    Get-ChildItem -LiteralPath $TempRoot -Directory -Filter "__pycache__" -Recurse -Force | Remove-Item -Recurse -Force
    Get-ChildItem -LiteralPath $TempRoot -File -Filter "*.pyc" -Recurse -Force | Remove-Item -Force
    Compress-Archive -Path (Join-Path $TempRoot $SkillName) -DestinationPath $Output -CompressionLevel Optimal
    Write-Host "Packaged: $Output"
  }
  finally {
    if (Test-Path -LiteralPath $TempRoot) { Remove-Item -LiteralPath $TempRoot -Recurse -Force }
  }
}

$HomeDir = [Environment]::GetFolderPath("UserProfile")
switch ($Target.ToLowerInvariant()) {
  { $_ -in @("codex", "codex-user") } {
    $Root = if ($env:CODEX_SKILLS_HOME) { $env:CODEX_SKILLS_HOME } else { Join-Path $HomeDir ".agents/skills" }
    Install-ToRoot $Root
    break
  }
  "codex-project" {
    $Project = if ($Destination) { $Destination } else { (Get-Location).Path }
    Install-ToRoot (Join-Path $Project ".agents/skills")
    break
  }
  { $_ -in @("claude", "claude-user") } {
    $ClaudeRoot = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HomeDir ".claude" }
    Install-ToRoot (Join-Path $ClaudeRoot "skills")
    break
  }
  "claude-project" {
    $Project = if ($Destination) { $Destination } else { (Get-Location).Path }
    Install-ToRoot (Join-Path $Project ".claude/skills")
    break
  }
  { $_ -in @("workbuddy", "workbuddy-package", "package") } {
    Package-Skill $Destination
    break
  }
  "codebuddy-project" {
    $Project = if ($Destination) { $Destination } else { (Get-Location).Path }
    Install-ToRoot (Join-Path $Project ".codebuddy/skills")
    break
  }
  "custom" {
    if (-not $Destination) { throw "custom requires an absolute skills root." }
    Install-ToRoot $Destination
    break
  }
  default { throw "Unknown target: $Target" }
}
