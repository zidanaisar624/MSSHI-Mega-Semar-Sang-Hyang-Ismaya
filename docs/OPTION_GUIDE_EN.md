# MSSHI v3.1.0 - What each installation choice does

[Bahasa Indonesia](OPTION_GUIDE.md) | [English](OPTION_GUIDE_EN.md)

Explanations appear directly in `msshi setup`, `msshi select`, `msshi optional list` and the application selection/catalog menus. This revision keeps version 3.1.0 and existing defaults. `--lang en` changes setup/select explanations; input IDs and syntax stay the same.

```sh
msshi choices rea
msshi choices --kind packs
msshi choices --kind skills
msshi choices --kind apps
msshi choices --lang en
msshi optional list --lang en
```

These commands only read help. They do not install, authenticate, open apps, fetch upstreams or call an LLM. Skill instructions, application/runtime installation, model weights, accounts and task execution are separate steps. Pressing Enter keeps the shown default: REA is No/OFF; KAT is Skip. Skipped options may be added later.

## Setup modes

| ID | Function / prerequisites |
| --- | --- |
| solo | Install all standard skills for one agent; REA stays separate and OFF by default. |
| custom-bots | Choose the number, names and roles of bots, then select each bot's skills. |
| selective | Install selected categories plus the package's mandatory foundation skills. |
| muza-preset | Create a team: Yukino for ideas, Shizuka for coordination, Val for research, Kiki for creative work and Shikaku for code. |

## Target agents

| ID | Function / prerequisites |
| --- | --- |
| hermes | Install into the Hermes Agent skills folder; the user retains control of accounts and the main model. |
| openclaw | Install skill instructions for OpenClaw; service connections depend on the user's OpenClaw setup. |
| claude | Install into the Claude Code skills folder; for Claude.ai use the README's ZIP-upload route. |
| codex | Install into the Codex skills folder; this does not upload Knowledge to ChatGPT. |
| antigravity | Install skill instructions into the selected Antigravity location without changing the IDE's model. |
| manual | Choose the destination folder for another agent that supports SKILL.md. |

## Skill packs

| ID | Function / prerequisites |
| --- | --- |
| core | Foundations for ideation, writing style, persona, OCR, coordination and task-based tool access. |
| filmmaking | Film/photo planning, visuals, motion graphics and video; production uses separately configured tools. |
| business | Business analysis, financial scenarios and calculations through a local harness. |
| thesis | Research ideas, literature, methods, data analysis, writing, revision and thesis presentations. |
| webdev | Project mapping, web/UI development, code experiments and testing. |
| cybersec | Code mapping and security-audit guidance for authorized targets; engines are installed separately. |

## Optional features and prerequisites

