#!/usr/bin/env bash

set -Eeuo pipefail

PACKAGE_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
MANIFEST_NAME=".sdd-orchestrator-package/manifest.tsv"
TARGET="${XDG_CONFIG_HOME:-${HOME:?HOME must be set}/.config}/opencode"

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
info() { printf '%s\n' "$*"; }
warn() { printf 'WARNING: %s\n' "$*" >&2; }
hash_file() { sha256sum -- "$1" | awk '{print $1}'; }
manifest_path() { printf '%s/%s' "$TARGET" "$MANIFEST_NAME"; }

assert_no_symlink_path() {
  local rel="$1" current="$TARGET" part
  IFS='/' read -r -a components <<< "$rel"
  for part in "${components[@]}"; do
    current="$current/$part"
    [[ ! -L "$current" ]] || die "Se rechaza una ruta con symlink: $current"
  done
}

parse_target() {
  while (($#)); do
    case "$1" in
      --target)
        (($# >= 2)) || die "--target requiere un directorio"
        TARGET="$2"; shift 2 ;;
      --target=*)
        TARGET="${1#*=}"; shift ;;
      -h|--help) return 2 ;;
      *) die "Argumento no reconocido: $1" ;;
    esac
  done
  [[ -n "$TARGET" ]] || die "El directorio destino no puede estar vacío"
  TARGET="$(mkdir -p -- "$TARGET" && cd -- "$TARGET" && pwd -P)"
}

package_files() {
  (cd "$PACKAGE_ROOT" && find agents commands skills -type f -name '*.md' -print0 | sort -z)
}

valid_relpath() {
  [[ "$1" =~ ^(agents|commands|skills)/[A-Za-z0-9._/-]+\.md$ && "$1" != *"/../"* && "$1" != ../* ]]
}

manifest_load() {
  declare -gA OLD_HASH=()
  local mf
  mf="$(manifest_path)"
  [[ ! -L "$TARGET/.sdd-orchestrator-package" && ! -L "$mf" ]] || die "Estado del paquete no puede ser symlink."
  [[ -f "$mf" ]] || return 0
  local hash rel
  while IFS=$'\t' read -r hash rel; do
    [[ -n "$hash" && -n "$rel" ]] || continue
    valid_relpath "$rel" || die "Ruta inválida en manifest: $rel"
    assert_no_symlink_path "$rel"
    [[ "$hash" =~ ^[a-f0-9]{64}$ ]] || die "Hash inválido en manifest: $rel"
    OLD_HASH["$rel"]="$hash"
  done < "$mf"
}

write_manifest() {
  local tmp mf rel
  mf="$(manifest_path)"
  [[ ! -L "$TARGET/.sdd-orchestrator-package" && ! -L "$mf" ]] || die "Estado del paquete no puede ser symlink."
  mkdir -p -- "$(dirname -- "$mf")"
  tmp="$(mktemp "$(dirname -- "$mf")/.manifest.XXXXXX")"
  for rel in "${!NEW_HASH[@]}"; do
    printf '%s\t%s\n' "${NEW_HASH[$rel]}" "$rel"
  done | sort -k2,2 > "$tmp"
  chmod 600 "$tmp"
  mv -f -- "$tmp" "$mf"
}

clean_state_dir() {
  local dir
  dir="$(dirname -- "$(manifest_path)")"
  [[ -f "$(manifest_path)" ]] || rmdir -- "$dir" 2>/dev/null || true
}
