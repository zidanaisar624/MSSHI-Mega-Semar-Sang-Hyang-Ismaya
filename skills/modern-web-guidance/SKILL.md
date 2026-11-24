---
name: modern-web-guidance
description: Panduan platform web modern berstandar Baseline (Chrome, Edge, Firefox, MDN) khusus Coder (Shikaku / Sir. Robot) untuk mengutamakan fitur HTML/CSS/JS native modern, aksesibilitas, dan Core Web Vitals dibanding pola warisan atau library JS berlebih.
license: MIT
metadata:
  upstream: https://github.com/GoogleChrome/modern-web-guidance
  upstream_commit: 2b4aa13a72dd47cd135b06ce5abfccd92e19b24f
  upstream_license: Apache-2.0
  activation: contextual-coding-modern-web
---

# Modern Web Guidance (`GoogleChrome/modern-web-guidance` — Khusus Coder)

Gunakan skill ini pada peran **Coder (`shikaku` / `Sir. Robot`)** saat membangun, meninjau, atau memodernisasi aplikasi web, komponen frontend, CSS, DOM, dan performa halaman.

Sumber rujukan dikelola bersama oleh tim **Google Chrome, Microsoft Edge, Mozilla Firefox, dan MDN** (`https://developer.chrome.com/docs/modern-web-guidance`) agar agen pengodean mengutamakan kapabilitas **Baseline** platform web modern dibanding pola *legacy* atau ketergantungan JavaScript yang tidak perlu.

## 1. Utamakan Fitur Native Web Platform (Baseline-First)

Sebelum memasang paket npm UI tambahan atau menulis *polyfill* rumit, cek apakah fitur native berikut sudah memenuhi target browser proyek:

- **Elemen Interaktif & Overlay**: Gunakan `<dialog>` (`showModal()`, fokus & `Esc` bawaan) dan **Popover API** (`popover`, `popovertarget`) alih-alih modal/dropdown `div` kustom dengan `z-index` rapuh.
- **Tata Letak & CSS Modern**:
  - **Container Queries** (`container-type: inline-size`, `@container`) untuk komponen adaptif selain `@media` viewport.
  - **Selektor `:has()`** untuk logika relasional orang-tua/anak murni CSS tanpa listener JS.
  - **Native CSS Nesting**, Cascade Layers (`@layer`), `color-mix()`, `light-dark()`, `clamp()`, `dvh`/`svh`, dan `aspect-ratio`.
  - **CSS Anchor Positioning** & `@starting-style` (dengan *progressive enhancement* jika mendukung browser lama).
- **Transisi & Navigasi**: Gunakan **View Transitions API** (`document.startViewTransition`) dengan menghormati `@media (prefers-reduced-motion: reduce)`.
- **JavaScript & Web API Modern**: Gunakan `structuredClone()`, `Object.groupBy()`, `Promise.withResolvers()`, ` AbortSignal.timeout()`, `URLPattern`, dan `Intl.*` bawaan.

## 2. Core Web Vitals & Aksesibilitas Wajib

1. **LCP (*Largest Contentful Paint*)**: Hindari menyembunyikan elemen utama di balik *client-side waterfall*; beri `fetchpriority="high"` pada gambar hero utama dan tentukan `width`/`height` eksplisit.
2. **INP (*Interaction to Next Paint*)**: Jaga *event handler* tetap ringan; pecah komputasi panjang dan hindari *layout thrashing* sinkron.
3. **CLS (*Cumulative Layout Shift*)**: Kunci dimensi media, font (`size-adjust` / `font-display: swap`), dan ruang slot dinamis.
4. **Aksesibilitas Semantik**: Utamakan `<button>`, `<a>`, `<nav>`, `<main>`, `<form>`, dan `<label>` asli sebelum menambahkan atribut `role`/`aria-*`.

## 3. Sinergi dengan Ekosistem Coder MSSHI

- Padukan dengan `anti-slop` & `unslop` untuk kerapian antarmuka, `knip` untuk membersihkan ekspor/dependensi tak terpakai, `ast-grep` untuk refaktor AST terstruktur, dan `open-code-review` untuk audit *diff* sebelum rilis.
- Sepenuhnya **model-agnostic**: tidak mengubah model, provider, endpoint, atau konfigurasi Hermes pengguna.

Lisensi upstream: **Apache License 2.0** (`GoogleChrome/modern-web-guidance`, disimpan di `LICENSE.upstream`). Wrapper MSSHI berlisensi MIT.
