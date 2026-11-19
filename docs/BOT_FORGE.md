# Bot Forge - penambahan bot sesuai kebutuhan

Pengguna dapat meminta anggota tim baru kepada bot mana saja. Pada preset 5 bot, Shizuka mengoordinasikan penilaian Yukino, Val, Kiki-Chii dan Coder jika pengguna setuju dengan panggilan model tambahan. Bot yang diminta menilai apakah tugas dapat ditangani peran saat ini. Untuk Solo atau tim kustom, gunakan peran yang benar-benar tersedia. Tanyakan dulu tujuan, keluaran, jangka waktu, alat dan anggaran.

Hasil akhir adalah usulan nama, tanggung jawab, skill, alur handoff, batas persetujuan manusia, dan rekomendasi kemampuan model (misalnya penalaran, vision, konteks, biaya dan kecepatan). Pengguna memasukkan pilihan model, provider, endpoint, base URL dan API key melalui Hermes. Tidak ada konfigurasi model bawaan atau pewarisan kredensial dari MSSHI.

Alur lokal MSSHI terinspirasi oleh [Hermes Bot Forge by Bikash Joshi](https://github.com/BkashJEE/hermes-bot-forge) dan [listing marketplace](https://hermes-agent.nousresearch.com/marketplace/bot-forge). MSSHI memakai pembuat profil native yang sudah ada agar tidak menjalankan kickoff chat, routine, notifikasi email, pewarisan memori atau gateway baru secara otomatis. Plugin upstream resmi merupakan tambahan terpisah yang dapat dipertimbangkan pengguna setelah meninjau pengaturan dan biaya; alur MSSHI tidak mengaktifkannya diam-diam. Fitur gateway/sandbox upstream berbeda pada Windows.

## Contoh dari chat dan terminal

> Saya membutuhkan bot pengelola jadwal komunitas. Tinjau apakah tim sekarang cukup, tanyakan pendapat peran terkait dan buat usulan untuk saya setujui.

```powershell
msshi forge --roster
```

Simpan rancangan yang sudah diperiksa ke `rancangan.json`:

```json
{
  "id": "community-planner",
  "name": "Community Planner",
  "purpose": "Menyiapkan usulan agenda komunitas dan ringkasan tugas.",
  "gap": "Tanggung jawab koordinasi agenda berulang memerlukan profil khusus.",
  "skills": ["prep-for-meetings", "focus-my-energy"],
  "reviews": {"coordinator": "Contoh hasil evaluasi; ganti dengan penilaian peran yang benar-benar diterima."}
}
```

```powershell
msshi forge --blueprint rancangan.json
msshi forge --blueprint rancangan.json --apply
```

Perintah pertama hanya meninjau rancangan. Perintah kedua meminta konfirmasi di terminal sebelum membuat profil baru. Profil mendapat SOUL, metadata dan skill yang dipilih, beserta MSSHITrim jika runtime lokal terverifikasi. Tidak menyalin pengaturan model/profile akun dari bot lain. Setelah itu atur model dan provider sendiri melalui Hermes, kemudian buka kembali panel bot bila perlu. Periksa `msshi doctor --json` dan `msshi trim --status`. Tidak ada janji bahwa setiap aplikasi atau model sudah siap setelah profil dibuat.
