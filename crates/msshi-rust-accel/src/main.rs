use regex::Regex;
use serde::Serialize;
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, HashSet};
use std::env;
use std::fs::{self, File};
use std::io::{Read, stdin};
use std::path::{Path, PathBuf};
use std::process;
use std::time::UNIX_EPOCH;
use walkdir::WalkDir;

const FRONTMATTER_LIMIT_BYTES: usize = 4096;

#[cfg(windows)]
fn is_reparse_or_symlink(meta: &fs::Metadata) -> bool {
    use std::os::windows::fs::MetadataExt;
    const FILE_ATTRIBUTE_REPARSE_POINT: u32 = 0x0400;
    meta.file_type().is_symlink() || (meta.file_attributes() & FILE_ATTRIBUTE_REPARSE_POINT) != 0
}

#[cfg(not(windows))]
fn is_reparse_or_symlink(meta: &fs::Metadata) -> bool {
    meta.file_type().is_symlink()
}

fn check_no_links_in_ancestors(path: &Path) -> Result<(), String> {
    let mut cur = PathBuf::new();
    for comp in path.components() {
        cur.push(comp);
        if let Ok(meta) = fs::symlink_metadata(&cur) {
            if is_reparse_or_symlink(&meta) {
                return Err(format!("Symlink or reparse point rejected: {}", cur.display()));
            }
        }
    }
    Ok(())
}

fn sha256_file(path: &Path) -> Result<String, String> {
    let mut file = File::open(path).map_err(|e| format!("open {}: {}", path.display(), e))?;
    let mut hasher = Sha256::new();
    let mut buf = vec![0u8; 256 * 1024];
    loop {
        let n = file
            .read(&mut buf)
            .map_err(|e| format!("read {}: {}", path.display(), e))?;
        if n == 0 {
            break;
        }
        hasher.update(&buf[..n]);
    }
    Ok(format!("{:x}", hasher.finalize()))
}

// ── 1. Hot-Path: Secret & Privacy Guardrail Scanner ─────────────────────────

#[derive(Serialize)]
struct SecretFinding {
    #[serde(rename = "type")]
    kind: String,
    file: String,
    detail: String,
}

#[derive(Serialize)]
struct SecretScanReport {
    status: String,
    repo_root: String,
    files_scanned: usize,
    findings_count: usize,
    findings: Vec<SecretFinding>,
    engine: &'static str,
}

fn cmd_secret_scan(root: &Path) -> Result<String, String> {
    let excluded: HashSet<&str> = [
        ".git",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        ".venv",
        "venv",
        "target",
    ]
    .into_iter()
    .collect();

    let text_exts: HashSet<&str> = [
        "json", "md", "py", "ps1", "sh", "svg", "cmd", "bat", "txt", "yml", "yaml", "ipynb", "rs",
        "toml",
    ]
    .into_iter()
    .collect();

    let sensitive_re = Regex::new(
        r"(?i)(?:^|/)(?:\.env(?:\.[^/]+)?|[^/]+\.(?:pem|key|p12)|auth\.json|credentials\.json)$",
    )
    .unwrap();
    let secret_re = Regex::new(
        r"(?:sk-[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AIza[A-Za-z0-9_-]{35}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)",
    )
    .unwrap();
    let private_re = Regex::new(
        r"(?i)(?:[A-Z]:\\Zidan\\|https?://(?:notebooklm|notebook)\.google\.com/notebook/)",
    )
    .unwrap();

    let mut findings = Vec::new();
    let mut files_scanned = 0usize;

    let walker = WalkDir::new(root).follow_links(false).into_iter().filter_entry(|e| {
        if e.depth() == 0 {
            return true;
        }
        let name = e.file_name().to_string_lossy();
        if e.file_type().is_dir() {
            return !excluded.contains(name.as_ref()) && !name.starts_with(".msshi-check-");
        }
        true
    });

    for entry in walker {
        let entry = entry.map_err(|e| e.to_string())?;
        if !entry.file_type().is_file() {
            continue;
        }
        let path = entry.path();
        let rel = path
            .strip_prefix(root)
            .unwrap_or(path)
            .to_string_lossy()
            .replace('\\', "/");
        let file_name = entry.file_name().to_string_lossy();

        if file_name != ".env.example" && sensitive_re.is_match(&rel) {
            findings.push(SecretFinding {
                kind: "sensitive_file".to_string(),
                file: rel.clone(),
                detail: "Blocked secret filename".to_string(),
            });
        }

        let ext = path
            .extension()
            .map(|s| s.to_string_lossy().to_lowercase())
            .unwrap_or_default();
        if !text_exts.contains(ext.as_str()) {
            continue;
        }
        files_scanned += 1;

        let raw = fs::read(path).map_err(|e| format!("read {}: {}", path.display(), e))?;
        let text = String::from_utf8_lossy(&raw);
        let stripped = text.strip_prefix('\u{feff}').unwrap_or(&text);

        if let Some(m) = secret_re.find(stripped) {
            let start = m.start();
            let prev_ok = if start == 0 {
                true
            } else {
                let prev = stripped[..start].chars().next_back().unwrap_or(' ');
                !(prev.is_ascii_alphanumeric() || prev == '_' || prev == '-')
            };
            if prev_ok {
                let preview: String = m.as_str().chars().take(12).collect();
                findings.push(SecretFinding {
                    kind: "secret_token".to_string(),
                    file: rel.clone(),
                    detail: format!("{}...", preview),
                });
            }
        }
        if let Some(m) = private_re.find(stripped) {
            findings.push(SecretFinding {
                kind: "private_reference".to_string(),
                file: rel,
                detail: m.as_str().to_string(),
            });
        }
    }

    let report = SecretScanReport {
        status: if findings.is_empty() {
            "PASS".to_string()
        } else {
            "FAIL".to_string()
        },
        repo_root: root.to_string_lossy().to_string(),
        files_scanned,
        findings_count: findings.len(),
        findings,
        engine: "rust",
    };
    serde_json::to_string(&report).map_err(|e| e.to_string())
}

