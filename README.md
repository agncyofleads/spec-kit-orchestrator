# Spec Kit Orchestrator

Portable, file-based SDD coordination for OpenCode: three Agents, six slash-command prompt templates, nine custom Skills and five workflow references. Includes a static, self-contained dashboard and conservative install/update/uninstall scripts.

**Repository:** <https://github.com/agncyofleads/spec-kit-orchestrator><br>
**License:** MIT — see [`LICENSE`](LICENSE).

This project is a custom OpenCode layer, not a fork or distribution of Spec Kit. Spec Kit and this package are installed, updated and removed independently.

## Architecture

```text
agents/       Coordinator, Implementer and read-only Reviewer
commands/     /sdd-* OpenCode Markdown prompt templates
skills/       Custom SDD phase/workflow contracts
  sdd-workflow/references/
              Full/Delta paths, gates, ownership and execution policy
install.sh    Installs package-owned Agents, Commands and Skills
update.sh     Hash-checked update with conflict preflight
uninstall.sh  Removes only files recorded as package-owned
dashboard/    Generated HTML and its Python standard-library generator
tests/        Isolated installer lifecycle tests
```

The operational package contains 3 Agents, 6 Commands, 9 Skills and 5 references. The seven historical `sdd-engine/*.draft` files are intentionally excluded. No engine, scheduler, extra Agent or SDD phase is introduced.

### Permission and dependency boundaries

- The Coordinator is primary, keeps the existing human gates and delegates only to the named Reviewer and Implementer.
- The Implementer remains a subagent with its existing read/discovery permissions, approval asks and Git mutation denials.
- The Reviewer remains read-only with its existing sensitive-path denials and review Skill allowlist.
- Existing permission declarations are preserved verbatim. In particular, some Agents declare broad `read: * allow` rules; effective permission behavior depends on OpenCode's evaluation and runtime and is not claimed as verified here.
- The workflow expects the project’s independently installed Spec Kit/OpenCode integration to expose the public Agent Skill IDs `speckit-constitution`, `speckit-specify`, `speckit-clarify`, `speckit-checklist`, `speckit-plan`, `speckit-tasks`, `speckit-analyze`, `speckit-implement` and `speckit-converge`.
- This repository does not install, copy, patch, or uninstall Spec Kit Skills, manifests, integrations, scripts or configuration.

## Requirements

For installation: Ubuntu/Linux, Git and OpenCode. The project must separately have the Spec Kit integration needed for the SDD phases. The installer uses Bash and standard Linux utilities (`sha256sum`, `find`, `sort`, `install`, `mktemp`, `awk`).

Python 3 is needed only to regenerate or check the dashboard. It uses the standard library; no framework, server, network access or Python package is required.

## Install

```bash
git clone https://github.com/agncyofleads/spec-kit-orchestrator.git
cd spec-kit-orchestrator
./install.sh
```

The default destination is `${XDG_CONFIG_HOME:-$HOME/.config}/opencode`. To target a separate OpenCode config root explicitly:

```bash
./install.sh --target "$HOME/.config/opencode"
```

Only package files under `agents/`, `commands/` and `skills/` are installed. OpenCode configuration, plugins, Spec Kit and unrelated files are untouched. Identical pre-existing files are not adopted. Differing collisions abort installation before writes. Ownership and installed hashes are recorded in `.sdd-orchestrator-package/manifest.tsv` inside the target.

Reload/restart OpenCode if needed. Commands are user-invoked Markdown prompt templates; the browser dashboard only copies text and never runs them.

## Commands

| Command | Purpose |
| --- | --- |
| `/sdd-init` | Distinguishes a genuinely new project from an existing one. For a new project it asks for principles before creating Constitution, then requests the feature and follows the existing Full path. |
| `/sdd-feature` | Starts a feature through Full without reinitializing the project or changing its Constitution. |
| `/sdd-delta` | Applies a bounded change to an existing feature, preserving demonstrably valid artifacts and recovering affected upstream phases when necessary. |
| `/sdd-resume` | Continues only from verifiable artifacts, approvals and evidence; it does not invent durable workflow state. |
| `/sdd-status` | Read-only status report constrained to paths, evidence and context supplied by the user. |
| `/sdd-approve` | Optional validation of an explicit human decision for a currently pending gate and exact scope. Invoking it alone is not approval. |

Examples:

```text
/sdd-init Describe the project and its principles or constraints
/sdd-feature Describe the requested feature
/sdd-delta feature=<feature> change=<change> artifacts=<known paths>
/sdd-resume <artifact paths and verifiable context>
/sdd-status <user-supplied paths, evidence and context>
/sdd-approve gate=<pending gate> decision=<outcome> scope=<exact scope>
```

These are illustrative prompt arguments, not parsers or execution APIs. Human gates and the existing Full/Delta contract remain authoritative.

## Update

From the cloned repository:

```bash
git pull --ff-only
./update.sh
```

Or specify the target:

```bash
./update.sh --target "$HOME/.config/opencode"
```

Update compares current files with the previous package manifest and the new package. Local edits, untracked collisions and modified obsolete files cause a conflict report and abort the update before file changes. Resolve the conflict deliberately and retry; local changes are never silently overwritten.

## Uninstall

From the repository that owns the installed manifest:

```bash
./uninstall.sh
```

Modified package-owned files prompt for confirmation (`y` removes; `n` preserves). Without an interactive terminal, modified files are preserved. Unchanged files recorded by the package are removed; unrelated and pre-existing files are not. The manifest remains when modified files are preserved, allowing a later retry.

## Dashboard

Open the generated, self-contained HTML directly:

```bash
firefox dashboard/sdd-orchestrator.html
```

Regenerate from the repository source:

```bash
python3 dashboard/generate.py
```

Generate a separate snapshot of a real installation (read-only):

```bash
python3 dashboard/generate.py \
  --source-root "$HOME/.config/opencode" \
  --output "$HOME/spec-kit-orchestrator-installed.html"
```

Check freshness without rewriting the output:

```bash
python3 dashboard/generate.py \
  --source-root "$HOME/.config/opencode" \
  --output "$HOME/spec-kit-orchestrator-installed.html" --check
```

The dashboard covers the custom layer only. It may identify inactive drafts in an installation snapshot but never packages them. It includes copyable distribution instructions and SDD command examples; copied text is not executed. Freshness is checked on demand; no watcher or persistent service is installed.

## Tests and publication safety

Run the installer lifecycle tests in temporary directories:

```bash
bash tests/test-package.sh
```

The tests cover idempotence, pre-existing files, conflicts, updates, uninstall confirmation/preservation, symlink defenses and generator freshness. They do not modify the current user's global OpenCode configuration or invoke any Spec, Full or Delta workflow.

## License

MIT. See [`LICENSE`](LICENSE). Spec Kit remains independently licensed and is not included in this repository.
