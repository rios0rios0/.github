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

### Added

- added `scripts/harden_repos.py`, a compliance audit and hardening script for every `rios0rios0` GitHub repository (repo settings, Dependabot, secret scanning, branch protection, `main-protection` ruleset with admin bypass)
- added `.github/workflows/repo-compliance-audit.yaml`, a daily scheduled workflow that runs `harden_repos.py --phase 1 --fail-on-noncompliant` and fails CI when any repo drifts from the compliance policy
- added `CLAUDE.md` at the repo root to give future Claude Code sessions the project's purpose, the `harden_repos.py` phase model and invariants, and this repo's conventions
- added `.github/workflows/claude-md-refresh.yaml`, a daily workflow that runs `anthropics/claude-code-action@v1` against every non-fork non-archived `rios0rios0` repo and opens a PR only when the target repo's `CLAUDE.md` has drifted from its code
- added `scripts/refresh_claude_md_prompt.md`, the prompt consumed by the refresh workflow that instructs Claude to make no edits when the existing `CLAUDE.md` is accurate
- added `--list-json` mode to `scripts/harden_repos.py` that emits a JSON array of `{name, default_branch}` filtered to non-fork non-archived repos for GitHub Actions matrix consumption

### Changed

- updated `README.md` to document `scripts/harden_repos.py`, the `repo-compliance-audit` workflow, and the `COMPLIANCE_AUDIT_TOKEN` secret
- clarified `COMPLIANCE_AUDIT_TOKEN` documentation in `README.md` and `.github/workflows/repo-compliance-audit.yaml` to distinguish classic PAT scopes from fine-grained PAT permissions
- updated `list_repos` in `scripts/harden_repos.py` to honor `HARDEN_OWNER` by selecting `/user/repos`, `/orgs/{owner}/repos`, or `/users/{owner}/repos` based on the authenticated user and the owner's account type
- updated `scripts/harden_repos.py` ruleset compliance to validate the `non_fast_forward` rule and the `refs/heads/main` target, not just the ruleset name
- updated `phase4_branch_protection` in `scripts/harden_repos.py` to skip repos when branch protection is unavailable due to plan/permissions
- upgraded `actions/checkout` to `v6` and `actions/upload-artifact` to `v7` across all workflows for consistency on the latest major versions

### Fixed

- fixed `check_vulnerability_alerts` in `scripts/harden_repos.py` to return `None` on API failure instead of conflating "unavailable" with "disabled"; `compute_issues` now reports `dependabot_alerts=unknown` for the unknown state

### Removed


## [0.1.0] - 2026-03-24

The changes weren't tracked until this version.
