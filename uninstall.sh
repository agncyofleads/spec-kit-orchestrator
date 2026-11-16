#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "$0")" && pwd -P)/lib/package.sh"

usage() {
  cat <<'EOF'
Desinstala solo los archivos registrados como instalados por este paquete.
Uso: ./uninstall.sh [--target DIRECTORIO]
EOF
}

parse_target "$@" || { usage; exit 0; }
manifest_load
if ((${#OLD_HASH[@]} == 0)); then
  info "No hay archivos registrados por este paquete en: $TARGET"
  exit 0
fi

declare -A NEW_HASH=()
removed=0
preserved=0

for rel in "${!OLD_HASH[@]}"; do
  valid_relpath "$rel" || die "Ruta del paquete inválida en manifest: $rel"
  assert_no_symlink_path "$rel"
  dst="$TARGET/$rel"
  if [[ ! -e "$dst" ]]; then
    continue
  fi
  current="$(hash_file "$dst")"
  if [[ "$current" == "${OLD_HASH[$rel]}" ]]; then
    rm -- "$dst"
    ((removed+=1))
    continue
  fi

  answer="n"
  if [[ -t 0 ]]; then
    printf 'El archivo fue modificado localmente: %s\n¿Eliminarlo? [y/N] ' "$dst" >&2
    IFS= read -r answer || answer="n"
  else
    warn "Se preserva el archivo modificado (sin TTY no se solicita confirmación): $dst"
  fi
  case "$answer" in
    y|Y|yes|YES)
      rm -- "$dst"
      ((removed+=1))
      ;;
    *)
      NEW_HASH["$rel"]="${OLD_HASH[$rel]}"
      ((preserved+=1))
      ;;
  esac
done

if ((${#NEW_HASH[@]})); then
  write_manifest
else
  rm -f -- "$(manifest_path)"
  clean_state_dir
fi
info "Desinstalación: eliminados=$removed preservados=$preserved destino=$TARGET"
