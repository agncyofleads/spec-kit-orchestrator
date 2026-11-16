#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "$0")" && pwd -P)/lib/package.sh"

usage() {
  cat <<'EOF'
Instala los Agents, Commands y Skills propios en OpenCode.
Uso: ./install.sh [--target DIRECTORIO]
Destino por defecto: ${XDG_CONFIG_HOME:-$HOME/.config}/opencode
EOF
}

parse_target "$@" || { usage; exit 0; }
manifest_load
declare -A NEW_HASH=()
conflicts=()
to_copy=()

while IFS= read -r -d '' rel; do
  valid_relpath "$rel" || die "Ruta del paquete inválida: $rel"
  assert_no_symlink_path "$rel"
  src="$PACKAGE_ROOT/$rel"
  dst="$TARGET/$rel"
  desired="$(hash_file "$src")"
  if [[ -e "$dst" ]]; then
    current="$(hash_file "$dst")"
    if [[ -n "${OLD_HASH[$rel]+x}" ]]; then
      if [[ "$current" == "${OLD_HASH[$rel]}" && "$current" == "$desired" ]]; then
        NEW_HASH["$rel"]="$desired"
      elif [[ "$current" == "${OLD_HASH[$rel]}" ]]; then
        conflicts+=("$rel (ya instalado; el paquete cambió: usa update.sh)")
      else
        conflicts+=("$rel (modificado localmente)")
      fi
    elif [[ "$current" != "$desired" ]]; then
      conflicts+=("$rel (archivo ajeno existente)")
    fi
  else
    to_copy+=("$rel")
    NEW_HASH["$rel"]="$desired"
  fi
done < <(package_files)

if ((${#conflicts[@]})); then
  printf 'Instalación abortada; no se modificó ningún componente:\n' >&2
  printf '  - %s\n' "${conflicts[@]}" >&2
  exit 1
fi

for rel in "${to_copy[@]}"; do
  install -D -m 0644 -- "$PACKAGE_ROOT/$rel" "$TARGET/$rel"
done
write_manifest
info "Instalación completada en: $TARGET"
info "Componentes propiedad del paquete: ${#NEW_HASH[@]}"
info "Archivos preexistentes idénticos quedaron sin adoptar."
