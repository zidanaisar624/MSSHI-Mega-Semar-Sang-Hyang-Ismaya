# Academic completion, long context, and specialist references

Use the following playbook in solo mode or with the MuZA preset. Shizuka scopes the task, Val validates evidence, and other specialists support individual steps. A host with the full package can consult `docs/TUJUH_MESIN_AKADEMIK.md` and `docs/LIMA_LAPIS_KONTEKS.md`.

## Seven academic workflows

| Workflow | Result | Relevant skills |
| --- | --- | --- |
| Gap and novelty | Compare nearest papers, search criteria, and candidate gaps. | `deep-research`, `literature-review`, `novelty-assessment` |
| Reading and evidence | Indexed text and exact page pointers, checked against the original. | `paper-context-resolver`, `backward-traceability`, optional local OCR |
| Method and analysis | Method assumptions, reproducible analysis, and leakage checks before evaluation. | `data-analysis`, `math-reasoning`, `academic-plotting` |
| Supervisor or reviewer feedback | Trace each comment to a decision, concrete revision, and evidence. | `paper-revision`, `rebuttal-writing` |
| Draft and edit | Structure claim–evidence–reasoning and preserve meaning and citations during editing. | `paper-writing-section`, `research-paper-writing`, optional Indonesian or English humanizer |
| Working rhythm | One task matched to the time and energy reported by the user. | `focus-my-energy`, `parenting-6d-gad-mdd` |
| Defense rehearsal | Questions, short responses, and supporting slide/page references. | `slide-generation`, `get-more-perspectives` |

Verify quotations, citations, and results before submission. Use user-authorized NotebookLM exports only. The suite provides skill instructions and an index approach for a private collection; access to the collection is set up separately.

## Five context layers

1. Index local documents and source versions, optionally with Graphify.
2. Extract text in page-addressed chunks; use configured OCR for scans and check the result on the original.
3. Retrieve and compact the evidence relevant to the question. Jev is optional, with `jev_model_routing: false`.
4. Record agreed decisions, source pointers, and unresolved questions in a private project memory with the user's permission.
5. Keep static instructions stable, fit dynamic evidence into a measured budget, and verify cache and billing from the host where available.

Use local search and manual excerpts as fallback. Report missing pages or limited retrieval when they affect the result.

## Goose and remote jobs

Shikaku may use the [Goose](https://github.com/aaif-goose/goose) CLI on demand for a permitted edit-and-verify workflow. Limit its files, commands, and network scope before invocation. In its absence, use the host's normal tools. For career research, use [Remote Jobs](https://github.com/remoteintech/remote-jobs) as a discovery list, then verify location and current vacancies on employer pages.
