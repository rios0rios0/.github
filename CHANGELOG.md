# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This file is not edited by hand. Every change writes its own fragment under
`.changes/unreleased/` with [chlog](https://github.com/luizjhonata/chlog), and a release compiles
the pending fragments into a version section here — so two branches each adding an entry no
longer touch the same lines, and a rebase that used to conflict on this file now conflicts on
nothing.

When a new release is proposed:

1. Create a new branch `bump/x.x.x` (this isn't a long-lived branch!!!);
2. The fragments pending under `.changes/unreleased/` are compiled into a version section by `chlog batch auto && chlog merge` (AutoBump does this for you — it reads the fragments directly);
3. Open a Pull Request with the bump version changes targeting the `main` branch;
4. When the Pull Request is merged, a new Git tag must be created using <LINK TO THE PLATFORM TO OPEN THE PULL REQUEST>.

Releases to productive environments should run from a tagged version.
Exceptions are acceptable depending on the circumstances (critical bug fixes that can be cherry-picked, etc.).

## [Unreleased]

## [0.4.1] - 2026-08-28

### Changed

- changed the Claude Code workflows to callers: the reusable `workflow_call` definitions moved to [`rios0rios0/pipelines`](https://github.com/rios0rios0/pipelines) as `reusable-claude-review.yaml` and `reusable-claude-mention.yaml`. The `reusable-` prefix marks a definition, so the callers here drop it: `.github/workflows/claude-review.yaml`, `.github/workflows/claude-mention.yaml` and both `workflow-templates/` starter templates (with their paired `.properties.json`) now carry the same names a consuming repository uses, and pass `CLAUDE_CODE_OAUTH_TOKEN` explicitly instead of `secrets: inherit`, which fails Semgrep's `yaml.github-actions.security.secrets-inherit` rule. The starter templates are now byte-identical to the callers this account actually runs, so adopting one from the **Actions > New workflow** picker yields the same file every other repository has, job-level permissions included.

### Fixed

- changed the Claude workflow callers to single-quote every `types:` sequence entry, per the account YAML standard, and renamed the changelog fragment added by the previous change to chlog's documented `<unix-nanoseconds>-<four hex characters>.yaml` form -- its former suffix was not hexadecimal. The mention workflow is now named `Claude Mention` with a matching `claude-mention` job id.
- restored the `.changes/unreleased/` directory with a `.gitkeep`, so the release tooling keeps recognising this project as [chlog](https://github.com/luizjhonata/chlog)-based after a release consumes the last fragment. Git tracks files rather than directories, so the bump commit that removed the final fragment removed the directory too, and the next run read the empty `[Unreleased]` section as "nothing to release"
- restored the `id-token: write` permission on both Claude workflow callers. Without it the caller grants less than the reusable workflow declares, which GitHub rejects before the job starts -- runs ended in `startup_failure`. The action needs the scope because `setupGitHubToken()` exchanges a GitHub OIDC token for the GitHub App token it posts with, unless a `github_token` is passed explicitly.

### Removed

- removed the unused `id-token: write` permission from the Claude workflow callers, and changed `claude-review.yaml`'s display name to `Claude Review` so it matches its file name and its `Claude Mention` sibling. `anthropics/claude-code-action` needs `id-token: write` only for workload identity federation or the Bedrock / Vertex / Foundry OIDC paths; these authenticate with `claude_code_oauth_token`, so the scope allowed minting OIDC tokens for any audience without ever being used.

## [0.4.0] - 2026-08-26

### Added

- added a tailored `code-review` skill under `.github/skills/` so GitHub Copilot reviews changes against the [rios0rios0/guide](https://github.com/rios0rios0/guide/wiki) standards and this repository's own load-bearing invariants

### Changed

- changed the changelog to [chlog](https://github.com/luizjhonata/chlog) fragments: a change now writes its own YAML file under `.changes/unreleased/` through `chlog new --kind <Kind> --body "..."`, and `CHANGELOG.md` is GENERATED from them at release time by `chlog batch auto && chlog merge`. That is the one thing a single shared file cannot do — two branches each adding an entry no longer touch the same lines, so a rebase that used to conflict on `CHANGELOG.md` now conflicts on nothing. The `[Unreleased]` section was empty, so nothing had to be carried across. AutoBump already reads the fragments directly, so the release flow is unchanged.
- changed the fallback `CONTRIBUTING.md` so the changelog rule is stated conditionally, the way `PULL_REQUEST_TEMPLATE.md` already stated it. This file is GitHub's fallback for every repository without its own, and not every repository has adopted chlog yet: the Changelog section now splits explicitly into the `.chlog.yaml` case (add a fragment) and the no-`.chlog.yaml` case (edit `CHANGELOG.md` under `[Unreleased]`), and the prerequisites table marks chlog as needed only in the former.

## [0.3.2] - 2026-08-15

### Changed

- changed the documentation to record that the fleet-wide maintenance automation now covers `medhub-tech` and `prefy` alongside `rios0rios0`, while stating explicitly that this repository's community health fallback remains account-scoped by GitHub's design and does not reach those organizations

### Fixed

- fixed `README.md`, `CLAUDE.md`, and `.github/copilot-instructions.md` pointing the fleet-wide scheduled workflows at `rios0rios0/fleet-maintenance`, which was renamed to [`rios0rios0/config-automation`](https://github.com/rios0rios0/config-automation); the same references also named the retired `ai-docs-refresh` workflow and `harden_repos.py` script instead of the current `config-and-docs-refresh`, `release-reconcile`, and the `harden-repos` Go CLI

## [0.3.1] - 2026-05-29

### Changed

- changed the reusable Claude Code workflows `.github/workflows/claude.yaml` and `.github/workflows/claude-code-review.yaml` to pin `claude-opus-4-8` instead of `claude-opus-4-6`, so every `rios0rios0` repository consuming these reusable workflows runs the on-demand `@claude` and PR-review jobs on Claude Opus 4.8

## [0.3.0] - 2026-05-08

### Added

- added `.github/copilot-instructions.md` with repository purpose, conventions, and cross-reference to `CLAUDE.md` so GitHub Copilot sessions get the same non-obvious guidance (YAML extension rules, single-quote policy, actions pin discipline, template pairing)

## [0.2.2] - 2026-04-21

### Changed

- changed `.github/workflows/ai-docs-refresh.yaml` matrix concurrency from `max-parallel: 5` to `max-parallel: 1` so the refresh job iterates serially through the ~60 target repos, feeding Anthropic's API a steady drip instead of a parallel burst and keeping the per-minute rate limit out of the failure envelope; `README.md` and the adjacent workflow comment were updated to match
- tightened the `anthropics/claude-code-action@v1` allowlist in `.github/workflows/ai-docs-refresh.yaml` to `Read`, `Grep`, `Glob`, and path-scoped `Edit`/`Write` against only `CLAUDE.md` and `.github/copilot-instructions.md` via `--allowedTools`; prior runs logged `permission_denials_count: 30` per repo because the default harness let Claude probe tools that the scheduled context blocks, which burned turns and API spend on no-drift no-ops

### Fixed

- fixed `.github/workflows/ai-docs-refresh.yaml` pushing drift commits to the wrong repository — `anthropics/claude-code-action@v1` rewrites `origin` to point at `github.repository` (the workflow-hosting `.github` repo) regardless of which repository `actions/checkout@v6` pulled, so `git push origin` in the drift-detection step landed on `rios0rios0/.github` instead of the target repo and the subsequent `gh pr create --repo ${TARGET_REPO}` failed with `No commits between main and chore/ai-docs-refresh`; the drift-detection step now explicitly resets `origin` with an authenticated URL pointing at `${TARGET_REPO}` before pushing
- fixed `CLAUDE.md` references to workflow-template file extensions so both `*.yml` (language templates) and `*.yaml` (Claude templates) are covered when describing paired `*.properties.json` files and the inspection checklist

### Removed

- removed `.github/workflows/repo-compliance-audit.yaml`, `.github/workflows/ai-docs-refresh.yaml`, `scripts/harden_repos.py`, and `scripts/refresh_ai_docs_prompt.md`; the fleet-wide scheduled workflows and hardening script moved to [`rios0rios0/fleet-maintenance`](https://github.com/rios0rios0/fleet-maintenance) so this repo stays focused on community health files and workflow templates. `README.md` and `CLAUDE.md` were updated to point at the new home and drop the dedicated sections

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
