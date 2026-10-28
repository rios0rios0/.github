# AGENTS.md

This file provides guidance to AI coding agents (Claude Code, Codex, Cursor, GitHub Copilot) when working with code in this repository.

## What This Repository Is

This is GitHub's special `.github` repository for the `rios0rios0` account. It serves two distinct purposes, and changes usually affect one of them:

1. **Community health file fallback** — files at the repo root (`CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `LICENSE`, `PULL_REQUEST_TEMPLATE.md`, `ISSUE_TEMPLATE/`, `FUNDING.yml`, `.editorconfig`) are automatically applied to every `rios0rios0` repository that does not define its own copy. Edits here propagate to the entire account.
2. **Workflow templates** — files in `workflow-templates/` appear in the **Actions → New workflow** picker across all `rios0rios0` repos. Each template (`*.yml`/`*.yaml`) has a paired `*.properties.json` (name/description/icon/categories); renaming one renames both. All templates are thin callers of reusable workflows in [`rios0rios0/pipelines`](https://github.com/rios0rios0/pipelines): the language templates pin the `@v3` major tag (e.g. `go-docker.yaml@v3`, `terra.yaml@v3`), while the Claude templates call `reusable-claude-review.yaml` / `reusable-claude-mention.yaml` at `@main`. The `reusable-` prefix marks a definition, so the callers — `workflow-templates/claude*.yaml` and this repo's own `.github/workflows/claude*.yaml` — drop it and are named `claude-review.yaml` / `claude-mention.yaml`, the same names a consuming repository uses. The Claude callers pass `CLAUDE_CODE_OAUTH_TOKEN` explicitly rather than with `secrets: inherit`.

**Fleet-wide scheduled workflows live elsewhere.** The daily `repo-compliance-audit`, the weekly `config-and-docs-refresh`, the weekly `release-reconcile`, and the `harden-repos` Go CLI that drives them live in [`rios0rios0/config-automation`](https://github.com/rios0rios0/config-automation). Changes to repo hardening policy, the refresh prompt, or any of those workflows belong there, not here.

**Community health fallback is account-scoped; the automation is not.** Files in this repo only reach `rios0rios0` repositories — GitHub's fallback does not cross accounts. The `config-automation` workflows read a comma-separated `HARDEN_OWNER` and currently cover `rios0rios0`, `medhub-tech`, and `prefy`. So "every repo we maintain" and "every repo that inherits these files" are different sets: do not widen wording here to imply the other organizations inherit anything from this repository.

## Build / Test / Lint

There is no build, test, or lint tooling in this repo. Pull requests run `.github/workflows/checks.yaml`, the shared `rios0rios0/pipelines` gate for rebase status and the changelog-fragment rule. Everything else is validated by inspection — verify YAML syntax, confirm `workflow-templates/*.yml` and `workflow-templates/*.yaml` still have their paired `*.properties.json`, and ensure every `uses:` names a reusable workflow that exists in `rios0rios0/pipelines`.

## Conventions Specific to This Repo

- **YAML files must use `.yaml`** (not `.yml`), with string values single-quoted. The existing `workflow-templates/*.yml` predate this rule and intentionally match GitHub's template filename convention — leave them as-is. `FUNDING.yml` and `ISSUE_TEMPLATE/config.yml` keep their names because GitHub looks them up exactly. New workflows under `.github/workflows/` should follow the single-quote rule.
- **Actions pins:** no workflow here calls a third-party action — every `uses:` points at a reusable workflow in `rios0rios0/pipelines`, which pins its own actions to commit SHAs. Language templates stay on `@v3`; the Claude callers and `.github/workflows/checks.yaml` stay on `@main`.
- **Changelog discipline:** every change writes its own fragment with `chlog new --kind <Kind> --body '...'` in the same commit. `CHANGELOG.md` is generated from the fragments and is never edited by hand. Simple past tense, backticks around code identifiers.
- **Commits:** `type(SCOPE): message` in simple past tense, no trailing period. See the guide's [Git-Flow](https://github.com/rios0rios0/guide/wiki/Git-Flow) page.

## Related Repositories (load-bearing context)

- [`rios0rios0/config-automation`](https://github.com/rios0rios0/config-automation) — scheduled fleet-wide workflows (compliance audit, config/docs refresh, release reconciliation) and the `harden-repos` Go CLI. Changes to repo hardening policy or any scheduled workflow belong there. Covers `rios0rios0`, `medhub-tech`, and `prefy` via `HARDEN_OWNER`.
- [`rios0rios0/pipelines`](https://github.com/rios0rios0/pipelines) — every workflow template and workflow here delegates to reusable workflows there (language templates at `@v3`, the rest at `@main`). Changes to pipeline behavior belong in that repo, not here.
- [`rios0rios0/autobump`](https://github.com/rios0rios0/autobump) — releases `CHANGELOG.md` entries into versioned sections.
- [`rios0rios0/guide`](https://github.com/rios0rios0/guide/wiki) — canonical development standards (architecture, Git flow, testing, code style).

<!-- chlog:start -->
## Changelog (chlog) — MANDATORY

If the repository you are working in uses chlog (a `.chlog.yaml` or `.chlog.yml`
config file, or a `.changes/` directory, exists at the project root), the
following is binding and ALWAYS applies: whenever you make ANY change, you MUST
create a changelog fragment as part of the same change — automatically, without
being asked, before committing.

- Do NOT edit CHANGELOG.md directly; it is generated from fragments.
- Create the fragment with:
  `chlog new --kind <Kind> --body '<past-tense description>'`
- Write an apostrophe inside the single-quoted body as `'\''`.
- Valid kinds: Added, Changed, Deprecated, Removed, Fixed, Security
- Choose the kind that best matches the change (e.g., new feature → Added,
  bug fix → Fixed, behavior change → Changed, removal → Removed, security fix → Security).
- If the change is backward-INCOMPATIBLE with the public API (a breaking
  change), you MUST add the `--breaking` flag:
  `chlog new --kind <Kind> --breaking --body '<past-tense description>'`.
  This is the ONLY thing that triggers a major version bump — the kind alone
  never does (per SemVer, major = incompatible change). When unsure whether a
  change breaks compatibility, ask the user instead of guessing.
- Fragments are YAML files in `.changes/unreleased/`; stage them with your commit.
- `chlog check` fails the build when a fragment is missing — never skip it.
<!-- chlog:end -->
