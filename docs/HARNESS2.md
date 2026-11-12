# Harness² untuk Val dan Coder

MSSHI v3.1 mengintegrasikan [Harness² dari Google Research](https://github.com/google-research/harness2) sebagai alat proposal dan demonstrasi lokal. Framework upstream menjalankan dua tingkat rekursi dengan bobot model tetap: Propose–Probe–Compose pada tugas, serta library pengalaman untuk perbaikan lintas tugas. Integrasi ini membatasi tindakan pada proposal yang ditinjau manusia dan demo ledger deterministik dalam runtime privat.

| Bot | Tanggung jawab |
| --- | --- |
| Val | Desain evaluasi, baseline, holdout, ukuran keberhasilan, pemeriksaan bukti dan ketidakpastian |
| Coder | Kandidat harness di workspace terisolasi, diff, probe yang dapat diulang, dan rollback |
| Shizuka | Menerima ringkasan lewat koordinasi yang sudah diotorisasi; tidak mendapat instalasi skill baru ini |

Delapan permukaan eksperimen upstream adalah system prompt, guardrails, memory, tool guidance, subagents, skills, scripts, dan plugins. Permukaan itu hanya dipakai pada salinan eksperimen. Provider/model/fallback/MoA, persona, SOUL, DNA, memori, plugin native, browser, GDrive, dan Brightdata aktif tidak diubah. Tidak ada auto-promotion lesson, perubahan bobot model, daemon, desktop MCP, atau layanan cloud baru.

## Perintah aman

CLI MSSHI merutekan empat verb berikut ke helper mandiri. Contoh langsung dari root repositori:

```text
python scripts/msshi_harness2.py --hermes-home D:/HermesData status --verify
python scripts/msshi_harness2.py --hermes-home D:/HermesData install --source D:/HermesData/msshi-private/v3.1-sources/harness2
python scripts/msshi_harness2.py --hermes-home D:/HermesData demo
python scripts/msshi_harness2.py --hermes-home D:/HermesData plan --goal "Uji hipotesis dengan baseline dan holdout"
```

`status` tidak mengimpor framework dan dapat memverifikasi hash seluruh file paket terpasang. `plan` hanya mencetak proposal JSON. `install` membutuhkan Python 3.12 dan Git, membuat venv khusus, memverifikasi commit, lalu membangun paket dari `git archive` commit tersebut; file tidak terlacak dan `.env` checkout tidak masuk build. Installer memasang core dengan `--no-deps --no-build-isolation --no-compile`, tanpa extras `render`/`bridge`; setuptools 80.9.0 dan wheel 0.45.1 adalah build tools yang dipin. Pengunduhan instalasi memakai PyPI; demo berikutnya berjalan tanpa jaringan.

Untuk mesin lain, siapkan checkout resmi pada pin di bawah lalu berikan path-nya lewat `--source`. Installer menolak commit berbeda. Direktori runtime harus berada di luar source, profil, dan konfigurasi; `HERMES_HOME` yang menunjuk langsung ke sebuah profil dinormalisasi ke root data bersama. Helper tidak mengubah konfigurasi executor atau model.

## Demo yang benar-benar dijalankan

Worker memanggil `harness2.cli.demo.main` resmi dengan `--output NEWDIR --k 2 --mode both`. `DemoAdapter` menjalankan program Python yang membaca CSV dan menghitung Decimal; `DemoProposer` deterministik menghapus filter jumlah positif yang salah. Ia mencontohkan probe dan komposisi pada dua ledger, termasuk nominal negatif. Hasil benar yang diperiksa adalah `85.15` dan `20.25`, dibanding baseline yang hanya menghitung nilai positif.

Output selalu baru di `HERMES_ROOT/msshi-private/harness2-runtime/demo-runs/`, dengan nama sederhana maksimal 48 karakter. `--output` opsional hanya menerima anak langsung baru dari direktori tersebut. Symlink/junction, direktori existing, serta lokasi di profil, konfigurasi, dan source ditolak. Worker memakai CWD output yang baru tanpa `.env`, allowlist environment yang tidak mewarisi kredensial/proxy/agent home, guard socket tanpa jaringan, dan allowlist subprocess yang hanya menerima interpreter venv beserta program ledger yang byte-nya sesuai fixture yang ditinjau.

Windows Job Object memiliki kill-on-close dan dimiliki wrapper sebelum proses mulai berjalan. Timeout membersihkan worker serta keturunannya, termasuk redirector venv. Fixture terpisah menguji penghentian parent dan descendant sungguhan; helper tidak hanya mengandalkan timeout `subprocess.run` yang dapat meninggalkan turunan hidup.

Upstream menargetkan Linux/POSIX. Dua kompatibilitas **hanya di proses anak demo Windows** diperlukan pada pin ini:

1. `core/schedule.py` mengimpor `fcntl` saat menulis ringkasan. Shim menyediakan `LOCK_EX`/`LOCK_UN` melalui lock satu byte `msvcrt`, dengan waktu tunggu terbatas.
2. `core/tree.py:read_tree` memakai `str(relative_path)`, sehingga key komponen berisi backslash di Windows; lookup demo menggunakan slash. Wrapper in-memory menormalisasi key dan pengecualian stub ke bentuk POSIX.

Tidak ada file vendor/source terpasang yang dipatch. Ini membuktikan jalur demo deterministik lokal, bukan dukungan Windows umum atau kesiapan seluruh framework/benchmark. Run awal yang gagal akibat key path disimpan sebagai bukti privat; run berhasil memakai direktori baru.

## Batas benchmark dan review

Wrapper tidak menawarkan `harness2`, `harness2-setup`, judge, report benchmark, bridge, Vertex/gcloud, atau pemilihan model. Benchmark upstream bermodel menimbulkan biaya API, memerlukan dependensi tambahan dan kontrol kebocoran jawaban/rubrik. Executor Codex upstream berjalan dengan sandbox dinonaktifkan. Mode itu tidak dipasang, dikonfigurasi, atau diuji oleh integrasi otomatis MSSHI ini.

Proposal nyata harus memisahkan baseline/probe/holdout, mencatat model dan anggaran yang disetujui, melaporkan hasil negatif dan biaya, dan menyertakan diff serta rollback. Hasil demo tidak otomatis menjadi memory, skill, prompt, atau plugin Hermes. Ringkasan untuk Shizuka dan keputusan manusia tetap menjadi langkah koordinasi sebelum promosi perubahan nyata.

## Provenance dan bukti

| Item | Nilai |
| --- | --- |
| Upstream | [google-research/harness2](https://github.com/google-research/harness2) |
| Pin yang ditinjau | [`6868817518876de8fd170c6a8354daca273b6191`](https://github.com/google-research/harness2/tree/6868817518876de8fd170c6a8354daca273b6191) |
| Lisensi core | Apache-2.0, Google LLC; [LICENSE upstream](https://github.com/google-research/harness2/blob/6868817518876de8fd170c6a8354daca273b6191/LICENSE) |
| SHA-256 LICENSE canonical | `3ddf9be5c28fe27dad143a5dc76eea25222ad1dd68934a047064e56ed2fa40c5` |
| Metadata core | `harness2==0.1.0`, Python `>=3.12,<3.14`, tanpa dependensi inti; instalasi MSSHI memakai Python 3.12 |
| Sumber primer | README, pyproject.toml, cli/demo.py, demo.py, config.py, core/schedule.py, core/tree.py pada pin tersebut |
| Bukti runtime | `HERMES_ROOT/msshi-private/harness2-runtime/INSTALLATION.json` dan setiap `demo-runs/NEWDIR/MSSHI_DEMO_PROOF.json` |
| Audit integrasi privat | `HERMES_ROOT/msshi-private/v3.1-sources/harness2-integration-audit.json` |

Lisensi serta pemberitahuan pihak ketiga upstream tetap berlaku untuk framework dan benchmark terkait. Wrapper, skill, dan dokumentasi MSSHI adalah materi orisinal paket; helper ownership proses diadaptasi dari helper TimesFM MSSHI berlisensi MIT. Framework upstream tidak dibundel ke source publik MSSHI dan bukan produk Google yang didukung resmi.

Validasi integrasi mencakup instalasi core dari pin, verifikasi hash paket, demo kedua mode dengan total ledger yang benar, guard jaringan/proses, penolakan path/verb yang dilarang, fixture timeout parent+descendant, serta hash salinan skill Val/Coder. Tidak ada tes chat LLM atau kredit API.
