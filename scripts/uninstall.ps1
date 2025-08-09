#!/usr/bin/env pwsh
<#!
.SYNOPSIS
  Uninstall lookup-cli (lu) from Windows user installation.
#>

$ErrorActionPreference = 'Stop'
$CmdName = 'lu.exe'
$Project = 'lookup-cli'
$DefaultDir = Join-Path $Env:LOCALAPPDATA "Programs\$Project"

function Write-Info($m) { Write-Host "[+] $m" -ForegroundColor Green }
function Write-Warn($m) { Write-Host "[!] $m" -ForegroundColor Yellow }
function Write-Err($m) { Write-Host "[x] $m" -ForegroundColor Red }

param(
  [switch]$Force
)

# Gather all lu.exe occurrences in PATH plus default dir
$paths = @()
if (Test-Path (Join-Path $DefaultDir $CmdName)) { $paths += (Join-Path $DefaultDir $CmdName) }

$env:Path.Split([IO.Path]::PathSeparator) | ForEach-Object {
  $candidate = Join-Path $_ $CmdName
  if (Test-Path $candidate) { $paths += $candidate }
}

$paths = $paths | Sort-Object -Unique

if ($paths.Count -eq 0) { Write-Err "lu not found. Nothing to uninstall."; exit 1 }

Write-Info "Detected lu.exe locations:"; $i=1; foreach ($p in $paths) { Write-Host "  [$i] $p"; $i++ }

if (-not $Force) {
  $resp = Read-Host "Remove ALL of the above? (y/N)"
  if ($resp -ne 'y' -and $resp -ne 'Y') { Write-Warn 'Aborted.'; exit 0 }
}

foreach ($target in $paths) {
  if (Test-Path $target) {
    try {
      Remove-Item -Force $target
      Write-Info "Removed $target"
      $parent = Split-Path -Parent $target
      if ($parent -like "*$Project*") {
        if ((Get-ChildItem -Force $parent | Measure-Object).Count -eq 0) { Remove-Item -Force $parent -ErrorAction SilentlyContinue }
      }
    } catch {
      Write-Warn "Failed to remove $target: $_"
    }
  }
}

# Refresh current session PATH resolution
if (Get-Command lu -ErrorAction SilentlyContinue) {
  Write-Warn "'lu' still resolves to: $((Get-Command lu).Path). You may have another copy or alias." 
}

# Offer to remove default dir from PATH if empty
if (Test-Path $DefaultDir) {
  if ((Get-ChildItem -Force $DefaultDir | Measure-Object).Count -eq 0) {
    Remove-Item -Force $DefaultDir -ErrorAction SilentlyContinue
  }
}

# Optional PATH cleanup (user PATH only)
$userPath = [Environment]::GetEnvironmentVariable('Path','User')
if ($userPath -and $userPath -match [Regex]::Escape($DefaultDir)) {
  if ($Force -or (Read-Host "Remove $DefaultDir from User PATH? (y/N)" ) -in @('y','Y')) {
    $newUserPath = ($userPath.Split(';') | Where-Object { $_ -and ($_ -ne $DefaultDir) }) -join ';'
    [Environment]::SetEnvironmentVariable('Path',$newUserPath,'User')
    Write-Info "Removed $DefaultDir from User PATH (restart terminal to apply)."
  }
}

Write-Info "Uninstall complete."
