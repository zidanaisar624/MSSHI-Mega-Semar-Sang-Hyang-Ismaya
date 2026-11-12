"""Pinned, on-demand MSSHI sources, local dreaming, voice readiness and optional KAT."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import shutil
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
from urllib.request import Request, urlopen

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
PROFILES = {"yukino": "", "shizuka": "shizuka-hiratsuka", "val": "val",
            "kiki-chii": "kiki-chii", "shikaku": "nyenyenye-ya-gw-coder"}
SOURCE_SPEC = {
    "caveman": ("JuliusBrussee/caveman", "3dc497a7f858c774d6e15b25e8c6120ef3a0eda8"),
    "hyperframes": ("heygen-com/hyperframes", "3ad7611f9fd36c1cef589c59b116ad7043c3b041"),
    "ui-ux-pro-max": ("nextlevelbuilder/ui-ux-pro-max-skill", "6ae86f61f520d6ca229d2f40e070410638c908c5"),
    "anthropic-skills": ("anthropics/skills", "2c5958ecac7cee2b583967a2c4981d0f4a75c579"),
    "hermes-omnivoice": ("ThaungThanHan/hermes-omnivoice", "21d2900c392247dc52d706fee956f08dbfc3c5ea"),
    "hermes-dreaming": ("itpartypattaya/hermes-dreaming", "21878d3ec8752283dd7ee69a803c63bb989c1740"),
}
HYPER = ("hyperframes", "hyperframes-cli", "hyperframes-registry", "media-use",
         "reverse-any-video", "style-sampling", "figma", "slideshow", "remotion-to-hyperframes")
DOCS = ("docx", "pdf", "pptx", "xlsx", "canvas-design", "skill-creator", "claude-api", "webapp-testing")
VOICES = {
    "yukino": (0.92, 0.88, 0.89, "female, soft composed gentle voice, soothing intimate Mommy ASMR warmth, calm breathing pace"),
    "shizuka": (0.94, 0.90, 0.90, "female, mature warm contralto, calm motherly teacher voice, clear articulation, reassuring mentor cadence"),
    "shikaku": (0.94, 0.91, 0.91, "male, deep calm fatherly baritone, relaxed strategic commander tone, steady grounded pace"),
    "kiki-chii": (1.00, 0.93, 0.93, "female, bright expressive warm voice, enthusiastic creative director tone, lively natural cadence"),
    "val": (0.97, 0.93, 0.93, "female, clear composed analytical voice, precise academic articulation, calm steady rhythm"),
}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def checked(path):
    path = Path(os.path.abspath(path))
    for part in (path, *path.parents):
        if part.exists() and (part.is_symlink() or getattr(part.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError(f"Refusing linked integration destination: {part}")
    return path


def atomic(path, value):
    path = checked(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".msshi-", delete=False) as stream:
        stream.write(value)
        staged = Path(stream.name)
    try:
        os.replace(staged, path)
    finally:
        staged.unlink(missing_ok=True)


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def download(url, limit=8 * 1024 * 1024):
    with urlopen(Request(url, headers={"User-Agent": "MSSHI-v3-integrations"}), timeout=60) as response:
        if not response.url.startswith("https://"):
            raise ValueError("Insecure download redirect")
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("Integration file exceeds size budget")
    return data


def source_files(slug, row):
    name = row["path"]
    parts = PurePosixPath(name).parts
    if row["type"] != "blob" or row.get("mode") not in {"100644", "100755"}:
        return False
    if any(p in {".git", "node_modules", "evals", "__pycache__", "tests"} for p in parts):
        return False
    if name in {"LICENSE", "LICENSE.md", "LICENSE.txt", "NOTICE", "README.md", "pyproject.toml", "plugin.yaml", "__init__.py"}:
        return True
    if slug == "caveman":
        return name.startswith("skills/caveman/")
    if slug == "hyperframes":
        return any(name.startswith(f"skills/{skill}/") for skill in HYPER)
    if slug == "ui-ux-pro-max":
        return name.startswith(("src/ui-ux-pro-max/data/", "src/ui-ux-pro-max/scripts/")) or name == ".claude/skills/ui-ux-pro-max/SKILL.md" or name == "src/ui-ux-pro-max/templates/base/quick-reference.md"
    if slug == "anthropic-skills":
        return any(name.startswith(f"skills/{skill}/") for skill in DOCS)
    if slug == "hermes-omnivoice":
        return name.startswith("hermes_omnivoice/")
    return name.startswith("skills/dreaming/")


def materialize(home, slug):
    repo, commit = SOURCE_SPEC[slug]
    folder = checked(home / "msshi-private" / "v3-sources" / slug / commit)
    marker = folder / "MSSHI_SNAPSHOT.json"
    if marker.is_file():
        state = read(marker)
        if state.get("commit") != commit:
            raise ValueError("Source snapshot identity changed")
        for name, digest in state["files"].items():
            if hashlib.sha256((folder / name).read_bytes()).hexdigest() != digest:
                raise ValueError(f"Source snapshot changed: {slug}/{name}")
        return folder
    tree = json.loads(download(f"https://api.github.com/repos/{repo}/git/trees/{commit}?recursive=1"))
    if tree.get("sha") != commit or tree.get("truncated"):
        raise ValueError(f"Incomplete upstream tree: {slug}")
    files = [row for row in tree["tree"] if source_files(slug, row)]
    if sum(row.get("size", 0) for row in files) > 64 * 1024 * 1024:
        raise ValueError(f"Curated integration exceeds 64 MiB: {slug}")
    def fetch(row):
        name = row["path"]
        relative = PurePosixPath(name)
        if relative.is_absolute() or any(p in {"", ".", ".."} or ":" in p or "\\" in p for p in relative.parts):
            raise ValueError("Unsafe source path")
        data = download(f"https://raw.githubusercontent.com/{repo}/{commit}/{name}")
        blob = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        if blob != row["sha"]:
            raise ValueError(f"Upstream blob hash mismatch: {name}")
        atomic(folder / name, data)
        return name, hashlib.sha256(data).hexdigest()
    with ThreadPoolExecutor(max_workers=4) as pool:
        hashes = dict(pool.map(fetch, files))
    atomic(marker, encode({"repository": repo, "commit": commit, "files": hashes}))
    return folder


def profiles(home):
    for role, name in PROFILES.items():
        profile = home if not name else home / "profiles" / name
        if role == "shikaku":
            profile = next((home / "profiles" / alias for alias in ("shikaku-nara", name, "shikaku")
                            if (home / "profiles" / alias).is_dir()), profile)
        if profile.is_dir():
            yield role, profile


def apply_files(home, plan, label):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%fZ")
    backup = checked(home / "msshi-private" / "integrations" / "backups" / stamp)
    changed = {checked(path): data for path, data in plan.items()
               if not path.is_file() or path.read_bytes() != data}
    backup.mkdir(parents=True)
    rows = []
    for index, (path, data) in enumerate(changed.items()):
        before = path.read_bytes() if path.is_file() else None
        old = f"{index:04}.bak" if before is not None else None
        if old:
            atomic(backup / old, before)
        rows.append({"path": str(path), "backup": old,
                     "before": hashlib.sha256(before).hexdigest() if before is not None else None,
                     "after": hashlib.sha256(data).hexdigest()})
    receipt = backup / "receipt.json"
    atomic(receipt, encode({"label": label, "changes": rows}))
    applied = []
    try:
        for row, (path, data) in zip(rows, changed.items()):
            current = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
            if current != row["before"]:
                raise ValueError(f"Integration target changed concurrently: {path}")
            atomic(path, data)
            applied.append((path, row))
    except BaseException:
        for path, row in reversed(applied):
            if hashlib.sha256(path.read_bytes()).hexdigest() == row["after"]:
                if row["backup"]:
                    atomic(path, (backup / row["backup"]).read_bytes())
                else:
                    path.unlink()
        raise
    return {"changed_files": len(rows), "rollback_receipt": str(receipt)}


def install(home, antigravity=None):
    state_file = home / "msshi-private" / "integrations" / "installed.json"
    previous = read(state_file).get("files", {}) if state_file.is_file() else {}
    sources = {slug: materialize(home, slug) for slug in SOURCE_SPEC}
    plan = {}
    installed = {}
    for role, profile in profiles(home):
        target = profile / "skills"
        chosen = [("caveman", "caveman", sources["caveman"] / "skills" / "caveman")]
        chosen.extend((f"anthropic-{slug}", "anthropic-skills", sources["anthropic-skills"] / "skills" / slug) for slug in DOCS)
        if role in {"kiki-chii", "shikaku"}:
            chosen.extend((f"hf-{slug}", "hyperframes", sources["hyperframes"] / "skills" / slug) for slug in HYPER)
            ui_skill = target / "msshi-ui-ux-pro-max"
            ui = sources["ui-ux-pro-max"]
            text = (ui / ".claude/skills/ui-ux-pro-max/SKILL.md").read_text(encoding="utf-8")
            text = re.sub(r"(?m)^name: ui-ux-pro-max$", "name: msshi-ui-ux-pro-max", text, count=1)
            location = str(ui / "src/ui-ux-pro-max/scripts/search.py")
            text = text.replace("# UI/UX Pro Max - Design Intelligence",
                "# UI/UX Pro Max - Design Intelligence\n\nMSSHI local runtime. Run Python with " + location +
                " for all search commands. Data stays in the pinned source cache. Use only the local search and design-system commands.")
            plan[ui_skill / "SKILL.md"] = text.encode("utf-8")
            plan[ui_skill / "references/quick-reference.md"] = (ui / "src/ui-ux-pro-max/templates/base/quick-reference.md").read_bytes()
            plan[ui_skill / "LICENSE"] = (ui / "LICENSE").read_bytes()
        for name, package, source in chosen:
            if not (source / "SKILL.md").is_file():
                raise ValueError(f"Missing skill entrypoint: {source}")
            dest = target / name
            for file in source.rglob("*"):
                if file.is_file():
                    content = file.read_bytes()
                    if file.name == "SKILL.md" and name.startswith(("anthropic-", "hf-")):
                        content = re.sub(rb"(?m)^name: [^\r\n]+", f"name: {name}".encode(), content, count=1)
                    if file.name == "SKILL.md" and name == "caveman":
                        content = re.sub(rb"(?m)^description:.*(?:\r?\n[ \t]+[^\r\n]*)*", b'description: "Use to compact internal handoffs or structured logs. Preserve natural user-facing persona and complete evidence."', content, count=1)
                        content += (
                            "\n\n## MSSHI activation scope\n\n"
                            "Apply concise formatting only to internal handoffs, log summaries, and structured data. "
                            "Keep the user-facing supportive persona, full meaning, evidence, code, quotations, names, "
                            "paths, commands, and academic citations intact. Do not change providers or models. "
                            "Do not install Caveman proxy routing or write over source memory.\n"
                        ).encode("utf-8")
                    path = dest / file.relative_to(source)
                    if path.is_file() and path.read_bytes() != content and previous.get(str(path)) != hashlib.sha256(path.read_bytes()).hexdigest():
                        raise ValueError(f"Preserved customized integration: {path}")
                    plan[path] = content
            for license_name in ("LICENSE", "LICENSE.txt", "LICENSE.md", "NOTICE"):
                license_path = sources[package] / license_name
                if license_path.is_file():
                    plan[dest / license_name] = license_path.read_bytes()
        installed[role] = [name for name, _, _ in chosen] + (["msshi-ui-ux-pro-max"] if role in {"kiki-chii", "shikaku"} else [])
    if antigravity:
        coder = next((p for role, p in profiles(home) if role == "shikaku"), None)
        if coder:
            root = coder / "skills"
            for path, data in list(plan.items()):
                if path.is_relative_to(root):
                    dest = antigravity / path.relative_to(root)
                    if dest.is_file() and dest.read_bytes() != data and previous.get(str(dest)) != hashlib.sha256(dest.read_bytes()).hexdigest():
                        raise ValueError(f"Preserved customized Antigravity skill: {dest}")
                    plan[dest] = data
    settings = {role: {"speed": c[0], "calm_speed": c[1], "tired_speed": c[2],
                       "incident_speed": 0.95 if role == "shikaku" else c[0],
                       "voice": "instruct:" + c[3]} for role, c in VOICES.items()}
    policy = home / "msshi-private/integrations/voice-personas.json"
    if not policy.exists():
        plan[policy] = encode(settings)
    hashes = {str(path): hashlib.sha256(data).hexdigest() for path, data in plan.items()}
    plan[state_file] = encode({"sources": {s: str(p) for s, p in sources.items()},
                              "roles": installed, "files": hashes, "auto_start": False})
    result = apply_files(home, plan, "v3 curated upstream skills")
    return {**result, "roles": installed, "sources": len(sources), "models_downloaded": False,
            "caveman_proxy_enabled": False, "caveman_model_routing": False}


def dream(home):
    source = materialize(home, "hermes-dreaming")
    script = source / "skills/dreaming/scripts/dream.py"
    root = home / "msshi-private/integrations/dream"
    root.mkdir(parents=True, exist_ok=True)
    rows = []
    for role, profile in profiles(home):
        cfg = root / f"{role}.json"
        settings = {
            "timezone": "Asia/Jakarta", "trusted_chat_ids": [], "trust_private_chats": True,
            "agent_names": list(VOICES), "judge": {"mode": "off"},
            "corroboration": {"memory_mb": 64}, "gates": {"new_facts_cap": 12, "publish_cap": 12},
            "cron": {"expected_roles": []}, "chat_stores": {"read": False, "promote_from": []},
        }
        atomic(cfg, encode(settings))
        report = root / f"{role}-latest.json"
        env = dict(os.environ, HERMES_HOME=str(profile), PYTHONDONTWRITEBYTECODE="1")
        for key in ("OPENAI_API_KEY", "OPENROUTER_API_KEY", "ANTHROPIC_API_KEY"):
            env.pop(key, None)
        result = subprocess.run([sys.executable, "-B", str(script), "--hermes-home", str(profile),
                                 "--config", str(cfg), "--out", str(report),
                                 "--diary", str(profile / "memories/DREAMS.md")],
                                env=env, capture_output=True, text=True, errors="replace", timeout=180)
        row = {"role": role, "exit": result.returncode, "report": str(report),
               "agent_woken": False, "llm_calls": 0, "memory_promotion": "requires user review"}
        if result.returncode:
            row["error"] = result.stderr[-500:]
        rows.append(row)
    summary = {"mode": "deterministic proposals only", "upstream_commit": SOURCE_SPEC["hermes-dreaming"][1],
               "llm_calls": 0, "memory_budget_mb": 64, "profiles": rows}
    atomic(root / "last-run.json", encode(summary))
    return summary


def register_dream(home):
    if os.name != "nt":
        raise ValueError("Automatic task registration requires Windows Task Scheduler.")
    zone = subprocess.run(["tzutil", "/g"], capture_output=True, text=True, check=True).stdout.strip()
    if zone != "SE Asia Standard Time":
        raise ValueError("Task needs WIB local zone. Current zone: " + zone)
    task = "MSSHI_v3_Nightly_Dream_Consolidation"
    action = f'"{sys.executable}" -B "{Path(__file__).resolve()}" dream --home "{home}" --run-now'
    result = subprocess.run(["schtasks", "/Create", "/TN", task, "/SC", "DAILY", "/ST", "03:00",
                             "/TR", action, "/F"], capture_output=True, text=True, errors="replace")
    if result.returncode:
        raise ValueError("Task registration failed: " + result.stderr[-500:])
    return {"task": task, "time": "03:00 Asia/Jakarta", "agent_woken": False, "llm_calls": 0}


def voice_environment(home):
    runtime = home / "msshi-private/omnivoice-runtime"
    env = dict(os.environ, TEMP=str(runtime / "temp"), TMP=str(runtime / "temp"),
               PIP_CACHE_DIR=str(runtime / "pip-cache"), HF_HOME=str(runtime / "hf-cache"),
               HF_HUB_DISABLE_XET="1", HF_HUB_DISABLE_SYMLINKS_WARNING="1")
    for name in ("temp", "pip-cache", "hf-cache"):
        (runtime / name).mkdir(parents=True, exist_ok=True)
    return runtime, env


def voice_install_runtime(home):
    runtime, env = voice_environment(home)
    python = runtime / ("venv/Scripts/python.exe" if os.name == "nt" else "venv/bin/python")
    if not python.is_file():
        subprocess.run([sys.executable, "-m", "venv", str(runtime / "venv")], env=env, check=True)
    commands = (
        [str(python), "-m", "pip", "install", "torch==2.8.0+cpu", "torchaudio==2.8.0+cpu",
         "--index-url", "https://download.pytorch.org/whl/cpu"],
        [str(python), "-m", "pip", "install", "omnivoice==0.2.1", "PyYAML>=6.0"],
        [str(python), "-m", "pip", "install", "--no-deps", str(materialize(home, "hermes-omnivoice"))],
    )
    for command in commands:
        subprocess.run(command, env=env, check=True)
    download_code = (
        "from huggingface_hub import snapshot_download; "
        "snapshot_download('k2-fsa/OmniVoice',revision='c5fdb5ccb189668d56333f77ba2629f4cd7535f4',"
        f"local_dir={str(runtime / 'model')!r},max_workers=2)"
    )
    subprocess.run([str(python), "-c", download_code], env=env, check=True)
    worker = ROOT / "scripts/omnivoice_prosody_router.py"
    atomic(runtime / "omnivoice_prosody_router.py", worker.read_bytes())
    samples = runtime / "samples"
    samples.mkdir(exist_ok=True)
    text = samples / "smoke.txt"
    atomic(text, "Halo, Zidan. Kita mulai pelan-pelan.".encode("utf-8"))
    output = samples / "smoke-yukino.wav"
    command = [str(python), "-B", "-X", "utf8", str(runtime / worker.name), "--home", str(home),
               "--role", "yukino", "--text-file", str(text), "--output", str(output), "--format", "wav"]
    subprocess.run(command, env=env, check=True, timeout=600)
    import wave
    with wave.open(str(output)) as audio:
        if audio.getnframes() <= 0 or audio.getframerate() != 24000:
            raise ValueError("OmniVoice produced invalid calibration audio")
        duration = audio.getnframes() / audio.getframerate()
    proof = {"model_revision": "c5fdb5ccb189668d56333f77ba2629f4cd7535f4",
             "sample": str(output), "duration_seconds": duration,
             "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
             "local_only": True, "model_license": "CC-BY-NC", "process_unload": True,
             "verified_at": datetime.now(timezone.utc).isoformat()}
    atomic(runtime / "verified.json", encode(proof))
    return voice_status(home)


def voice_enable(home):
    status = voice_status(home)
    if not status["synthesis_verified"]:
        raise ValueError("Run msshi voice --install-runtime and pass the local synthesis test first.")
    import yaml
    from omnivoice_prosody_router import parameters
    runtime, env = voice_environment(home)
    python = runtime / ("venv/Scripts/python.exe" if os.name == "nt" else "venv/bin/python")
    worker = runtime / "omnivoice_prosody_router.py"
    plan = {worker: (ROOT / "scripts/omnivoice_prosody_router.py").read_bytes()}
    for role, profile in profiles(home):
        config = profile / "config.yaml"
        prior = config.read_bytes()
        text = prior.decode("utf-8-sig")
        cfg = yaml.safe_load(text) or {}
        tts = dict(cfg.get("tts") or {})
        providers = dict(tts.get("providers") or {})
        command = (
            f'"{python}" -B -X utf8 "{worker}" --home "{home}" --role {role} '
            "--text-file {input_path} --output {output_path} --format {format}"
        )
        providers["omnivoice"] = {"type": "command", "command": command, "timeout": 600,
                                  "max_text_length": 1500, "format": "wav", "voice_compatible": True}
        tts.update(provider="omnivoice", providers=providers,
                   omnivoice={"model": str(runtime / "model"), "voice": parameters(role, "normal")["voice"], "persona_style": VOICES[role][3],
                              "speed": VOICES[role][0], "device": "cpu", "dtype": "float32",
                              "load_asr": False, "auto_start": False, "unload": "process exit"})
        replacement = yaml.safe_dump({"tts": tts}, sort_keys=False, allow_unicode=True)
        block = re.search(r"(?m)^tts:[^\r\n]*(?:\r?\n|$)", text)
        if block:
            following = re.search(r"(?m)^[A-Za-z_][A-Za-z0-9_-]*:", text[block.end():])
            stop = block.end() + following.start() if following else len(text)
            updated = text[:block.start()] + replacement + "\n" + text[stop:]
        else:
            updated = text.rstrip() + "\n\n" + replacement
        revised = yaml.safe_load(updated)
        if {k: v for k, v in revised.items() if k != "tts"} != {k: v for k, v in cfg.items() if k != "tts"}:
            raise ValueError("TTS update attempted to change another configuration section")
        encoding = "utf-8-sig" if prior.startswith(b"\xef\xbb\xbf") else "utf-8"
        newline = "\r\n" if b"\r\n" in prior else "\n"
        plan[config] = updated.replace("\r\n", "\n").replace("\n", newline).encode(encoding)
        skill = profile / "skills/msshi-voice-persona/SKILL.md"
        instructions = f"""---