| ID | Function / prerequisites |
| --- | --- |
| rea | Static CLI analysis of owned JavaScript/archives, useful for understanding applications and artifacts. Default No; this installs only the wrapper, not the runtime or native engines. |
| rea-runtime | Install REA npm dependencies into an isolated runtime; compatible Node/npm and an internet download are required. Engines such as Ghidra are separate; no MCP server is registered. |
| pull-upstreams | Download external reference repositories into a cache for additional modules. Uses internet and disk space; it does not automatically run their code or make dependencies/accounts ready. |
| custom-display-names | Change display names in the preset while keeping role assignments and folder IDs the same. |
| artcraft | Optional creative apps for photo, video, audio, design and documents through available adapters. You may skip them; apps, licenses or service accounts are separate and do not open at boot. |
| kat | An additional coding subagent, separate from the main model. This choice only saves readiness preferences; it does not download a model or enable the subagent yet. |
| kat-light | Plan local KAT with IQ2_XS/IQ3_XXS quantization for a smaller memory footprint. Requires model files and a real RAM check; selection does not download or load the model. |
| kat-ideal | Plan local KAT with Q4_K_M quantization, generally heavier than the light option. Requires model files and enough RAM; selection does not download or load the model. |
| kat-cloud | Plan a separate API endpoint for the coding subagent. Requires an account/endpoint and cost approval; this choice makes no API call and does not replace the main model. |
| kat-skip | Skip KAT configuration; coding can still use the agent and main model already configured. |
| skill-vs-pack | Packs select skill groups by subject; individual skills give one-by-one control. Mandatory foundations remain included, and external references are not necessarily ready to run. |
| voice | Local OmniVoice speech for requested audio or read-aloud, not every chat automatically. Requires weights, RAM and audio setup; the weights license restricts commercial use. |
| dream | Create deterministic local summary/learning proposals from selected material. Does not call an LLM or automatically promote proposals into active memory. |
| steel | Primary browser for general browsing once a key/endpoint is configured; service use may cost money. Personal-account access needs task-scoped approval, and other browser logins are not copied automatically. |
| gitlab | Access GitLab projects through web MCP with appropriate account authentication and permissions. Read only task-scoped data; project changes need explicit instructions. |
| tinyfish | Search or fetch web information through web MCP after service login. Operations may consume quota/credits; registration alone does not prove authentication or successful operation. |
| brightdata | Optional web-data service; remains disabled without an account and API key. Use requires service setup and a cost/quota check before running. |
| llmtrim | Compact eligible large JSON outputs without losing values, with an equality check. Does not compress every chat or guarantee a particular billing reduction. |
| hersona | Find persona references and prepare character-adjustment drafts through the CLI. Active persona still follows native SOUL; drafts do not automatically overwrite user settings. |
| timesfm-runtime | Set up TimesFM dependencies and weights for local time-series forecasts. Requires downloads, disk space and enough RAM; a small test does not guarantee accuracy on user data. |
| brag-runtime | Set up Hyperframes to validate and render local video from editable HTML compositions. Needs Node, a compatible browser/FFmpeg, RAM/disk and asset rights; fonts may need downloads. |
| scrapling-runtime | Set up an isolated parser for CSS/XPath extraction from local HTML files. Requires compatible Python dependencies; this option supplies no stealth browser or network crawler. |
| harness2-runtime | Set up the framework for deterministic harness-improvement demos and experiment proposals. Needs compatible Python/dependencies; model-backed benchmarks and promotion into the bot are not automatically enabled. |
| managed-update | Update registered skill copies whose fingerprints match, preserving differing local edits. Enrollment does not authorize replacing SOUL, provider/model or every runtime dependency. |
| upstream-cache | Keep external reference checkouts outside skill folders for separate review or integration. The cache uses internet/disk and is not the same as an installed or active capability. |

## Application connection choices

These choices configure the route registry only. Apps, runtimes, sign-in, account permissions, and service costs are separate prerequisites; no app opens at boot.

| ID | Function |
| --- | --- |
| auto-reconnect | Register routes already detected/configured; this does not open apps, sign in, or prove successful service operations. |
| select | Choose routes individually for this profile registry; only selected routes are added and apps remain task-triggered. |

