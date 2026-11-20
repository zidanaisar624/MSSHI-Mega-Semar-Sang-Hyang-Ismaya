"""Offline test suite for MSSHI v3.1.2 Windows 10 RAM 4 GB (Light Build) roadmap.

Covers:
1. Light Installer bundle size <= 50 MB, determinism, extraction & doctor HEALTHY.
2. Fast Skill Scanner p95 <= 2.0 s (25 iters), targeted cache invalidation, heavy-dir hygiene.
3. Idle process RAM <= 150 MB (WorkingSet & PrivateMemory/Commit).
4. Low-RAM auto-detect (<= 6 GB), Type 1/Type 2 sequential guardrails, heavy-target blocks,
   forge/doctor/desktop --prefer-cli integration, and zero mutation of protected files.
5. Windows 10 C:-only adaptive path resolution (with spaces/apostrophes) and PowerShell 5.1 AST lint.
6. 100% model-agnostic & user-agnostic checks (no model IDs, API keys, tokens, or personal paths).
"""
from __future__ import annotations

from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import install_msshi as installer
import msshi_cli as cli
import msshi_desktop as desktop
import msshi_doctor as doctor
import msshi_forge as forge
import msshi_hermes_profiles as hp
import msshi_light as light
import msshi_manuals as manuals
import msshi_runtime as runtime
import msshi_skill_index as skill_index
import msshi_skripsi_drop as skripsi_drop

BRIDGE_SPEC = importlib.util.spec_from_file_location(
    "test_win10_bridge_runtime",
    ROOT / "skills" / "cli-anything-universal-bridge" / "scripts" / "msshi_bridge_runtime.py",
)
bridge_runtime = importlib.util.module_from_spec(BRIDGE_SPEC)
BRIDGE_SPEC.loader.exec_module(bridge_runtime)

INTERACTION_SPEC = importlib.util.spec_from_file_location(
    "test_win10_interaction_plugin",
    ROOT / "hermes_plugins" / "msshi-interaction" / "__init__.py",
)
interaction_plugin = importlib.util.module_from_spec(INTERACTION_SPEC)
INTERACTION_SPEC.loader.exec_module(interaction_plugin)


