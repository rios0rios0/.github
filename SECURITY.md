# Security Policy

## Scope

This policy applies to all public repositories under the [`rios0rios0`](https://github.com/rios0rios0) GitHub account that do not define their own `SECURITY.md`. If a repository has a repository-specific `SECURITY.md`, that document takes precedence.

---

## Supported Versions

Only the two most recent major release lines receive security fixes:

| Version | Supported |
|---|---|
| Latest major | ✅ Active |
| Previous major | ✅ Critical fixes only |
| Older versions | ❌ End of life |

---

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

All security reports must be submitted privately so that a fix can be prepared before any public disclosure.

### Option 1 — GitHub Private Vulnerability Reporting (preferred)

Use GitHub's built-in [private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability) feature available on each repository's **Security** tab.

### Option 2 — Email

Send a detailed report to:

<!-- TODO: Replace with your actual security contact email -->
**security@rios0rios0.dev**

Please encrypt sensitive details with the PGP key listed below.

### What to Include

A useful report includes:

- Affected repository and version / commit SHA
- A clear description of the vulnerability and its potential impact
- Step-by-step reproduction instructions
- Proof-of-concept code or screenshots (if available)
- Suggested remediation (optional but appreciated)

---

## Response Timeline

| Milestone | Target |
|---|---|
| Initial acknowledgement | ≤ 48 hours |
| Severity assessment | ≤ 7 days |
| Fix developed | ≤ 30 days for critical / high; 90 days for medium / low |
| Public advisory | After fix is released and users have had time to upgrade |

These are targets, not guarantees. Complex vulnerabilities may require more time. You will be kept informed of progress throughout.

---

## Automated Security Tooling

All repositories consuming the [`pipelines`](https://github.com/rios0rios0/pipelines) CI/CD library run the following automated security gates on every pull request and push to `main`:

| Category | Tools |
|---|---|
| SAST | CodeQL, Semgrep, Hadolint |
| Secrets scanning | Gitleaks |
| SCA (dependencies) | Trivy, govulncheck (Go), Safety (Python), OWASP Dependency-Check (Java) |
| Container scanning | Trivy |
| Quality gate | SonarQube |

Automated tooling catches a large class of common vulnerabilities, but it is not exhaustive. Responsible disclosure for anything the automation misses is strongly encouraged.

---

## PGP / GPG Public Key

<!-- TODO: Add your PGP public key block or a link to a keyserver entry -->
<!-- Example: https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xYOURKEYID -->

A PGP public key will be listed here once available. Until then, please use GitHub's private vulnerability reporting as the primary disclosure channel.

---

## Recognition

Responsible reporters are credited in the release notes of the affected repository (with the reporter's explicit consent). We do not currently offer monetary bounties, but we are genuinely grateful for responsible disclosure and will acknowledge your contribution publicly if you wish.

---

## Disclosure Policy

We follow a **coordinated disclosure** model:

1. Reporter submits a private report.
2. Maintainer acknowledges receipt and begins investigation.
3. A fix is developed in a private branch.
4. A patched release is published.
5. A GitHub Security Advisory (GHSA) is published no later than 90 days after the initial report, or sooner if the fix is available.

We ask reporters to respect this timeline and refrain from public disclosure until a fix is available or the 90-day window has elapsed.
