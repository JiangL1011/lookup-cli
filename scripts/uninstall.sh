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

# Collect all lu binaries in PATH (unique, resolve symlinks)
declare -a FOUND=()
IFS=":" read -r -a PATH_DIRS <<< "$PATH"
for d in "${PATH_DIRS[@]}"; do
  [[ -z "$d" ]] && continue
  if [[ -x "$d/$CMD_NAME" ]]; then
    realpath=$( (command -v realpath >/dev/null 2>&1 && realpath "$d/$CMD_NAME") || readlink "$d/$CMD_NAME" 2>/dev/null || echo "$d/$CMD_NAME")
    # Avoid duplicates
    skip=0
    for existing in "${FOUND[@]}"; do
      [[ "$existing" == "$d/$CMD_NAME" ]] && skip=1 && break
    done
    [[ $skip -eq 0 ]] && FOUND+=("$d/$CMD_NAME")
  fi
done

# If user specified PREFIX, prioritize that path (move it to front)
if [[ -n "$PREFIX_DIR" && -x "$PREFIX_DIR/bin/$CMD_NAME" ]]; then
  pref="$PREFIX_DIR/bin/$CMD_NAME"
  NEW=("$pref")
  for f in "${FOUND[@]}"; do [[ "$f" == "$pref" ]] && continue; NEW+=("$f"); done
  FOUND=("${NEW[@]}")
fi

if [[ ${#FOUND[@]} -eq 0 ]]; then
  err "Cannot find '$CMD_NAME' in PATH. Nothing to uninstall."; exit 1
fi

info "Detected the following installed '$CMD_NAME' binaries:"
idx=1
for f in "${FOUND[@]}"; do
  echo "  [$idx] $f"; idx=$((idx+1))
done

if ! confirm "Remove ALL of the above?"; then
  warn "Aborted."; exit 0
fi

for target in "${FOUND[@]}"; do
  if [[ ! -e "$target" ]]; then
    continue
  fi
  SUDO=""
  if [[ ! -w "$target" && $(id -u) -ne 0 ]]; then
    SUDO="sudo"
  fi
  info "Removing $target";
  if ! $SUDO rm -f "$target" 2>/dev/null; then
    warn "Failed to remove $target"
  else
    # Attempt prune if directory now empty and looks project-specific
    parent_dir=$(dirname "$target")
    if [[ "$parent_dir" =~ lookup-cli && -d "$parent_dir" && -z "$(ls -A "$parent_dir" 2>/dev/null)" ]]; then
      $SUDO rmdir "$parent_dir" 2>/dev/null || true
    fi
  fi
done

# Refresh shell command cache
hash -r 2>/dev/null || true
if command -v rehash >/dev/null 2>&1; then rehash || true; fi

# Check if lu still resolves (could be alias/function)
if type lu >/dev/null 2>&1; then
  kind=$(type -t lu || echo command)
  warn "'lu' still resolves as a $kind after binary removal. It may be an alias or function defined in your shell init files."
fi

if [[ -n "$PREFIX_DIR" ]]; then
  warn "If you added $PREFIX_DIR/bin to PATH manually, remove it from your shell profile if no longer needed.";
fi

info "Uninstall complete."
