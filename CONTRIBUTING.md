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

### Format

```
<type>(<optional scope>): <short description>

[optional body]

[optional footer(s)]
```

### Types

| Type | When to use |
|---|---|
| `feat` | A new feature (triggers a `MINOR` version bump) |
| `fix` | A bug fix (triggers a `PATCH` version bump) |
| `docs` | Documentation changes only |
| `style` | Formatting, whitespace — no logic change |
| `refactor` | Code restructuring without feature or fix |
| `perf` | Performance improvement |
| `test` | Adding or correcting tests |
| `build` | Build system or dependency changes |
| `ci` | CI/CD pipeline changes |
| `chore` | Maintenance tasks (housekeeping, tooling) |
| `revert` | Reverts a previous commit |

### Breaking Changes

Append `!` after the type, **or** add `BREAKING CHANGE:` in the footer:

```
feat!: remove deprecated API endpoint

BREAKING CHANGE: The /v1/users endpoint has been removed. Use /v2/users instead.
```

### Examples

**Good commits:**

```
feat(auth): add OAuth2 PKCE flow
fix(parser): handle empty input without panic
docs(readme): update local setup instructions
ci: add CodeQL scanning step
refactor(storage)!: replace MySQL driver with pgx
```

**Bad commits — these will fail CI:**

```
Fixed stuff
WIP
update
feat - add login
```

### Specification

Full specification: [conventionalcommits.org](https://www.conventionalcommits.org/en/v1.0.0/)

---

## Changelog

Every pull request that introduces a user-facing change **must** update `CHANGELOG.md` under the `[Unreleased]` section following [Keep a Changelog v1.1.0](https://keepachangelog.com/en/1.1.0/).

```markdown
## [Unreleased]

### Added
- Short description of new functionality (#PR-number)

### Changed
- Description of changed behaviour (#PR-number)

### Fixed
- Description of bug fix (#PR-number)

### Security
- Description of security fix (#PR-number)
```

> **CI enforcement:** The pipeline validates that any PR modifying source files also touches the `[Unreleased]` section. PRs that modify the changelog below an existing version header will fail.

---

## Branching Strategy

- **`main`** is the only long-lived branch. All work branches off `main` and merges back into `main`.
- **Keep your branch rebased** on top of `main` — merge commits in a PR branch are rejected by CI.
- Branch naming convention (loosely enforced):
  - `feat/<short-description>`
  - `fix/<short-description>`
  - `chore/<short-description>`
  - `ci/<short-description>`

```bash
# Keep your branch up-to-date
git fetch upstream
git rebase upstream/main
```

---

## Code Quality

All of the following gates run in CI. Run them locally before pushing to avoid wasted cycles.

| Gate | Command | Scope |
|---|---|---|
| Lint | `make lint` | Language-specific linter (see below) |
| Tests | `make test` | Unit + integration tests |
| SAST | CI only | CodeQL, Semgrep, Gitleaks |
| SCA | CI only | Trivy, govulncheck / Safety / OWASP Dependency-Check |

### Language-Specific Linters

| Language | Linter |
|---|---|
| Go | `golangci-lint` (config in `.golangci.yml`) |
| Python | `isort` + `black` + `flake8` + `mypy` |
| JavaScript / TypeScript | `eslint` |
| Java | Checkstyle via Gradle |
| C# | `dotnet format` |

New features **must** include corresponding tests. The CI pipeline enforces minimum coverage thresholds where configured.

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
