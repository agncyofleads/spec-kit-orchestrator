#!/usr/bin/env python3
"""Generate a self-contained, read-only SDD layer documentation dashboard."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = PACKAGE_ROOT
OUTPUT = Path(__file__).resolve().parent / "sdd-orchestrator.html"
ROOTS = ("agents", "commands", "skills", "plugins/sdd-engine")
OTHER_GLOBAL_FILES = ("opencode.json",)
SENSITIVE_PATH = re.compile(r"(^|[/_.-])(secret|credential|token|private[-_]?key)([/_.-]|$)", re.I)
SENSITIVE_CONTENT = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    r"\bgh[pousr]_[A-Za-z0-9_]{25,}\b|"
    r"\bBearer\s+[A-Za-z0-9._~+/=-]{32,}",
    re.I,
)
PHASE_WORDS = (
    "constitution", "specify", "general clarification", "ux/ui clarification",
    "integral-semantic spec review", "plan", "post-plan architectural review",
    "tasks", "test scope review", "tasks refinement", "human dag review",
    "analyze → remediation → reanalysis", "implement", "converge",
    "operational human tests", "git closeout", "delta path",
)


def safe_text(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if len(raw) > 1_000_000:
        return "[Contenido omitido: archivo mayor a 1 MB]", digest
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return "[Contenido omitido: no es texto UTF-8]", digest
    if "\x00" in text or SENSITIVE_CONTENT.search(text):
        return "[Contenido omitido: se detectó un patrón sensible o binario]", digest
    return text, digest


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$", line)
        if match:
            result[match.group(1)] = match.group(2).strip("\"'")
    return result


def collect_sources() -> list[dict]:
    records = []
    for root_name in ROOTS:
        root = SOURCE_ROOT / root_name
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_symlink() or not path.is_file():
                continue
            rel = path.relative_to(SOURCE_ROOT).as_posix()
            if SENSITIVE_PATH.search(rel):
                continue
            content, digest = safe_text(path)
            frontmatter = parse_frontmatter(content)
            suffix = path.suffix.lower()
            inactive = suffix in {".draft", ".disabled", ".inactive"}
            kind = (
                "Agent" if rel.startswith("agents/")
                else "Command" if rel.startswith("commands/")
                else "Skill" if "/SKILL.md" in rel
                else "Referencia" if rel.startswith("skills/sdd-workflow/references/")
                else "Componente inactivo" if inactive
                else "Archivo"
            )
            records.append({
                "rel": rel,
                "abs": rel,
                "content": content,
                "sha256": digest,
                "kind": kind,
                "inactive": inactive,
                "description": frontmatter.get("description", ""),
                "frontmatter": frontmatter,
                "mtime": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
            })
    # Extract binding/activation facts only; global config stays out of payload.
    config = get_config_probe()
    for rel in OTHER_GLOBAL_FILES:
        path = SOURCE_ROOT / rel
        if not path.is_file() or SENSITIVE_PATH.search(rel):
            continue
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if rel == "opencode.json":
            content = json.dumps({
                "plugin": config.get("sddPluginIds", []),
                "command": {key: {"agent": value} for key, value in config.get("commandBindings", {}).items()},
                "_note": "Redacted allowlisted activation metadata; other config keys/values omitted.",
            }, ensure_ascii=False, indent=2)
            kind = "Configuración (metadata)"
            description = "Subset saneado: solo plugins SDD y bindings de Commands SDD."
        else:
            content, _ = safe_text(path)
            kind = "Configuración global"
            description = "Configuración global de UI, filtrada por patrones sensibles."
        records.append({
            "rel": rel + (" [activation metadata only]" if rel == "opencode.json" else ""),
            "abs": rel, "content": content, "sha256": digest, "kind": kind,
            "inactive": False, "description": description, "frontmatter": {},
            "mtime": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
            "activation": config if rel == "opencode.json" else {},
        })
    command_path = SOURCE_ROOT / "commands"
    command_files = sorted(command_path.glob("sdd-*.md")) if command_path.is_dir() else []
    command_relpaths = {p.relative_to(SOURCE_ROOT).as_posix() for p in command_files}
    for path in command_files:
        rel = path.relative_to(SOURCE_ROOT).as_posix()
        if not any(f["rel"] == rel for f in records):
            content, digest = safe_text(path)
            fm = parse_frontmatter(content)
            records.append({
                "rel": rel, "abs": rel, "content": content, "sha256": digest,
                "kind": "Command", "inactive": False, "description": fm.get("description", ""),
                "frontmatter": fm,
                "mtime": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
            })
    for f in records:
        if f["kind"] == "Command":
            f["activation"] = {
                "commandFilePresent": f["rel"] in command_relpaths,
                "configuredAgent": config.get("commandBindings", {}).get(Path(f["rel"]).stem),
                "frontmatterAgent": f["frontmatter"].get("agent"),
            }
    config["commandNames"] = sorted(p.stem for p in command_files)
    return records


def get_config_probe() -> dict:
    """Read activation keys only; never embed arbitrary config contents."""
    try:
        config_path = SOURCE_ROOT / "opencode.json"
        raw = config_path.read_bytes()
        data = json.loads(raw)
        plugins = data.get("plugin", [])
        commands = data.get("command", {})
        command_bindings = {}
        if isinstance(commands, dict):
            for command_id, command_value in commands.items():
                if command_id.startswith("sdd-") and isinstance(command_value, dict) and isinstance(command_value.get("agent"), str) and re.fullmatch(r"[A-Za-z0-9_-]+", command_value["agent"]):
                    command_bindings[command_id] = command_value["agent"]
                elif command_id.startswith("sdd-") and isinstance(command_value, str) and re.fullmatch(r"[A-Za-z0-9_-]+", command_value):
                    command_bindings[command_id] = command_value
        return {
            "path": "~/.config/opencode/opencode.json" if SOURCE_ROOT != PACKAGE_ROOT else "opencode.json (source repo; absent unless supplied)",
            "sha256": hashlib.sha256(raw).hexdigest(),
            "mtime": datetime.fromtimestamp(config_path.stat().st_mtime, timezone.utc).isoformat(),
            "pluginKeyDeclared": "plugin" in data,
            "sddPluginIds": [x for x in plugins if isinstance(x, str) and "sdd" in x.lower()] if isinstance(plugins, list) else [],
            "commandBindings": command_bindings,
            "configuredSddCommandNames": sorted(k for k in commands if isinstance(commands, dict) and k.startswith("sdd-")),
            "scope": "Solo la interfaz incluye bindings command sdd-* y plugin ids con sdd; no copia otras claves.",
        }
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {
            "path": "~/.config/opencode/opencode.json" if SOURCE_ROOT != PACKAGE_ROOT else "opencode.json",
            "sha256": "unavailable",
            "mtime": "unavailable",
            "pluginKeyDeclared": None,
            "sddPluginIds": [],
            "commandBindings": {},
            "configuredSddCommandNames": [],
            "scope": "No hay opencode.json en la raíz consultada; activación no verificada.",
        }


def audit_payload(files: list[dict], config: dict) -> dict:
    """Small mechanical checks over audited sources; findings remain evidence-bound."""
    by_path = {f["rel"]: f for f in files}
    texts = "\n".join(f["content"] for f in files)
    commands = [f for f in files if f["kind"] == "Command"]
    bindings = config.get("commandBindings", {})
    unbound = [Path(f["rel"]).stem for f in commands if not f.get("frontmatter", {}).get("agent")]
    missing_files = sorted(set(config.get("configuredSddCommandNames", [])) - {Path(f["rel"]).stem for f in commands})
    bad_agents = sorted({f.get("frontmatter", {}).get("agent") for f in commands
                         if f.get("frontmatter", {}).get("agent")
                         and f"agents/{f['frontmatter']['agent']}.md" not in by_path})
    checks = [
        {"state": "Incompleto" if unbound else "Verificado estáticamente", "title": "Agent declarado por Commands",
         "detail": f"Sin Agent en frontmatter: {', '.join(unbound)}." if unbound else "Todos los Commands declaran su Agent en frontmatter."},
        {"state": "Atención" if missing_files or bad_agents else "Verificado estáticamente", "title": "Comandos/Agents referenciados que faltan",
         "detail": f"Command sin archivo: {', '.join(missing_files) or 'ninguno'}; Agent sin archivo: {', '.join(bad_agents) or 'ninguno'}."},
        {"state": "Atención" if "/speckit.clarify" in texts or "sdd-full-pilot-vad0lxfj" in texts else "Verificado estáticamente",
            "title": "Referencias legacy conocidas", "detail": "Coincidencia detectada en snapshot." if ("/speckit.clarify" in texts or "sdd-full-pilot-vad0lxfj" in texts) else "No aparecen los dos identificadores legacy buscados."},
        {"state": "Atención" if re.search(r"at most\s+\*\*two|two correction-and-re-review rounds|bounded retry policy", texts, re.I) else "Verificado estáticamente",
         "title": "Límite fijo de reintentos", "detail": "Se detectó wording de límite fijo/bounded." if re.search(r"at most\s+\*\*two|two correction-and-re-review rounds|bounded retry policy", texts, re.I) else "No aparece wording conocido de límite fijo."},
        {"state": "Riesgo de permisos" if any(re.search(r"action: read\s+resource: \"\*\"\s+effect: allow", f["content"]) for f in files if f["rel"].startswith("agents/")) else "Verificado estáticamente",
         "title": "Permisos de lectura amplios", "detail": "Hay una regla read * allow; evaluar junto con denegaciones y precedencia de OpenCode, no equivale al permiso efectivo." if any(re.search(r"action: read\s+resource: \"\*\"\s+effect: allow", f["content"]) for f in files if f["rel"].startswith("agents/")) else "No se detectó read * allow en los Agents."},
        {"state": "No verificado", "title": "Activación efectiva del plugin",
          "detail": "La configuración revisada y la presencia de archivos no prueban la carga real; existen registros externos u otros mecanismos fuera de esta allowlist."},
        {"state": "Atención" if len([f for f in files if f["kind"] == "Skill"]) != 9 else "Verificado estáticamente",
         "title": "Inventario de Skills personalizadas",
         "detail": f"{len([f for f in files if f['kind'] == 'Skill'])} SKILL.md localizados; contrastar cambios de inventario tras regeneración."},
    ]
    decisions = [
        {"title": "Contrato runtime frente a borradores",
         "detail": f"Se detectaron {sum(1 for f in files if f['inactive'])} archivos inactivos bajo plugins/sdd-engine. El paquete operativo los excluye; no se infiere ejecución por su presencia."},
        {"title": "Configuración saneada",
         "detail": "El panel expone solo la allowlist de bindings command sdd-* y plugins cuyos ids contienen sdd; el resto de opencode.json queda fuera del HTML."},
        {"title": "Spec Kit boundary",
         "detail": "Los archivos oficiales del proyecto no se leen ni copian aquí; el árbol representa solo las raíces personalizadas y la configuración de activación saneada."},
        {"title": "Freshness",
         "detail": "El SHA-256 cubre rutas y bytes de las fuentes incluidas; --check detecta alta, cambio o borrado. No hay watcher; hay que invocarlo."},
    ]
    return {"checks": checks, "decisions": decisions}


def make_payload() -> tuple[dict, str]:
    files = collect_sources()
    generator_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    hash_input = "\n".join(
        [*(f"{x['rel']}\0{x['sha256']}" for x in files), f"dashboard/generate.py\0{generator_hash}"]
    ).encode()
    source_hash = hashlib.sha256(hash_input).hexdigest()
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sourceRoot": "~/.config/opencode" if SOURCE_ROOT != PACKAGE_ROOT else "repository source",
        "sourceHash": source_hash,
        "generatorHash": generator_hash,
        "files": files,
        "roots": list(ROOTS),
        "configProbe": get_config_probe(),
        "audit": audit_payload(files, get_config_probe()),
        "phaseVocabulary": list(PHASE_WORDS),
    }
    return payload, source_hash


HTML_TEMPLATE = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark">
<title>Spec Kit Orchestrator · documentación viva</title>
<style>
:root{color-scheme:dark;--bg:#0b0e14;--panel:#111722;--panel2:#151d2a;--line:#263246;--text:#e8edf5;--muted:#96a3b7;--accent:#72a7ff;--mint:#62d7b3;--amber:#f0bc66;--red:#ff7d86;--purple:#c4a6ff;--radius:14px;font:14px/1.55 Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(1000px 420px at 70% -180px,#1c3351 0%,transparent 70%),var(--bg);color:var(--text);min-height:100vh}
button,input{font:inherit}button{color:inherit}a{color:var(--accent)}:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.top{position:sticky;top:0;z-index:5;background:#0c1119ed;backdrop-filter:blur(14px);border-bottom:1px solid var(--line);padding:12px 22px;display:flex;gap:18px;align-items:center}
.brand{display:flex;align-items:center;gap:11px;min-width:230px}.mark{width:34px;height:34px;display:grid;place-items:center;border-radius:10px;background:linear-gradient(135deg,#6f9fff,#74e0bd);color:#07111b;font-weight:900}.brand strong{display:block;letter-spacing:.01em}.brand small{color:var(--muted)}
.topmeta{margin-left:auto;text-align:right;color:var(--muted);font-size:12px}.topmeta b{color:var(--text);font-weight:600}.fresh{color:var(--amber)!important}
.shell{display:grid;grid-template-columns:235px minmax(0,1fr);min-height:calc(100vh - 59px)}.rail{border-right:1px solid var(--line);padding:18px 12px;background:#0d121a}.rail-label{font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:#71819a;padding:10px 11px 7px}.nav{display:grid;gap:4px}.nav button{border:0;background:transparent;text-align:left;padding:10px 11px;border-radius:9px;color:#aeb9ca;cursor:pointer;display:flex;gap:10px;align-items:center}.nav button:hover{background:#182233;color:var(--text)}.nav button[aria-selected=true]{background:#1b2b43;color:#cfe0ff;box-shadow:inset 2px 0 var(--accent)}.nav .ico{width:18px;text-align:center;color:var(--accent)}
.rail-note{margin:22px 8px;padding:12px;border:1px solid var(--line);background:#101721;border-radius:10px;color:var(--muted);font-size:12px}
main{min-width:0;padding:28px clamp(16px,3vw,42px) 60px;max-width:1600px;width:100%;margin:0 auto}.view[hidden]{display:none!important}.eyebrow{color:var(--mint);font-size:11px;letter-spacing:.14em;text-transform:uppercase;font-weight:700}.title-row{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;margin:5px 0 23px}h1{font-size:clamp(25px,3vw,36px);line-height:1.15;letter-spacing:-.035em;margin:5px 0 8px}h2{font-size:20px;letter-spacing:-.02em;margin:0 0 8px}h3{font-size:15px;margin:0 0 8px}.lead{max-width:850px;color:#b0bdce;margin:0}.subtle{color:var(--muted)}.mono,code,pre{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
.grid{display:grid;gap:14px}.stats{grid-template-columns:repeat(4,minmax(0,1fr));margin:20px 0}.card{background:linear-gradient(180deg,#141c29,#101620);border:1px solid var(--line);border-radius:var(--radius);padding:17px;min-width:0}.stat{font-size:27px;font-weight:750;letter-spacing:-.04em}.stat-label{color:var(--muted);font-size:12px}.pill{display:inline-flex;align-items:center;gap:6px;padding:3px 8px;border:1px solid var(--line);border-radius:99px;font-size:11px;color:#bdc8d8;background:#111925}.pill.good{color:var(--mint);border-color:#29594e}.pill.warn{color:var(--amber);border-color:#6d542c}.pill.bad{color:var(--red);border-color:#703942}.pill.purple{color:var(--purple);border-color:#58477d}
.row{display:flex;align-items:center;gap:10px;flex-wrap:wrap}.between{justify-content:space-between}.button{border:1px solid #35455d;background:#172235;border-radius:9px;padding:8px 12px;cursor:pointer}.button:hover{background:#20304a}.button.primary{background:#244a76;border-color:#37699f}.button.ghost{background:transparent}.button.small{padding:5px 9px;font-size:12px}
.callout{border-left:3px solid var(--accent);background:#111d2c;padding:13px 15px;border-radius:0 10px 10px 0;color:#bac8dc}.callout.warn{border-color:var(--amber);background:#201b12}.callout.danger{border-color:var(--red);background:#21151a}.cards-2{grid-template-columns:repeat(2,minmax(0,1fr))}.cards-3{grid-template-columns:repeat(3,minmax(0,1fr))}
.section-head{display:flex;justify-content:space-between;align-items:center;margin:26px 0 12px;gap:12px}.section-head p{margin:0;color:var(--muted);font-size:12px}
.explorer{display:grid;grid-template-columns:minmax(230px,310px) minmax(0,1fr);gap:14px;align-items:start}.tree-card{padding:0;overflow:hidden}.tree-top{padding:13px;border-bottom:1px solid var(--line);display:flex;gap:8px}.search{width:100%;border:1px solid #334158;border-radius:8px;background:#0c121b;color:var(--text);padding:9px 10px}.tree{padding:10px 8px;max-height:66vh;overflow:auto}.tree button{border:0;background:none;color:#bec9d8;text-align:left;width:100%;padding:5px 7px;border-radius:6px;cursor:pointer;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.tree button:hover,.tree button[aria-current=true]{background:#1a2a40;color:#e7f0ff}.tree .dir{color:#9eb9dd;font-weight:650}.tree .file{font-weight:400}.tree .inactive{color:#8c94a1}.tree .indent{display:inline-block;width:calc(var(--depth)*13px)}.file-icon{display:inline-block;width:17px;color:#79aefc}.tree .inactive .file-icon{color:var(--amber)}.detail-card{min-height:400px}.detail-title{overflow-wrap:anywhere}.detail-description{font-size:16px;color:#c5d2e4}.detail-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:15px}.detail-box{border-top:1px solid var(--line);padding-top:12px}.detail-box h3{color:#9fb0c7;font-size:11px;text-transform:uppercase;letter-spacing:.1em}.detail-box p,.detail-box li{color:#c4cedd;font-size:13px}.detail-box ul{padding-left:18px;margin:6px 0}.source{margin-top:16px}.source summary{cursor:pointer;color:#aac0df}.source pre{max-height:52vh;overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere;background:#0a0e14;border:1px solid var(--line);border-radius:9px;padding:13px;color:#c5cedb;font-size:12px}
.command-card{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;align-items:start}.command-card code{display:block;color:#c7e3ff;background:#0b111a;border:1px solid #253449;border-radius:8px;padding:10px;overflow-wrap:anywhere}.cmd-arg{width:100%;min-height:74px;resize:vertical;border:1px solid #334158;border-radius:8px;background:#0b111a;color:var(--text);padding:10px}.cmd-template{font-size:12px;color:var(--muted)}.copy-line{display:flex;gap:8px;align-items:center}.copy-line input{flex:1}.live{min-height:1.4em;color:var(--mint);font-size:12px}
.workflow-toolbar{display:flex;gap:8px;margin:12px 0}.steps{display:grid;gap:9px}.step{display:grid;grid-template-columns:36px minmax(0,1fr) auto;gap:12px;align-items:start}.step-num{width:29px;height:29px;border-radius:50%;display:grid;place-items:center;background:#1b2b43;color:#b9d5ff;font-weight:700;border:1px solid #334c6f}.step-body{min-width:0}.step-body p{margin:4px 0;color:#adb9cb;font-size:13px}.step-title{font-weight:700}.step-meta{display:flex;gap:6px;flex-wrap:wrap}.step-detail[hidden]{display:none}.step-detail{margin-top:8px;padding:10px;border-left:2px solid #344a67;color:#bdc8d7;background:#101722;font-size:12px}
.relation-list{display:grid;gap:9px}.relation{display:grid;grid-template-columns:minmax(120px,.8fr) auto minmax(150px,1fr);gap:10px;align-items:center;padding:10px;border-bottom:1px solid #222e40}.relation button{background:none;border:0;color:#cfe0f5;text-align:left;cursor:pointer;overflow-wrap:anywhere}.relation-type{font-size:11px;color:var(--mint);text-align:center}.filters{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.filter{border:1px solid var(--line);background:#111925;padding:6px 10px;border-radius:99px;color:#b7c4d7;cursor:pointer}.filter[aria-pressed=true]{border-color:#527bb3;color:#d7e6ff;background:#19273a}
.checks{display:grid;gap:10px}.check{display:grid;grid-template-columns:130px minmax(0,1fr);gap:12px;padding:12px;border:1px solid var(--line);border-radius:10px;background:#101721}.check p{margin:3px 0 0;color:#b7c3d3;font-size:13px}.check small{color:var(--muted)}.sources-list{columns:2;column-gap:30px}.sources-list li{break-inside:avoid;margin:5px 0;color:#b7c4d5;font-size:12px;overflow-wrap:anywhere}
.footer{border-top:1px solid var(--line);padding-top:18px;margin-top:36px;color:#77859a;font-size:12px}.muted-link{color:#9fb9da;text-decoration:none}.empty{padding:24px;text-align:center;color:var(--muted)}
.install-command{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;align-items:start}.install-code{overflow:auto;background:#0b111a;border:1px solid #253449;border-radius:8px;padding:12px}.install-code code{white-space:pre;display:block;color:#c7e3ff}.copy-value{white-space:nowrap}
@media(max-width:900px){.shell{grid-template-columns:1fr}.rail{position:sticky;top:59px;z-index:4;padding:7px;border-right:0;border-bottom:1px solid var(--line);overflow:auto}.rail-label,.rail-note{display:none}.nav{display:flex;min-width:max-content}.nav button{padding:9px}.top{padding:10px 14px}.brand{min-width:0}.topmeta{font-size:10px}.explorer{grid-template-columns:minmax(0,1fr)}.tree{max-height:260px}.stats{grid-template-columns:repeat(2,1fr)}.cards-3{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){main{padding:20px 13px 42px}.cards-2,.cards-3{grid-template-columns:1fr}.detail-grid{grid-template-columns:1fr}.title-row{display:block}.step{grid-template-columns:30px minmax(0,1fr)}.step-meta{grid-column:2}.relation{grid-template-columns:1fr auto 1fr}.sources-list{columns:1}.check{grid-template-columns:1fr}.topmeta{max-width:44%;overflow-wrap:anywhere}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;animation-duration:.01ms!important;transition-duration:.01ms!important}}
</style>
</head>
<body>
<header class="top">
  <div class="brand"><div class="mark" aria-hidden="true">S</div><div><strong>Spec Kit Orchestrator</strong><small>Documentación viva · global OpenCode</small></div></div>
  <div class="topmeta"><div>Generado <b id="generated"></b></div><div id="freshness" class="fresh">Snapshot · actualiza para verificar fuentes</div></div>
</header>
<div class="shell">
<aside class="rail" aria-label="Navegación principal">
  <div class="rail-label">Workspace</div>
  <nav class="nav" role="tablist" aria-label="Secciones del panel">
    <button role="tab" aria-selected="true" data-view="overview"><span class="ico">⌂</span>Resumen</button>
    <button role="tab" aria-selected="false" data-view="explorer"><span class="ico">▤</span>Explorador</button>
    <button role="tab" aria-selected="false" data-view="commands"><span class="ico">⌘</span>Comandos</button>
    <button role="tab" aria-selected="false" data-view="workflows"><span class="ico">⇢</span>Workflows</button>
    <button role="tab" aria-selected="false" data-view="architecture"><span class="ico">⌬</span>Arquitectura</button>
    <button role="tab" aria-selected="false" data-view="alignment"><span class="ico">◎</span>Alineación</button>
    <button role="tab" aria-selected="false" data-view="distribution"><span class="ico">⇩</span>Instalar</button>
  </nav>
  <div class="rail-note">Solo consulta. Los botones copian texto; no ejecutan comandos ni modifican OpenCode.</div>
</aside>
<main>
  <section id="view-overview" class="view" role="tabpanel">
    <div class="eyebrow">Auditoría estática · fuentes locales</div>
    <div class="title-row"><div><h1>Mapa operativo del orquestador</h1><p class="lead">Explora Agents, Commands, Skills y contratos. La vista se genera desde el filesystem global; las etiquetas diferencian citas textuales de bindings y permisos explícitos.</p></div><button class="button primary" data-goto="explorer">Abrir explorador</button></div>
  <div class="grid stats" id="stats"></div>
    <div class="grid cards-2">
      <article class="card"><div class="eyebrow">Full</div><h2>Iniciar o recorrer Full</h2><p>Proyecto nuevo: <code>/sdd-init</code>. Nueva funcionalidad en proyecto existente: <code>/sdd-feature</code>. Ambos son prompts globales asignados al Coordinator.</p><button class="button small" data-goto="commands">Ver catálogo</button></article>
      <article class="card"><div class="eyebrow">Delta</div><h2>Cambio acotado</h2><p><code>/sdd-delta</code> preserva artefactos válidos y recupera fases upstream cuando falten o estén obsoletas. El DAG y sus gates siguen aplicando.</p><button class="button small" data-goto="workflows">Ver transiciones</button></article>
    </div>
    <div class="section-head"><h2>Capas y límites</h2></div>
    <div class="grid cards-3">
      <article class="card"><span class="pill purple">OpenCode personalizado</span><p>Commands, Agents, Skills y referencias globales definen coordinación, permisos, owners y gates.</p></article>
      <article class="card"><span class="pill">Spec Kit por proyecto</span><p>Skills oficiales y artefactos del proyecto se cargan mediante la interfaz pública de Skills y se usan como procedimiento de fase.</p></article>
      <article class="card"><span class="pill warn">Sin motor automático</span><p>La documentación define coordinación conversacional; no implementa scheduler, recuperación durable ni aislamiento de archivos.</p></article>
    </div>
    <div class="callout warn" style="margin-top:15px"><strong>Freshness:</strong> este HTML es un snapshot autocontenido. El navegador no compara el filesystem desde <code>file://</code>; usa el comando <code>generate.py --check</code> para detectar cambios pendientes.</div>
  </section>

  <section id="view-explorer" class="view" role="tabpanel" hidden>
    <div class="eyebrow">Filesystem global · archivos detectados</div><div class="title-row"><div><h1>Explorador</h1><p class="lead">Selecciona un archivo para ver metadatos derivados, límites, fases citadas y relaciones verificables.</p></div><span class="pill" id="file-count"></span></div>
    <div class="explorer">
      <section class="card tree-card" aria-label="Árbol de archivos"><div class="tree-top"><input id="tree-search" class="search" type="search" placeholder="Filtrar archivos…" aria-label="Filtrar archivos"></div><div id="tree" class="tree" role="tree"></div></section>
      <article class="card detail-card" id="detail" aria-live="polite"><div class="empty">Selecciona un archivo del árbol.</div></article>
    </div>
  </section>

  <section id="view-commands" class="view" role="tabpanel" hidden>
    <div class="eyebrow">Plantillas OpenCode · no ejecutables desde aquí</div><div class="title-row"><div><h1>Centro de comandos</h1><p class="lead">Sintaxis y argumentos se leen de los Commands instalados. Prepara texto y cópialo para ejecutarlo manualmente en OpenCode.</p></div></div>
    <div class="grid" id="command-list"></div>
  </section>

  <section id="view-workflows" class="view" role="tabpanel" hidden>
    <div class="eyebrow">Transiciones declaradas en las referencias</div><div class="title-row"><div><h1>Visualizador de workflows</h1><p class="lead">Los pasos se extraen de Full/Delta. Los chips separan trabajo de Spec Kit, coordinación personalizada y gates; abre cada paso para consultar su texto fuente.</p></div></div>
    <div class="workflow-toolbar"><button class="button" data-flow="full" aria-pressed="true">Full</button><button class="button" data-flow="delta" aria-pressed="false">Delta</button></div>
    <div id="workflow-list" class="steps"></div>
  </section>

  <section id="view-architecture" class="view" role="tabpanel" hidden>
    <div class="eyebrow">Relaciones desde frontmatter y menciones</div><div class="title-row"><div><h1>Arquitectura y dependencias</h1><p class="lead">Bindings y permisos se muestran como relaciones explícitas. Las menciones del cuerpo son referencias textuales: por sí solas no prueban invocación.</p></div></div>
    <div class="filters" id="edge-filters">
      <button class="filter" data-kind="all" aria-pressed="true">Todas</button><button class="filter" data-kind="binding" aria-pressed="false">Binding de Command</button><button class="filter" data-kind="permission" aria-pressed="false">Permisos de Skill</button><button class="filter" data-kind="mention" aria-pressed="false">Menciones textuales</button>
    </div>
    <div class="card"><div class="relation-list" id="relations"></div></div>
    <div class="section-head"><h2>Frontera Spec Kit</h2></div><div class="grid cards-2">
      <article class="card"><span class="pill purple">Interfaz pública</span><p>El Coordinator permite Skills oficiales por ID; el Reviewer permite <code>speckit-analyze</code>. OpenCode carga el <code>SKILL.md</code> de la integración activa y expone su base directory.</p></article>
      <article class="card"><span class="pill">Fuera de esta capa</span><p>Skills, scripts, plantillas y manifests oficiales viven en el proyecto. No se incluyen en este snapshot ni se parchean desde este panel.</p></article>
    </div>
  </section>

  <section id="view-alignment" class="view" role="tabpanel" hidden>
    <div class="eyebrow">Reglas y comprobaciones reproducibles</div><div class="title-row"><div><h1>Control de alineación</h1><p class="lead">Separación entre decisiones documentadas y resultados estáticos calculados al regenerar. Ningún check de este panel representa ejecución de un workflow.</p></div><span id="plugin-status"></span></div>
    <div class="callout" id="generated-note"></div>
    <div class="section-head"><h2>Comprobaciones estáticas</h2><p>Generadas leyendo las fuentes listadas</p></div><div class="checks" id="checks"></div>
    <div class="section-head"><h2>Decisiones arquitectónicas documentadas</h2></div><div class="grid cards-2" id="decisions"></div>
    <div class="section-head"><h2>Fuentes incluidas</h2><p id="source-root"></p></div><ul class="sources-list" id="sources"></ul>
  </section>
  <section id="view-distribution" class="view" role="tabpanel" hidden>
    <div class="eyebrow">Repositorio fuente · instalación independiente de Spec Kit</div>
    <div class="title-row"><div><h1>Instalar Spec Kit Orchestrator</h1><p class="lead">Instala solamente nuestros Agents, Commands y Skills en la configuración global de OpenCode. Spec Kit debe instalarse por separado en cada proyecto.</p></div><a class="button primary" href="https://github.com/agncyofleads/spec-kit-orchestrator" target="_blank" rel="noopener noreferrer">Abrir repositorio ↗</a></div>
    <div class="grid cards-2">
      <article class="card"><span class="pill good">Requisitos previos</span><ul><li>Ubuntu/Linux, Git y OpenCode instalados.</li><li>Spec Kit y su integración pública de Skills instalados independientemente en el proyecto.</li><li>Bash y utilidades estándar; Python 3 solo para regenerar el dashboard.</li></ul></article>
      <article class="card"><span class="pill purple">Alcance seguro</span><p>El instalador escribe solo Agents, Commands y Skills del paquete. No modifica Spec Kit, archivos de configuración de OpenCode ni plugins. Colisiones diferentes detienen la operación.</p></article>
    </div>
    <div class="section-head"><h2>Clonar e instalar</h2><p>Desde un terminal Linux</p></div>
    <article class="card install-command"><div class="install-code"><code>git clone https://github.com/agncyofleads/spec-kit-orchestrator.git
cd spec-kit-orchestrator
./install.sh</code></div><button class="button small primary copy-value" data-copy="git clone https://github.com/agncyofleads/spec-kit-orchestrator.git&#10;cd spec-kit-orchestrator&#10;./install.sh">Copiar</button></article>
    <div class="section-head"><h2>Actualizar</h2><p>Ejecuta desde el directorio clonado</p></div>
    <article class="card install-command"><div class="install-code"><code>git pull --ff-only
./update.sh</code></div><button class="button small primary copy-value" data-copy="git pull --ff-only&#10;./update.sh">Copiar</button></article>
    <p class="subtle">La actualización se detiene ante archivos modificados localmente o colisiones; resuelve el conflicto y vuelve a intentarlo.</p>
    <div class="section-head"><h2>Desinstalar</h2><p>Los cambios locales requieren confirmación</p></div>
    <article class="card install-command"><div class="install-code"><code>./uninstall.sh</code></div><button class="button small primary copy-value" data-copy="./uninstall.sh">Copiar</button></article>
    <p class="subtle">Los archivos modificados se conservan por defecto si no hay terminal interactiva. Los archivos ajenos y Spec Kit permanecen intactos.</p>
    <div class="section-head"><h2>Comandos disponibles</h2><p>Prompt templates: se invocan manualmente en OpenCode</p></div>
    <div class="grid cards-2">
      <article class="card"><h3><code>/sdd-init</code></h3><p>Inicia un proyecto nuevo —solicita sus principios antes de crear Constitution— o distingue un proyecto existente y respeta su Constitution. Luego solicita la funcionalidad para Full.</p><button class="button small copy-value" data-copy="/sdd-init Describe el proyecto y sus principios o restricciones">Copiar ejemplo</button></article>
      <article class="card"><h3><code>/sdd-feature</code></h3><p>Inicia una funcionalidad por la ruta Full sin reinicializar el proyecto ni cambiar su Constitution.</p><button class="button small copy-value" data-copy="/sdd-feature Describe la funcionalidad solicitada">Copiar ejemplo</button></article>
      <article class="card"><h3><code>/sdd-delta</code></h3><p>Procesa un cambio acotado a una funcionalidad existente, conserva artefactos válidos y recupera fases upstream cuando haga falta.</p><button class="button small copy-value" data-copy="/sdd-delta feature=&lt;feature&gt; change=&lt;cambio&gt; artifacts=&lt;rutas conocidas&gt;">Copiar ejemplo</button></article>
      <article class="card"><h3><code>/sdd-resume</code></h3><p>Continúa únicamente desde estado, aprobaciones, artefactos y evidencia verificables; no inventa estado persistente.</p><button class="button small copy-value" data-copy="/sdd-resume &lt;rutas de artefactos y contexto verificable&gt;">Copiar ejemplo</button></article>
      <article class="card"><h3><code>/sdd-status</code></h3><p>Informe consultivo, de solo lectura, limitado a rutas, evidencia y contexto proporcionados por el usuario.</p><button class="button small copy-value" data-copy="/sdd-status &lt;rutas, evidencia y contexto proporcionados&gt;">Copiar ejemplo</button></article>
      <article class="card"><h3><code>/sdd-approve</code></h3><p>Opcional: valida una decisión humana explícita contra un gate pendiente y su alcance. Invocarlo no constituye por sí solo una aprobación.</p><button class="button small copy-value" data-copy="/sdd-approve gate=&lt;gate pendiente&gt; decision=&lt;resultado&gt; scope=&lt;alcance exacto&gt;">Copiar sintaxis</button></article>
    </div>
    <div class="callout warn" style="margin-top:16px">Copiar solo prepara texto. Este dashboard no ejecuta shell, OpenCode ni comandos SDD. La presencia de archivos no demuestra activación runtime.</div>
  </section>
  <footer class="footer">Spec Kit Orchestrator · HTML estático autocontenido · sin red, servidor, framework ni llamadas de ejecución. <span id="hash"></span></footer>
</main>
</div>
<div id="live" class="live" aria-live="polite" style="position:absolute;left:-10000px"></div>
<script>
const DATA = __SDD_DATA_JSON__;
const AUDIT = DATA.audit;
const $ = (s,root=document)=>root.querySelector(s);
const $$ = (s,root=document)=>[...root.querySelectorAll(s)];
const esc = v => String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
const byRel = new Map(DATA.files.map(f=>[f.rel,f]));
const nameOf = f => f.rel.split("/").at(-1);
const pathId = f => f.rel.replace(/\/SKILL\.md$/,"").split("/").at(-1);
function firstParagraph(text){let body=text.replace(/^---[\s\S]*?---\s*/,"");const lines=body.split(/\r?\n/);let out=[];for(const line of lines){if(/^#{1,6}\s/.test(line)&&out.length)break;if(/^#{1,6}\s/.test(line)||!line.trim())continue;out.push(line.trim());if(out.join(" ").length>600)break}return out.join(" ").replace(/[`*_]/g,"")}
function headings(text){return [...text.matchAll(/^#{1,4}\s+(.+)$/gm)].map(m=>m[1].replace(/[*`]/g,""))}
function clauses(text){return text.split(/\r?\n/).filter(x=>/^\s*(?:[-*]\s+|\d+\.\s+)/.test(x)&&/\b(?:must|do not|does not|never|only|stop|remain|requires?|deny|allow|PASS|FAIL|read-only|no fixed|sin límite|detener)\b/i.test(x)).slice(0,8).map(x=>x.trim().replace(/^[-*]\s+|^\d+\.\s+/,""))}
 function phases(text){const low=text.toLowerCase();return DATA.phaseVocabulary.filter(p=>low.includes(p.toLowerCase()))}
function relationEdges(){
 const edges=[];
 const resolveRel=(base,target)=>{const parts=base.split("/");parts.pop();for(const part of target.split("/")){if(!part||part===".")continue;if(part==="..")parts.pop();else parts.push(part)}return parts.join("/")};
 for(const f of DATA.files){
   if(f.kind==="Command"){
     const configured=(DATA.configProbe.commandBindings||{})[nameOf(f).replace(/\.md$/,"")];
     f.activation={...(f.activation||{}),fileAgentBinding:configured||null,frontmatterAgent:(f.frontmatter||{}).agent||null};
   }
   const fm=f.frontmatter||{};
   if(fm.agent && byRel.has(`agents/${fm.agent}.md`)) edges.push({from:f.rel,to:`agents/${fm.agent}.md`,kind:"binding",label:"frontmatter: agent"});
   const body=f.content;
   for(const m of body.matchAll(/resource:\s*(sdd-[a-z0-9-]+|speckit-[a-z0-9-]+)/g)){
     const target=DATA.files.find(x=>x.kind==="Skill"&&pathId(x)===m[1]);
     if(target) edges.push({from:f.rel,to:target.rel,kind:"permission",label:`permiso ${m[1]}`});
   }
   for(const target of DATA.files){
     if(target.rel===f.rel)continue;
     const id=pathId(target);
     if(id.length<8)continue;
     if(new RegExp(`\\b${id.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")}\\b`,"i").test(body))
       edges.push({from:f.rel,to:target.rel,kind:"mention",label:`mención literal «${id}»`});
   }
   for(const m of body.matchAll(/\]\(([^)#]+\.md)(?:#[^)]+)?\)/g)){
     const target=byRel.get(resolveRel(f.rel,m[1]));
     if(target) edges.push({from:f.rel,to:target.rel,kind:"mention",label:"enlace Markdown"});
   }
 }
 const seen=new Set();
  for(const f of DATA.files.filter(x=>x.kind==="Command")){
    const configured=(DATA.configProbe.commandBindings||{})[nameOf(f).replace(/\.md$/,"")];
    const agent=byRel.get(`agents/${configured}.md`);
    if(agent)edges.push({from:f.rel,to:agent.rel,kind:"binding",label:`opencode.json command.agent=${configured}`});
  }
  return edges.filter(e=>{const k=[e.from,e.to,e.kind,e.label].join("|");if(seen.has(k))return false;seen.add(k);return true});
}
const EDGES=relationEdges();
function buildTree(){
 const root={name:"~/.config/opencode",dirs:new Map(),files:[]};
  for(const f of DATA.files){let n=root;const parts=f.rel.split("/");for(const p of parts.slice(0,-1)){if(!n.dirs.has(p))n.dirs.set(p,{name:p,dirs:new Map(),files:[]});n=n.dirs.get(p)}n.files.push(f)}
 return root;
}
const TREE=buildTree();let selected=null;let openDirs=new Set(["agents","commands","skills","skills/sdd-workflow","skills/sdd-workflow/references","plugins","plugins/sdd-engine"]);
function treeHTML(node,depth=0,prefix=""){
 let out="";
 for(const [name,child] of node.dirs){const rel=prefix?`${prefix}/${name}`:name;const has=DATA.files.some(f=>f.rel.startsWith(rel+"/"));if(!has)continue;const isOpen=openDirs.has(rel);out+=`<button class="dir" role="treeitem" aria-expanded="${isOpen}" data-dir="${esc(rel)}"><span class="indent" style="--depth:${depth}"></span>${isOpen?"▾":"▸"} ${esc(name)}/</button>`;if(isOpen)out+=treeHTML(child,depth+1,rel)}
  for(const f of node.files){const q=($("#tree-search").value||"").toLowerCase();if(q&&!`${f.rel} ${f.description} ${f.content}`.toLowerCase().includes(q))continue;out+=`<button class="file ${f.inactive?"inactive":""}" role="treeitem" aria-current="${selected===f.rel}" data-file="${esc(f.rel)}"><span class="indent" style="--depth:${depth}"></span><span class="file-icon">${f.inactive?"◇":"▧"}</span>${esc(nameOf(f))}</button>`}
 return out;
}
function renderTree(){const el=$("#tree");el.innerHTML=treeHTML(TREE);if(!el.children.length)el.innerHTML='<div class="empty">Sin coincidencias.</div>'}
function renderDetail(f){
 if(!f){$("#detail").innerHTML='<div class="empty">Selecciona un archivo del árbol.</div>';return}
 const rels=EDGES.filter(e=>e.from===f.rel);const used=EDGES.filter(e=>e.to===f.rel);
  const status=f.inactive?'<span class="pill warn">Inactivo · borrador</span>':f.kind.startsWith("Configuración")?'<span class="pill">Configuración · subset redactado</span>':'<span class="pill good">Fuente instalada · activación no inferida</span>';
  const phase=phases(f.content.replace(/^---[\s\S]*?---\s*/,""));const cs=clauses(f.content);const hs=headings(f.content);
 const isRisk=/sdd-coordinator|sdd-implementer|sdd-reviewer|sdd-converge|sdd-architecture-review|sdd-tasks-refinement/.test(f.rel);
  const provenance=f.kind.startsWith("Configuración")?"Configuración · subset explícito sin secretos":f.rel.startsWith("commands/")?"Fuente de prompt; binding es solo el configurado":"Filesystem de ~/.config/opencode · instalación no equivale a activación";
 $("#detail").innerHTML=`<div class="row between"><span class="pill">${esc(f.kind)}</span>${status}</div><h2 class="detail-title mono" style="margin-top:12px">${esc(f.rel)}</h2><p class="detail-description">${esc(f.description||firstParagraph(f.content)||"Sin descripción declarativa; consulta el contenido fuente.")}</p>
 <div class="detail-grid">
 <div class="detail-box"><h3>Función / responsabilidades</h3><p>${esc(firstParagraph(f.content)||"No se extrajo un párrafo introductorio.")}</p><ul>${hs.slice(0,7).map(x=>`<li>${esc(x)}</li>`).join("")||"<li>Sin encabezados detectados.</li>"}</ul></div>
 <div class="detail-box"><h3>Límites / cláusulas</h3><ul>${cs.map(x=>`<li>${esc(x)}</li>`).join("")||"<li>Consultar fuente completa; no se detectaron cláusulas por regla léxica.</li>"}</ul></div>
  <div class="detail-box"><h3>Fases / etapas mencionadas</h3><p>${phase.map(x=>`<span class="pill">${esc(x)}</span>`).join(" ")||"No detectadas por vocabulario."}</p><small class="subtle">Búsqueda léxica en el cuerpo (sin frontmatter); no implica intervención o responsabilidad.</small></div>
 <div class="detail-box"><h3>Relaciones</h3><p><b>Sale:</b> ${rels.length?rels.map(e=>`<button class="muted-link jump" data-target="${esc(e.to)}">${esc(e.label)} → ${esc(e.to)}</button>`).join("<br>"):"Sin aristas extraídas."}</p><p><b>Entrante:</b> ${used.length?used.map(e=>`<button class="muted-link jump" data-target="${esc(e.from)}">${esc(e.from)} → ${esc(e.label)}</button>`).join("<br>"):"Sin aristas extraídas."}</p><small class="subtle">Bindings y permisos vienen del frontmatter; el resto son menciones, no prueba de ejecución.</small></div>
  </div><div class="row" style="margin-top:14px"><span class="pill ${isRisk?"warn":""}">${esc(provenance)}</span><small class="subtle mono">${esc(f.abs)}</small></div>
  <details class="source"><summary>${f.content?`Ver contenido fuente (${f.content.split("\n").length} líneas · SHA-256 ${f.sha256.slice(0,12)}…)`:"Ver metadatos de activación"}</summary><pre>${esc(f.content||JSON.stringify(f.activation,null,2))}</pre></details>`;
}
function renderStats(){
  const n=k=>DATA.files.filter(f=>f.kind===k).length;
  $("#stats").innerHTML=[[n("Agent"),"Agents"],[n("Command"),"Commands"],[DATA.files.filter(f=>f.kind==="Skill"||f.kind==="Referencia").length,"Skills + referencias"],[DATA.files.filter(f=>f.inactive).length,"Borradores inactivos"],[n("Configuración (metadata)"),"Metadata config disponible"],[Object.keys(DATA.configProbe.commandBindings||{}).length,"Bindings explícitos en config"],[EDGES.length,"Relaciones extraídas"],[DATA.files.length,"Fuentes incorporadas"]].map(([v,l])=>`<article class="card"><div class="stat">${v}</div><div class="stat-label">${l}</div></article>`).join("");
 $("#file-count").textContent=`${DATA.files.filter(f=>!f.rel.startsWith("opencode.json [")).length} archivos · 1 config parcial`;
 $("#generated").textContent=new Date(DATA.generatedAt).toLocaleString("es-ES",{dateStyle:"medium",timeStyle:"short",timeZone:"UTC"})+" UTC";
 $("#hash").textContent=`· snapshot ${DATA.sourceHash.slice(0,12)}`;
 $("#source-root").textContent=DATA.sourceRoot;
  const activeIds=DATA.configProbe.sddPluginIds||[];
  $("#plugin-status").innerHTML=activeIds.length?`<span class="pill good">Plugin SDD configurado: ${activeIds.map(esc).join(", ")}</span>`:'<span class="pill warn">Plugin SDD no identificado en la configuración global; revisar mecanismo de activación de esta instalación</span>';
 $("#generated-note").innerHTML=`Snapshot generado desde <code>${esc(DATA.sourceRoot)}</code>. Digest de fuentes: <code>${esc(DATA.sourceHash)}</code>. La marca horaria no verifica por sí sola que el filesystem siga igual; ejecuta el generador en modo <code>--check</code>. Configuración consultada de forma acotada: ${esc(DATA.configProbe.path)} — ${esc(DATA.configProbe.scope)}`;
 $("#sources").innerHTML=DATA.files.map(f=>`<li><code>${esc(f.rel)}</code> · ${f.inactive?"inactivo":f.rel.startsWith("opencode.json [")?"subset de bindings/plugins SDD":"incluido"}</li>`).join("");
}
function renderCommands(){
  const commands=DATA.files.filter(f=>f.kind==="Command");
 const examples={"sdd-init":"Describe aquí el proyecto y los principios solicitados","sdd-feature":"Describe aquí la funcionalidad","sdd-delta":"feature=<feature existente> cambio=<cambio solicitado>","sdd-approve":"gate=<gate pendiente> decision=<resultado> scope=<artefacto o acción exacta>","sdd-resume":"<rutas de artefactos y contexto verificable>","sdd-status":"<rutas y evidencia que el operador proporciona>"};
  $("#command-list").innerHTML=commands.map(f=>{const id=nameOf(f).replace(/\.md$/,"");const format=(f.content.match(/Input format:\s*([^\n]+)/i)||[])[1]||"";const syntax=format?`/${id} ${format}`:`/${id} <argumentos según la plantilla>`;const sample=`/${id} ${examples[id]||"argumentos de texto"}`;const declared=f.frontmatter?.agent;const configured=f.activation?.configuredAgent;const invoked=declared?`frontmatter → ${declared}`:"Sin Agent declarado";const mismatch=configured&&declared&&configured!==declared;return `<article class="card command-card"><div><div class="row"><span class="pill">/${esc(id)}</span><span class="pill purple">${esc(invoked)}</span>${configured?`<span class="pill">config → ${esc(configured)}</span>`:""}${mismatch?'<span class="pill bad">Discrepancia config/frontmatter</span>':''}</div><h2 style="margin-top:12px">${esc(f.description||id)}</h2><p class="subtle">${esc(firstParagraph(f.content))}</p><div class="cmd-template"><b>Sintaxis:</b> <code>${esc(syntax)}</code><br><b>Argumentos:</b> texto sustituye <code>$ARGUMENTS</code>; ${format?"formato declarado por la plantilla":"sin formato formal de argumentos declarado"}.</div><details style="margin-top:10px"><summary>Fuente completa, requisitos y límites</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere">${esc(f.content)}</pre></details><label class="cmd-template" for="arg-${esc(id)}">Preparar argumentos</label><textarea id="arg-${esc(id)}" class="cmd-arg" data-command="${esc(id)}" placeholder="${esc(examples[id]||"argumentos")}"></textarea><div class="live" id="live-${esc(id)}"></div></div><div><button class="button small primary copy-command" data-id="${esc(id)}" data-sample="${esc(sample)}">Copiar</button></div></article>`}).join("");
}
function flowData(which){
 const rel=which==="full"?"skills/sdd-workflow/references/full-path.md":"skills/sdd-workflow/references/delta-path.md";const f=byRel.get(rel);if(!f)return[];
 const lines=f.content.split(/\r?\n/);const start=which==="full"?lines.findIndex(line=>/^##\s+Sequence and transitions/i.test(line)):0;
 if(start<0)return[];
 const end=which==="full"?lines.findIndex((line,i)=>i>start&&/^##\s+/.test(line)):lines.findIndex(line=>/^##\s+Narrow refinement omission/i.test(line));
 const block=lines.slice(start+1,end<0?lines.length:end);
 return block.map(line=>{const m=line.match(/^\s*(\d+)\.\s+(?:\*\*(.*?)\*\*\s*:\s*)?(.*)$/);return m?{n:m[1],title:m[2]||m[3].split(/[.:]/)[0],body:m[3]}:null}).filter(Boolean);
}
let activeFlow="full";
const gateWords=/review|approval|approve|suspend|PASS|gate/i;
function origin(title){
  const t=title.toLowerCase();
  if(/constitution|specify|general clarification|plan|tasks/.test(t))return ["Spec Kit · artefacto/fase","SDD custom · ownership/handoff/gate"];
  if(/analyze/.test(t))return ["Spec Kit · Skill analyze","SDD custom · remediación/avance"];
  if(/review|test scope|dag|refinement|converge|implement|git closeout|operational|ux\/ui/.test(t))return ["SDD custom · gate/coordinación","Spec Kit artifact interface; not every step is Spec Kit"];
  return ["SDD custom · Full/Delta contract","Spec Kit only when explicitly named"];
}
function renderWorkflow(){
  const steps=flowData(activeFlow);$("#workflow-list").innerHTML=steps.map(s=>{const [a,b]=origin(s.title);const gate=/stop|suspend|approval|approve|PASS|FAIL|gate|human/i.test(s.body)||/review|approval|approve|gate/i.test(s.title);return `<article class="card step"><div class="step-num">${esc(s.n)}</div><div class="step-body"><div class="step-title">${esc(s.title)}</div><p>${esc(s.body)}</p><div class="step-meta"><span class="pill purple">${esc(a)}</span><span class="pill">${esc(b)}</span>${gate?'<span class="pill warn">Condición de avance / detención explícita</span>':'<span class="pill">Sin gate destacado en esta etapa</span>'}</div><details class="step-detail"><summary>Texto de origen</summary>${esc(s.body)}</details></div><button class="button small" data-goto="explorer" data-select="${esc(activeFlow==="full"?"skills/sdd-workflow/references/full-path.md":"skills/sdd-workflow/references/delta-path.md")}">Fuente</button></article>`}).join("");
}
let edgeKind="all";
function renderEdges(){const edges=EDGES.filter(e=>edgeKind==="all"||e.kind===edgeKind);$("#relations").innerHTML=edges.length?edges.map(e=>`<div class="relation"><button data-target="${esc(e.from)}" class="jump">${esc(e.from)}</button><span class="relation-type">${esc(e.label)}</span><button data-target="${esc(e.to)}" class="jump">${esc(e.to)}</button></div>`).join(""):'<div class="empty">No hay relaciones de ese tipo.</div>'}
 function checks(){
 const texts=DATA.files.map(f=>f.content).join("\n");const get=rel=>byRel.get(rel)?.content||"";
 const full=get("skills/sdd-workflow/references/full-path.md"),delta=get("skills/sdd-workflow/references/delta-path.md");
 const commandFiles=DATA.files.filter(f=>f.kind==="Command");const bindings=DATA.configProbe.commandBindings||{};const badBindings=commandFiles.filter(f=>f.frontmatter.agent&&!byRel.has(`agents/${f.frontmatter.agent}.md`));
 const unbound=commandFiles.filter(f=>!f.frontmatter.agent);
 const configuredCommands=Object.keys(bindings);
 const missingCommandFiles=configuredCommands.filter(id=>!commandFiles.some(f=>nameOf(f).replace(/\.md$/,"")===id));
 const legacy=texts.includes("/speckit.clarify")||texts.includes("sdd-full-pilot-vad0lxfj");
 const cap=/at most\s+\*\*two|two correction-and-re-review rounds|bounded retry policy/i.test(texts);
 const flock=/flock/.test(get("agents/sdd-implementer.md")+get("skills/sdd-implement/SKILL.md"));
 const noLock=/not an atomic lock|not a scheduler, lock/i.test(get("skills/sdd-workflow/references/execution-policy.md")+get("skills/sdd-tasks-refinement/SKILL.md"));
 const broadRead=DATA.files.filter(f=>/agents\/sdd-(?:coordinator|implementer)\.md/.test(f.rel)&&/action: read[\s\S]{0,35}resource: "\*"[\s\S]{0,35}effect: allow/.test(f.content)).map(f=>f.rel);
  return [
  {state:badBindings.length?"Atención":unbound.length?"Incompleto":"Verificado estáticamente",title:"Agent declarado por Commands",detail:badBindings.length?`Agent no encontrado: ${badBindings.map(x=>x.rel).join(", ")}`:unbound.length?`Commands sin Agent en frontmatter: ${unbound.map(x=>nameOf(x)).join(", ")}`:`${commandFiles.length} Commands declaran un Agent existente en frontmatter.`},
  {state:legacy?"Atención":"Verificado estáticamente",title:"Referencias obsoletas",detail:legacy?"Persisten referencias al fixture anterior o al comando /speckit.clarify.":"No se detectaron la ruta del fixture ni /speckit.clarify en las fuentes incluidas."},
  {state:cap?"Atención":"Verificado estáticamente",title:"Límite fijo de reintentos",detail:cap?"Se detectó wording de retry fijo/bounded.":"No se detectó el límite anterior de dos rondas en las fuentes incluidas."},
  {state:(flock&&noLock)?"Inconsistencia textual":"Verificado estáticamente",title:"Actualización concurrente de tasks.md",detail:(flock&&noLock)?"Implementer/Skill ordenan flock para el checkbox; otras referencias dicen que la coordinación no proporciona lock/atomicidad. El alcance es ambiguo y debería explicitarse.":"No se detectó simultáneamente la instrucción flock y la negación general de locks."},
  {state:broadRead.length?"Riesgo de permisos":"Verificado estáticamente",title:"Lectura amplia de Agents",detail:broadRead.length?`read * allow en: ${broadRead.join(", ")}. Aplicar el orden de permisos de OpenCode y comprobar los denies específicos posteriores; este match textual no equivale al permiso efectivo.`:"No se detectó read * allow en Coordinator/Implementer."},
   {state:"No verificado",title:"Ejecución real / gates / tests",detail:"El generador solo inspecciona texto y filesystem permitido. No ejecuta Skills, Commands, pruebas ni transiciones SDD."},
  ];
}
function renderAlignment(){
 $("#checks").innerHTML=[...checks(),...AUDIT.checks].map(c=>`<article class="check"><div><span class="pill ${/Verificado/.test(c.state)?"good":/No verificado/.test(c.state)?"":"warn"}">${esc(c.state)}</span></div><div><b>${esc(c.title)}</b><p>${esc(c.detail)}</p></div></article>`).join("");
  const cards=[
  ["Ownership","La fase propietaria corrige sus artefactos; los reviewers diagnostican y no editan."],
  ["Aprobaciones","Un PASS técnico no es aprobación humana; cambios materiales pueden invalidar gates downstream."],
  ["Analyze","Read-only; remediación por owner y reanálisis tras cada corrección; sin límite fijo si hay progreso."],
  ["Ejecución","Subagentes nativos y paralelismo solo por DAG y outputs disjuntos; no se garantiza aislamiento."],
  ["Converge","Una revisión global final, sin revisiones por tarea o por wave; operational tests quedan al operador."],
   ["Git","Cierre solo tras aceptación operativa y autorización explícita; no asumida por este panel."],
 ];
 $("#decisions").innerHTML=[...cards,...AUDIT.decisions.map(x=>[x.title,x.detail])].map(([h,p])=>`<article class="card"><span class="pill">Contrato documental</span><h3 style="margin-top:10px">${esc(h)}</h3><p class="subtle">${esc(p)}</p></article>`).join("");
}
function setView(name){
 $$(".view").forEach(v=>v.hidden=v.id!==`view-${name}`);
 $$(".nav [role=tab]").forEach(b=>{const yes=b.dataset.view===name;b.setAttribute("aria-selected",String(yes));b.tabIndex=yes?0:-1});
}
async function copyText(text){
 try{await navigator.clipboard.writeText(text)}catch(_){const t=document.createElement("textarea");t.value=text;t.style.position="fixed";t.style.opacity="0";document.body.append(t);t.select();document.execCommand("copy");t.remove()}
  $("#live").textContent="Copiado al portapapeles. El panel no ejecuta el contenido.";
}
document.addEventListener("click",e=>{
 const tab=e.target.closest("[data-view]");if(tab){setView(tab.dataset.view);return}
 const go=e.target.closest("[data-goto]");if(go){setView(go.dataset.goto);if(go.dataset.select){selected=go.dataset.select;renderTree();renderDetail(byRel.get(selected))}return}
 const dir=e.target.closest("[data-dir]");if(dir){openDirs.has(dir.dataset.dir)?openDirs.delete(dir.dataset.dir):openDirs.add(dir.dataset.dir);renderTree();return}
 const file=e.target.closest("[data-file]");if(file){selected=file.dataset.file;renderTree();renderDetail(byRel.get(selected));return}
 const jump=e.target.closest("[data-target]");if(jump){selected=jump.dataset.target;setView("explorer");renderTree();renderDetail(byRel.get(selected));return}
 const flow=e.target.closest("[data-flow]");if(flow){activeFlow=flow.dataset.flow;$$("[data-flow]").forEach(b=>b.setAttribute("aria-pressed",String(b===flow)));renderWorkflow();return}
 const filter=e.target.closest("[data-kind]");if(filter){edgeKind=filter.dataset.kind;$$("[data-kind]").forEach(b=>b.setAttribute("aria-pressed",String(b===filter)));renderEdges();return}
  const copy=e.target.closest(".copy-command");if(copy){const area=$(`#arg-${CSS.escape(copy.dataset.id)}`);const arg=area.value.trim()||copy.dataset.sample.replace(/^\/[^ ]+\s*/,"");copyText(`/${copy.dataset.id}${arg?" "+arg:""}`);return}
  const copyValue=e.target.closest(".copy-value");if(copyValue){copyText(copyValue.dataset.copy);return}
});
document.addEventListener("keydown",e=>{const tabs=$$(".nav [role=tab]");const i=tabs.indexOf(document.activeElement);if(i>=0&&(e.key==="ArrowDown"||e.key==="ArrowUp")){e.preventDefault();tabs[(i+(e.key==="ArrowDown"?1:tabs.length-1))%tabs.length].focus()}});
$("#tree-search").addEventListener("input",renderTree);
function init(){renderStats();renderTree();renderCommands();renderWorkflow();renderEdges();renderAlignment();$("#freshness").title="Snapshot hash "+DATA.sourceHash+". Usa generate.py --check para comparar con el filesystem actual."}
init();
</script>
</body></html>
"""


