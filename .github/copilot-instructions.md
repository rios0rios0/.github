This is the `.github` repository for the `rios0rios0` account — community health file defaults and workflow templates for all repos.

## Repository purpose

1. **Community health file fallback** — root files (`CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `LICENSE`, `PULL_REQUEST_TEMPLATE.md`, `ISSUE_TEMPLATE/`, `FUNDING.yml`, `.editorconfig`) propagate to every `rios0rios0` repo that lacks its own copy.
2. **Workflow templates** — `workflow-templates/` entries appear in the Actions picker. Language templates (`*.yml`) call `rios0rios0/pipelines` reusable workflows (`@v3`). Claude templates (`*.yaml`) call reusable workflows in `.github/workflows/` of this repo.

## Conventions

- **YAML extension**: new workflows use `.yaml`, not `.yml`. Existing `workflow-templates/*.yml` are grandfathered — leave them as-is.
- **YAML strings**: single-quoted.
- **Actions pins**: keep all workflows on the same latest major (`actions/checkout@v6`, `anthropics/claude-code-action@v1`). Bump everywhere in one commit.
- **Changelog**: every change writes its own fragment with `chlog new --kind <Kind> --body "..."` in the same commit; `CHANGELOG.md` is generated from them and never edited by hand. Simple past tense.
- **Commits**: `type(SCOPE): message`, simple past tense, no trailing period.
- **Template pairing**: every `workflow-templates/*.yml` or `*.yaml` must have a paired `*.properties.json`.

## No build tooling

Validate by inspection: YAML syntax, template pairing, and workflow input declarations.

## Related repos

- `rios0rios0/config-automation` — fleet-wide scheduled workflows (compliance audit, config/docs refresh, release reconciliation) and the `harden-repos` Go CLI. Not here. Covers `rios0rios0`, `medhub-tech`, and `prefy` via its comma-separated `HARDEN_OWNER`.
- `rios0rios0/pipelines` — reusable CI/CD workflows called by language templates.

See `CLAUDE.md` at the repo root for full context.

<!-- chlog:start -->
## Changelog (chlog) — MANDATORY

If the repository you are working in uses chlog (a `.chlog.yaml` or `.chlog.yml`
config file, or a `.changes/` directory, exists at the project root), the
following is binding and ALWAYS applies: whenever you make ANY change, you MUST
create a changelog fragment as part of the same change — automatically, without
being asked, before committing.

- Do NOT edit CHANGELOG.md directly; it is generated from fragments.
- Create the fragment with:
  `chlog new --kind <Kind> --body "<imperative description>"`
- Valid kinds: Added, Changed, Deprecated, Removed, Fixed, Security
- Choose the kind that best matches the change (e.g., new feature → Added,
  bug fix → Fixed, behavior change → Changed, removal → Removed, security fix → Security).
- If the change is backward-INCOMPATIBLE with the public API (a breaking
  change), you MUST add the `--breaking` flag:
  `chlog new --kind <Kind> --breaking --body "<description>"`.
  This is the ONLY thing that triggers a major version bump — the kind alone
  never does (per SemVer, major = incompatible change). When unsure whether a
  change breaks compatibility, ask the user instead of guessing.
- Fragments are YAML files in `.changes/unreleased/`; stage them with your commit.
- `chlog check` fails the build when a fragment is missing — never skip it.
<!-- chlog:end -->
