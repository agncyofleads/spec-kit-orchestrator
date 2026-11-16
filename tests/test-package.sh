#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/sdd-package-test.XXXXXX")"
trap 'rm -rf -- "$TMP"' EXIT
PKG="$TMP/package"
TARGET="$TMP/opencode"
FOREIGN="$TARGET/custom/untouched.md"
mkdir -p "$PKG" "$TARGET/agents" "$TARGET/custom"
cp -a "$ROOT/agents" "$ROOT/commands" "$ROOT/skills" "$ROOT/lib" "$ROOT/dashboard" \
  "$ROOT/install.sh" "$ROOT/update.sh" "$ROOT/uninstall.sh" "$PKG/"

assert() { "$@" || { printf 'FAIL: %s\n' "$*" >&2; exit 1; }; }
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

printf 'unrelated content\n' > "$FOREIGN"
# Identical preexisting files are deliberately not adopted/owned.
cp "$PKG/agents/sdd-coordinator.md" "$TARGET/agents/sdd-coordinator.md"

"$PKG/install.sh" --target "$TARGET"
manifest="$TARGET/.sdd-orchestrator-package/manifest.tsv"
assert test -f "$manifest"
if grep -q '^agents/sdd-coordinator.md$' <(cut -f2 "$manifest"); then fail "installer adopted identical preexisting file"; fi
assert test -f "$TARGET/skills/sdd-workflow/references/full-path.md"
assert test ! -e "$TARGET/plugins/sdd-engine"
assert test "$(stat -c '%a' "$TARGET/agents/sdd-implementer.md")" = 644
assert test "$(stat -c '%a' "$manifest")" = 600

cp "$manifest" "$TMP/manifest.before"
"$PKG/install.sh" --target "$TARGET"
cmp -s "$TMP/manifest.before" "$manifest" || fail "install is not idempotent"

# A differing unowned collision aborts before any other files are copied.
mkdir -p "$TMP/conflict/commands"
printf 'foreign\n' > "$TMP/conflict/commands/sdd-feature.md"
if "$PKG/install.sh" --target "$TMP/conflict" >"$TMP/install.out" 2>&1; then fail "initial collision was accepted"; fi
assert test ! -e "$TMP/conflict/agents/sdd-coordinator.md"
assert grep -q 'archivo ajeno existente' "$TMP/install.out"

# A normal update replaces an unchanged managed file with package changes.
cp "$TARGET/agents/sdd-implementer.md" "$TMP/implementer.old"
printf '\n# package update fixture\n' >> "$PKG/agents/sdd-implementer.md"
"$PKG/update.sh" --target "$TARGET"
if cmp -s "$TMP/implementer.old" "$TARGET/agents/sdd-implementer.md"; then fail "package update did not replace owned file"; fi

# Local modifications abort the complete update before unrelated candidates change.
cp "$TARGET/commands/sdd-feature.md" "$TMP/feature.old"
printf '\n# local edit\n' >> "$TARGET/commands/sdd-feature.md"
printf '\n# package change\n' >> "$PKG/commands/sdd-feature.md"
printf '\n# second package change\n' >> "$PKG/commands/sdd-status.md"
cp "$TARGET/commands/sdd-status.md" "$TMP/status.before-conflict"
if "$PKG/update.sh" --target "$TARGET" >"$TMP/update.out" 2>&1; then fail "modified-file update conflict was accepted"; fi
cmp -s "$TMP/status.before-conflict" "$TARGET/commands/sdd-status.md" || fail "update partially changed another file"
assert grep -q 'modificado localmente' "$TMP/update.out"

# Restore the local file to the exact owned hash; the pending package update can proceed.
cp "$TMP/feature.old" "$TARGET/commands/sdd-feature.md"
"$PKG/update.sh" --target "$TARGET"
assert grep -q 'package change' "$TARGET/commands/sdd-feature.md"

# Removed package files are removed only when their installed hash is unchanged.
rm "$PKG/skills/sdd-architecture-review/SKILL.md"
"$PKG/update.sh" --target "$TARGET"
assert test ! -e "$TARGET/skills/sdd-architecture-review/SKILL.md"

