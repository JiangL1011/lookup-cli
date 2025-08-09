#!/usr/bin/env bash
set -euo pipefail

REPO="JiangL1011/lookup-cli"
PROJECT="lookup-cli"
CMD_NAME="lu"

# Allow overriding version via env LU_VERSION (e.g. v0.1.0). If empty, use latest.
LU_VERSION="${LU_VERSION:-}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

err() { echo -e "${RED}[x] $*${NC}" >&2; }
info() { echo -e "${GREEN}[+] $*${NC}"; }
warn() { echo -e "${YELLOW}[!] $*${NC}"; }

need_cmd() { command -v "$1" >/dev/null 2>&1 || { err "Missing required command: $1"; exit 1; }; }

need_cmd curl || need_cmd wget

detect_target() {
  local uname_s
  uname_s=$(uname -s 2>/dev/null | tr 'A-Z' 'a-z') || uname_s="unknown"
  case "$uname_s" in
    linux*) echo "linux" ;;
    darwin*) echo "macos" ;;
    msys*|mingw*|cygwin*) echo "windows" ;;
    *) err "Unsupported OS: $uname_s"; exit 1 ;;
  esac
}

TARGET=$(detect_target)
ASSET_NAME="${CMD_NAME}-${TARGET}"
if [[ "$TARGET" == "windows" ]]; then
  ASSET_NAME="${ASSET_NAME}.exe"
fi

if [[ -n "$LU_VERSION" ]]; then
  DOWNLOAD_URL="https://github.com/${REPO}/releases/download/${LU_VERSION}/${ASSET_NAME}"
else
  # 'latest' convenience redirect
  DOWNLOAD_URL="https://github.com/${REPO}/releases/latest/download/${ASSET_NAME}"
fi

TEMP_DIR="$(mktemp -d 2>/dev/null || mktemp -d -t ${PROJECT})"
trap 'rm -rf "$TEMP_DIR"' EXIT

# Determine install dir
DEFAULT_BIN_DIR="/usr/local/bin"
if [[ "${PREFIX:-}" != "" ]]; then
  INSTALL_BIN_DIR="${PREFIX}/bin"
else
  INSTALL_BIN_DIR="$DEFAULT_BIN_DIR"
fi

if [[ ! -w "$INSTALL_BIN_DIR" ]]; then
  if [[ $(id -u) -ne 0 ]]; then
    warn "${INSTALL_BIN_DIR} not writable; will try sudo"
    SUDO="sudo"
  fi
fi

info "Target platform: $TARGET"
info "Downloading ${ASSET_NAME} ..."
OUT_FILE="$TEMP_DIR/${CMD_NAME}"
if command -v curl >/dev/null 2>&1; then
  curl -fL --retry 3 --connect-timeout 10 -o "$OUT_FILE" "$DOWNLOAD_URL" || { err "Download failed: $DOWNLOAD_URL"; exit 1; }
else
  wget -O "$OUT_FILE" "$DOWNLOAD_URL" || { err "Download failed: $DOWNLOAD_URL"; exit 1; }
fi

chmod +x "$OUT_FILE"

info "Installing to ${INSTALL_BIN_DIR}"
$SUDO mkdir -p "$INSTALL_BIN_DIR"
ACTION="Installing"
if [[ -x "${INSTALL_BIN_DIR}/${CMD_NAME}" ]]; then
  ACTION="Updating"
  info "Existing installation detected at ${INSTALL_BIN_DIR}/${CMD_NAME}, will overwrite."
else
  # Also detect if different path in PATH
  if command -v "$CMD_NAME" >/dev/null 2>&1; then
    PREV_PATH="$(command -v "$CMD_NAME")"
    info "Previous version found at ${PREV_PATH}; new version will install to ${INSTALL_BIN_DIR}/${CMD_NAME}."
    ACTION="Updating"
  fi
fi
$SUDO install -m 0755 "$OUT_FILE" "${INSTALL_BIN_DIR}/${CMD_NAME}"

which "$CMD_NAME" >/dev/null 2>&1 || warn "Binary not in PATH. Add ${INSTALL_BIN_DIR} to PATH."
hash -r 2>/dev/null || true

info "${ACTION} complete: $(command -v $CMD_NAME)"
info "Run: ${CMD_NAME} --help"