// ── 2. Hot-Path: Deterministic SHA-256 Tree Inventory ───────────────────────

fn cmd_inventory(dir: &Path) -> Result<String, String> {
    check_no_links_in_ancestors(dir)?;
    let meta = fs::symlink_metadata(dir).map_err(|e| format!("{}: {}", dir.display(), e))?;
    if is_reparse_or_symlink(&meta) || !meta.is_dir() {
        return Err(format!("Invalid directory: {}", dir.display()));
    }

    let mut files = BTreeMap::new();
    for entry in WalkDir::new(dir).follow_links(false) {
        let entry = entry.map_err(|e| e.to_string())?;
        let p = entry.path();
        if p == dir {
            continue;
        }
        let emeta = fs::symlink_metadata(p).map_err(|e| e.to_string())?;
        if is_reparse_or_symlink(&emeta) {
            return Err(format!("Symlink or junction rejected: {}", p.display()));
        }
        let rel = p
            .strip_prefix(dir)
            .map_err(|e| e.to_string())?
            .to_string_lossy()
            .replace('\\', "/");
        if rel
            .split('/')
            .any(|part| part.eq_ignore_ascii_case("__pycache__"))
        {
            continue;
        }
        if let Some(ext) = p.extension().map(|e| e.to_string_lossy().to_lowercase()) {
            if ext == "pyc" || ext == "pyo" {
                continue;
            }
        }
        if emeta.is_file() {
            files.insert(rel, sha256_file(p)?);
        } else if !emeta.is_dir() {
            return Err(format!("Unsupported entry: {}", p.display()));
        }
    }
    serde_json::to_string(&files).map_err(|e| e.to_string())
}

// ── 3. Hot-Path: SKILL.md 4KB Frontmatter Scanner ───────────────────────────

#[derive(Serialize)]
struct ScannedSkillEntry {
    slug: String,
    name: String,
    description: String,
    rel_path: String,
    mtime_ns: u128,
    size: u64,
    head_sha256: String,
    has_references: bool,
    has_scripts: bool,
    body_loaded: bool,
}

#[derive(Serialize)]
struct SkillScanOutput {
    entries: BTreeMap<String, ScannedSkillEntry>,
    excluded_skipped: Vec<String>,
    hygiene_warnings: Vec<String>,
    engine: &'static str,
}

