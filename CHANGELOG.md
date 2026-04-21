# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

When a new release is proposed:

1. Create a new branch `bump/x.x.x` (this isn't a long-lived branch!!!);
2. The Unreleased section on `CHANGELOG.md` gets a version number and date;
3. Open a Pull Request with the bump version changes targeting the `main` branch;
4. When the Pull Request is merged, a new Git tag must be created using <LINK TO THE PLATFORM TO OPEN THE PULL REQUEST>.

Releases to productive environments should run from a tagged version.
Exceptions are acceptable depending on the circumstances (critical bug fixes that can be cherry-picked, etc.).

## [Unreleased]

### Changed

- changed `.github/workflows/ai-docs-refresh.yaml` matrix concurrency from `max-parallel: 5` to `max-parallel: 1` so the refresh job iterates serially through the ~60 target repos, feeding Anthropic's API a steady drip instead of a parallel burst and keeping the per-minute rate limit out of the failure envelope; `README.md` and the adjacent workflow comment were updated to match
- tightened the `anthropics/claude-code-action@v1` allowlist in `.github/workflows/ai-docs-refresh.yaml` to `Read`, `Grep`, `Glob`, and path-scoped `Edit`/`Write` against only `CLAUDE.md` and `.github/copilot-instructions.md` via `--allowedTools`; prior runs logged `permission_denials_count: 30` per repo because the default harness let Claude probe tools that the scheduled context blocks, which burned turns and API spend on no-drift no-ops

## [0.2.1] - 2026-04-20

### Changed

- changed `.github/workflows/ai-docs-refresh.yaml` schedule from daily to weekly (Mondays at 07:00 UTC) to reduce drift-check noise and API usage; documentation in `README.md`, `CLAUDE.md`, the PR body, and `scripts/refresh_ai_docs_prompt.md` was updated accordingly

## [0.2.0] - 2026-04-19

### Added

- added `--list-json` mode to `scripts/harden_repos.py` that emits a JSON array of `{name, default_branch}` filtered to non-fork non-archived repos for GitHub Actions matrix consumption
- added `.github/workflows/ai-docs-refresh.yaml`, a daily matrix workflow that runs `anthropics/claude-code-action@v1` against every non-fork non-archived `rios0rios0` repo, reviews both `CLAUDE.md` and `.github/copilot-instructions.md` against the current code, and opens a single PR on the `chore/ai-docs-refresh` branch when either file has drifted
- added `.github/workflows/repo-compliance-audit.yaml`, a daily scheduled workflow that runs `harden_repos.py --phase 1 --fail-on-noncompliant` and fails CI when any repo drifts from the compliance policy
- added `CLAUDE.md` at the repo root to give future Claude Code sessions the project's purpose, the `harden_repos.py` phase model and invariants, and this repo's conventions
- added `scripts/harden_repos.py`, a compliance audit and hardening script for every `rios0rios0` GitHub repository (repo settings, Dependabot, secret scanning, branch protection, `main-protection` ruleset with admin bypass)
- added `scripts/refresh_ai_docs_prompt.md`, the prompt consumed by the refresh workflow that instructs Claude to cover both Claude Code and GitHub Copilot guidance files and make no edits when the existing files are accurate
- added `WIKI_ALLOWLIST` to `scripts/harden_repos.py` so repos that host an actual wiki (currently only `guide`) keep `has_wiki=True` without being flagged or reverted by phase 2; verified via `git ls-remote <repo>.wiki.git` that all other `has_wiki=True` repos had empty wikis
- added carve-outs to `scripts/harden_repos.py` compliance policy: `allow_auto_merge` is skipped for private repos (GitHub Free silently ignores the `PATCH`, making the check unfixable); `secret_scanning`, `push_protection`, `dependabot_alerts`, and `dependabot_updates` are skipped for forks (every upstream sync wipes Dependabot work and secret scanning belongs to the upstream owner). Phase 2 no longer attempts `allow_auto_merge=True` on private repos, and phase 3 now skips forks entirely with a `SKIP (fork)` line

### Changed

- clarified `COMPLIANCE_AUDIT_TOKEN` documentation in `README.md` and `.github/workflows/repo-compliance-audit.yaml` to distinguish classic PAT scopes from fine-grained PAT permissions
- updated `list_repos` in `scripts/harden_repos.py` to honor `HARDEN_OWNER` by selecting `/user/repos`, `/orgs/{owner}/repos`, or `/users/{owner}/repos` based on the authenticated user and the owner's account type
- updated `phase4_branch_protection` in `scripts/harden_repos.py` to skip repos when branch protection is unavailable due to plan/permissions
- updated `README.md` to document `scripts/harden_repos.py`, the `repo-compliance-audit` workflow, and the `COMPLIANCE_AUDIT_TOKEN` secret
- updated `scripts/harden_repos.py` ruleset compliance to validate the `non_fast_forward` rule and the `refs/heads/main` target, not just the ruleset name
- upgraded `actions/checkout` to `v6` and `actions/upload-artifact` to `v7` across all workflows for consistency on the latest major versions

### Fixed

- fixed `check_vulnerability_alerts` in `scripts/harden_repos.py` to return `None` on API failure instead of conflating "unavailable" with "disabled"; `compute_issues` now reports `dependabot_alerts=unknown` for the unknown state

## [0.1.0] - 2026-03-24

The changes weren't tracked until this version.