| ID | Function / prerequisites |
| --- | --- |
| existing | Reuse connectors already enabled in this Hermes profile; authentication and successful operations still need separate verification. |
| artcraft | Register the group of 15 ArtCraft creative apps for video, images, audio, design, documents, and 3D; apps/runtimes are installed separately. |
| gdrive-web | Access Google Drive files through the web for a requested task; requires account sign-in and permission under the active browser policy. |
| perplexity | Research and search with Perplexity; web/app access and account limits are checked when used, without opening the app now. |
| youtube-chrome | Access YouTube for video research through the available route; personal-browser access requires task-scoped permission and the active policy. |
| tiktok | Research TikTok content through the web/app; sign-in, account permissions, and browser policy still apply. |
| antigravity | Use Antigravity IDE for the selected coding workspace; the IDE must be installed and opens only for a task. |
| blender | Work on Blender scenes, models, animation, and 3D renders through the registered route; requires Blender and a compatible adapter. |
| blender-cli | Control Blender through the CLI-Anything harness for 3D/render tasks; requires Blender and cli-anything-blender. |
| ffmpeg | Convert, trim, combine, or inspect local audio/video through the CLI; requires the FFmpeg executable. |
| cli-hub | Find and manage CLI-Anything harnesses; viewing the catalog does not install or run other harnesses/apps. |
| libreoffice | Work with documents, spreadsheets, and presentations through the LibreOffice harness; requires the app and CLI-Anything harness. |
| gimp | Edit raster images and compositions through the GIMP harness; requires GIMP and its CLI-Anything harness. |
| obs | Manage OBS scenes and recording/streaming through its harness; starting recording or broadcasting remains a separate task action. |
| audacity | Edit and process audio through the Audacity harness; requires Audacity and its CLI-Anything harness. |
| inkscape | Create and edit vector/SVG graphics through the Inkscape harness; requires Inkscape and its CLI-Anything harness. |
| krita | Create illustrations and digital paintings through the Krita harness; requires Krita and its CLI-Anything harness. |
| kdenlive | Assemble and edit video timelines through the Kdenlive harness; requires Kdenlive and its CLI-Anything harness. |
| drawio | Create and edit flowcharts or architecture diagrams through the draw.io harness; requires the app and compatible harness. |
| filmcraft | Work on video and editing timelines in FilmCraft; requires the app and an available CLI adapter. |
| effectcraft | Work on visual effects and motion in EffectCraft; requires the app and an available CLI adapter. |
| photocraft | Work on and edit photos in PhotoCraft; requires the app and an available CLI adapter. |
| lightcraft | Manage and develop photos, color, and exports in LightCraft; requires the app/adapter and an available photo library. |
| soundcraft | Work on audio editing and mixing in SoundCraft; requires the app and an available CLI adapter. |
| designcraft | Work on visual design and layouts in DesignCraft; requires the app and an available CLI adapter. |
| vectorcraft | Work on vector illustrations and graphics in VectorCraft; requires the app and an available CLI adapter. |
| figcraft | Work on interface designs and layouts in FigCraft; requires the app and an available CLI adapter. |
| wordcraft | Work on text documents and formatting in WordCraft; requires the app and an available CLI adapter. |
| gridcraft | Work on tables and spreadsheets in GridCraft; requires the app and an available CLI adapter. |
| deckcraft | Work on slides and presentations in DeckCraft; requires the app and an available CLI adapter. |
| pdfcraft | Work on PDF documents in PDFCraft; requires the app and an available CLI adapter. |
| cadcraft | Work on CAD drawings and designs in CADCraft; requires the app and an available CLI adapter. |
| solidcraft | Work on solid models and 3D designs in SolidCraft; requires the app and an available CLI adapter. |
| craftanything | Work on creative projects through Craft Anything; callable functions depend on the installed app/adapter. |
| materialcraft | Work on materials for visual/3D projects in MaterialCraft; requires the app and an available CLI adapter. |
| texturecraft | Work on textures for visual/3D projects in TextureCraft; requires the app and an available CLI adapter. |
| git | Manage source versions and change history with Git; pushing or writing to a remote still requires task permission and account access. |
| gitlab | Access GitLab projects and data through the registered adapter; requires authentication and appropriate project permissions. |
| mcp:gitlab | Access GitLab projects, issues, and data through the registered MCP connector; authentication and project permissions are checked separately, and registration does not prove successful operations. |
| mcp:tinyfish | Use Tinyfish web automation/search through MCP for authorized tasks; sign-in and quota/cost permission are required, and registration does not prove a working connection. |
| node | Run JavaScript tools/projects with local Node.js; selecting the route does not install packages or execute a project. |
| python | Run local Python tools/projects; selecting the route does not install dependencies or execute code. |
| graphify | Map file/code relationships into a project graph through local Graphify; requires its runtime and selected project input. |
| whatsapp-web | Access WhatsApp Web when required by a task; requires an account session and task-scoped permission, with authorization for sending messages. |
| hersona | Manage personalization/personas through Hersona CLI; selecting the route does not change personas or model configuration. |
| llmtrim | Compact eligible payloads through llmtrim CLI; savings depend on the input and do not guarantee lower total token billing. |

App names explain intended use; detection or registration alone is not proof of successful authentication or task completion. Unknown CLI extensions and existing MCP connectors receive a generic explanation until their own documentation is reviewed. Connection menu language follows `MSSHI_LANG=en` (PowerShell: `$env:MSSHI_LANG="en"`) or an English `LANG` locale.

## Individual skill catalogue

The catalogue has 121 canonical names: 62 bundled instruction folders and 59 external references. These are not 121 repositories; the upstream manifest still contains 49 sources. Aliases are alternate names, not extra skills. “Bundled” means instructions are included, not that apps, accounts or runtime dependencies are already installed. REA is listed for discovery but remains outside the standard bundle and default OFF.