# Non-interactive uninstall conservatively preserves modified files.
printf '\n# retain me\n' >> "$TARGET/commands/sdd-status.md"
"$PKG/uninstall.sh" --target "$TARGET" >"$TMP/uninstall.out" 2>&1
assert test -f "$TARGET/commands/sdd-status.md"
assert test -f "$manifest"
assert test -f "$FOREIGN"
# Retry after restoring the package-owned hash.
cp "$PKG/commands/sdd-status.md" "$TARGET/commands/sdd-status.md"
"$PKG/uninstall.sh" --target "$TARGET"
assert test ! -e "$TARGET/commands/sdd-status.md"
assert test -f "$TARGET/agents/sdd-coordinator.md" # preexisting identical file survived
assert test -f "$FOREIGN"
assert test ! -e "$manifest"

# Interactive confirmation can explicitly remove a locally modified owned file.
mkdir -p "$TMP/confirm-target"
"$PKG/install.sh" --target "$TMP/confirm-target"
printf '\n# modified\n' >> "$TMP/confirm-target/agents/sdd-reviewer.md"
python3 - "$PKG/uninstall.sh" "$TMP/confirm-target" <<'PY'
import os, pty, sys, time
pid, fd = pty.fork()
if pid == 0:
    os.execv(sys.argv[1], [sys.argv[1], "--target", sys.argv[2]])
os.write(fd, b"y\n")
status = 0
while True:
    try:
        chunk = os.read(fd, 4096)
        if not chunk:
            break
    except OSError:
        break
_, status = os.waitpid(pid, 0)
if not os.WIFEXITED(status) or os.WEXITSTATUS(status) != 0:
    raise SystemExit("interactive uninstall failed")
PY
assert test ! -e "$TMP/confirm-target/agents/sdd-reviewer.md"

# Symlink path protection: no package file may be written through a target symlink.
mkdir -p "$TMP/symlink-target" "$TMP/outside"
ln -s "$TMP/outside" "$TMP/symlink-target/agents"
if "$PKG/install.sh" --target "$TMP/symlink-target" >"$TMP/symlink.out" 2>&1; then fail "symlink destination accepted"; fi
assert test -z "$(find "$TMP/outside" -type f -print -quit)"

# Generator checks repository and installation-shaped roots without network/runtime dependencies.
python3 "$PKG/dashboard/generate.py" --source-root "$PKG" --output "$TMP/repo.html"
python3 - "$TMP/repo.html" <<'PY'
from html.parser import HTMLParser
from pathlib import Path
import sys

class DashboardAudit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.distribution = False
        self.copy_buttons = 0
        self.tabs = set()
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id") == "view-distribution":
            self.distribution = True
        if "copy-value" in attrs.get("class", "").split() and attrs.get("data-copy"):
            self.copy_buttons += 1
        if attrs.get("data-view"):
            self.tabs.add(attrs["data-view"])

audit = DashboardAudit()
audit.feed(Path(sys.argv[1]).read_text())
expected = {"overview", "explorer", "commands", "workflows", "architecture", "alignment", "distribution"}
if not audit.distribution or audit.copy_buttons != 9 or audit.tabs != expected:
    raise SystemExit(f"bad distribution UI: section={audit.distribution}, copies={audit.copy_buttons}, tabs={audit.tabs}")
PY
python3 "$PKG/dashboard/generate.py" --source-root "$TMP/repo.html" --output "$TMP/bad.html" >/dev/null 2>&1 && fail "invalid source root accepted"
python3 "$PKG/dashboard/generate.py" --source-root "$TARGET" --output "$TMP/installed.html"
python3 "$PKG/dashboard/generate.py" --source-root "$TARGET" --output "$TMP/installed.html" --check
# Snapshot freshness covers generator/template changes as well as audited files.
printf '\n# generator freshness fixture\n' >> "$PKG/dashboard/generate.py"
if python3 "$PKG/dashboard/generate.py" --source-root "$TARGET" --output "$TMP/installed.html" --check >/dev/null 2>&1; then fail "generator change was not detected as stale"; fi
python3 "$PKG/dashboard/generate.py" --source-root "$TARGET" --output "$TMP/installed.html"
python3 "$PKG/dashboard/generate.py" --source-root "$TARGET" --output "$TMP/installed.html" --check
printf '\n# dashboard stale fixture\n' >> "$TARGET/commands/sdd-init.md"
if python3 "$PKG/dashboard/generate.py" --source-root "$TARGET" --output "$TMP/installed.html" --check >/dev/null 2>&1; then fail "stale dashboard check passed"; fi
python3 "$PKG/dashboard/generate.py" --source-root "$TARGET" --output "$TMP/installed.html"
python3 "$PKG/dashboard/generate.py" --source-root "$TARGET" --output "$TMP/installed.html" --check

printf 'PASS: install/update/uninstall safety, idempotence, conflicts, symlink defense, generator freshness\n'
