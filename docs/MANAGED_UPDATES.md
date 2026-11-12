# Pembaruan skill terkelola / Managed skill updates

`msshi update` memperbarui rilis MSSHI, paket bundel yang terdaftar, migrasi runtime, dan (kecuali `--skip-upstreams`) cache repositori upstream serta integrasi curated yang didukung. Mengambil cache Git tidak otomatis menginstal semua program, semua skill pihak ketiga, atau model berat. Kredensial dan layanan opsional tetap perlu disiapkan sendiri.

## Pemasangan lama dan junction

```powershell
msshi managed register --skills-dir "PATH_TO_SKILLS" --apply
msshi managed status
msshi update
```

Ulangi `--skills-dir` untuk beberapa profil. Pendaftaran hanya menerima isi folder yang persis sama dengan bundel rilis yang diperiksa. Untuk membuktikan salinan rilis lama, tambahkan `--baseline PATH_TO_REVIEWED_OLD_RELEASE`. Berkas yang berbeda atau asalnya tidak terbukti dilaporkan sebagai `custom_or_unproven` dan dipertahankan. Jangan memakai baseline pribadi untuk memaksa menimpa perubahan yang masih ingin disimpan.

Junction pada satu folder skill yang didaftarkan secara eksplisit dapat diterima. Ancestor dan isi target fisik harus berupa direktori/berkas biasa. Manifest menyimpan jalur logis, target fisik, slug, versi baseline dan fingerprint isi. Target bersama diperbarui sekali untuk seluruh referensi. Jika junction berubah arah, pembaruan berhenti untuk ditinjau. Perubahan isi lokal menghasilkan `custom_preserved`, bukan ditimpa. Modul tidak melakukan migrasi cookie atau registrasi seluruh folder pengguna.

## Cadangan dan pemulihan

`state.json` berada pada data user MSSHI (`%LOCALAPPDATA%\MSSHI` di Windows; `MSSHI_HOME` dapat mengubah lokasi). Simpan salinannya sebelum mendaftarkan pemasangan lama. Perubahan skill menyimpan salinan isi sebelumnya dalam `.msshi-backup-*` di luar folder scanner `skills`; laporan pembaruan mencetak jalur backup yang digunakan. Cadangan SOUL/DNA untuk target installer standar dan receipt migrasi runtime terpisah dari backup skill.

Untuk pemulihan satu skill: hentikan tugas yang memakainya, pastikan hash versi kini sesuai laporan update, simpan versi kini ke folder cadangan lain, lalu pulihkan folder skill dari backup ke **target fisik yang sama**. Jangan menghapus atau meretarget junction. Pulihkan juga fingerprint dari salinan `state.json` terkait, atau biarkan updater memperlakukan hasilnya sebagai kustom sampai ditinjau kembali. Rollback runtime memakai `msshi runtime rollback` dengan receipt migrasi terkait; itu tidak otomatis memulihkan semua checkout Git, database, dan skill.

## English

Registration accepts exact, provenance-backed MSSHI bundle copies only. A reviewed old release can establish a baseline. Explicitly enrolled skill junctions resolve to a recorded physical directory; shared content updates once. Retargeted links are blocked and local changes are preserved. `msshi managed status` shows enrolled scope. It does not imply that every installed third-party skill is automatically updated. Backups are outside scanner roots; runtime receipts, skill backups, and updater state have different rollback scopes.
