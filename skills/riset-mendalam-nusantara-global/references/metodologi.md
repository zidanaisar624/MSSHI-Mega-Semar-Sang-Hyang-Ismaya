# Referensi Metodologi Penelitian (Kuantitatif, Kualitatif, Campuran, R&D & PTK)

Gunakan rujukan ini untuk membantu memilih desain penelitian yang sahih, menentukan sampel secara rasional, dan memvalidasi instrumen maupun analisis data.

---

## 1. Memilih Paradigma Penelitian

| Paradigma | Ontologi & Fokus | Pendekatan Umum | Pertanyaan Kunci |
| --- | --- | --- | --- |
| **Positivisme / Post-positivisme** | Realitas objektif yang dapat diukur secara probabilistik | Kuantitatif (eksperimen, survei, pemodelan) | Seberapa besar pengaruh X terhadap Y dan seberapa signifikan? |
| **Konstruktivisme / Interpretivisme** | Makna dibentuk secara sosial dan kontekstual | Kualitatif (fenomenologi, studi kasus, etnografi) | Bagaimana partisipan memaknai pengalaman X dalam konteks Y? |
| **Pragmatisme** | Fokus pada pemecahan masalah nyata dengan kombinasi metode terbaik | *Mixed Methods*, R&D, *Design Science* | Apa yang bekerja, untuk siapa, dan mengapa hal itu bekerja? |
| **Transformatif / Partisipatoris** | Pemberdayaan, keadilan sosial, perbaikan praktik langsung | Penelitian Tindakan (PTK / PAR) | Perubahan nyata apa yang tercapai bersama komunitas/kelas? |

---

## 2. Desain Penelitian Utama

### A. Kuantitatif
- **Eksperimen Murni (*True Experimental*):** ada pengacakan (*random assignment*), kelompok perlakuan & kontrol (contoh: *Pretest-Posttest Control Group*). Terkuat untuk klaim kausalitas.
- **Kuasi-Eksperimen (*Quasi-Experimental*):** tanpa pengacakan penuh (umum di sekolah/kampus/lapangan Indonesia, mis. *Nonequivalent Control Group*, *Difference-in-Differences*). Wajib laporkan ancaman bias seleksi dan uji kesetaraan awal (*baseline balance*).
- **Survei / Korelasional / Kausal-Komparatif (*Ex-post facto*):** mengukur hubungan atau prediksi antar-variabel (regresi, SEM-PLS, CB-SEM, path analysis). **Jangan mengklaim sebab-akibat murni** tanpa desain kausal atau identifikasi ekonometrik yang kuat.
- **Deret Waktu & Peramalan (*Time-Series*):** wajib pisahkan *chronological holdout* (anti-kebocoran masa depan) dan bandingkan model terhadap *naive* / *seasonal-naive baseline* (selaras `timesfm-forecasting`).

### B. Kualitatif
- **Studi Kasus (*Case Study*):** telaah mendalam atas batas kasus yang jelas (*single* atau *multiple-case*; triangulasi wawancara, observasi, dokumen).
- **Fenomenologi:** menggali esensi pengalaman hidup partisipan terhadap fenomena tertentu.
- **Grounded Theory:** membangun teori/model konseptual dari data lapangan melalui *open → axial → selective coding* dan *theoretical sampling* hingga saturasi.
- **Etnografi / Netnografi:** memahami pola budaya, norma, dan praktik komunitas fisik maupun digital.

### C. Metode Campuran (*Mixed Methods*)
1. **Konvergen Paralel (*Convergent*):** kumpulkan data kuantitatif dan kualitatif bersamaan, analisis terpisah, lalu integrasikan (*joint display*) untuk melihat konvergensi atau divergensi.
2. **Sekuensial Eksplanatori (*Explanatory Sequential*, `KUAN → kual`):** hasil statistik dulu, lalu wawancara/studi kasus untuk menjelaskan *mengapa* pola atau *outlier* tersebut muncul.
3. **Sekuensial Eksploratori (*Exploratory Sequential*, `KUAL → kuan`):** eksplorasi tema kualitatif dulu untuk menyusun instrumen/kuesioner/model, lalu uji pada sampel besar kuantitatif.

### D. Penelitian Pengembangan & Tindakan (Umum di Kampus Indonesia)
- **R&D (*Research & Development*) / *Design Science Research* (DSR):** model **ADDIE** (*Analysis, Design, Development, Implementation, Evaluation*), **4D** (*Define, Design, Develop, Disseminate*), atau **Borg & Gall** yang disederhanakan secara logis. Wajib memisahkan **validasi ahli** (*expert judgment*), **uji keterbacaan/kelayakan**, dan **uji efektivitas empiris**.
- **PTK (Penelitian Tindakan Kelas):** minimal 2 siklus (*Plan → Act → Observe → Reflect*) dengan indikator keberhasilan terukur sejak awal dan refleksi perbaikan antar-siklus yang konkret.

---

## 3. Strategi Sampling & Ukuran Sampel
- **Probabilitas (untuk generalisasi statistik):** *Simple Random*, *Stratified Random* (proporsional/disproporsional), *Cluster*, *Systematic*.
- **Non-probabilitas (eksplorasi / populasi tanpa kerangka sampling lengkap):** *Purposive* (kriteria inklusi/eksklusi tertulis jelas), *Snowball*, *Quota*, *Theoretical sampling*.
- **Menentukan Ukuran Sampel Secara Rasional (jangan asal angka):**
  - **Kuantitatif:** utamakan analisis daya statistik (*a priori power analysis*, mis. $\alpha = 0.05$, $1-\beta = 0.80$, estimasi *effect size* dari studi terdahulu) atau aturan rasio parameter untuk SEM/regresi. Rumus Slovin boleh dipakai bila memang diminta pedoman kampus untuk survei deskriptif populasi terbatas, tetapi sebutkan margin error dan keterbatasannya.
  - **Kualitatif:** berpedoman pada **saturasi data/tema** (*information power*) dan kecukupan variasi informan — jelaskan kriteria bagaimana saturasi diputuskan.

---

## 4. Uji Mutu Data & Instrumen

### Kuantitatif
- **Validitas:** validitas isi (*Content Validity Index* / Aiken's V dari panel ahli), validitas konstruk (EFA/CFA, *convergent* AVE ≥ 0.50, *discriminant* HTMT < 0.85/0.90), validitas kriteria.
- **Reliabilitas:** Cronbach's Alpha / McDonald's Omega / Composite Reliability (umumnya ≥ 0.70 untuk riset konfirmatori; ≥ 0.60 untuk eksploratori) serta reliabilitas antar-penilai (*Cohen's Kappa* / *Intraclass Correlation*).
- **Asumsi Statistik:** laporkan pemeriksaan normalitas, homogenitas, multikolinearitas (VIF), heteroskedastisitas, atau gunakan metode non-parametrik / *robust* / *bootstrapping* bila asumsi tidak terpenuhi — jangan memaksakan uji parametrik tanpa verifikasi.

### Kualitatif (*Trustworthiness* — Lincoln & Guba)
1. **Kredibilitas (*Credibility*):** triangulasi sumber/metode/peneliti, *member checking*, keterlibatan memadai.
2. **Transferabilitas (*Transferability*):** deskripsi kaya (*thick description*) tentang konteks agar pembaca bisa menilai kecocokan pada latar lain.
3. **Dependabilitas (*Dependability*):** jejak audit (*audit trail*) kode, memo analitik, dan keputusan metodologis.
4. **Konfirmabilitas (*Confirmability*):** refleksivitas peneliti dan pemisahan kutipan verbatim informan dari tafsir peneliti.
