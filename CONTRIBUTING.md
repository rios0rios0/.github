# Contributing Guide

Thank you for your interest in contributing! This guide covers everything you need to know to get started and to meet the quality bar required for all [`rios0rios0`](https://github.com/rios0rios0) projects.

> **Security issues:** Please do **not** open a public issue. Read [`SECURITY.md`](SECURITY.md) first.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Getting Started](#getting-started)
3. [Commit Convention](#commit-convention)
4. [Changelog](#changelog)
5. [Branching Strategy](#branching-strategy)
6. [Code Quality](#code-quality)
7. [Pull Request Process](#pull-request-process)
8. [Local Development Setup](#local-development-setup)
9. [License](#license)

---

## Prerequisites

Make sure you have the following installed before you begin:

| Tool | Purpose |
|---|---|
| `git` | Version control |
| `make` | Task runner (lint, test, build) |
| `docker` | Containerised builds and tests |
| Language runtime | Go, Python, Java, Node.js, etc. — see the repository's own README |

---

## Getting Started

```bash
# 1. Fork the repository on GitHub, then clone your fork
git clone https://github.com/<your-username>/<repo>.git
cd <repo>

# 2. Add the upstream remote
git remote add upstream https://github.com/rios0rios0/<repo>.git

# 3. Create a feature branch from main
git checkout -b feat/my-feature

# 4. Set up the local development environment
make setup

# 5. Make your changes, then lint and test
make lint
make test

# 6. Push to your fork and open a Pull Request against main
git push origin feat/my-feature
```

---

## Commit Convention

**Conventional Commits is mandatory.** The CI pipeline validates every commit message and rejects non-conforming commits. [`autobump`](https://github.com/rios0rios0/autobump) relies on this to generate the `CHANGELOG.md` and determine the next semantic version automatically.

The format is `type(optional scope): short description`. Common types include `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, and `ci`. Append `!` after the type or add `BREAKING CHANGE:` in the footer to flag breaking changes.

> For the complete specification including all types, message format rules, and examples, see the [Git Flow](https://github.com/rios0rios0/guide/wiki/Git-Flow) page in the Development Guide.

---

## Changelog

Every pull request that introduces a user-facing change **must** update `CHANGELOG.md` under the `[Unreleased]` section following [Keep a Changelog v1.1.0](https://keepachangelog.com/en/1.1.0/). Use the standard categories: Added, Changed, Deprecated, Removed, Fixed, Security.

> **CI enforcement:** The pipeline validates that any PR modifying source files also touches the `[Unreleased]` section.

> For the full changelog standard and writing rules, see [Documentation & Change Control](https://github.com/rios0rios0/guide/wiki/Documentation-&-Change-Control) in the Development Guide.

---

## Branching Strategy

- **`main`** is the only long-lived branch. All work branches off `main` and merges back into `main`.
- **Keep your branch rebased** on top of `main` — merge commits in a PR branch are rejected by CI.

```bash
# Keep your branch up-to-date
git fetch upstream
git rebase upstream/main
```

> For the complete branching model, naming conventions, and rebase workflow, see [Git Flow](https://github.com/rios0rios0/guide/wiki/Git-Flow) in the Development Guide.

---

## Code Quality

All of the following gates run in CI. Run them locally before pushing to avoid wasted cycles.

| Gate | Command |
|---|---|
| Lint | `make lint` |
| Tests | `make test` |
| SAST | `make sast` (or individual targets: `make semgrep`, `make trivy`, `make hadolint`, `make gitleaks`) |

New features **must** include corresponding tests. The CI pipeline enforces minimum coverage thresholds where configured.

> For the full SAST toolchain, language-specific linters, and quality gate details, see [CI & CD](https://github.com/rios0rios0/guide/wiki/CI-&-CD) in the Development Guide.

---

## Pull Request Process

1. **Use the PR template** — fill in all sections honestly.
2. **One approval required** from a maintainer before merging.
3. **All CI stages must be green:**
   - Code Check (lint, format)
   - Security (SAST, SCA, secrets scanning)
   - Tests (unit, integration)
   - Management (CHANGELOG validation, commit message validation, rebase check)
   - Delivery (build, Docker image push — only on `main`)
4. **Squash or rebase merge only.** Merge commits are not allowed.
5. Link related issues with `Closes #<issue-number>` in the PR description.

---

## Local Development Setup

All repositories consume shared Makefile targets from the [`pipelines`](https://github.com/rios0rios0/pipelines) repository. The top of each `Makefile` looks like:

```makefile
SCRIPTS_DIR ?= $(HOME)/Development/github.com/rios0rios0/pipelines

-include $(SCRIPTS_DIR)/makefiles/common.mk
-include $(SCRIPTS_DIR)/makefiles/<language>.mk
```

### Setup Steps

```bash
# Clone the pipelines repo to the expected location (one-time)
mkdir -p $(HOME)/Development/github.com/rios0rios0
git clone https://github.com/rios0rios0/pipelines \
  $(HOME)/Development/github.com/rios0rios0/pipelines

# Bootstrap the project (installs tools, language runtimes, pre-commit hooks)
make setup

# Run the linter
make lint

# Run the tests
make test
```

> Individual repositories may have additional steps — always check the project's own `README.md`.

---

## License

By submitting a pull request you agree that your contribution will be licensed under the same **MIT License** that covers the project. See the `LICENSE` file in each repository.