fn parse_frontmatter(head: &[u8], fallback_name: &str) -> (String, String, String) {
    let mut hasher = Sha256::new();
    hasher.update(head);
    let digest = format!("{:x}", hasher.finalize());

    let raw = String::from_utf8_lossy(head);
    let text = raw.strip_prefix('\u{feff}').unwrap_or(&raw);
    let mut name = fallback_name.to_string();
    let mut desc = String::new();

    if text.starts_with("---") {
        let name_re = Regex::new(r#"(?m)^name:[ \t]*['"]?([^'"\r\n]+?)['"]?[ \t]*$"#).unwrap();
        let desc_re = Regex::new(r#"(?m)^description:[ \t]*['"]?(.+?)['"]?[ \t]*$"#).unwrap();
        let mut block_lines = Vec::new();
        for line in text.lines().skip(1) {
            if line.trim() == "---" {
                break;
            }
            block_lines.push(line);
        }
        let block = block_lines.join("\n");
        if let Some(cap) = name_re.captures(&block) {
            let v = cap[1].trim();
            if !v.is_empty() {
                name = v.to_string();
            }
        }
        if let Some(cap) = desc_re.captures(&block) {
            let v = cap[1].trim();
            desc = v.chars().take(240).collect();
        }
    }
    (name, desc, digest)
}

fn cmd_skill_scan(skills_dir: &Path, excluded_csv: &str) -> Result<String, String> {
    check_no_links_in_ancestors(skills_dir)?;
    let excluded: HashSet<String> = excluded_csv
        .split(',')
        .map(|s| s.trim().to_lowercase())
        .filter(|s| !s.is_empty())
        .collect();

    let mut entries = BTreeMap::new();
    let mut excluded_skipped = Vec::new();
    let mut hygiene_warnings = Vec::new();

    if skills_dir.is_dir() {
        let mut children: Vec<_> = fs::read_dir(skills_dir)
            .map_err(|e| e.to_string())?
            .filter_map(|r| r.ok())
            .collect();
        children.sort_by_key(|e| e.file_name().to_string_lossy().to_lowercase());

        for child in children {
            let fname = child.file_name().to_string_lossy().to_string();
            let lower = fname.to_lowercase();
            let cpath = child.path();
            let Ok(cmeta) = fs::symlink_metadata(&cpath) else {
                continue;
            };
            if fname.starts_with(".msshi-backup-")
                || fname.starts_with(".msshi-stage-")
                || is_reparse_or_symlink(&cmeta)
            {
                excluded_skipped.push(fname);
                continue;
            }
            if excluded.contains(&lower) {
                hygiene_warnings.push(format!(
                    "Excluded heavy directory '{}' found inside skills root ({}); move outside skills.",
                    fname,
                    skills_dir.display()
                ));
                excluded_skipped.push(fname);
                continue;
            }
            if !cmeta.is_dir() {
                continue;
            }
            let skill_md = cpath.join("SKILL.md");
            let Ok(smeta) = fs::symlink_metadata(&skill_md) else {
                continue;
            };
            if is_reparse_or_symlink(&smeta) || !smeta.is_file() {
                continue;
            }
            let mut f = match File::open(&skill_md) {
                Ok(f) => f,
                Err(_) => continue,
            };
            let mut head = vec![0u8; FRONTMATTER_LIMIT_BYTES];
            let n = f.read(&mut head).unwrap_or(0);
            head.truncate(n);
            let (parsed_name, parsed_desc, digest) = parse_frontmatter(&head, &fname);
            let mtime_ns = smeta
                .modified()
                .ok()
                .and_then(|t| t.duration_since(UNIX_EPOCH).ok())
                .map(|d| d.as_nanos())
                .unwrap_or(0);

            let mut sub_names = HashSet::new();
            if let Ok(sub_rd) = fs::read_dir(&cpath) {
                for sub_e in sub_rd.flatten() {
                    if let Ok(sub_m) = fs::symlink_metadata(sub_e.path()) {
                        if sub_m.is_dir() && !is_reparse_or_symlink(&sub_m) {
                            sub_names.insert(sub_e.file_name().to_string_lossy().to_lowercase());
                        }
                    }
                }
            }
            let mut nested_heavy: Vec<String> =
                sub_names.intersection(&excluded).cloned().collect();
            nested_heavy.sort();
            for heavy in nested_heavy {
                excluded_skipped.push(format!("{}/{}", fname, heavy));
                hygiene_warnings.push(format!(
                    "Excluded heavy directory '{}/{}' inside skill '{}'; skipped by lazy indexer.",
                    fname, heavy, fname
                ));
            }

            entries.insert(
                fname.clone(),
                ScannedSkillEntry {
                    slug: fname.clone(),
                    name: parsed_name,
                    description: parsed_desc,
                    rel_path: format!("{}/SKILL.md", fname),
                    mtime_ns,
                    size: smeta.len(),
                    head_sha256: digest,
                    has_references: sub_names.contains("references"),
                    has_scripts: sub_names.contains("scripts"),
                    body_loaded: false,
                },
            );
        }
    }

    serde_json::to_string(&SkillScanOutput {
        entries,
        excluded_skipped,
        hygiene_warnings,
        engine: "rust",
    })
    .map_err(|e| e.to_string())
}

// ── 4. Hot-Path: Citation & Code-Preserving Council Dossier Compactor ───────

fn cmd_compact_text(max_chars: usize) -> Result<String, String> {
    let mut raw = String::new();
    stdin()
        .read_to_string(&mut raw)
        .map_err(|e| e.to_string())?;
    let cleaned = raw.trim();
    if cleaned.chars().count() <= max_chars {
        return Ok(cleaned.to_string());
    }

    let fence_re = Regex::new(r"(?m)(```[\s\S]*?```)").unwrap();
    let ws_re = Regex::new(r"[ \t]+").unwrap();
    let keep_re = Regex::new(
        r"(?i)(?:https?://|doi[:\s]|10\.\d{4,9}/|\bdoc#p\d+|`[^`]+`|\[[^\]]+\]|:\d+\b|\b(?:approv|budget|constraint|limit|risk|citation|source|must|never)\w*)",
    )
    .unwrap();

    let mut kept_blocks = Vec::new();
    let mut prose_lines = Vec::new();
    let mut last_end = 0usize;

    for m in fence_re.find_iter(cleaned) {
        let before = &cleaned[last_end..m.start()];
        for raw_line in before.lines() {
            let collapsed = ws_re.replace_all(raw_line, " ").trim().to_string();
            if !collapsed.is_empty() {
                prose_lines.push(collapsed);
            }
        }
        kept_blocks.push(m.as_str().to_string());
        last_end = m.end();
    }
    for raw_line in cleaned[last_end..].lines() {
        let collapsed = ws_re.replace_all(raw_line, " ").trim().to_string();
        if !collapsed.is_empty() {
            prose_lines.push(collapsed);
        }
    }

    let mut essential = Vec::new();
    let mut filler = Vec::new();
    for (idx, line) in prose_lines.iter().enumerate() {
        if idx < 3 || keep_re.is_match(line) {
            essential.push(line.clone());
        } else {
            filler.push(line.clone());
        }
    }

    let code_tail = kept_blocks.join("\n\n");
    let code_chars = code_tail.chars().count();
    let reserve = code_chars + if code_tail.is_empty() { 0 } else { 4 };
    let prose_budget = std::cmp::max(200, max_chars.saturating_sub(reserve));

    let mut out_lines = Vec::new();
    let mut used = 0usize;
    for line in &essential {
        let need = line.chars().count() + 1;
        if used + need <= prose_budget || keep_re.is_match(line) {
            out_lines.push(line.clone());
            used += need;
        }
    }
    let mut omitted = filler.len();
    if !filler.is_empty() && used + 40 < prose_budget {
        for line in &filler {
            let need = line.chars().count() + 1;
            if used + need <= prose_budget.saturating_sub(28) {
                out_lines.push(line.clone());
                used += need;
                omitted -= 1;
            } else {
                break;
            }
        }
    }
    if omitted > 0 {
        out_lines.push(format!("[... {} non-citation prose lines compacted ...]", omitted));
    }
    let prose_text = out_lines.join("\n");
    if !code_tail.is_empty() {
        if prose_text.is_empty() {
            Ok(code_tail)
        } else {
            Ok(format!("{}\n\n{}", prose_text, code_tail))
        }
    } else {
        Ok(prose_text)
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: msshi-accel <secret-scan|inventory|skill-scan|compact-text|version> [options]");
        process::exit(2);
    }
    let sub = args[1].as_str();
    let result = match sub {
        "version" | "--version" => Ok(r#"{"name":"msshi-rust-accel","version":"3.2.1"}"#.to_string()),
        "secret-scan" => {
            let root = args.get(2).map(PathBuf::from).unwrap_or_else(|| PathBuf::from("."));
            cmd_secret_scan(&root)
        }
        "inventory" => {
            let Some(dir) = args.get(2) else {
                eprintln!("Missing <dir>");
                process::exit(2);
            };
            cmd_inventory(Path::new(dir))
        }
        "skill-scan" => {
            let Some(dir) = args.get(2) else {
                eprintln!("Missing <skills_dir>");
                process::exit(2);
            };
            let excluded = args.get(3).map(|s| s.as_str()).unwrap_or("");
            cmd_skill_scan(Path::new(dir), excluded)
        }
        "compact-text" => {
            let max_chars = args
                .get(2)
                .and_then(|v| v.parse::<usize>().ok())
                .unwrap_or(4000);
            cmd_compact_text(max_chars)
        }
        _ => Err(format!("Unknown subcommand: {}", sub)),
    };

    match result {
        Ok(out) => {
            println!("{}", out);
        }
        Err(err) => {
            eprintln!("{}", err);
            process::exit(1);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn frontmatter_extracts_name_and_description() {
        let sample = b"---\nname: cindy-grand-plan\ndescription: Contextual big-plan review\n---\n# Title\n";
        let (name, desc, sha) = parse_frontmatter(sample, "fallback");
        assert_eq!(name, "cindy-grand-plan");
        assert_eq!(desc, "Contextual big-plan review");
        assert_eq!(sha.len(), 64);
    }
}
