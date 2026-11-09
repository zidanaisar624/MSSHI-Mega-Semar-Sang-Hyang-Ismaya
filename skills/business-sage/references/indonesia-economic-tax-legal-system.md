# Indonesian Economic, Tax, Legal, Accounting & Sharia Business System Reference

Use this reference when executing **Pillar 2** of `business-sage` for businesses operating in or expanding into Indonesia (synthesizing SBM ITB, MM FEB UI, and MBA FEB UGM frameworks with current Indonesian laws).

## 1. Macroeconomic Structure & Sistem Ekonomi Pancasila

- **Pasal 33 UUD 1945 Tri-Pillar Architecture**: Indonesia operates a mixed constitutional economy (*Sistem Ekonomi Pancasila*) anchored by three distinct actors:
  1. **BUMN / BUMD & Danantara**: State-owned enterprises controlling strategic sectors (energy, infrastructure, state banking: Mandiri, BRI, BNI, BTN, BSI).
  2. **Koperasi**: Member-owned cooperative enterprises operating on family/mutual-aid principles (*asas kekeluargaan*).
  3. **Swasta & UMKM**: Private corporations and Micro, Small, and Medium Enterprises, where **UMKM accounts for ~61% of Indonesia's GDP and ~97% of national employment**.
- **Regional Purchasing Power & Tiered Market Strategy**:
  - *Tier 1 (Jabodetabek, Surabaya, Bandung, Medan, Bali, Makassar)*: High digital penetration, higher AOV, intense CAC competition.
  - *Tier 2 & Tier 3 Cities / Kabupaten*: Lower CAC, strong community/word-of-mouth trust dynamics, high sensitivity to unit pack size (*ekonomi sachet / kemasan terjangkau*), and COD / QRIS payment preference.

## 2. Official UMKM Classification (`PP Nomor 7 Tahun 2021`)

Under **Pasal 35 PP No. 7 Tahun 2021** (implementing UU Cipta Kerja), Indonesian enterprises are classified by **Modal Usaha** (business capital excluding land and buildings) at registration, or by **Hasil Penjualan Tahunan** (annual sales turnover):

| Scale Tier | Capital Criterion (Excl. Land & Building) | Annual Sales Turnover Criterion | Recommended Accounting Standard (IAI) |
| :--- | :--- | :--- | :--- |
| **Usaha Mikro** | $\le 	ext{Rp1,000,000,000}$ ($\le 	ext{Rp1 Miliar}$) | $\le 	ext{Rp2,000,000,000}$ ($\le 	ext{Rp2 Miliar}$) | **SAK EMKM** (Simplified Balance Sheet + P&L) |
| **Usaha Kecil** | $>	ext{Rp1 Miliar}$ to $\le 	ext{Rp5 Miliar}$ | $>	ext{Rp2 Miliar}$ to $\le 	ext{Rp15 Miliar}$ | **SAK EMKM** or **SAK Entitas Privat (SAK EP)** |
| **Usaha Menengah** | $>	ext{Rp5 Miliar}$ to $\le 	ext{Rp10 Miliar}$ | $>	ext{Rp15 Miliar}$ to $\le 	ext{Rp50 Miliar}$ | **SAK Entitas Privat (SAK EP)** |
| **Usaha Besar** | $>	ext{Rp10 Miliar}$ | $>	ext{Rp50 Miliar}$ | **SAK Indonesia (PSAK / IFRS Convergence)** |

## 3. Indonesian Corporate & UMKM Taxation (`PP No. 20 Tahun 2026`, `PP 55/2022` & `Pasal 31E`)

Apply the updated Indonesian tax rules verified under **Peraturan Pemerintah Nomor 20 Tahun 2026** (effective 22 April 2026, amending PP 55/2022) and the **Coretax DJP** system:

| Taxpayer Entity Type | Gross Turnover $\le 	ext{Rp500 Juta/Year}$ | Gross Turnover $>	ext{Rp500 Juta}$ to $\le 	ext{Rp4.8 Miliar/Year}$ | Gross Turnover $>	ext{Rp4.8 Miliar}$ to $\le 	ext{Rp50 Miliar/Year}$ |
| :--- | :--- | :--- | :--- |
| **WP Orang Pribadi (Individual Entrepreneur)** | **0% (Tax-Free / Bebas PPh)** on the first Rp500M cumulative annual turnover (`Pasal 60 ayat (2) PP 55/2022`). | **0.5% PPh Final** on turnover exceeding Rp500M. Under **`PP 20/2026`**, this 0.5% rate applies **indefinitely (selamanya)** with no time limit! | Normal progressive PPh OP brackets (`5%, 15%, 25%, 30%, 35%`) on net taxable income (or NPPN if eligible). |
| **PT Perorangan (Single-Founder UMK LLC)** | **0.5% PPh Final** on gross monthly turnover. | **0.5% PPh Final** on gross turnover. Under **`PP 20/2026`**, PT Perorangan can use the 0.5% rate **indefinitely (selamanya)** while turnover $\le 	ext{Rp4.8B}$! | Transitions to standard PT corporate tax (**22% PPh Badan** with **Pasal 31E** discount). |
| **Koperasi (Cooperative)** | **0.5% PPh Final** (max 4 years from registration). | **0.5% PPh Final** (max 4 years from registration). | Standard Corporate Tax (**22% PPh Badan** / **Pasal 31E**). |
| **Newly Registered CV, Firma, or Standard PT (Multi-Founder)** | **No longer eligible for 0.5% PPh Final under `PP 20/2026`!** Uses **Pasal 31E PPh Badan**: **11% effective rate on Net Fiscal Profit** (Rp0 tax if operating at a loss). | **Pasal 31E PPh Badan**: **11% effective rate on Net Fiscal Profit** ($50\% 	imes 22\%$ on net taxable income). | Proportional **Pasal 31E** discount on the first Rp4.8B slice of revenue, and **22% PPh Badan** on the remainder. |