name: msshi-voice-persona
description: "Use when the user requests spoken audio or a calmer/faster speaking preference."
---
# Local voice for {role}

Use the user's natural persona and factual wording. Before speech, select normal, calm,
tired, or incident only from the user's expressed preference and the current task.
This choice does not diagnose a medical condition. Set the preference through
msshi voice --home "{home}" --role {role} --state calm when requested.
The native text_to_speech tool uses the installed command provider. It normalizes Markdown
and code and invokes the local CPU model in a separate process that unloads on completion.
Keep code, quotes, evidence, names, paths and full meaning unchanged in the visible answer.
Use Caveman only for compact internal handoffs or large structured data, while preserving
the supportive conversation voice. No audio reference was found, so voice design is used.
"""
        if not skill.exists() or skill.read_text(encoding="utf-8") == instructions:
            plan[skill] = instructions.encode("utf-8")
        else:
            raise ValueError(f"Preserving customized voice skill: {skill}")
    return {**apply_files(home, plan, "activate verified local voice"), "provider": "omnivoice",
            "profiles": len(list(profiles(home))), "main_model_changed": False}


def voice_status(home):
    runtime = home / "msshi-private/omnivoice-runtime"
    python = runtime / ("venv/Scripts/python.exe" if os.name == "nt" else "venv/bin/python")
    model = runtime / "model"
    ready = (runtime / "verified.json").is_file()
    return {"python": str(python), "runtime_present": python.is_file(), "model_path": str(model),
            "model_present": (model / "model.safetensors").is_file(),
            "synthesis_verified": ready, "auto_start": False,
            "unload": "process exits after each synthesis", "provider": "omnivoice" if ready else "pending"}


def kat(home, mode):
    target = home / "msshi-private/integrations/kat.json"
    if mode == "status":
        return read(target) if target.is_file() else {"mode": "skip", "enabled": False}
    value = {"mode": mode, "enabled": False, "role": "shikaku", "trigger": "coding task only",
             "model": "Kwaipilot/KAT-Coder-V2.5-Dev", "auto_unload_seconds": 60,
             "base_provider_or_model_mutation": False, "downloaded": False,
             "status": "not configured" if mode == "skip" else "requires verified endpoint or local quantized model"}
    if mode in {"light", "ideal"}:
        value["quantization"] = "IQ2_XS/IQ3_XXS" if mode == "light" else "Q4_K_M"
        value["hardware_check"] = "Check actual model size and free RAM. Nominal RAM does not prove fit."
    atomic(target, encode(value))
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("install", "dream", "voice", "kat"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--home", type=Path, default=Path(os.getenv("HERMES_HOME", str(Path.home() / ".hermes"))))
        if name == "install":
            cmd.add_argument("--antigravity", type=Path)
        elif name == "dream":
            flags = cmd.add_mutually_exclusive_group(required=True)
            flags.add_argument("--run-now", action="store_true")
            flags.add_argument("--register", action="store_true")
        elif name == "voice":
            cmd.add_argument("--status", action="store_true")
            cmd.add_argument("--enable", action="store_true")
            cmd.add_argument("--install-runtime", action="store_true")
            cmd.add_argument("--role", choices=PROFILES)
            cmd.add_argument("--state", choices=("normal", "calm", "tired", "incident"))
        else:
            cmd.add_argument("--mode", choices=("skip", "cloud", "light", "ideal", "status"), default="status")
    args = parser.parse_args(argv)
    home = checked(args.home)
    try:
        if args.command == "install":
            result = install(home, checked(args.antigravity) if args.antigravity else None)
        elif args.command == "dream":
            result = dream(home) if args.run_now else register_dream(home)
        elif args.command == "voice":
            if args.install_runtime:
                result = voice_install_runtime(home)
            elif args.enable:
                result = voice_enable(home)
            elif args.state:
                if not args.role:
                    raise ValueError("A voice state requires --role.")
                path = home / "msshi-private/integrations/voice-state" / (args.role + ".json")
                result = {"role": args.role, "state": args.state, "source": "explicit task preference"}
                atomic(path, encode(result))
            else:
                result = voice_status(home)
        else:
            result = kat(home, args.mode)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return int(args.command == "dream" and args.run_now and any(p["exit"] for p in result["profiles"]))
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        parser.exit(1, f"msshi integrations: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
