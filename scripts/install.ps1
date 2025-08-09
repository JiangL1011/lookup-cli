#!/usr/bin/env pwsh
<#!
.SYNOPSIS
  Install lookup-cli on Windows by cloning and building with PyInstaller.
#>

$ErrorActionPreference = 'Stop'

$Repo = 'JiangL1011/lookup-cli'
$CmdName = 'lu.exe'
$Project = 'lookup-cli'
$Version = $Env:LU_VERSION  # optional like v0.1.0; if empty use latest

function Write-Info($m) { Write-Host "[+] $m" -ForegroundColor Green }
function Write-Warn($m) { Write-Host "[!] $m" -ForegroundColor Yellow }
function Write-Err($m) { Write-Host "[x] $m" -ForegroundColor Red }

function Need-Cmd($name) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    Write-Err "Missing required command: $name"; exit 1
  }
}

Need-Cmd curl
if (-not (Get-Command curl -ErrorAction SilentlyContinue)) { Need-Cmd Invoke-WebRequest }

 $TempDir = New-Item -ItemType Directory -Path ([System.IO.Path]::GetTempPath()) -Name ("$Project-" + [System.Guid]::NewGuid().ToString('N'))
 try {
  Write-Info "Determining download URL..."
  if ($Version) { $DownloadUrl = "https://github.com/$Repo/releases/download/$Version/lu-windows.exe" }
  else { $DownloadUrl = "https://github.com/$Repo/releases/latest/download/lu-windows.exe" }

  Write-Info "Downloading binary: $DownloadUrl"
  $OutFile = Join-Path $TempDir 'lu.exe'
  try {
    curl -fL $DownloadUrl -o $OutFile | Out-Null
  } catch {
    Write-Warn 'curl failed, trying Invoke-WebRequest'
    Invoke-WebRequest -UseBasicParsing -Uri $DownloadUrl -OutFile $OutFile
  }
  if (-not (Test-Path $OutFile)) { Write-Err 'Download failed'; exit 1 }

  # Determine install directory
  $InstallDir = "$Env:LOCALAPPDATA\Programs\$Project"
  New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
  $Dest = Join-Path $InstallDir $CmdName
  if (Test-Path $Dest) {
    Write-Info "Existing installation detected at $Dest. Overwriting for upgrade..."
  } elseif (Get-Command lu -ErrorAction SilentlyContinue) {
    $Prev = (Get-Command lu).Path
    if ($Prev -ne $Dest) { Write-Info "Previous version found at $Prev (different location). Installing new version to $Dest ..." }
  }
  Copy-Item $OutFile $Dest -Force

  # Add to PATH for current user if not already
  $UserPath = [Environment]::GetEnvironmentVariable('Path', 'User')
  if (-not ($UserPath -split ';' | Where-Object { $_ -eq $InstallDir })) {
    [Environment]::SetEnvironmentVariable('Path', "$UserPath;$InstallDir", 'User')
    Write-Info "Added $InstallDir to User PATH. Restart terminal to use 'lu' globally."
  }

  # Also append to current session PATH so it's usable immediately without restart
  if (-not ($env:Path -split ';' | Where-Object { $_ -eq $InstallDir })) {
    $env:Path = "$env:Path;$InstallDir"
  }

  Write-Info "Install/Upgrade complete: $InstallDir\$CmdName"
  Write-Info "Run: lu --help"
 }
 finally {
  if (Test-Path $TempDir) { Remove-Item -Recurse -Force $TempDir }
 }
