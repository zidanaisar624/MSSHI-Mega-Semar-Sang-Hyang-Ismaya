# Install MSSHI for this user

MSSHI is a collection of portable skill instructions, optional runtime adapters and a guarded setup CLI. Read [README.md](README.md), [VERSION.json](VERSION.json) and the selected host's current documentation before applying changes. User instructions and existing account choices take precedence over this document.

1. Identify the actual host, existing skill directories and user-selected mode. On Hermes, use its real data root, including custom C:/D: locations. Do not create a second home just to match an example.
2. Download/clone this repository into a separate source/cache directory. Do not place `.git`, `node_modules`, model weights or full upstream checkouts under the host's scanned `skills` directory.
3. Preview the selected plan with `python scripts/install_msshi.py --platform HOST --mode MODE --target-dir PATH`. Replace the placeholders; use `--apply` only within the user's authorized scope.
4. For Hermes's five-bot preset, use the actual root's `profiles` directory. The installer provisions five named native profiles; default remains neutral. Preserve existing SOUL, chat history, credentials and every primary/MoA/delegation model/provider choice. Native team routing uses supported plugin APIs; custom backends are retained.
5. To install a global terminal launcher, run `install.ps1 -SourcePath PATH` on Windows or `bash install.sh --source-dir PATH` on macOS/Linux. The bundled PDF is automatically copied to Downloads/MSSHI_Manuals (or the configured destination); `-NoPdf` / `--no-pdf` opts out. Inspect every optional feature's explanation before selecting it.
6. Optional runtime/model/account setup is separate. KAT is Coder-only and opens an endpoint/key wizard; it must not be reported as active without its prerequisites. See [KAT](docs/CODER_KAT.md), [contextual sources](docs/CONTEXTUAL_INTEGRATIONS.md) and `msshi choices`.
7. Verify with help, static audits and local fixtures first. Do not spend model/API credits, send messages, publish output, import browser sessions or buy cloud resources merely to test installation.

For ChatGPT Projects/Custom GPTs use the portable Knowledge/Instructions files instead of claiming a terminal plugin was installed. For other hosts use supported discovery/install routes; a README example is not evidence that an unavailable host command exists. Report the actual installed files, pending dependencies and rollback receipt.

## Public preset selection (v3.1.2)

For a fresh Hermes installation, `academic-mahasiswa` is the initial choice for Indonesian S1/S2/S3 students. `academic-dosen` is a separate lecturer/campus-leadership option. The existing `muza-preset`, solo, custom-bots, and selective modes remain available. Preserve an existing installation's preset and custom SOUL files unless the user explicitly chooses a change; explain any retained custom persona instead of overwriting it.

Use `msshi setup --mode academic-mahasiswa --platform hermes` or the corresponding `academic-dosen`/`muza-preset` command. The Academic preset keeps profile/status notes, meeting templates and role outputs inside native Hermes home at `workspace/academic`. It does not create an Obsidian vault, connect accounts, transfer cookies, supply models/providers/API keys, or grant access to any Private folder. Ask for the user's preferred form of address rather than assuming the preset creator's identity.

Apps remain on demand. Academic defaults prioritize document/slide/data tools. Heavy CAD/3D/recording/security routes need a separately named opt-in plus an installed executable; no app is launched by registering its route. Confirm tools, budget and meeting-recording permission before actual use. Generated minutes must be based on supplied notes or an authorized transcript, never invented from the planned agenda.
