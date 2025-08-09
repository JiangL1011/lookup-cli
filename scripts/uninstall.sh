#!/usr/bin/env bash
set -euo pipefail

CMD_NAME="lu"
PROJECT="lookup-cli"
# Allow override of install dir (if user used PREFIX during install)
PREFIX_DIR="${PREFIX:-}"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info() { echo -e "${GREEN}[+] $*${NC}"; }
warn() { echo -e "${YELLOW}[!] $*${NC}"; }
err() { echo -e "${RED}[x] $*${NC}" >&2; }

confirm() {
  if [[ "${FORCE:-}" == "1" ]]; then return 0; fi
  read -r -p "$1 [y/N]: " ans
  [[ "$ans" == "y" || "$ans" == "Y" ]]
}

# Determine binary path
BIN_PATH=""
if command -v "$CMD_NAME" >/dev/null 2>&1; then
  BIN_PATH="$(command -v "$CMD_NAME")"
fi

# If user gave a prefix, prefer that location
if [[ -n "$PREFIX_DIR" ]]; then
  if [[ -x "$PREFIX_DIR/bin/$CMD_NAME" ]]; then
    BIN_PATH="$PREFIX_DIR/bin/$CMD_NAME"
  fi
fi

if [[ -z "$BIN_PATH" ]]; then
  err "Cannot find '$CMD_NAME' in PATH. Nothing to uninstall."; exit 1
fi

info "Found $CMD_NAME at: $BIN_PATH"

if ! confirm "Remove $BIN_PATH?"; then
  warn "Aborted."; exit 0
fi

REMOVE_TARGET="$BIN_PATH"

# Need sudo if not writable
if [[ ! -w "$REMOVE_TARGET" ]]; then
  if [[ $(id -u) -ne 0 ]]; then
    SUDO="sudo"
  fi
fi
$SUDO rm -f "$REMOVE_TARGET" || { err "Failed to remove $REMOVE_TARGET"; exit 1; }
info "Removed binary."

# Attempt to prune empty parent directory if it's a project-specific dir (rare)
PARENT_DIR="$(dirname "$REMOVE_TARGET")"
if [[ "$PARENT_DIR" =~ lookup-cli && -d "$PARENT_DIR" ]]; then
  if [[ -z "$(ls -A "$PARENT_DIR" 2>/dev/null)" ]]; then
    $SUDO rmdir "$PARENT_DIR" 2>/dev/null || true
  fi
fi

# Advise user about PATH if custom dir
if [[ -n "$PREFIX_DIR" ]]; then
  warn "If you added $PREFIX_DIR/bin to PATH manually, you may remove it from your shell config.";
fi

info "Uninstall complete."