- **Anti-Splitting Aggregation Rule (`PP 20/2026`)**: The Rp4.8 Billion cap aggregates the combined gross turnover of husband, wife, and all `PT Perorangan` entities established by either spouse.
- **VAT / PPN & PKP Threshold**: Businesses exceeding **Rp4.8 Billion/year** in gross sales must register as **PKP (Pengusaha Kena Pajak)** and collect PPN (standard 11% effective formula / 12% luxury tier under `PMK 131/2024`).

## 4. Legal Entity Selection, `OSS-RBA` Licensing & Mandatory Halal (`BPJPH`)

1. **Choosing the Optimal Indonesian Legal Entity**:
   - **Solo Founder / Bootstrap UMK ($	ext{Sales} \le 	ext{Rp4.8B}$)**: Choose **PT Perorangan**. It separates personal assets from business liabilities, requires only 1 founder (KTP + NPWP), registers online via AHU without expensive notary deeds, and locks in the **0.5% PPh Final** tax rate indefinitely under `PP 20/2026`.
   - **Multi-Founder SME / Bootstrapped Partnership**: Choose **PT Biasa (Perseroan Terbatas)** rather than CV if personal asset protection or future investor equity issuance is desired (remembering that in a CV, the *Sekutu Aktif/Komplementer* has unlimited personal liability). Under `PP 20/2026`, a new PT/CV with thin margins (<4.5% net profit margin) actually pays *less* tax under `Pasal 31E` (11% of net profit) than 0.5% of gross revenue!

2. **OSS-RBA (`oss.go.id`) Risk-Based Licensing**:
   - Match the business activity to the exact 5-digit **KBLI 2020** code:
     - *Risiko Rendah*: **NIB (Nomor Induk Berusaha)** alone is full legal authorization to operate.
     - *Risiko Menengah Rendah*: **NIB + Sertifikat Standar** (self-declared online).
     - *Risiko Menengah Tinggi*: **NIB + Sertifikat Standar** (verified by ministry/region).
     - *Risiko Tinggi*: **NIB + Izin** (+ BPOM / AMDAL / sectoral permit).

3. **Mandatory Halal Certification (`BPJPH`)**:
   - Food, beverage, slaughtered products, cosmetics, and consumer goods sold in Indonesia require **BPJPH Halal Certification**. Micro and Small businesses (`UMK`) with low-risk ingredients qualify for the free **SEHATI Self-Declare** pathway.

## 5. Digital Payments (`QRIS` & `BI-FAST`), Sharia Economy (`DSN-MUI`), & Labor Law (`PP 35/2021`)

- **QRIS & BI-FAST Cashflow Optimization**:
  - Integrate **QRIS** for retail acceptance (note that Merchant Discount Rate / MDR is borne by the merchant per Bank Indonesia regulations and must be factored into unit contribution margin) and **BI-FAST** (Rp2,500 transfer cap) for B2B supplier settlements.
- **Islamic / Sharia Business Contracts (`DSN-MUI` & `PSAK Syariah`)**:
  - *Murabahah*: Cost-plus sale where cost and profit margin are transparently disclosed upfront.
  - *Mudharabah*: 100% capital from *Shahibul Maal* + management by *Mudharib*; profit shared by pre-agreed nisbah, financial loss borne by capital provider unless caused by misconduct.
  - *Musyarakah*: Joint capital partnership with profit shared by nisbah and loss shared strictly proportional to capital contribution.
  - *Ijarah / IMBT*: Operating or lease-to-own asset financing.
- **Indonesian Labor Cost Modeling (`UU Cipta Kerja` & `PP No. 35 Tahun 2021`)**:
  - Always budget total employee cost at **1.22x to 1.30x base monthly wage** to account for:
    1. **THR Keagamaan**: 1 month salary per year (pro-rated after 1 month of service).
    2. **Uang Kompensasi PKWT (`Pasal 15-16 PP 35/2021`)**: Mandatory 1 month salary per 12 months worked (pro-rated via $rac{	ext{Months}}{12} 	imes 	ext{Monthly Wage}$) payable whenever a fixed-term contract (`PKWT`) expires!
    3. **BPJS Ketenagakerjaan & Kesehatan**: Employer contributions for JKK, JKM, JHT (3.7%), JP (2%), and BPJS Kesehatan (4%).
