---
name: ast-grep
description: Pencarian kode struktural, linting aturan kustom, dan refaktor codemod lintas berkas berbasis Tree-sitter AST (ast-grep / sg) khusus Coder (Shikaku / Sir. Robot) sebagai pendamping deterministik 0-token untuk open-code-review.
license: MIT
metadata:
  upstream: https://github.com/ast-grep/ast-grep
  upstream_commit: 9065b02439d9b80aaa726ab41fcaa2f3854c66b3
  upstream_license: MIT
  activation: contextual-coding-ast-search-refactor
---

# Pencarian & Refaktor Struktural AST (`ast-grep` — Pendamping Coder)

Gunakan skill ini pada peran **Coder (`shikaku` / `Sir. Robot`)** ketika mencari pola sintaks di banyak berkas, mengganti API lama secara presisi (*codemod*), atau memeriksa anti-pola struktural sebelum menjalankan `open-code-review`.

Berbeda dari pencarian teks/regex biasa yang mudah salah karena komentar, string, atau pemformatan baris baru, **`ast-grep` (`sg`)** mencocokkan pohon sintaks abstrak (**Tree-sitter AST**) secara deterministik dengan **`0` panggilan LLM** pada Python, TypeScript, JavaScript, Rust, Go, C/C++, Java, Kotlin, C#, HTML, dan CSS.

## 1. Kapan Mengutamakan `ast-grep`

- Menemukan seluruh pemanggilan fungsi/kelas dengan bentuk argumen tertentu (mis. `subprocess.run($CMD, shell=True)` atau `eval($ARG)`).
- Melakukan refaktor aman lintas puluhan berkas sekaligus menggunakan *metavariable* (`$VAR`, `$$$ARGS`) tanpa merusak komentar atau string literal.
- Menulis aturan lint YAML ringan khusus proyek untuk mendeteksi bug berulang secara instan sebelum tahap diff review `open-code-review`.

## 2. Pola Perintah CLI (`sg` / `ast-grep`)

Periksa ketersediaan binary lokal terlebih dahulu (`sg --version` atau `ast-grep --version`; dipasang terpisah oleh pengguna via `npm i -g @ast-grep/cli`, `pip install ast-grep-cli`, atau `cargo install ast-grep`):

```text
# 1. Cari pola AST secara read-only (0 perubahan file)
sg run -l python -p "subprocess.run($$$ARGS, shell=True)" .
sg run -l ts -p "console.log($$$ARGS)" src/

# 2. Pratinjau codemod (tanpa menulis perubahan; tinjau diff dulu!)
sg run -l python -p "os.path.join($A, $B)" -r "Path($A) / $B" scripts/

# 3. Terapkan perubahan hanya setelah pratinjau diverifikasi
sg run -l python -p "OLD_PATTERN" -r "NEW_PATTERN" --update-all TARGET_DIR/

# 4. Audit aturan YAML proyek
sg scan
```

## 3. Sinergi Pendamping dengan `open-code-review` & `knip`

- **Sebelum/Saat Ngoding**: Gunakan `ast-grep` untuk memetakan struktur pemanggil dan menerapkan refaktor seragam secara deterministik.
- **Pembersihan Dead Code**: Jalankan `knip` pada proyek JS/TS untuk memastikan refaktor tidak menyisakan ekspor atau dependensi yatim.
- **Sesudah Ngoding**: Jalankan `open-code-review` (`ocr`) pada `git diff` untuk memverifikasi logika tepi, keamanan, dan kelengkapan tes.

Wrapper MSSHI ini 100% **model-agnostic** (`0` perubahan pada `config.yaml`, provider, model, atau `SOUL.md`). Lisensi upstream: **MIT License** (Copyright (c) 2022 Herrington Darkholme, disimpan di `LICENSE.upstream`).