| Skill | Status | Function |
| --- | --- | --- |
| academic-plotting | Bundled instructions | Create publication figures from agreed data and visual specifications. |
| addy-agent-skills | External; separate setup | Apply software engineering practices to implementation and code review. |
| ai-research-explore | Bundled instructions | Plan candidate research experiments separately from the baseline. |
| ai-research-reproduction | Bundled instructions | Define a small, verifiable target for reproducing a research result. |
| analyze-project | Bundled instructions | Map project structure, configuration, entry points and change risks. |
| anti-slop | External; separate setup | Check repetitive cliches, interface patterns and code structures. |
| antigravity-webdev-cybersec | Bundled instructions | Coordinate web development and authorized security review with Antigravity and available local tools. |
| artcraft-cadcraft | External; separate setup | Use an available app adapter for technical drawings and CAD work. |
| artcraft-craftanything | External; separate setup | Use an available app adapter to coordinate creative work across tools. |
| artcraft-deckcraft | External; separate setup | Use an available app adapter to build and edit presentations. |
| artcraft-designcraft | External; separate setup | Use an available app adapter to create and edit visual designs. |
| artcraft-effectcraft | External; separate setup | Use an available app adapter for visual effects and compositing. |
| artcraft-figcraft | External; separate setup | Use an available app adapter for interface designs and prototypes. |
| artcraft-filmcraft | External; separate setup | Use an available app adapter to plan scenes and shots. |
| artcraft-gridcraft | External; separate setup | Use an available app adapter for tables and production planning. |
| artcraft-lightcraft | External; separate setup | Use an available app adapter to develop, crop and export photos. |
| artcraft-pdfcraft | External; separate setup | Use an available app adapter to prepare PDF documents. |
| artcraft-photocraft | External; separate setup | Use an available app adapter to process and review photos. |
| artcraft-solidcraft | External; separate setup | Use an available app adapter to work with solid models. |
| artcraft-soundcraft | External; separate setup | Use an available app adapter for sound design and mixing. |
| artcraft-vectorcraft | External; separate setup | Use an available app adapter to create and edit vector assets. |
| artcraft-wordcraft | External; separate setup | Use an available app adapter to write production documents. |
| auto-curiousity-for-film-making | Bundled instructions | Explore creative tools and production techniques in separate, reviewable experiments. |
| autoresearch | Bundled instructions | Coordinate experiment and synthesis cycles with a defined stopping point. |
| awesome-copilot | External; separate setup | Find adaptable examples of agent instructions and development practices. |
| backward-traceability | Bundled instructions | Trace reported numbers and findings back to data, scripts or calculations. |
| bang-motion | External; separate setup | Plan code-based motion graphics from a creative brief. |
| barty-motion-graphics | External; separate setup | Plan motion graphic compositions and code-based animation. |
| better-design | External; separate setup | Review design quality, hierarchy and visual consistency. |
| blender-mcp | External; separate setup | Coordinate 3D scenes and rendering through an available Blender adapter; desktop setup uses native CLI. |
| brag | Bundled instructions | Plan editable product-launch videos with Hyperframes, starting with concepts and human review. |
| brainstorming-research-ideas | Bundled instructions | Use structured prompts to find feasible research questions. |
| business-sage | Bundled instructions | Explore business plans, financial scenarios and facts that require current verification. |
| canvas-ui | External; separate setup | Review canvas-based interface components for custom interactions. |
| charlie-motion-graphics | External; separate setup | Translate a storyboard into motion graphics and animation sequences. |
| chatgpt-hermes-portability-kit | Bundled instructions | Adapt workflows and agent profiles to other platforms using authorized source material. |
| cli-anything | External; separate setup | Call an available application CLI adapter for the active task. |
| cli-anything-business-sage | Bundled instructions | Run structured business calculations through the available local harness. |
| cli-anything-catalog | External; separate setup | Find CLI adapters relevant to the current task. |
| cli-anything-universal-bridge | Bundled instructions | Register, check and run available application, browser and agent-tool routes on demand. |
| creative-thinking-for-research | Bundled instructions | Use reframing, analogy and combinations of ideas to open new research directions. |
| cursify | External; separate setup | Choose cursor interactions suited to an interface's purpose. |
| cybersecurity-library | External; separate setup | Find security guidance within an authorized audit scope. |
| data-analysis | Bundled instructions | Check data quality, statistical assumptions, tests and uncertainty. |
| deep-research | Bundled instructions | Frame questions, search the literature and synthesize checkable evidence. |
| design-taste | External; separate setup | Choose visual style, typography and composition for the brief. |
| evaluating-code-models | Bundled instructions | Evaluate code-model outputs using relevant tasks and benchmarks. |
| evaluating-llms-harness | Bundled instructions | Plan LLM evaluations with a compatible test harness and explicit budget. |
| explore-code | Bundled instructions | Implement experimental changes in an isolated workspace. |
| explore-run | Bundled instructions | Run bounded experiments with a budget and recorded results. |
| filmmaking-videography-photography-s2 | Bundled instructions | Plan concepts, direction, camera work, photography, editing, color and sound. |
| firecrawl-competitive-intel | Bundled instructions | Compare dated evidence of changes in products, pricing and features. |
| firecrawl-dashboard-reporting | Bundled instructions | Extract and check dashboard indicators for a report. |
| firecrawl-deep-research | Bundled instructions | Collect attributed web evidence for a research synthesis. |
| firecrawl-knowledge-base | Bundled instructions | Organize documents, chunks and source metadata into a knowledge base. |
| firecrawl-research-papers | Bundled instructions | Find and verify papers from relevant academic sources. |
| focus-my-energy | Bundled instructions | Match workload and a manageable first step to the energy the user reports. |
| generate-fresh-ideas | Bundled instructions | Generate alternative content ideas from several creative perspectives. |
| get-more-perspectives | Bundled instructions | Stress-test a decision from several perspectives before choosing. |
| github-research | Bundled instructions | Review a repository's license, design, maintenance and integration readiness. |
| goose | External; separate setup | Run code-change and test cycles when the separate Goose harness is available. |
| gpt-researcher | External; separate setup | Collect research material for Val to verify before handing over findings. |
| graphify | External; separate setup | Build a structural map of a project for finding relevant context. |
| harness2 | Bundled instructions | Explore harness improvements through deterministic demonstrations and human-reviewed proposals. |
| hermes-jev-skills | External; separate setup | Choose skills from context while keeping model routing disabled. |
| hermes-steel | External; separate setup | Use an available Steel browser integration for an authorized browsing task. |
| higgsfield-brandkit | External; separate setup | Apply a consistent brand identity to creative assets. |
| higgsfield-faceless-video | External; separate setup | Plan videos without an on-camera presenter using scripts, pacing and assets. |
| higgsfield-generate | External; separate setup | Generate or process media after the concept and parameters are approved. |
| higgsfield-marketplace-cards | External; separate setup | Plan product promotional cards for a specific channel and message. |
| higgsfield-product-photoshoot | External; separate setup | Plan product photographs, lighting and framing. |
| higgsfield-skills | Bundled instructions | Route an approved creative concept to the relevant Higgsfield module. |
| higgsfield-soul-id | External; separate setup | Keep a subject visually consistent using authorized references. |
| higgsfield-video-explainer | External; separate setup | Turn an explanation into a sequence of scenes. |
| higgsfield-websites | External; separate setup | Translate a product brief into a website concept and supporting assets. |
| higgsfield-youtube-thumbnail | External; separate setup | Design thumbnail concepts that match the video and channel identity. |
| humanizer-en | Bundled instructions | Edit English prose for natural wording while preserving meaning, author voice and citations. |
| humanizer-indonesia | Bundled instructions | Edit Indonesian prose for its audience while preserving meaning, terminology and citations. |
| idea-generation | Bundled instructions | Develop and filter research ideas through several review rounds. |
| langsmith-observability | Bundled instructions | Plan LangSmith tracing and evaluations in an approved environment. |
| literature-review | Bundled instructions | Build a literature review using multiple perspectives and source traceability. |
| match-my-writing-style | Bundled instructions | Apply the user's Voice Card to the audience and type of writing. |
| math-reasoning | Bundled instructions | Check mathematical reasoning steps and the conditions under which they hold. |
| mindrally-skills | External; separate setup | Find relevant implementation guidance in an external skill catalog. |
| motion-graphics-suite | Bundled instructions | Choose among four motion-graphics references for compositions that remain editable. |
| motion-primitives | External; separate setup | Design interface motion with reusable animation components. |
| nemo-evaluator-sdk | Bundled instructions | Plan model evaluations with NeMo Evaluator SDK when its dependencies are available. |
| notebooklm-thinking-datascience | Bundled instructions | Apply systems-thinking and data-science methods from the user's source index. |
| novelty-assessment | Bundled instructions | Test novelty claims against the closest studies and search limits. |
| paper-context-resolver | Bundled instructions | Tie reproduction decisions to paper sections, figures, tables or appendices. |
| paper-revision | Bundled instructions | Map reviewer comments to concrete edits and evidence of improvement. |
| paper-shaders | External; separate setup | Choose shader effects suited to the design and device budget. |
| paper-writing-section | Bundled instructions | Draft and edit an academic section with two review passes. |
| parenting-6d-gad-mdd | Bundled instructions | Support discussion with empathy, structure and respect for autonomy; this does not replace clinical care. |
| persona-shizuka-yukino-shikaku | Bundled instructions | Keep five-bot character voices, handoffs and task ownership consistent. |
| phoenix-observability | Bundled instructions | Plan Phoenix tracing and evaluations within the approved data scope. |
| playwright-best-practices | External; separate setup | Test user journeys and improve end-to-end test reliability. |
| ponytail | External; separate setup | Reduce unnecessary complexity and choose changes proportionate to the task. |
| prep-for-meetings | Bundled instructions | Prepare a meeting brief from available notes and goals. |
| prep-for-meetings-2 | Bundled instructions | Condense meeting material into key points and a quick reminder card. |
| rea | Optional, OFF; separate runtime | Optionally analyze owned JavaScript or archives through a local static-analysis CLI; native formats need separate engines. |
| rebuttal-writing | Bundled instructions | Draft point-by-point responses to supervisor or reviewer feedback. |
| remote-jobs | External; separate setup | Shortlist remote employers, then verify location requirements and current vacancies. |
| remotion-skills | External; separate setup | Build editable video compositions as code and render them when the runtime is available. |
| research-paper-writing | Bundled instructions | Review argument structure and the links between claims, evidence and discussion. |
| reverse-engineer-anything | External; separate setup | Inspect incident artifacts within an explicit forensic mandate. |
| scrapling | Bundled instructions | Extract CSS/XPath data from saved local HTML in an isolated parser runtime. |
| slide-generation | Bundled instructions | Build a presentation from checkable arguments, results and visuals. |
| strix | External; separate setup | Review the security of targets with an agreed scope and authorization. |
| superdesign-skill | External; separate setup | Review layout, design tokens and interface consistency. |
| superpowers | External; separate setup | Structure planning, implementation and validation for a code change. |
| symbolic-equation | Bundled instructions | Search for interpretable equations that can be tested against data. |
| table-generation | Bundled instructions | Build academic tables from verified results, units and notes. |
| timesfm-forecasting | Bundled instructions | Forecast numeric time series locally with TimesFM 2.5 after separate runtime and weight setup. |
| token-monitor | External; separate setup | Read additional quota status for budget decisions when a compatible source is available. |
| tokenshield | External; separate setup | Combine usage readings, cost estimates and budget checks without claiming a provider-enforced spending cap. |
| tokentracker | External; separate setup | Read available local usage data for budget decisions. |
| unlimited-ocr | External; separate setup | Plan a separately installed local OCR runtime and page index. |
| unlimited-ocr-2 | Bundled instructions | Route document and image extraction to available OCR with page-linked evidence. |
| unslop | Bundled instructions | Review and improve interface design; it changes UI, not the bot's prose style. |
| wise-judgment-and-sovereign-orchestrator | Bundled instructions | Coordinate workflow choices, budgets, approvals, delegation and synthesis of Val's findings. |

### Aliases

| Alias | Canonical name |
| --- | --- |
| auto-curiosity-for-film-making | auto-curiousity-for-film-making |

Source of the menu copy: [option_help.json](../configs/option_help.json), [application help](../skills/cli-anything-universal-bridge/scripts/connection_help.json). See [CLI](CLI.md), [REA](REA.md), and [third-party licenses](../THIRD_PARTY_NOTICES.md).
