# Kompatibilitas platform MSSHI

**MSSHI — Mega Semar Sang Hyang Ismaya: Sovereign Sage** (M.S.S.H.I., Multi-Agent Sovereign Sage & Hermes Intelligence) membundel direktori Agent Skills. Installer menyalin isi paket ke target yang Anda pilih. Integrasi berstatus eksternal memerlukan setup tersendiri.

| Platform | Jalur yang tersedia di paket |
|---|---|
| Hermes Agent | Salin ke folder skill profil aktif. Deteksi mempertimbangkan HERMES_HOME, folder profil pengguna, dan D:/HermesData jika ditemukan pada Windows. Gunakan --target-dir untuk memilih profil tertentu. |
| OpenClaw | Pasang pintu masuk dengan `openclaw skills install git:zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya --global`. Untuk seluruh katalog, ikuti jalur Skills CLI di [Quick Start](../README.md). |
| Claude Code | Salin ke ~/.claude/skills atau instal plugin dari marketplace lokal. Pengguna Claude Desktop dapat memakai jalur plugin ini pada Claude Code di desktop jika tersedia. |
| Google Antigravity | Pakai `msshi setup --platform antigravity` atau salin ke `~/.gemini/config/skills`. Untuk opsi Skills CLI, cek lokasi tujuan yang dicetak sesuai versinya. |
| ChatGPT Projects | Tambah [Knowledge Bundle](../portable/MSSHI_ChatGPT_Knowledge_Bundle.md) sebagai sumber dan salin [instruksi pilihan](../portable/CHATGPT_CUSTOM_INSTRUCTIONS.md) ke Project settings. |
| Custom GPT | Salin instruksi ke GPT Builder dan unggah materi pilihan ke Knowledge. |
| CLI-Anything | Gunakan harness dari paket atau upstream yang Anda pasang secara terpisah. Periksa aplikasi dan dependensinya sebelum memanggil harness. |

## Installer lokal

Jalankan dari root paket dengan Python 3.10+. Semua contoh berikut adalah simulasi. Tambahkan --apply setelah memeriksa target, daftar file dan rute platform.

~~~text
python scripts/install_msshi.py --platform hermes --mode solo
python scripts/install_msshi.py --platform openclaw --mode selective --packs core,thesis
python scripts/install_msshi.py --mode custom-bots --matrix configs/bot_role_and_skill_matrix.json --target-dir ./my-team
python scripts/install_msshi.py --mode muza-preset --target-dir ./muza-team
python scripts/install_msshi.py --platform chatgpt --mode selective --packs core --target-dir ./chatgpt-reference
~~~

Mode tim menyiapkan folder workspace per bot dengan SOUL.md, AGENTS.md dan skills/. Buat atau pilih profil/agen di aplikasi Anda, lalu salin skill pilihan ke folder skill profilnya dan masukkan persona ke tempat instruksi yang didukung aplikasi. Terapkan langkah yang sama untuk setiap bot. Ubah jumlah dan nama bot lewat matriks Anda sendiri. Mode preset memilih lima ID yang tercantum di matriks.

Referensi: [Hermes Skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/), [OpenClaw Skills](https://docs.openclaw.ai/tools/skills), [Antigravity customization discovery](https://antigravity.google/docs/customization-discovery?tab=cli).

## Marketplace Claude Code

Dari root paket, validasi dan tinjau plugin sebelum mengaktifkannya. Plugin menawarkan skill bundel melalui mekanisme plugin Claude Code. Gunakan installer selektif bila ingin subset.

~~~text
claude plugin validate .
claude plugin marketplace add .
claude plugin install msshi@msshi-marketplace
~~~

Marketplace menunjuk ke root paket, tempat direktori skills berada. Untuk Claude.ai Web/Desktop di mode chat, unggah [portable/msshi.zip](../portable/msshi.zip) melalui **Customize → Skills → + → Upload a skill**. ZIP itu memuat satu skill portabel beserta panduan 50 skill inti. **Code → Download ZIP** memberi salinan lengkap repositori. Ekstrak salinan itu dan ambil `portable/msshi.zip` untuk diunggah. MCP Anthropic membutuhkan server MCP yang terpisah dengan transport dan konfigurasi yang sesuai. Paket skill ini menyediakan instruksi lokal.

Referensi: [Marketplace Claude Code](https://code.claude.com/docs/en/plugin-marketplaces), [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference).

## ChatGPT Projects dan Custom GPT Actions

Untuk Projects, gunakan Project settings dan Add sources. Untuk Custom GPT, gunakan Instructions untuk aturan kerja dan Knowledge untuk referensi. Pilih materi yang relevan sesuai batas akun dan unggah hanya file yang boleh dibagikan. Skrip dan direktori skill tetap tersedia untuk runtime lokal.

File openai_custom_gpt_schema.json menjelaskan tiga operasi katalog baca saja yang dilayani scripts/catalog_api.py. Uji dari root paket pada komputer Anda.

~~~text
python scripts/catalog_api.py --port 8765
curl http://127.0.0.1:8765/packs
curl "http://127.0.0.1:8765/skills?pack=core"
curl http://127.0.0.1:8765/skills/business-sage
~~~

Server membaca metadata publik skill dan paket dari matriks. Operasi tersedia melalui GET dan tidak membaca berkas lain, mengakses persona atau kredensial, menjalankan skill, memanggil model, atau menulis konfigurasi. Hentikan server dengan Ctrl+C.

Untuk Actions, sediakan reverse proxy HTTPS sendiri pada host yang sama dengan server loopback. Tetapkan MSSHI_CATALOG_TOKEN melalui pengelola rahasia atau lingkungan proses server sebelum menyalakannya. Teruskan header Authorization melalui proxy. Ganti hostname .invalid pada OpenAPI dengan domain HTTPS milik Anda. Impor skema ke GPT Builder, pilih API key → Bearer, masukkan token yang sama, lalu uji tiga operasi. Jangan simpan token di repo, skema atau instruksi. Terapkan batas akses dan laju permintaan di proxy sesuai kebutuhan. Ketersediaan Actions mengikuti akun dan aturan workspace. ChatGPT Projects tetap memakai jalur instruksi dan referensi manual.

Referensi: [ChatGPT Projects](https://help.openai.com/en/articles/10169521-projects-in-chatgpt), [GPT Knowledge](https://help.openai.com/en/articles/8554397-creating-and-editing-gpts), [GPT Actions](https://help.openai.com/en/articles/9442513-configuring-actions-in-gpts), [CLI-Anything](https://github.com/HKUDS/CLI-Anything).



## Impor ZIP melalui OpenClaw

Jika gateway mendukung arsip dan kanalnya meneruskan lampiran, kirim ZIP skill ke chat Telegram, Discord, atau Web lalu ketik `install this skill`. Agen harus bisa membaca lampiran dan memiliki izin memasang skill. Untuk impor arsip terkelola, gateway perlu mengizinkan `skills.install.allowUploadedArchives` dan menjalankan alur staging serta tinjauan host. Jika unggahan chat tidak tersedia, gunakan instalasi Git di tabel. CLI OpenClaw menerima sumber Git atau direktori hasil ekstrak.

[Instalasi dan arsip privat OpenClaw](https://docs.openclaw.ai/tools/skills) · [Skill khusus Claude](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) · [ID agen Skills CLI](https://github.com/vercel-labs/skills/blob/main/docs/agents.md).