class TestLightInstallerBundle(unittest.TestCase):
    def test_light_bundle_under_50mb_deterministic_and_valid(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            zip_a = tmp_path / "light_a.zip"
            zip_b = tmp_path / "light_b.zip"
            manifest_path = tmp_path / "light_a.manifest.json"

            rep_a = light.build_light_bundle(ROOT, zip_a, manifest_out=manifest_path)
            rep_b = light.build_light_bundle(ROOT, zip_b)

            self.assertTrue(rep_a["within_download_budget"])
            self.assertLessEqual(rep_a["zip_mb"], 50.0)
            self.assertEqual(rep_a["zip_sha256"], rep_b["zip_sha256"])
            self.assertTrue(manifest_path.is_file())

            with zipfile.ZipFile(zip_a) as zf:
                names = set(zf.namelist())
                self.assertIn("configs/light_build_active.json", names)
                self.assertIn("configs/academic_presets.json", names)
                self.assertIn("scripts/msshi_light.py", names)
                self.assertIn("scripts/msshi_skill_index.py", names)
                self.assertFalse(any(n.startswith("assets/") for n in names))
                self.assertFalse(any(n.startswith("notebooks/") for n in names))
                self.assertFalse(any(n.startswith("docs/pdf-guides/") for n in names))
                self.assertFalse(any(n.startswith("docs/reports/") for n in names))
                self.assertFalse(any(n.endswith(".pdf") for n in names))
                self.assertFalse(any(n.endswith(".png") for n in names))

                extracted = tmp_path / "extracted-light"
                zf.extractall(extracted)

            # Validate extracted light bundle passes release validation & preserves 67 skills
            _, catalog, _ = cli.validate_release(extracted, "3.1.2")
            self.assertEqual(sum(p is not None for p in catalog.values()), 67)

            # Academic Mahasiswa & Dosen presets remain intact and do not force Obsidian
            presets = json.loads((extracted / "configs" / "academic_presets.json").read_text(encoding="utf-8-sig"))
            self.assertIn("academic-mahasiswa", presets["presets"])
            self.assertIn("academic-dosen", presets["presets"])
            self.assertNotIn("obsidian", json.dumps(presets["presets"]["academic-mahasiswa"]).lower())

            # Light Build skips implicit PDF network downloads
            with patch("urllib.request.urlopen", side_effect=AssertionError("network forbidden")):
                res = manuals.prompt_manual_download(
                    type("Args", (), {"no_pdf": False, "download_pdf": False, "pdf_version": None, "pdf_dest": None})(),
                    source_root=extracted,
                )
            self.assertIsNone(res)

            # Doctor recognizes Light Build cleanly without false SKRIPSI_FILES_MISSING error
            with patch.object(doctor, "ROOT", extracted), \
                 patch.object(doctor, "inject_adaptive_pylibs", return_value=[]), \
                 patch.object(doctor, "has_module", return_value=True), \
                 patch.object(doctor, "_native_health", return_value={"status": "NOT_INSTALLED", "profiles": [], "provider_execution_tested": False}):
                diag = doctor.diagnose()
            self.assertEqual(diag["status"], "HEALTHY")
            self.assertEqual(diag["exit_code"], 0)
            self.assertEqual(diag["build_profile"], "light")
            self.assertTrue(diag["muza_skripsi_ready"])

    def test_stage_release_light_mode_creates_compact_release(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp) / "msshi-home"
            home.mkdir()
            rel_id = cli.stage_release(ROOT, home, build_profile="light")
            staged = home / "releases" / rel_id
            self.assertTrue((staged / "configs" / "light_build_active.json").is_file())
            self.assertFalse((staged / "assets").exists())
            self.assertFalse((staged / "notebooks").exists())
            staged_mb = light._tree_size_bytes(staged) / (1024 * 1024)
            self.assertLessEqual(staged_mb, 50.0)


class TestFastSkillScanner(unittest.TestCase):
    def test_bundled_67_skills_scan_p95_under_2s(self):
        metrics = light.quick_skill_scan_metrics(ROOT / "skills", iterations=25, source=ROOT)
        self.assertEqual(metrics["skill_count"], 67)
        self.assertEqual(metrics["iterations"], 25)
        self.assertEqual(metrics["warm_cache_hits"], 67)
        self.assertLessEqual(metrics["cold_seconds"], 2.0)
        self.assertLessEqual(metrics["warm_p95_seconds"], 2.0)
        self.assertTrue(metrics["within_2s_target"])

    def test_targeted_cache_invalidation_and_heavy_dir_hygiene(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            skills_dir = tmp_path / "skills"
            cache_file = tmp_path / "cache" / "default.json"

            for slug in ("alpha-skill", "beta-skill"):
                d = skills_dir / slug
                d.mkdir(parents=True)
                (d / "SKILL.md").write_text(f"---\nname: {slug}\ndescription: Initial {slug}\n---\n# Body\n", encoding="utf-8")
            (skills_dir / "alpha-skill" / "references").mkdir()
            (skills_dir / "alpha-skill" / "references" / "guide.md").write_text("Reference content", encoding="utf-8")

            # Add excluded heavy dirs that MUST be skipped and reported as hygiene warnings
            (skills_dir / "node_modules" / "pkg").mkdir(parents=True)
            (skills_dir / "node_modules" / "pkg" / "SKILL.md").write_text("---\nname: fake\n---\n", encoding="utf-8")
            (skills_dir / ".git").mkdir()
            (skills_dir / "models").mkdir()
            (skills_dir / "alpha-skill" / "cache").mkdir()

            # 1. Cold scan
            cold = skill_index.scan_profile_skills(skills_dir, cache_file, write_cache=True, source=ROOT)
            self.assertEqual(cold["skill_count"], 2)
            self.assertEqual(cold["cache_misses"], 2)
            self.assertEqual(cold["cache_hits"], 0)
            self.assertFalse(cold["body_loaded"])
            self.assertIn("node_modules", cold["excluded_dirs_skipped"])
            self.assertIn(".git", cold["excluded_dirs_skipped"])
            self.assertIn("models", cold["excluded_dirs_skipped"])
            self.assertIn("alpha-skill/cache", cold["excluded_dirs_skipped"])
            self.assertTrue(cold["hygiene_warnings"])

            # Verify installer.indexed_skills also skips excluded heavy dirs
            occupied = installer.indexed_skills(skills_dir)
            self.assertEqual(occupied, {"alpha-skill", "beta-skill"})

            # 2. Warm scan -> 100% cache hit
            warm = skill_index.scan_profile_skills(skills_dir, cache_file, write_cache=True, source=ROOT)
            self.assertEqual(warm["cache_hits"], 2)
            self.assertEqual(warm["cache_misses"], 0)

            # 3. Edit 1 skill -> targeted invalidation only for edited skill
            alpha_md = skills_dir / "alpha-skill" / "SKILL.md"
            alpha_md.write_text("---\nname: alpha-skill\ndescription: Updated description longer\n---\n# Updated\n", encoding="utf-8")
            edited = skill_index.scan_profile_skills(skills_dir, cache_file, write_cache=True, source=ROOT)
            self.assertEqual(edited["invalidated"], ["alpha-skill"])
            self.assertEqual(edited["cache_hits"], 1)
            self.assertEqual(edited["cache_misses"], 1)

            # 4. Add 1 skill -> only new skill parsed
            gamma_dir = skills_dir / "gamma-skill"
            gamma_dir.mkdir()
            (gamma_dir / "SKILL.md").write_text("---\nname: gamma-skill\ndescription: Added\n---\n", encoding="utf-8")
            added = skill_index.scan_profile_skills(skills_dir, cache_file, write_cache=True, source=ROOT)
            self.assertEqual(added["added"], ["gamma-skill"])
            self.assertEqual(added["cache_hits"], 2)
            self.assertEqual(added["skill_count"], 3)

            # 5. Delete 1 skill -> removed cleanly
            shutil.rmtree(skills_dir / "beta-skill")
            removed = skill_index.scan_profile_skills(skills_dir, cache_file, write_cache=True, source=ROOT)
            self.assertEqual(removed["removed"], ["beta-skill"])
            self.assertEqual(removed["skill_count"], 2)

            # 6. Lazy load single skill & reference; reject traversal
            loaded = skill_index.load_skill_content(skills_dir, "alpha-skill")
            self.assertIn("Updated", loaded["content"])
            loaded_ref = skill_index.load_skill_content(skills_dir, "alpha-skill", reference="guide.md")
            self.assertEqual(loaded_ref["content"], "Reference content")
            with self.assertRaises(ValueError):
                skill_index.load_skill_content(skills_dir, "alpha-skill", reference="../SKILL.md")


class TestIdleMemoryBudget(unittest.TestCase):
    def test_idle_process_memory_under_150mb(self):
        scripts_dir = json.dumps(str(ROOT / "scripts"))
        code = (
            f"import json, sys; sys.path.insert(0, {scripts_dir}); "
            "import msshi_cli, msshi_runtime, msshi_doctor, msshi_forge, msshi_light, msshi_skill_index; "
            "print(json.dumps(msshi_light.process_memory_mb()))"
        )
        proc = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", "-c", code],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True, timeout=30,
        )
        mem = json.loads(proc.stdout)
        self.assertIsNotNone(mem["working_set_mb"])
        self.assertGreater(mem["working_set_mb"], 0.0)
        self.assertLessEqual(mem["working_set_mb"], 150.0)
        if os.name == "nt":
            self.assertIsNotNone(mem["commit_charge_mb"])
            self.assertGreater(mem["commit_charge_mb"], 0.0)
            self.assertLessEqual(mem["commit_charge_mb"], 150.0)


class TestLowRamRuntimeAndInteraction(unittest.TestCase):
    def test_auto_detect_low_ram_threshold_and_atomic_apply_preserves_protected_files(self):
        hw_4gb = light.hardware_profile(physical_gib=4.0, available_gib=1.6, source=ROOT)
        self.assertTrue(hw_4gb["low_ram_detected"])
        self.assertEqual(hw_4gb["recommended_resource_profile"], "light")
        self.assertFalse(hw_4gb["certified_for_win10_4gb"])

        rt_4gb = runtime.hardware(physical_gib=4.0, available_gib=1.6)
        self.assertTrue(rt_4gb["low_ram_detected"])
        self.assertEqual(rt_4gb["recommended_resource_profile"], "light")

        hw_16gb = light.hardware_profile(physical_gib=16.0, available_gib=8.0, source=ROOT)
        self.assertFalse(hw_16gb["low_ram_detected"])
        self.assertEqual(hw_16gb["recommended_resource_profile"], "normal")

        with TemporaryDirectory() as tmp:
            home = Path(tmp) / "hermes"
            home.mkdir()
            protected_payloads = {
                "config.yaml": b"model:\n  provider: user-provider\n  default: user-model\n",
                "SOUL.md": b"# Custom User Soul\n",
                ".env": b"CUSTOM_FLAG=keep\n",
                "auth.json": b'{"token":"keep"}\n',
            }
            for fname, raw in protected_payloads.items():
                (home / fname).write_bytes(raw)

            preview = light.apply_resource_profile(home, "auto", apply=False, physical_gib=4.0, source=ROOT)
            self.assertFalse(preview["applied"])
            self.assertEqual(preview["profile"], "light")
            self.assertFalse((home / light.RESOURCE_PROFILE_REL).exists())

            applied = light.apply_resource_profile(home, "auto", apply=True, physical_gib=4.0, source=ROOT)
            self.assertTrue(applied["applied"])
            self.assertEqual(applied["profile"], "light")
            self.assertFalse(applied["model_provider_mutated"])
            self.assertTrue(Path(applied["receipt"]).is_file())

            # Protected files must remain untouched byte-for-byte
            for fname, raw in protected_payloads.items():
                self.assertEqual((home / fname).read_bytes(), raw)

            loaded = light.read_resource_profile(home)
            self.assertTrue(loaded["configured"])
            self.assertEqual(loaded["profile"], "light")

    def test_interaction_controller_and_runtime_guardrails_in_light_mode(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp) / "hermes"
            home.mkdir()
            light.apply_resource_profile(home, "light", apply=True, physical_gib=4.0, source=ROOT)

            # Type 2 (shikaku): MoA council_round blocked; sequential direct approve permitted
            cfg_t2 = {
                "model": {"provider": "user-prov", "default": "user-main"},
                "moa": {
                    "enabled": True,
                    "reference_models": [{"provider": "user-prov", "model": f"ref-{i}"} for i in range(3)],
                    "aggregator": {"provider": "user-prov", "model": "agg"},
                },
            }
            ctrl_t2 = interaction_plugin.Controller(home, "shikaku", lambda: "sess-1", config=cfg_t2)
            self.assertEqual(ctrl_t2.summary()["resource_profile"], "light")
            self.assertFalse(ctrl_t2.summary()["allow_parallel_moa"])
            job2 = ctrl_t2.begin({"scope": "Fix bug", "initial_plan": "Edit and test", "confirmed": True})["job_id"]
            with self.assertRaisesRegex(ValueError, "LIGHT_MODE_MOA_DISABLED"):
                ctrl_t2.step({"job_id": job2, "action": "council_round"})
            approved2 = ctrl_t2.step({"job_id": job2, "action": "approve", "message": "Sequential plan checked"})
            self.assertEqual(approved2["state"], "READY_EXECUTION")
            self.assertTrue(approved2["light_mode_sequential_only"])
            self.assertFalse(approved2["user_approval_granted"])

            # Type 1 (yukino): parallel advisor delegation blocked; sequential approve permitted
            cfg_t1 = {"delegation": {"provider": "user-prov", "model": "advisor"}}
            ctrl_t1 = interaction_plugin.Controller(home, "yukino", lambda: "sess-2", config=cfg_t1)
            self.assertFalse(ctrl_t1.summary()["allow_parallel_delegation"])
            job1 = ctrl_t1.begin({"scope": "Outline essay", "initial_plan": "Draft sections", "confirmed": True})["job_id"]
            with self.assertRaisesRegex(ValueError, "LIGHT_MODE_PARALLEL_DELEGATION_DISABLED"):
                ctrl_t1.step({"job_id": job1, "action": "advisor"})
            approved1 = ctrl_t1.step({"job_id": job1, "action": "approve", "message": "Sequential plan ready"})
            self.assertEqual(approved1["state"], "READY_EXECUTION")
            self.assertTrue(approved1["light_mode_sequential_only"])

            # Runtime dispatcher blocks heavy targets (blender, obs) in light mode
            for blocked_target in ("blender", "obs"):
                with self.assertRaisesRegex(ValueError, "Low-RAM light resource profile"):
                    runtime.ticket(home, "kiki-chii", blocked_target, "Render scene 3D locally", "direct", 60)

            # Forge surfaces low_ram_mode & refreshes lazy skill index on apply
            (home / "config.yaml").write_text("model:\n  provider: p\n  default: m\n", encoding="utf-8")
            (home / ".env").write_text("# env\n", encoding="utf-8")
            design = {
                "id": "lite-helper",
                "name": "Lite Helper",
                "purpose": "Lightweight study planning",
                "gap": "Dedicated lightweight helper",
                "skills": ["prep-for-meetings"],
                "reviews": {"default": "Reviewed for low-ram host."},
            }
            plan = forge.provision(home, design, apply=False)
            self.assertTrue(plan["low_ram_mode"])
            self.assertTrue(plan["single_active_runtime_advised"])
            with patch.object(forge.trim, "install", return_value={"profiles": [], "binary": {"status": "pending_binary"}, "receipt": None}):
                created = forge.provision(home, design, apply=True)
            self.assertEqual(created["status"], "CREATED_PENDING_USER_MODEL")
            self.assertTrue((home / "msshi-runtime" / "skill-index" / "lite-helper.json").is_file())

            # Desktop --prefer-cli prints fallback JSON without launching Desktop
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = desktop.main(["--hermes-home", str(home), "--prefer-cli"])
            self.assertEqual(rc, 0)
            cli_info = json.loads(buf.getvalue())
            self.assertEqual(cli_info["mode"], "hermes_cli_fallback")
            self.assertFalse(cli_info["desktop_launched"])


class TestWindows10COnlyAndPS51(unittest.TestCase):
    def test_c_only_adaptive_paths_with_spaces_and_apostrophe(self):
        with TemporaryDirectory() as tmp:
            fake_user = Path(tmp) / "User's Profile With Spaces"
            fake_local = fake_user / "AppData" / "Local"
            fake_local.mkdir(parents=True)
            env = {
                **os.environ,
                "USERPROFILE": str(fake_user),
                "HOME": str(fake_user),
                "LOCALAPPDATA": str(fake_local),
                "MSSHI_WINDOWS_D_DRIVE": "",
                "MSSHI_IGNORE_REGISTRY_HERMES_HOME": "1",
            }
            env.pop("HERMES_HOME", None)
            env.pop("HERMES_DESKTOP_USER_DATA_DIR", None)
            env.pop("MSSHI_ARTCRAFT_ROOT", None)
            env.pop("MSSHI_WINDOWS_D_ROOT", None)

            with patch.dict(os.environ, env, clear=True), patch.object(Path, "home", return_value=fake_user):
                resolved_home = hp.resolve_hermes_home(create_adaptive=False, persist_windows_env=False)
                self.assertTrue(resolved_home.is_relative_to(fake_user), f"Leaked outside C:-only user profile: {resolved_home}")
                self.assertIn("User's Profile With Spaces", str(resolved_home))

                art_root = bridge_runtime.artcraft_root()
                self.assertTrue(art_root.is_relative_to(fake_user), f"ArtCraft leaked outside user profile: {art_root}")
                self.assertIn("ArtCraft Apps", str(art_root))

                drop_home = skripsi_drop.adaptive_data_home()
                self.assertTrue(drop_home.is_relative_to(fake_user), f"Skripsi home leaked: {drop_home}")

                drop_out = skripsi_drop.adaptive_output_dir()
                self.assertTrue(drop_out.is_relative_to(fake_user), f"Skripsi output leaked: {drop_out}")
                self.assertTrue(drop_out.is_dir())

                doc_out = doctor.adaptive_skripsi_output()
                self.assertTrue(doc_out.is_relative_to(fake_user), f"Doctor skripsi output leaked: {doc_out}")

            # Pure path-resolution assertion with explicit C:\ user profile (read-only, no writes)
            c_user = Path(r"C:\Users\Student's Laptop")
            c_local = c_user / "AppData" / "Local"
            c_env = {**env, "USERPROFILE": str(c_user), "HOME": str(c_user), "LOCALAPPDATA": str(c_local)}
            with patch.dict(os.environ, c_env, clear=True), patch.object(Path, "home", return_value=c_user):
                self.assertTrue(str(hp.resolve_hermes_home(create_adaptive=False, persist_windows_env=False)).upper().startswith("C:\\"))
                self.assertTrue(str(bridge_runtime.artcraft_root()).upper().startswith("C:\\"))
                self.assertTrue(str(doctor.adaptive_skripsi_output()).upper().startswith("C:\\"))

    @unittest.skipUnless(os.name == "nt" and shutil.which("powershell.exe"), "Windows PowerShell 5.1 check")
    def test_all_ps1_scripts_valid_in_windows_powershell_51(self):
        ps1_files = sorted(
            p for p in ROOT.rglob("*.ps1")
            if not any(part in {".git", "__pycache__"} or part.startswith(".msshi-check-") for part in p.parts)
        )
        self.assertGreaterEqual(len(ps1_files), 3)

        # Run Windows PowerShell 5.1 Parser::ParseFile on every .ps1 script
        check_script = r"""
$ErrorActionPreference = 'Stop'
$files = @($env:MSSHI_PS1_LIST -split '\|')
$bad = @()
foreach ($f in $files) {
    if (-not $f) { continue }
    $tokens = $null
    $errors = $null
    [void][System.Management.Automation.Language.Parser]::ParseFile($f, [ref]$tokens, [ref]$errors)
    if ($errors -and $errors.Count -gt 0) {
        $bad += "$f : " + (($errors | ForEach-Object { $_.Message }) -join '; ')
    }
    $raw = Get-Content -LiteralPath $f -Raw -Encoding UTF8
    if ($raw -match '(\?\?=|\?\?|\s&&\s|\s\|\|\s|-Parallel\b)') {
        $bad += "$f : PowerShell 7+ operator detected"
    }
}
if ($bad.Count -gt 0) {
    $bad | ForEach-Object { Write-Error $_ }
    exit 1
}
Write-Output ("PS51_OK:" + $files.Count)
"""
        env = {**os.environ, "MSSHI_PS1_LIST": "|".join(str(p) for p in ps1_files)}
        with TemporaryDirectory() as tmp:
            checker = Path(tmp) / "check_ps51.ps1"
            checker.write_text(check_script, encoding="utf-8")
            proc = subprocess.run(
                [shutil.which("powershell.exe"), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(checker)],
                env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60,
            )
        self.assertEqual(proc.returncode, 0, msg=f"PowerShell 5.1 check failed: {proc.stderr}\n{proc.stdout}")
        self.assertIn(f"PS51_OK:{len(ps1_files)}", proc.stdout)

    def test_cmd_and_ps1_wrappers_use_utf8_and_py_fallback(self):
        cmd_text = (ROOT / "scripts" / "msshi-update.cmd").read_text(encoding="utf-8-sig")
        self.assertIn("py -3 -B -X utf8", cmd_text)
        self.assertIn("python -B -X utf8", cmd_text)
        biz_ps1 = (ROOT / "scripts" / "installers" / "install_business_sage.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("-B", biz_ps1)
        self.assertIn("utf8", biz_ps1)

    def test_any_custom_directory_and_drive_supported(self):
        from msshi_sources import data_root
        with TemporaryDirectory() as tmp:
            custom_msshi = Path(tmp) / "Custom Drive Area" / "My MSSHI"
            custom_hermes = Path(tmp) / "Custom Drive Area" / "My HermesData"
            custom_skripsi = Path(tmp) / "Custom Drive Area" / "Skripsi Export"
            env = {
                **os.environ,
                "MSSHI_HOME": str(custom_msshi),
                "HERMES_HOME": str(custom_hermes),
                "MSSHI_IGNORE_REGISTRY_HERMES_HOME": "1",
            }
            env.pop("MSSHI_SKRIPSI_OUTPUT", None)
            with patch.dict(os.environ, env, clear=True):
                self.assertEqual(data_root(), custom_msshi)
                self.assertEqual(hp.resolve_hermes_home(create_adaptive=False, persist_windows_env=False), custom_hermes)
                self.assertEqual(skripsi_drop.adaptive_data_home(), custom_hermes)
                self.assertEqual(skripsi_drop.adaptive_output_dir(), custom_hermes / "Skripsi_Output")
                self.assertEqual(doctor.adaptive_skripsi_output(), custom_hermes / "Skripsi_Output")
            with patch.dict(os.environ, {**env, "MSSHI_SKRIPSI_OUTPUT": str(custom_skripsi)}, clear=True):
                self.assertEqual(skripsi_drop.adaptive_output_dir(), custom_skripsi)
                self.assertEqual(doctor.adaptive_skripsi_output(), custom_skripsi)

            # Verify arbitrary drive path (e.g. E:\) resolves cleanly without forcing C: or D:
            e_env = {
                **os.environ,
                "MSSHI_HOME": r"E:\PortableApps\MSSHI",
                "HERMES_HOME": r"E:\PortableApps\HermesData",
                "MSSHI_IGNORE_REGISTRY_HERMES_HOME": "1",
            }
            e_env.pop("MSSHI_SKRIPSI_OUTPUT", None)
            with patch.dict(os.environ, e_env, clear=True):
                self.assertTrue(str(data_root()).upper().startswith("E:\\"))
                self.assertTrue(str(hp.resolve_hermes_home(create_adaptive=False, persist_windows_env=False)).upper().startswith("E:\\"))
                self.assertTrue(str(doctor.adaptive_skripsi_output()).upper().startswith("E:\\"))

    def test_installers_expose_custom_dir_and_mode_hemat_selection(self):
        ps1 = (ROOT / "install.ps1").read_text(encoding="utf-8-sig")
        for token in ("[string]$InstallDir", "[string]$HermesHome", "[string]$TargetDir", "Mode Hemat Windows 10 RAM 4 GB"):
            self.assertIn(token, ps1)
        sh = (ROOT / "install.sh").read_text(encoding="utf-8-sig")
        for token in ("--install-dir", "--hermes-home", "--target-dir", "Mode Hemat RAM 4 GB"):
            self.assertIn(token, sh)
        bat = (ROOT / "MULAI_DI_SINI_PEMULA.bat").read_text(encoding="utf-8-sig")
        self.assertIn("Mode Hemat Windows 10 RAM 4 GB", bat)
        self.assertIn("--low-ram", bat)

        # Verify interactive msshi setup allows choosing option 2 (Mode Hemat) even on >6 GB host
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            msshi_home = root / "custom-msshi"
            hermes_home = root / "custom-hermes"
            msshi_home.mkdir()
            hermes_home.mkdir()
            orig_cfg = b"model:\n  provider: user-p\n  default: user-m\n"
            (hermes_home / "config.yaml").write_bytes(orig_cfg)
            (hermes_home / "SOUL.md").write_text("# Keep User Soul\n", encoding="utf-8")
            env = {
                **os.environ,
                "MSSHI_HOME": str(msshi_home),
                "HERMES_HOME": str(hermes_home),
                "MSSHI_IGNORE_REGISTRY_HERMES_HOME": "1",
                "MSSHI_NO_PDF": "1",
            }
            answers = "\n".join([
                "1",  # mode: solo
                "hermes",
                str(hermes_home / "skills"),
                "y",  # confirm apply
                "1",  # [1/4] Skills: keep bundled
                "5",  # [2/4] Plugin: keep optional
                "4",  # [3/4] Browser: none
                "4",  # [4/4] Bot -> Apps: skip
                "2",  # [5/5] Mode Resource: Mode Hemat Windows 10 RAM 4 GB!
            ]) + "\n"
            with patch.dict(os.environ, env, clear=False), \
                 patch.object(cli, "active_script", return_value=None), \
                 patch.object(cli, "migrate_runtime", return_value=0), \
                 patch.object(cli, "_stage_auto_trim_plugin", return_value={"staged": False, "profiles": [], "llmtrim_binary": False, "fail_open": True}), \
                 patch("sys.stdin", io.StringIO(answers)), \
                 patch("sys.stdout", new_callable=io.StringIO):
                rc = cli.main(["setup", "--no-pdf"])
            self.assertEqual(rc, 0)
            self.assertEqual(light.read_resource_profile(hermes_home)["profile"], "light")
            self.assertEqual((hermes_home / "config.yaml").read_bytes(), orig_cfg)
            self.assertEqual((hermes_home / "SOUL.md").read_text(encoding="utf-8"), "# Keep User Soul\n")


class TestAgnosticAndHygiene(unittest.TestCase):
    def test_public_light_artifacts_are_model_and_user_agnostic(self):
        secret_re = re.compile(
            r"(?<![\w-])(?:sk-[a-zA-Z0-9_-]{24,}|gh[pousr]_[a-zA-Z0-9]{30,}|"
            r"github_pat_[a-zA-Z0-9_]{30,}|AIza[a-zA-Z0-9_-]{35})"
            r"|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
        )
        private_re = re.compile(
            r"[A-Z]:\\" + "Zid" + r"an\\|https?://(?:notebooklm|notebook)\.google\.com/notebook/",
            re.I,
        )
        model_id_re = re.compile(
            r"\b(?:gpt-4o|gpt-5|claude-3|claude-4|gemini-2\.5|gemini-3|deepseek-r1|deepseek-v3|qwen2\.5|llama-3)\b",
            re.I,
        )

        targets = [
            ROOT / "configs" / "light_build_manifest.json",
            ROOT / "configs" / "academic_presets.json",
            ROOT / "docs" / "WIN10_4GB_LIGHT_BUILD.md",
            ROOT / "scripts" / "msshi_light.py",
            ROOT / "scripts" / "msshi_skill_index.py",
        ]
        for path in targets:
            text = path.read_text(encoding="utf-8-sig")
            self.assertIsNone(secret_re.search(text), f"Secret pattern found in {path}")
            self.assertIsNone(private_re.search(text), f"Private path found in {path}")
            self.assertIsNone(model_id_re.search(text), f"Hardcoded AI model ID found in {path}")

    def test_low_disk_space_check_fails_closed(self):
        with TemporaryDirectory() as tmp:
            fake_usage = shutil._ntuple_diskusage(total=100 * 1024 * 1024, used=95 * 1024 * 1024, free=5 * 1024 * 1024)
            with patch.object(shutil, "disk_usage", return_value=fake_usage):
                disk = light.check_disk_space(Path(tmp))
                self.assertFalse(disk["sufficient"])
                with self.assertRaisesRegex(ValueError, "Insufficient free disk space"):
                    runtime.ticket(Path(tmp), "default", "python", "Run small verification task", "direct", 60)


if __name__ == "__main__":
    unittest.main()
