#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "$0")" && pwd -P)/lib/package.sh"

usage() {
  cat <<'EOF'
Actualiza únicamente archivos bajo control del paquete y sin cambios locales.
Uso: ./update.sh [--target DIRECTORIO]
EOF
}

parse_target "$@" || { usage; exit 0; }
manifest_load
declare -p OLD_HASH >/dev/null
if ((${#OLD_HASH[@]} == 0)); then
  die "No hay manifest del paquete en $TARGET; ejecuta install.sh primero."
fi

declare -A NEW_HASH=()
conflicts=()
to_copy=()
to_remove=()

while IFS= read -r -d '' rel; do
  valid_relpath "$rel" || die "Ruta del paquete inválida: $rel"
  assert_no_symlink_path "$rel"
  src="$PACKAGE_ROOT/$rel"
  dst="$TARGET/$rel"
  desired="$(hash_file "$src")"
  if [[ -e "$dst" ]]; then
    current="$(hash_file "$dst")"
    if [[ -n "${OLD_HASH[$rel]+x}" ]]; then
      if [[ "$current" != "${OLD_HASH[$rel]}" && "$current" != "$desired" ]]; then
        conflicts+=("$rel (modificado localmente)")
      elif [[ "$current" == "$desired" ]]; then
        NEW_HASH["$rel"]="$desired"
      else
        to_copy+=("$rel")
        NEW_HASH["$rel"]="$desired"
      fi
    elif [[ "$current" == "$desired" ]]; then
      : # identical preexisting file remains unmanaged
    else
      conflicts+=("$rel (archivo ajeno existente)")
    fi
  else
    to_copy+=("$rel")
    NEW_HASH["$rel"]="$desired"
  fi
done < <(package_files)

for rel in "${!OLD_HASH[@]}"; do
  if [[ ! -f "$PACKAGE_ROOT/$rel" ]]; then
    dst="$TARGET/$rel"
    if [[ -e "$dst" ]]; then
      current="$(hash_file "$dst")"
      if [[ "$current" == "${OLD_HASH[$rel]}" ]]; then
        to_remove+=("$rel")
      else
        conflicts+=("$rel (obsoleto y modificado localmente)")
      fi
    fi
  fi
done

if ((${#conflicts[@]})); then
  printf 'Actualización abortada; no se modificó ningún archivo:\n' >&2
  printf '  - %s\n' "${conflicts[@]}" >&2
  exit 1
fi

for rel in "${to_copy[@]}"; do install -D -m 0644 -- "$PACKAGE_ROOT/$rel" "$TARGET/$rel"; done
for rel in "${to_remove[@]}"; do rm -- "$TARGET/$rel"; done
write_manifest
info "Actualización completada en: $TARGET"
info "Archivos gestionados: ${#NEW_HASH[@]}; retirados por obsolescencia: ${#to_remove[@]}"
