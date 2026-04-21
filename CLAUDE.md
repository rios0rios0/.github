# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

This is GitHub's special `.github` repository for the `rios0rios0` account. It serves two distinct purposes, and changes usually affect one of them:

1. **Community health file fallback** — files at the repo root (`CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `LICENSE`, `PULL_REQUEST_TEMPLATE.md`, `ISSUE_TEMPLATE/`, `FUNDING.yml`, `.editorconfig`) are automatically applied to every `rios0rios0` repository that does not define its own copy. Edits here propagate to the entire account.
2. **Workflow templates and reusable Claude Code workflows** — files in `workflow-templates/` appear in the **Actions → New workflow** picker across all `rios0rios0` repos. Each workflow template (`*.yml`/`*.yaml`) has a paired `*.properties.json` (name/description/icon/categories). All templates are thin wrappers that call reusable workflows from [`rios0rios0/pipelines`](https://github.com/rios0rios0/pipelines) via `uses: rios0rios0/pipelines/.github/workflows/<lang>-docker.yaml@v3`. `.github/workflows/claude.yaml` and `.github/workflows/claude-code-review.yaml` are reusable Claude Code workflows (`workflow_call`) consumed by `workflow-templates/claude*.yaml` in every repo.

**Fleet-wide scheduled workflows live elsewhere.** The daily `repo-compliance-audit`, the weekly `ai-docs-refresh`, and the `harden_repos.py` hardening script now live in [`rios0rios0/fleet-maintenance`](https://github.com/rios0rios0/fleet-maintenance). Changes to repo hardening policy, the AI docs refresh prompt, or either workflow belong there, not here.

## Build / Test / Lint

There is no build, test, or lint tooling in this repo. Changes are validated by inspection — verify YAML syntax, confirm `workflow-templates/*.yml` and `workflow-templates/*.yaml` still have their paired `*.properties.json`, and ensure reusable workflows still accept their declared inputs.

## Conventions Specific to This Repo

- **YAML files must use `.yaml`** (not `.yml`), with string values single-quoted. The existing `workflow-templates/*.yml` predate this rule and intentionally match GitHub's template filename convention — leave them as-is. New workflows under `.github/workflows/` should follow the single-quote rule.
- **Actions pins:** keep every workflow on the same latest major (currently `actions/checkout@v6`, `anthropics/claude-code-action@v1`). When bumping, bump across all workflows in the same commit.
- **Changelog discipline:** every change goes under `[Unreleased]` in `CHANGELOG.md` in the same commit. Keep a Changelog format, simple past tense, backticks around code identifiers.
- **Commits:** `type(SCOPE): message` in simple past tense, no trailing period. See `.claude/rules/git-flow.md` in the user's global rules.

## Related Repositories (load-bearing context)

- [`rios0rios0/fleet-maintenance`](https://github.com/rios0rios0/fleet-maintenance) — scheduled fleet-wide workflows (compliance audit + AI docs refresh) and the `harden_repos.py` hardening script. Changes to repo hardening policy or either scheduled workflow belong there.
- [`rios0rios0/pipelines`](https://github.com/rios0rios0/pipelines) — all workflow templates here delegate to reusable workflows there (`@v3`). Changes to pipeline behavior belong in that repo, not here.
- [`rios0rios0/autobump`](https://github.com/rios0rios0/autobump) — releases `CHANGELOG.md` entries into versioned sections.
- [`rios0rios0/guide`](https://github.com/rios0rios0/guide/wiki) — canonical development standards (architecture, Git flow, testing, code style).
