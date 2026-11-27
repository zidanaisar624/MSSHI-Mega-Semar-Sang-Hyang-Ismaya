# Panduan Pola Viral, Caption Craft & Katalog Template Meme (`Rp0`)

Dokumen referensi ringkas untuk **Kiki-Chii** yang menyatukan intisari **`RiskAverseTech/createa-meme-skill`**, **`csmoove530/meme-lord`**, **`dhruvmehra/makememe`**, dan **`edwinjhlee/awesome-meme`**.

---

## 1. Delapan Pola Sukses Universal (`meme-lord` Clean Synthesis)

| # | Pola Humor | Struktur Kontras (*The Turn*) | Contoh Penggunaan |
|---|---|---|---|
| 1 | **Ironic Contrast** | Visual tenang/mulia vs teks kacau (atau sebaliknya) | Anjing duduk santai di ruang terbakar: *"Deadline 10 menit lagi, baru buka laptop."* |
| 2 | **Self-Aware Tech / AI Humor** | Menertawakan kebiasaan konyol sendiri saat ngoding/riset | *"Menghabiskan 4 jam mengotomasi tugas yang aslinya cuma 5 menit."* |
| 3 | **Escalation** | Level 1 wajar -> Level 4 makin absurd (`Expanding Brain`) | `print("ok")` -> `logging` -> debugger -> ganti profesi jadi petani. |
| 4 | **Absurd Specificity** | Angka/detail super spesifik yang terasa nyata | *"PR 3 baris: 0 komentar. PR ganti 1 nama variabel: 38 komentar arsitektur."* |
| 5 | **Relatable Pain** | Penderitaan kolektif mahasiswa/engineer/kreator | Revisi `"Final_v2_FIX_BANGET_Bismillah.docx"`. |
| 6 | **Format Subversion** | Membalik ekspektasi panel klasik secara tak terduga | Panel kedua tidak memilih opsi baru karena opsi lama belum dibayar. |
| 7 | **Deadpan Understatement** | Reaksi datar terhadap bencana besar | Server produksi mati total -> *"Sedikit kendala teknis minor."* |
| 8 | **Visual Metaphor** | Objek fisik mewakili beban sistem/mental | Truk raksasa ditahan satu baut kecil bernama `legacy_utils.py`. |

---

## 2. Daftar Cek Cepat *Caption Craft* (`createa-meme-skill`)

- **Uji 1 Detik:** Bisakah orang menangkap leluconnya tanpa membaca paragraf penjelas?
- **Pangkas Kata:** Target **2–6 kata per slot**. Maksimal absolut 10 kata jika hanya 1 slot tunggal.
- **Jangan Jelaskan Leluconnya:** Biarkan gambar membawa setengah makna; jangan tulis ulang isi ekspresi gambar di dalam teks.
- **Sebelum vs Sesudah:**
  - *Terlalu panjang:* `"Perasaan saya ketika sudah mengira semua bug selesai diperbaiki ternyata muncul error baru saat demo."`
  - *Tajam (2 slot):* `"Lokal: 100% Hijau"` / `"Pas Share Screen ke Dosen: Segmentation Fault"`

---

## 3. Pemetaan Struktur Retoris -> Template Instan (`makememe` / `memegen.link`)

| Struktur Lelucon | Template ID (`memegen.link`) | Jumlah Slot | Fungsi Utama |
|---|---|---|---|
| Tolak X, pilih Y | `drake` / `icanhas` | 2 | Perbandingan preferensi tajam |
| Tergoda hal baru padahal tugas lama belum kelar | `db` (*Distracted Boyfriend*) | 3 | `Godaan Baru` / `Aku` / `Tugas Utama` |
| Semua terbakar tapi pura-pura tenang | `fine` (*This is Fine*) | 2 | *Deadpan denial* saat krisis |
| Menyadari kebenaran yang memang selalu begitu | `astronaut` (*Always Has Been*) | 2 | `"Semuanya cuma wrapper JSON?"` / `"Selalu begitu."` |
| Opini berani mengundang debat | `cmm` (*Change My Mind*) | 1 | Pernyataan kontroversial namun *relatable* |
| Rencana 3 langkah yang berbalik makan tuan | `gru` (*Gru's Plan*) | 4 | Langkah 3 & 4 diulang saat sadar salah |
| Panik -> Tenang -> Lebih Panik | `panik-kalm-panik` | 3 | *Plot twist* bertingkat |
| Ide terdengar pintar padahal konyol | `rollsafe` (*Roll Safe*) | 2 | *"Gak bakal kena bug kalau gak pernah deploy."* |
| Debat emosional vs reaksi bingung datar | `woman-cat` | 2 | Ekspektasi marah vs respon tak peduli |
| Tersenyum menahan perih | `harold` (*Hide the Pain Harold*) | 2 | Sopan di luar, hancur di dalam |
| Pilihan sulit dua tombol merah | `ds` (*Daily Struggle*) | 2–3 | Dua opsi sama-sama bikin pusing |
| Eskalasi ide 4 tingkat | `brain` (*Expanding Brain*) | 4 | Dari cara biasa ke tingkat parodi kosmik |

---

## 4. Katalog Pilihan Programmer & Klasik (`awesome-meme`)

Template populer untuk topik coding, kampus, dan kerja kreatif:
- **Developer & Engineering:** `vim-exit` (*How to Exit Vim*), `it-works-why` (*Code works, nobody knows why*), `wtf-per-minute` (*WTFs/minute saat code review*), `code-review-guy`, `monday-deploy` (*Deploy Jumat/Senin*), `stackoverflow-copy`, `bug-feature` (*It's not a bug, it's a feature*), `lgtm`, `programmer-drink`.
- **Reaksi Universal:** `distracted-boyfriend`, `drake-hotline-bling`, `this-is-fine`, `success-kid`, `roll-safe`, `woman-yelling-cat`, `hide-pain-harold`, `doge`, `expanding-brain`, `one-does-not-simply`, `change-my-mind`, `chill-guy`, `panda-head-work`, `table-flip`, `table-unflip`.

---

## 5. Rubrik Evaluasi A/B Lokal 6 Dimensi (`meme-rating`)

Saat Kiki-Chii menyiapkan proyek konten penting, buat **2–3 kandidat meme** lalu nilai menggunakan skor komposit berbobot (`1–10`):

`Skor Akhir = 0.30*Concept + 0.25*Visual_Quality + 0.20*Meme_Fit + 0.15*Consistency + 0.05*Speed + 0.05*Cost`

- Pada alur **Rp0 lokal**, dimensi `Cost` otomatis bernilai maksimal (`10/10`) karena tidak membakar kredit API berbayar.
