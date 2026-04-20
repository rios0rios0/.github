# .github

Default community health files, issue/PR templates, and workflow templates for all [`rios0rios0`](https://github.com/rios0rios0) repositories.

## What This Repository Is

This is a special `.github` repository that acts as the **default community health file hub** for every repository under the `rios0rios0` GitHub account. Any repository that does not define its own version of these files will automatically inherit them from here.

## What It Contains

| Path | Purpose |
|---|---|
| `CONTRIBUTING.md` | Default contributing guide (Conventional Commits, Make workflow, branching strategy) |
| `CODE_OF_CONDUCT.md` | Contributor Covenant v2.1 |
| `SECURITY.md` | Responsible disclosure policy and security tooling overview |
| `FUNDING.yml` | GitHub Sponsors configuration |
| `LICENSE` | MIT License |
| `.editorconfig` | Editor configuration defaults |
| `ISSUE_TEMPLATE/` | YAML-based bug report and feature request forms |
| `PULL_REQUEST_TEMPLATE.md` | Default PR checklist |
| `.github/workflows/` | Reusable Claude Code workflows (PR assistant and automatic code review) and the daily org-wide `repo-compliance-audit` workflow |
| `workflow-templates/` | Reusable CI/CD starter workflows for each supported language stack |
| `scripts/harden_repos.py` | Repo hardening and compliance-audit script, invoked by the `repo-compliance-audit` workflow and the `/harden-repos` Claude slash command |

## How the Fallback Mechanism Works

GitHub automatically applies files from this repository as defaults for any public repository under `rios0rios0` that does not contain its own copy of those files. This means:

- A new repository instantly gets issue templates, a PR template, contributing guidelines, and a code of conduct without any extra setup.
- Repositories can override any file by creating their own version at the same path.
- Workflow templates in `workflow-templates/` appear in the **Actions → New workflow** picker for all `rios0rios0` repositories.

See [GitHub's documentation on default community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file) for details.

## Claude Code Setup

The reusable Claude workflows in `.github/workflows/` require a `CLAUDE_CODE_OAUTH_TOKEN` secret on each repository that uses them. Since this is a personal account (no organization-level secrets), set the secret across all repos with:

```bash
read -sp 'CLAUDE_CODE_OAUTH_TOKEN: ' TOKEN && echo
for repo in $(gh repo list rios0rios0 --limit 1000 --json name -q '.[].name'); do
  echo -n "rios0rios0/${repo}: "
  if echo "$TOKEN" | gh secret set CLAUDE_CODE_OAUTH_TOKEN -R "rios0rios0/${repo}"; then
    echo "OK"
  else
    echo "SKIP (see error above)"
  fi
done
```

Then add the caller workflows to each repo (or use the workflow templates from the **Actions > New workflow** picker):

- `workflow-templates/claude.yaml` — Claude PR assistant (`@claude` mentions)
- `workflow-templates/claude-code-review.yaml` — automatic code review on PRs

## Repo Compliance Audit

`.github/workflows/repo-compliance-audit.yaml` runs daily (and on demand via `workflow_dispatch`) and invokes `scripts/harden_repos.py --phase 1 --fail-on-noncompliant`. The job fails if any `rios0rios0` repo drifts from the compliance policy (Dependabot on, secret scanning + push protection on public repos, branch protection with required signatures, `main-protection` ruleset with admin bypass, `has_wiki`/`has_projects` off, etc.).

The workflow reads from a `COMPLIANCE_AUDIT_TOKEN` repository secret. Create a Personal Access Token and store it:

```bash
gh secret set COMPLIANCE_AUDIT_TOKEN -R rios0rios0/.github
```

The token must be able to list all private repos under the account and read security/ruleset endpoints. You can use either:

- **Classic PAT** with the `repo` and `admin:repo_hook` scopes (simplest option); or
- **Fine-grained PAT** scoped to all repositories under the account, with read access to `Administration`, `Contents`, `Metadata`, `Webhooks`, and read/write (or as needed) access to `Dependabot alerts` and `Secret scanning alerts`. Fine-grained PATs use per-resource permissions rather than OAuth scopes.

To apply remediation locally (phases 2–4), use the `/harden-repos` Claude slash command, which wraps the same `scripts/harden_repos.py` from your `~/.claude/scripts/` copy.

## AI Assistant Docs Refresh

`.github/workflows/ai-docs-refresh.yaml` runs weekly on Mondays at 07:00 UTC (one hour after the compliance audit). For every non-fork non-archived `rios0rios0` repo it:

1. Enumerates targets via `python3 scripts/harden_repos.py --list-json`.
2. Checks out each repo into a matrix job (`max-parallel: 5`).
3. Invokes `anthropics/claude-code-action@v1` with the prompt in `scripts/refresh_ai_docs_prompt.md`, which instructs Claude to compare both `CLAUDE.md` and `.github/copilot-instructions.md` against the code and update whichever has **drifted**.
4. Marks each file intent-to-add (`git add -N`) so newly created files in repos that lacked `CLAUDE.md` or `.github/copilot-instructions.md` are visible to the diff, then detects meaningful drift with `git diff -w --quiet -- CLAUDE.md .github/copilot-instructions.md`. If drift is found, force-pushes to a stable `chore/ai-docs-refresh` branch on the target repo and opens (or updates) a single combined PR. Repos where both files are accurate get no PR.

The workflow needs two repository secrets on `rios0rios0/.github`:

| Secret | Purpose | Scope |
|---|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | Authenticates `anthropics/claude-code-action@v1` (already set for the existing Claude workflows). | n/a |
| `CLAUDE_MD_REFRESH_TOKEN` | Pushes the `chore/ai-docs-refresh` branch and opens PRs on every target repo. Distinct from the read-only `COMPLIANCE_AUDIT_TOKEN`. | Fine-grained PAT scoped to all repositories under `rios0rios0`, with `Contents: write`, `Pull requests: write`, and `Metadata: read`. |

To test against a single repo before letting the cron run account-wide, trigger the workflow manually with the `repo` input:

```bash
gh workflow run ai-docs-refresh.yaml -R rios0rios0/.github -f repo=autobump
```

## Related Repositories

- **[pipelines](https://github.com/rios0rios0/pipelines)** — Production-ready SDLC pipelines (GitHub Actions, GitLab CI, Azure DevOps). All workflow templates here delegate to reusable workflows defined there.
- **[autobump](https://github.com/rios0rios0/autobump)** — Automated CHANGELOG and release management enforcing Keep a Changelog + SemVer.
- **[guide](https://github.com/rios0rios0/guide/wiki)** — Development standards wiki covering Git Flow, architecture, CI/CD, security, testing, and code style conventions used across all `rios0rios0` projects.

