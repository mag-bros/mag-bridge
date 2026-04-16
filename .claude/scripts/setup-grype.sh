#!/usr/bin/env bash
# setup-grype.sh — Install a version-pinned, checksum-verified Grype binary.
#
# Usage:
#   .claude/scripts/setup-grype.sh                  # install to ./bin/grype
#   .claude/scripts/setup-grype.sh -d /usr/local/bin # install to /usr/local/bin/grype
#
# The script:
#   1. Detects OS and architecture
#   2. Downloads the pinned release tarball from GitHub
#   3. Verifies SHA256 checksum — fails hard on mismatch
#   4. Extracts and installs the binary
#
# To upgrade: bump GRYPE_VERSION and update the checksums below.

set -euo pipefail

# ─── Pinned version ──────────────────────────────────────────────────────────
GRYPE_VERSION="0.110.0"

# SHA256 checksums per platform (from grype_${GRYPE_VERSION}_checksums.txt)
# Source: https://github.com/anchore/grype/releases/download/v${GRYPE_VERSION}/grype_${GRYPE_VERSION}_checksums.txt
# To upgrade: download the new checksums.txt, verify its GPG signature, and replace the hashes below.
declare -A CHECKSUMS=(
    ["linux_amd64"]="aaa98d27d2d7efd9317c6a1ad6d9b15f3e65bab320e7d03bde41e251387bb71c"
    ["linux_arm64"]="804041ee69f119022e3e866741a558eae6f2df372a5dc1a5376d456d16f8c931"
)

# ─── CLI args ─────────────────────────────────────────────────────────────────
INSTALL_DIR="./bin"

while getopts "d:h" opt; do
    case "$opt" in
        d) INSTALL_DIR="$OPTARG" ;;
        h)
            echo "Usage: $0 [-d install_dir]"
            echo "  -d DIR   Install grype binary to DIR (default: ./bin)"
            exit 0
            ;;
        *) echo "Usage: $0 [-d install_dir]" >&2; exit 1 ;;
    esac
done

# ─── Detect platform ─────────────────────────────────────────────────────────
detect_os() {
    local os
    os="$(uname -s | tr '[:upper:]' '[:lower:]')"
    case "$os" in
        linux)  echo "linux" ;;
        *)      echo "ERROR: Unsupported OS: $os (only Linux is supported)" >&2; exit 1 ;;
    esac
}

detect_arch() {
    local arch
    arch="$(uname -m)"
    case "$arch" in
        x86_64|amd64)   echo "amd64" ;;
        aarch64|arm64)   echo "arm64" ;;
        *)               echo "ERROR: Unsupported architecture: $arch (supported: amd64, arm64)" >&2; exit 1 ;;
    esac
}

# ─── Preflight checks ────────────────────────────────────────────────────────
check_dependencies() {
    local missing=()
    for cmd in curl sha256sum tar; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "ERROR: Missing required commands: ${missing[*]}" >&2
        exit 1
    fi
}

verify_checksum() {
    local file="$1" expected="$2"
    local actual
    actual="$(sha256sum "$file" | awk '{print $1}')"
    if [[ "$actual" != "$expected" ]]; then
        echo "ERROR: Checksum mismatch!" >&2
        echo "  Expected: $expected" >&2
        echo "  Actual:   $actual" >&2
        echo "  File may be corrupted or tampered with." >&2
        rm -f "$file"
        exit 1
    fi
    echo "  Checksum verified: $actual"
}

# ─── Main ─────────────────────────────────────────────────────────────────────
main() {
    check_dependencies

    local os arch platform
    os="$(detect_os)"
    arch="$(detect_arch)"
    platform="${os}_${arch}"

    if [[ -z "${CHECKSUMS[$platform]+x}" ]]; then
        echo "ERROR: No checksum available for platform: $platform" >&2
        exit 1
    fi

    local expected_checksum="${CHECKSUMS[$platform]}"
    local tarball="grype_${GRYPE_VERSION}_${platform}.tar.gz"
    local url="https://github.com/anchore/grype/releases/download/v${GRYPE_VERSION}/${tarball}"
    local tmpdir
    tmpdir="$(mktemp -d)"
    trap 'rm -rf "${tmpdir:-}"' EXIT

    echo "=== Grype Setup ==="
    echo "  Version:  v${GRYPE_VERSION}"
    echo "  Platform: ${platform}"
    echo "  Target:   ${INSTALL_DIR}/grype"
    echo ""

    # Download
    echo "Downloading ${tarball}..."
    curl -sSfL -o "${tmpdir}/${tarball}" "$url"

    # Verify
    echo "Verifying checksum..."
    verify_checksum "${tmpdir}/${tarball}" "$expected_checksum"

    # Extract
    echo "Extracting..."
    tar -xzf "${tmpdir}/${tarball}" -C "$tmpdir" grype

    # Install
    mkdir -p "$INSTALL_DIR"
    mv "${tmpdir}/grype" "${INSTALL_DIR}/grype"
    chmod +x "${INSTALL_DIR}/grype"

    echo ""
    echo "Installed: ${INSTALL_DIR}/grype"
    "${INSTALL_DIR}/grype" version
}

main
