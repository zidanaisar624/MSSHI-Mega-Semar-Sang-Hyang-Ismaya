# Integrasi kontekstual: karier, engineering, harness, dan video

MSSHI memuat instruksi menurut topik atau permintaan. Instruksi tidak menjalankan
job scan, benchmark, download model atau aplikasi pada boot. Indeks nama/deskripsi
tetap dapat memakai konteks host; tidak ada jaminan seluruh tagihan menjadi nol.

| Instruksi | Penerima pada preset MuZA | Pemakaian |
| --- | --- | --- |
| `career-ops` | Kelima bot | CV/JD, skor kecocokan 1-5, tracker dan wawancara |
| `remote-jobs` | Kelima bot | Direktori perusahaan remote, lalu verifikasi posisi aktual |
| `mattpocock-engineering` | Kelima bot saat topik sesuai | TDD, diagnosis, domain model dan spesifikasi |
| `harness2` | Kelima bot | Proposal evaluasi dan demo deterministik yang ditinjau |
| `rea-video` | Kiki-Chii | Breakdown video per shot menjadi VIDEO.md dan rencana remake |

Berbagi instruksi memungkinkan semua peran memakai pengetahuan yang sama. Diskusi
lintas bot tetap memerlukan rute delegasi native yang terkonfigurasi dan tugas yang
memang didelegasikan. Menambah skill tidak dengan sendirinya memulai lima percakapan.

## Perintah source yang dapat dipakai langsung

```powershell
msshi integrations source --home "PATH_HERMES" --name career-ops
msshi integrations source --home "PATH_HERMES" --name career-ops --fetch
msshi integrations source --home "PATH_HERMES" --name remote-jobs --fetch
msshi integrations source --home "PATH_HERMES" --name remote-jobs --query python
msshi integrations source --home "PATH_HERMES" --name mattpocock-skills --fetch
msshi integrations source --home "PATH_HERMES" --name mattpocock-skills --list
msshi integrations source --home "PATH_HERMES" --name mattpocock-skills --skill tdd
msshi integrations source --home "PATH_HERMES" --name rea-video --fetch
```

Tanpa action, command hanya membaca status. `--fetch` mengambil source dari commit
terpin dan memeriksa hash Git blob serta SHA-256 cache. Source disimpan di
`msshi-private/context-sources/`, terpisah dari scanner `skills/`. Query direktori
dan pembacaan satu skill selanjutnya tidak melakukan akses jaringan atau model.

Cache mengandung kode/dokumentasi workflow yang dipilih, bukan history Git, vendor
dependency, contoh video/model besar atau data pengguna. Untuk CareerOps, AGENTS.md,
mode workflow termasuk `_shared.md`/`_writing.md`, scripts, dan `package.json` harus
tersedia. Pin ini tidak mempunyai `package-lock.json` pada root CLI; lock di `web/`
milik proyek web terpisah. Source ini berbeda dari User Layer privat.

## Runtime eksplisit

```powershell
msshi integrations source --home "PATH_HERMES" --name career-ops --install-runtime
msshi integrations source --home "PATH_HERMES" --name rea-video --install-runtime
```

CareerOps memerlukan Node sesuai rentang upstream. Pada pemasangan runtime eksplisit,
installer membuat resolusi dependency lokal dengan `npm install --package-lock-only
--ignore-scripts`, lalu menjalankan `npm ci --ignore-scripts`. Hash lock lokal dicatat
dan diperiksa saat status/reinstall; lock tersebut bukan pin yang disediakan upstream.
Resolusi pertama dapat mengikuti versi dependency yang tersedia sesuai rentang manifest.
Dengan `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1`, Chromium dan
aktivitas portal tidak dipasang/dijalankan otomatis. Data CV/tracker diletakkan pada
`msshi-private/career-ops-data/`. Gunakan `CAREER_OPS_DATA_DIR` yang dilaporkan status
untuk proses CareerOps; jangan menyimpan CV di source cache/repo publik. Tanpa CV dan
profil pengguna, evaluasi kecocokan personal belum siap meskipun source telah ada.

rea-video dipasang di venv privat tanpa extras OCR/ASR. Instalasi package tidak
menjalankan pipeline video. Operasi upstream standar dapat mengunduh model audio pada
pemakaian pertama, sehingga tahap lokal ringan memakai flag eksplisit:

```text
rea-video decompose INPUT.mp4 -o OUTPUT_BARU --no-vlm --no-whole --no-ocr --no-packaging --no-asr --no-speakers --no-stems --workers 1 --lang en
```

Python/FFmpeg, ruang disk/RAM dan input tetap harus tersedia. `--no-vlm` tidak boleh
digabung dengan `--vlm` pada tahap hemat; model video/vision, OCR/ASR, stem audio dan
generasi ulang dipilih terpisah. Baca VIDEO.md lalu shot yang relevan, bukan seluruh
JSON besar. Pin ini menyediakan bahasa report zh/en; agen dapat menerangkan hasil
dalam bahasa Indonesia tanpa mengarang flag CLI.

## Pilih disiplin engineering dengan tepat

`--list` Matt Pocock menampilkan `explicit_only` dan `in_progress`. TDD/domain-modeling/
diagnosing-bugs dapat dipilih saat konteks sesuai. `grill-me`, `to-spec` dan orkestrator
dengan `disable-model-invocation: true` memerlukan permintaan eksplisit. Source `to-spec`
dapat menerbitkan issue; izin instalasi tidak mengizinkan publikasi otomatis.

## Harness² untuk semua bot

Pembatasan Val/Coder telah dibuka pada matriks. Semua bot dapat mengusulkan dan
memeriksa eksperimen di bidangnya. [Wrapper Harness²](../skills/harness2/SKILL.md)
tetap memisahkan proposal, demo deterministik, benchmark bermodel, dan promosi perubahan.
Tidak ada perubahan provider/model, SOUL, memori atau harness aktif secara otomatis.

## Pin dan lisensi

| Sumber | Commit yang ditinjau | Ketentuan |
| --- | --- | --- |
| career-ops-hq/career-ops | `c687a6f89aa766de468d41402df1ce24bdd86315` | Kode MIT; employers data CC BY 4.0; merek terpisah |
| remoteintech/remote-jobs | `155939ad935d22afa8edbaaf0770b99f9d0dbf0d` | ISC; boilerplate MIT dan font SIL OFL |
| mattpocock/skills | `5863806dd4e15c63174bee4e7515a4256792ecfa` | MIT |
| JuneYaooo/rea-video | `820d661e807034e0f0284262b4e93085cfd3da49` | Apache-2.0, termasuk NOTICE |

Lisensi asli tersedia pada folder skill dan [audit lisensi](../configs/upstream_license_audit.json).
Wrapper MSSHI adalah instruksi/adaptor asli; runtime dan implementasi upstream tidak
dibundel di dalam folder skill. Tidak ada klaim instalasi runtime, autentikasi akun,
keberhasilan tugas atau kualitas hasil hanya berdasarkan keberadaan instruksi/source.
