# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

This is GitHub's special `.github` repository for the `rios0rios0` account. It serves three distinct purposes, and changes usually affect one of them:

1. **Community health file fallback** — files at the repo root (`CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `LICENSE`, `PULL_REQUEST_TEMPLATE.md`, `ISSUE_TEMPLATE/`, `FUNDING.yml`, `.editorconfig`) are automatically applied to every `rios0rios0` repository that does not define its own copy. Edits here propagate to the entire account.
2. **Workflow templates** — files in `workflow-templates/` appear in the **Actions → New workflow** picker across all `rios0rios0` repos. Each `*.yml` has a paired `*.properties.json` (name/description/icon/categories). All templates are thin wrappers that call reusable workflows from [`rios0rios0/pipelines`](https://github.com/rios0rios0/pipelines) via `uses: rios0rios0/pipelines/.github/workflows/<lang>-docker.yaml@v3`.
3. **Reusable workflows & cross-repo automation** — files in `.github/workflows/` run inside this repo (and are called by other repos):
   - `claude.yaml` / `claude-code-review.yaml` — reusable Claude Code workflows (`workflow_call`), consumed by `workflow-templates/claude*.yaml` in every repo.
   - `repo-compliance-audit.yaml` — daily (06:00 UTC) audit that runs `scripts/harden_repos.py --phase 1 --fail-on-noncompliant` against all `rios0rios0` repos.
   - `ai-docs-refresh.yaml` — daily (07:00 UTC) matrix workflow that enumerates non-fork non-archived repos via `harden_repos.py --list-json`, invokes `anthropics/claude-code-action@v1` on each one with the prompt in `scripts/refresh_ai_docs_prompt.md`, and opens a PR on the target repo **only when `CLAUDE.md` or `.github/copilot-instructions.md` has drifted**. Drift detection uses `git add -N` (intent-to-add) followed by `git diff -w --quiet` so both modified and newly-created files count; whitespace-only diffs are ignored. Branch name is stable (`chore/ai-docs-refresh`) and force-pushed so repeated runs update a single open PR rather than creating new ones.

## Build / Test / Lint

There are no build, test, or lint commands. The only runnable code is `scripts/harden_repos.py` (pure stdlib Python 3.12 + the `gh` CLI). To validate a change to the script:

```bash
python3 -c "import ast; ast.parse(open('scripts/harden_repos.py').read())"
python3 scripts/harden_repos.py --dry-run                # exercises phases 1-4 without mutating anything
python3 scripts/harden_repos.py --phase 1 --repo <name>  # single-repo audit
```

## The `harden_repos.py` Script

This script is the heart of the compliance system. Understanding its phase model is required before editing:

- **Phase 1 (`--phase 1`)** — read-only audit. Builds an `audits` list of dicts (one per repo) and writes `/tmp/gh_hardening_audit_before.json`. With `--fail-on-noncompliant` (used by CI) it exits 1 when `compute_issues()` reports any violations.
- **Phase 2/3/4** — mutations. Each first re-runs phase 1 to get fresh audit data, then applies only the diffs. Phase 4 (branch protection + `main-protection` ruleset) skips private repos and repos where `protection_available=False`.
- **Phase 5** — re-audits and diffs against the phase-1 snapshot on disk.
- **`--dry-run`** — runs phases 1-4 with no side effects; `--phase` is ignored.

Key invariants to preserve when modifying:

- `list_repos()` branches on authenticated user vs `HARDEN_OWNER` and owner account type (`User`/`Organization`). Keep all three code paths (`/user/repos`, `/users/{owner}/repos`, `/orgs/{owner}/repos`) in sync.
- `check_vulnerability_alerts()` is tri-state (`True`/`False`/`None` for unknown). `compute_issues()` distinguishes `unknown` from `off` — don't collapse them.
- Ruleset compliance checks three things together: the ruleset name exists, the `non_fast_forward` rule is present, and `conditions.ref_name.include` targets `refs/heads/main`. A name-only match is not compliant.
- `RULESET_BODY` bypasses `actor_type=RepositoryRole, actor_id=5` (Repository Admin) so the owner can force-push. `BRANCH_PROTECTION_BODY` sets `enforce_admins=False` for the same reason. Don't tighten either without intent.

## Conventions Specific to This Repo

- **YAML files must use `.yaml`** (not `.yml`), with string values single-quoted. The existing `workflow-templates/*.yml` predate this rule and intentionally match GitHub's template filename convention — leave them as-is. New workflows under `.github/workflows/` should follow the single-quote rule.
- **Actions pins:** keep every workflow on the same latest major (currently `actions/checkout@v6`, `actions/upload-artifact@v7`, `actions/setup-python@v6`, `anthropics/claude-code-action@v1`). When bumping, bump across all three workflows in the same commit.
- **Changelog discipline:** every change goes under `[Unreleased]` in `CHANGELOG.md` in the same commit. Keep a Changelog format, simple past tense, backticks around code identifiers.
- **Commits:** `type(SCOPE): message` in simple past tense, no trailing period. See `.claude/rules/git-flow.md` in the user's global rules.

## Related Repositories (load-bearing context)

- [`rios0rios0/pipelines`](https://github.com/rios0rios0/pipelines) — all workflow templates here delegate to reusable workflows there (`@v3`). Changes to pipeline behavior belong in that repo, not here.
- [`rios0rios0/autobump`](https://github.com/rios0rios0/autobump) — releases `CHANGELOG.md` entries into versioned sections.
- [`rios0rios0/guide`](https://github.com/rios0rios0/guide/wiki) — canonical development standards (architecture, Git flow, testing, code style).