def render(payload: dict) -> str:
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    # Prevent a source string from terminating the inline script element.
    data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    audit = json.dumps(payload["audit"], ensure_ascii=False, separators=(",", ":"))
    audit = audit.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return HTML_TEMPLATE.replace("__SDD_DATA_JSON__", data).replace("__SDD_AUDIT_JSON__", audit)


def main() -> int:
    global SOURCE_ROOT, OUTPUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=PACKAGE_ROOT,
                        help="raíz con agents/, commands/, skills/ (repositorio o instalación)")
    parser.add_argument("--output", type=Path, default=OUTPUT, help="ruta del HTML de salida")
    parser.add_argument("--check", action="store_true", help="solo comprobar si el HTML coincide con las fuentes")
    args = parser.parse_args()
    SOURCE_ROOT = args.source_root.expanduser().resolve()
    OUTPUT = args.output.expanduser().resolve()
    payload, digest = make_payload()
    if not payload["files"]:
        print(f"ERROR: no se encontraron fuentes SDD en {SOURCE_ROOT}", file=sys.stderr)
        return 2
    if args.check:
        try:
            current = OUTPUT.read_text(encoding="utf-8")
        except OSError:
            print(f"STALE: falta {OUTPUT}; ejecuta {Path(__file__).name}", file=sys.stderr)
            return 1
        marker = re.search(r'<meta name="sdd-source-sha256" content="([0-9a-f]{64})">', current)
        if marker and marker.group(1) == digest:
            print(f"ACTUALIZADO: {len(payload['files'])} fuentes · SHA-256 {digest}")
            return 0
        print(f"OBSOLETO: el HTML no coincide con las fuentes actuales · SHA-256 actual {digest}", file=sys.stderr)
        return 1
    output = render(payload)
    output = output.replace(
        '<meta name="color-scheme" content="dark">',
        f'<meta name="color-scheme" content="dark"><meta name="sdd-source-sha256" content="{digest}">',
        1,
    )
    OUTPUT.write_text(output, encoding="utf-8")
    print(f"Generado: {OUTPUT}")
    print(f"Fuentes: {len(payload['files'])} · SHA-256 {digest} · UTC {payload['generatedAt']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
