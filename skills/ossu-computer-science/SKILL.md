---
name: ossu-computer-science
description: Connect students in Hermes to the open-source OSSU Computer Science curriculum (Intro CS, Core CS, Advanced CS, Final Project) as a guided Socratic tutor. Reads pinned OSSU curriculum guides lazily from msshi-private/context-sources/ossu-computer-science, adapts study pacing, explains one concept at a time, runs quizzes/labs, and tracks progress.
---

# OSSU Computer Science — Guided Study Companion for Hermes

Upstream: `https://github.com/ossu/computer-science` (MIT License, Open Source Society University, pinned commit `8f8272b1d378d31494240aa1d667aa6b045c6552`).

Use this skill whenever a student (or lecturer preparing a syllabus/RPS) wants to learn Computer Science systematically via **OSSU** inside Hermes — without leaving chat or burning tokens on giant curriculum dumps.

## How to Teach With OSSU in Hermes (Mission 1 — Belajar / Jadi Guru)

1. **Diagnose Level, Goals & Weekly Time First (Token-Efficient)**:
   - Ask 3 brief questions before recommending courses: (a) current background (complete beginner vs already coding / S1/S2/S3), (b) target track or specific CS topic (e.g., Python/Intro CS, Algorithms, Math, Systems/OS, Security, ML), and (c) realistic weekly hours + current energy (`focus-my-energy`).
   - Do **not** dump the entire OSSU README in one reply.
2. **Read Only What Is Needed From the Local Pinned Curriculum Cache**:
   - Inspect status locally (`0` network calls):
     ```text
     msshi integrations source --home <HERMES_HOME> --name ossu-computer-science
     ```
   - Fetch/cache once if missing (optional, explicit user action):
     ```text
     msshi integrations source --home <HERMES_HOME> --name ossu-computer-science --fetch
     ```
   - Read only the specific relevant file from `<HERMES_HOME>/msshi-private/context-sources/ossu-computer-science/8f8272b1d378d31494240aa1d667aa6b045c6552/`:
     - `README.md` — full roadmap (`Prerequisites` -> `Intro CS` -> `Core CS` [Programming, Math, CS Tools, Systems, Theory, Security, Applications, Ethics] -> `Advanced CS` -> `Final Project`)
     - `coursepages/intro-programming/README.md`, `coursepages/intro-cs/README.md`, `coursepages/spd/README.md`, `coursepages/class-based/README.md`, `coursepages/ostep/README.md` (and xv6 lab guides)
     - `extras/courses.md`, `extras/readings.md`, `extras/puzzles-practice-plods.md`, `extras/other_curricula.md`
     - `CURRICULAR_GUIDELINES.md`, `FAQ.md`, `HELP.md`
3. **Interactive Tutor Loop (1 Concept / Module at a Time)**:
   - **Shizuka** leads curriculum planning, Socratic explanations (intuition -> analogy -> worked example -> formalization), active-recall quizzes, and study-plan checkpoints.
   - Hand off focused parts only when genuinely needed: **Val** for Core Math / Core Theory proofs & exercises; **Shikaku** for Core Programming, CS Tools, Systems (Nand2Tetris/OSTEP), Security, & coding labs; **Yukino** for daily study scheduling & energy pacing; **Kiki-Chii** for concept diagrams/slides.
   - Share official OSSU course links transparently when the student wants to enroll in a free/audit MOOC (Coursera/edX/MIT OCW/etc.); never fabricate course URLs or claim paid certificates are required.
4. **Track Progress Persistently**:
   - Help the student maintain a simple Markdown study tracker (`ossucs-progress.md`) in their writable workspace (`3. Read and Write for All BOTS` or chosen study folder) listing completed courses, current module, quiz scores, and knowledge gaps for offline reflection (`msshi dream`).

## Guardrails
- Curriculum reference & tutoring only: no background model calls, no automatic account login, no forced course enrollment, and no changes to provider/model/`SOUL.md`.
- Keep all upstream curriculum files outside `skills/` inside `msshi-private/context-sources/ossu-computer-science/`.
