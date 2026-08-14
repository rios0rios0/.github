# .github

Default community health files, issue/PR templates, and workflow templates for all [`rios0rios0`](https://github.com/rios0rios0) repositories.

## What This Repository Is

This is a special `.github` repository that acts as the **default community health file hub** for every repository under the `rios0rios0` GitHub account. Any repository that does not define its own version of these files will automatically inherit them from here.

The fallback is **scoped to one account by GitHub's design** — it does not reach other organizations. The scheduled maintenance automation in [`config-automation`](https://github.com/rios0rios0/config-automation) now covers `medhub-tech` and `prefy` as well, but those organizations do not inherit anything from this repository; each would need its own `.github` repository to get these defaults.

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
| `.github/workflows/` | Reusable Claude Code workflows (PR assistant and automatic code review) |
| `workflow-templates/` | Reusable CI/CD starter workflows for each supported language stack |

## How the Fallback Mechanism Works

GitHub automatically applies files from this repository as defaults for any public repository under `rios0rios0` that does not contain its own copy of those files. This means:

- A new repository instantly gets issue templates, a PR template, contributing guidelines, and a code of conduct without any extra setup.
- Repositories can override any file by creating their own version at the same path.
- Workflow templates in `workflow-templates/` appear in the **Actions → New workflow** picker for all `rios0rios0` repositories.

See [GitHub's documentation on default community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file) for details.

## Claude Code Setup

The reusable Claude workflows in `.github/workflows/` require a `CLAUDE_CODE_OAUTH_TOKEN` secret on each repository that uses them. Since this is a personal account (no organization-level secrets), set the secret across all repos with:

> The loop below targets `rios0rios0` because no repository in `medhub-tech` or `prefy` calls these reusable workflows today. If one adopts them, run the same loop against that organization — secrets are per-repository, and nothing propagates across accounts.

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

## Fleet-Wide Scheduled Workflows

The daily `repo-compliance-audit`, the weekly `config-and-docs-refresh`, and the weekly `release-reconcile` workflows, along with the `harden-repos` Go CLI that drives them, live in a dedicated repository: **[rios0rios0/config-automation](https://github.com/rios0rios0/config-automation)**. See that repo's README for secret setup and manual dispatch instructions.

Those workflows are **not** limited to `rios0rios0`: they read a comma-separated `HARDEN_OWNER` list and currently cover `rios0rios0`, `medhub-tech`, and `prefy`. Adding an organization there means extending that list, not editing this repository.

## Related Repositories

- **[config-automation](https://github.com/rios0rios0/config-automation)** — Scheduled workflows that audit repo compliance daily, refresh configuration and AI-assistant guidance weekly, and reconcile missing release tags weekly, across every organization in `HARDEN_OWNER` (`rios0rios0`, `medhub-tech`, `prefy`).
- **[pipelines](https://github.com/rios0rios0/pipelines)** — Production-ready SDLC pipelines (GitHub Actions, GitLab CI, Azure DevOps). All workflow templates here delegate to reusable workflows defined there.
- **[autobump](https://github.com/rios0rios0/autobump)** — Automated CHANGELOG and release management enforcing Keep a Changelog + SemVer.
- **[guide](https://github.com/rios0rios0/guide/wiki)** — Development standards wiki covering Git Flow, architecture, CI/CD, security, testing, and code style conventions used across all `rios0rios0` projects.

