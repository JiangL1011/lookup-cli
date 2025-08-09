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

$Target = $null
if (Test-Path (Join-Path $DefaultDir $CmdName)) {
  $Target = (Join-Path $DefaultDir $CmdName)
} elseif (Get-Command lu -ErrorAction SilentlyContinue) {
  $Target = (Get-Command lu).Path
}

if (-not $Target) { Write-Err "lu not found. Nothing to uninstall."; exit 1 }
Write-Info "Found: $Target"

if (-not $Force) {
  $resp = Read-Host "Remove $Target? (y/N)"
  if ($resp -ne 'y' -and $resp -ne 'Y') { Write-Warn 'Aborted.'; exit 0 }
}

try {
  Remove-Item -Force $Target
  Write-Info "Removed binary."
} catch {
  Write-Err "Failed to remove $Target: $_"; exit 1
}

# Attempt to remove directory if empty and is default dir
if (Test-Path $DefaultDir) {
  $remaining = Get-ChildItem -LiteralPath $DefaultDir -Force | Measure-Object
  if ($remaining.Count -eq 0) {
    Remove-Item -Force $DefaultDir -ErrorAction SilentlyContinue
  }
}

Write-Info "Uninstall complete."
Write-Info "If you previously added a custom directory to PATH manually, you may remove it from environment settings."
