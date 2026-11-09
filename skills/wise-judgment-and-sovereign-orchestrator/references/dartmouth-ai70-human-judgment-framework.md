# Dartmouth "AI at 70: What Must Remain Human?" Synthesis & Decision Framework

This module uses four Dartmouth lecture references as starting points for its decision framework:

1. **`bnO-uwTO4Us` - *Welcome & The Future Worth Building is Human*** (Mira Murati, CEO of Thinking Machines Lab & Prof. Sian Leah Beilock, President of Dartmouth)
2. **`beERLcCJFFI` - *Wise Decisions in an Age of Intelligent Machines*** (Prof. Ron Adner, Tuck School of Business; Allison Elworthy, Chief of Staff at HubSpot; Graham Brooks, Partner at 406 Ventures)
3. **`GoPGPyLFFuM` - *More Capable AI, More Human Judgment*** (Peter DeSantis, SVP at Amazon & Will Griffith, Dartmouth Trustee)
4. **`l4xUGsFblsQ` - *Teaching, Learning, and Pedagogy in the Age of AI*** (Prof. Jed Dobson & Prof. Roopika Risam, Dartmouth AI Fellows)

## 1. Core Architectural Laws Extracted from the 4 Lectures

| Lecture Source | Core Concept | Operational Rule for Hermes & Antigravity |
| :--- | :--- | :--- |
| **Mira Murati & Pres. Beilock** (`bnO-uwTO4Us`) | **Human Will vs Human Judgment & Tacit Knowledge** | - **Human Will**: Only the human decides *what* is worth building.<br>- **Human Judgment**: Keep human understanding at the center (`Responsible Person / RP`), not as a passive rubber-stamp.<br>- **Tacit Knowledge & Anti-Groupthink**: Store local experimental failures and personal nuances in `MEMORY.md` so the agent does not produce generic, homogenized "groupthink" outputs. |
| **Prof. Ron Adner, Allison Elworthy & Graham Brooks** (`beERLcCJFFI`) | **Winning the Right Game, The Context Harness, Deterministic vs Probabilistic, & Evals** | - **Deterministic First**: Never use a probabilistic LLM when a deterministic script, decision tree, or classical ML model is faster, cheaper ($0), and easier to audit.<br>- **6-Week Agile Sprints**: Keep the North Star fixed, but plan execution in adaptable 6-week (or micro-milestone) sprints.<br>- **The Harness Problem**: Flat AI ROI is caused by poor context harnesses, not weak models. Feed structured + unstructured domain context.<br>- **Evals as Moat**: Every agent loop must terminate against a deterministic **Eval** (automated test) that proves correctness. |
| **Peter DeSantis (Amazon SVP)** (`GoPGPyLFFuM`) | **More Capable AI Demands Stronger Engineering & Cost Judgment** | - Variable token cost scales with every invocation; unlike fixed-cost software, every token costs money.<br>- Pair high-capability AI with strict systems engineering, cost telemetry, and architectural accountability. |
| **Prof. Roopika Risam & Prof. Jed Dobson** (`l4xUGsFblsQ`) | **4 Dartmouth Competencies, Ontological Indeterminacy, & Preserving Agency** | - **4 Core Competencies**: (1) *Disciplinary Knowledge*, (2) *Critical Inquiry*, (3) *Ethical/Resource Awareness*, (4) *Responsible Agency*.<br>- **Ontological Indeterminacy**: AI excels in bounded deterministic ontologies, but human life, ethics, and relationships are ontologically indeterminate—never surrender personal agency to a black box. |

## 2. The Deterministic-First Routing Gate 

Before sending any subtask to a paid LLM provider, filter it through this 3-Tier Router:

1. **Tier 0 - Local Deterministic CLI / Python / PowerShell ($0.00 Token Cost)**:
   - File manipulation, directory scanning, math/financial formulas (`business-sage`), token counting (`TokenShield`), Git operations, system RAM checks, opening URLs, and static security linting (`Strix` local patterns).
   - *Action*: Execute via `cli_anything_sovereign_hub.py` or local shell scripts. **Cost: $0.00**.

2. **Tier 1 - Compact Context Single-Pass Agent Turn (Minimal Token Cost)**:
   - Code generation, UI refactoring, or structured synthesis where local scripts pre-extract only the exact 50-100 relevant lines rather than dumping entire repositories into the prompt window.

3. **Tier 2 - High-Stakes Human Judgment Gate (`RP Check`)**:
   - Strategic pivots, spending money, deleting data, changing security configurations, or personal life decisions.
   - *Action*: Present a concise Minto-Pyramid recommendation with 2-3 clear options (6D Parenting *Autonomy Support*) and let the user make the final call.
