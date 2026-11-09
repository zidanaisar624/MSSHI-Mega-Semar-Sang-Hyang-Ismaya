---
name: chatgpt-hermes-portability-kit
description: Builds a portable knowledge and skill inventory for Hermes and compatible agent hosts.
---

# chatgpt-hermes-portability-kit

Builds a portable knowledge and skill inventory for Hermes and compatible agent hosts.

## Workflow

1. Inventory the user-authorized source material, skills, index entries, desired host and capabilities already available. Distinguish content, local runtime dependencies, account-scoped connectors and private preferences.
2. Create a portable manifest with relative paths, provenance, purpose and prerequisites. Keep account identifiers, credentials, private documents and user voice samples out of public packages.
3. For each target host, map capabilities to documented supported mechanisms. Markdown instructions can transfer as skill guidance; accounts, tool registrations and runtime integration require host-specific configuration.
4. Validate a small representative workflow locally or by dry-run. Return the portable manifest, per-host setup notes and a list of items needing configuration or authorization.
