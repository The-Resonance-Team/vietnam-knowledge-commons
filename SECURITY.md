# Security Policy

## Reporting a vulnerability

Use GitHub's **private vulnerability reporting** on this repository (Security tab → "Report a vulnerability"). Do not open a public issue for security problems. Maintainers aim to acknowledge within 72 hours.

## Scope

This is a data project; the realistic risks are data-integrity and privacy issues, not remote code execution:

- **Personal data leakage** — a committed record, example, or fixture containing real personal data (names with IDs, filled forms, phone numbers, addresses of private individuals). This is our highest-severity class: report immediately.
- **Credential leakage** — tokens, keys, or authenticated URLs in code, configs, or data.
- **Provenance forgery** — records citing sources they did not come from, or checksums that don't match.
- **License misrepresentation** — content marked more open than its source permits.

## Data-safety rules (apply to every contribution)

- No personal data, no filled forms, no credentials — in code, tests, examples, fixtures, or issues.
- CI validates schemas and registries; it cannot catch a leaked secret. If you commit one, rotate it immediately, then purge history.
- Phase 0 tooling performs **no network access** — the CLI validates local files only. Report any dependency that changes that.
