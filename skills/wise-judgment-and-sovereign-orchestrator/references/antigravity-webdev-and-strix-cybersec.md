# Antigravity Elite WebDev, Design Taste & Strix Cybersecurity Arsenal

Use this reference when executing **Pillar 4** of `wise-judgment-and-sovereign-orchestrator` to select optional GitHub references for **Antigravity** and **Hermes**.

## 1. Complete Matrix of the 12 Integrated Repositories + Added WebSec Defenses

| Category | Repository | Intended use when available |
| :--- | :--- | :--- |
| **1. AI Pentesting & Vulnerability Scanner** | [`usestrix/strix`](https://github.com/usestrix/strix) | Autonomous AI penetration testing agent that scans codebases and live endpoints for SQLi, XSS, SSRF, IDOR, broken auth, and insecure headers before production. |
| **2. E2E & Security Testing** | [`currents-dev/playwright-best-practices-skill`](https://github.com/currents-dev/playwright-best-practices-skill) | Production-grade Playwright TypeScript patterns: web-first locators, Page Object Model (POM), visual regression, `axe-core` accessibility, and automated auth/checkout security tests. |
| **3. Anti-AI-Slop Design System** | [`superdesigndev/superdesign-skill`](https://github.com/superdesigndev/superdesign-skill) | Gives coding agents real design judgment: extracts design tokens from existing code, gathers style references, and generates tasteful, non-generic UI components. |
| **4. Design MCP + Registry** | [`marvkr/better-design`](https://github.com/marvkr/better-design) | Open-source design MCP server and curated `shadcn/ui` component patterns for clean layout composition. |
| **5. Aesthetic Curation** | `madebymustafa/design-taste` | Enforces high-taste typography, optical spacing, subtle border luminance, and cohesive dark/light palettes. |
| **6. WebGL & GPU Shaders** | `paper-design/shaders` | High-performance, lightweight WebGL/canvas shaders (mesh gradients, liquid metal, subtle noise grain) subject to device performance. |
| **7. Canvas-Driven UI** | `DavidHDev/canvas-ui` | Interactive spatial and canvas-based UI components for modern web apps and portfolios. |
| **8. Micro-Interactions** | [`ibelick/motion-primitives`](https://github.com/ibelick/motion-primitives) | Physics-based Framer Motion / CSS animation primitives (magnetic buttons, text morphing, smooth accordions, spotlight cards). |
| **9. Interactive Cursors & Layouts** | `ui-layouts/cursify` | Custom interactive cursor effects and responsive grid/bento layout primitives. |
| **10. Deep Autonomous Research** | `assafelovic/gpt-researcher` | Multi-source web and local document research agent for technical due diligence and architecture discovery. |
| **11. 265+ Stack Skills** | [`Mindrally/skills`](https://github.com/Mindrally/skills) | Comprehensive skill definitions across React, Next.js, TypeScript, Tailwind, Node.js, Python, Docker, and PostgreSQL. |
| **12. Copilot Prompts & Agents** | `github/awesome-copilot` | Curated custom instructions, security review prompts, and debugging workflows. |

## 2. The 7-Gate WebSec & Anti-Slop Production Checklist (`websec-audit`)

Every website or web app built in Antigravity/Hermes must pass these 7 gates before deployment:

1. **Gate 1 - Zero Hardcoded Secrets**: Scan all `.env`, `.js`, `.ts`, `.py` files for leaked API keys, JWT secrets, or database URLs.
2. **Gate 2 - Input Sanitization & Parameterized Queries**: Enforce strict `zod` / schema validation on every API route and parameterized ORM/SQL queries to block SQLi/NoSQLi.
3. **Gate 3 - Security Headers & CSRF/XSS Defense**: Configure strict `Content-Security-Policy (CSP)`, `Strict-Transport-Security (HSTS)`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, and `HttpOnly; Secure; SameSite=Strict` cookies.
4. **Gate 4 - Authentication, Rate Limiting & RBAC (IDOR Prevention)**: Verify object-level authorization on every `[id]` endpoint and enforce IP/token rate-limiting on login and API routes.
5. **Gate 5 - Dependency & Supply-Chain Audit**: Run `npm audit` / `pip-audit` and lock deterministic versions in `package-lock.json`.
6. **Gate 6 - Playwright E2E & Accessibility Verification**: Run `playwright-best-practices-skill` suites for critical user journeys (auth, checkout, form submission) with zero `waitForTimeout` anti-patterns.
7. **Gate 7 - SuperDesign Anti-Slop Visual Audit**: Verify consistent 8px/4px spacing scale, WCAG `>= 4.5:1` contrast, responsive mobile/desktop breakpoints, and smooth `60fps` motion primitives.


## 3. Extended Multi-Agent & Antigravity Ecosystem Integrations (Phase 2 Expansion)

### A. For Hermes (`Shikaku Nara` Coder Bot) & Antigravity IDE
1. **`aaif-goose/goose`**: Extensible developer agent CLI used on-demand for code execution, refactoring, and automated test repair (`lazy_start: true`).
2. **`mukul975/anthropic-cybersecurity-skills`**: 817 structured cybersecurity skills across 29 domains (MITRE ATT&CK, DFIR, Threat Hunting, AppSec); review upstream setup and licensing before use.
3. **`NabilRFG12/Reverse-Engineer-anything` & `morluto/rea` (Emergency-Only Defensive Forensics Protocol)**:
   - **Default Mode (`NORMAL`)**: Strictly **LOCKED / ON-COMMAND ONLY** (`require_user_permission: true`). Never runs automatically during routine tasks.
   - **Emergency Mode (`ANOMALY_OR_INTRUSION_DETECTED`)**:
     1. **Step 1 (Alert First)**: Immediately emit a high-priority alert to the user explaining the detected anomaly/threat.
     2. **Step 2 (Autonomous Defensive Action)**: If an explicit, time-bounded emergency authorization already exists, perform only the scoped local read-only inspection. Ask before changes, external targets, containment, or any work outside scope.
     3. **Step 3 (Full Post-Action Forensic Report)**: Deliver a complete breakdown of what happened, what triggered the alert, what artifacts were analyzed, and the findings, and which actions still need approval.
4. **`kerpopule/hermes-jev-skills` (Optional for all five bots; start with `Shizuka`, `Shikaku`, and `Val`)**:
   - Uses Jev for skill selection, passage scoring, and context compaction.
   - **CRITICAL HARD-LOCK RULE**: `jev_model_routing` is strictly set to `false` (disabled) so Jev NEVER alters or overrides the existing Main Agent, Sub-Agent, or MoA `provider` and `model` settings!

### B. For All 5 Hermes Bots & Antigravity IDE
1. **`baidu/Unlimited-OCR` & `huggingface.co/baidu/Unlimited-OCR-2`**: Optional OCR for documents. Process pages in verified batches within device memory.
2. **`miqdadbadjuber/anti-slop`**: Enforces strict filtering against generic AI-generated UI designs, boilerplate prose, and bloated code across all 5 bots.
3. **`obra/superpowers`**: Structured agentic software development methodology (`writing-plans`, `executing-plans`, `using-superpowers`), available only after host-specific setup.
4. **`dietrichgebert/ponytail`**: Senior-developer minimalism principle (*"The best code is the code you never wrote"*)—prevents over-engineering and saves output tokens.
5. **`addyosmani/agent-skills`**: Production-grade web engineering, Core Web Vitals, and architecture skills by Addy Osmani.
6. **`Graphify-Labs/graphify`**: Local deterministic AST parsing (`graphify` CLI) for source and document structure when configured.

### C. Hermes Specialized Extensions
1. **`steel-dev/hermes-steel`**: Cloud/headless browser provider plugin for Hermes (`lazy_start: true`, on-demand only).
2. **`remoteintech/remote-jobs`**: Directory of global remote-friendly tech companies referenced by `business-sage` for international B2B client prospecting and remote career arbitrage.
