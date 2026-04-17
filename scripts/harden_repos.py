#!/usr/bin/env python3
"""GitHub Repository Hardening Script for rios0rios0.

Audits and enforces consistent security and configuration settings across all repos.

Usage:
    python3 harden_repos.py --phase 1                       Audit only (read-only)
    python3 harden_repos.py --phase 1 --fail-on-noncompliant Exit 1 if any repo is non-compliant
    python3 harden_repos.py --phase 2                       Apply repo settings
    python3 harden_repos.py --phase 3                       Apply security settings
    python3 harden_repos.py --phase 4                       Apply branch protection
    python3 harden_repos.py --phase 5                       Re-audit and comparison report
    python3 harden_repos.py --dry-run                       Show changes without applying
    python3 harden_repos.py --repo autobump                 Target single repo

Owner is in the bypass_actors list so they can force-push to main when needed.
"""

import argparse
import json
import os
import subprocess
import sys
import time

OWNER = os.environ.get("HARDEN_OWNER", "rios0rios0")
GH = os.environ.get("GH_BIN", "gh")
DEFAULT_BRANCH = "main"

REPO_SETTINGS = {
    "delete_branch_on_merge": True,
    "allow_auto_merge": True,
    "allow_squash_merge": True,
    "allow_rebase_merge": True,
    "allow_merge_commit": True,
    "has_wiki": False,
    "has_projects": False,
}

BRANCH_PROTECTION_BODY = {
    "required_pull_request_reviews": {
        "dismiss_stale_reviews": True,
        "require_code_owner_reviews": False,
        "require_last_push_approval": False,
        "required_approving_review_count": 1,
    },
    "required_status_checks": None,
    # enforce_admins=False means repo admins (the owner) can bypass branch protection
    "enforce_admins": False,
    "required_linear_history": False,
    "allow_force_pushes": False,
    "allow_deletions": False,
    "required_conversation_resolution": True,
    "restrictions": None,
    "lock_branch": False,
    "allow_fork_syncing": False,
    "block_creations": False,
}

RULESET_NAME = "main-protection"

# Repository Admin role is actor_id=5 in the RepositoryRole actor_type.
# This lets the repo admin (the owner) bypass the ruleset and force-push.
RULESET_BODY = {
    "name": RULESET_NAME,
    "target": "branch",
    "enforcement": "active",
    "bypass_actors": [
        {
            "actor_id": 5,
            "actor_type": "RepositoryRole",
            "bypass_mode": "always",
        }
    ],
    "conditions": {
        "ref_name": {
            "include": ["refs/heads/main"],
            "exclude": [],
        }
    },
    "rules": [{"type": "non_fast_forward"}],
}


def gh_api(path, method="GET", body=None, raw=False, timeout=30):
    """Execute a gh api call. Returns (exit_code, stdout, stderr)."""
    cmd = [GH, "api", path, "--method", method]
    if raw:
        cmd.append("--include")
    stdin_data = None
    if body is not None:
        cmd.extend(["--input", "-"])
        stdin_data = json.dumps(body).encode()

    for attempt in range(3):
        try:
            r = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                input=stdin_data.decode() if stdin_data else None,
            )
            if "rate limit" in r.stderr.lower() or "403" in r.stderr:
                if "rate limit" in r.stderr.lower():
                    print("  Rate limited, waiting 60s...")
                    time.sleep(60)
                    continue
            return r.returncode, r.stdout, r.stderr
        except subprocess.TimeoutExpired:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return -1, "", "TIMEOUT"
    return -1, "", "MAX_RETRIES"


def gh_api_json(path, method="GET", body=None):
    """Execute gh api call and return parsed JSON, or None on error."""
    rc, out, err = gh_api(path, method, body)
    if rc != 0:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def list_repos():
    """List all repos for the owner (including private, via authenticated endpoint)."""
    repos = []
    page = 1
    while True:
        rc, out, err = gh_api(
            f"/user/repos?per_page=100&page={page}&affiliation=owner", timeout=60
        )
        if rc != 0:
            print(f"ERROR listing repos: {err}")
            sys.exit(1)
        batch = json.loads(out)
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    return sorted(repos, key=lambda r: r["name"])


def get_repo_details(name):
    """Get full repo details."""
    return gh_api_json(f"/repos/{OWNER}/{name}")


def get_branch_protection(name):
    """Get branch protection. Returns (data_or_None, error_reason_or_None)."""
    rc, out, err = gh_api(f"/repos/{OWNER}/{name}/branches/{DEFAULT_BRANCH}/protection")
    if rc != 0:
        if "Not Found" in err or "Branch not protected" in err:
            return None, "not_protected"
        if "Upgrade to GitHub Pro" in err or "403" in err:
            return None, "unavailable"
        return None, f"error: {err[:100]}"
    try:
        return json.loads(out), None
    except json.JSONDecodeError:
        return None, "parse_error"


def get_required_signatures(name):
    """Check if required signatures are enabled."""
    rc, out, err = gh_api(
        f"/repos/{OWNER}/{name}/branches/{DEFAULT_BRANCH}/protection/required_signatures"
    )
    if rc != 0:
        return None
    try:
        data = json.loads(out)
        return data.get("enabled", False)
    except json.JSONDecodeError:
        return None


def check_vulnerability_alerts(name):
    """Check if Dependabot vulnerability alerts are enabled. Returns True/False/None."""
    rc, out, err = gh_api(
        f"/repos/{OWNER}/{name}/vulnerability-alerts", raw=True
    )
    if rc == 0 and "204" in out.split("\n")[0]:
        return True
    if "204" in (out or ""):
        return True
    return False


def check_automated_security_fixes(name):
    """Check if Dependabot automated security fixes are enabled."""
    data = gh_api_json(f"/repos/{OWNER}/{name}/automated-security-fixes")
    if data is None:
        return False
    return data.get("enabled", False)


def get_ruleset(name):
    """Check if the main-protection ruleset exists. Returns ruleset id or None."""
    data = gh_api_json(f"/repos/{OWNER}/{name}/rulesets")
    if not data:
        return None
    for rs in data:
        if rs.get("name") == RULESET_NAME:
            return rs.get("id")
    return None


def get_ruleset_details(name, ruleset_id):
    """Fetch a ruleset's full body so we can inspect bypass_actors."""
    return gh_api_json(f"/repos/{OWNER}/{name}/rulesets/{ruleset_id}")


def audit_repo(name, repo_list_data=None):
    """Audit a single repo. Returns a dict of current state."""
    # Always fetch individual details — list endpoint omits security_and_analysis
    detail = get_repo_details(name)
    if not detail:
        return {"name": name, "error": "could not fetch details"}

    sa = detail.get("security_and_analysis") or {}

    audit = {
        "name": name,
        "private": detail.get("private", False),
        "fork": detail.get("fork", False),
        "visibility": detail.get("visibility", "unknown"),
        # repo settings
        "delete_branch_on_merge": detail.get("delete_branch_on_merge", False),
        "allow_auto_merge": detail.get("allow_auto_merge", False),
        "allow_squash_merge": detail.get("allow_squash_merge", True),
        "allow_rebase_merge": detail.get("allow_rebase_merge", True),
        "allow_merge_commit": detail.get("allow_merge_commit", True),
        "has_wiki": detail.get("has_wiki", False),
        "has_projects": detail.get("has_projects", False),
        # security
        "secret_scanning": sa.get("secret_scanning", {}).get("status"),
        "push_protection": sa.get("secret_scanning_push_protection", {}).get("status"),
        "dependabot_alerts": check_vulnerability_alerts(name),
        "dependabot_updates": check_automated_security_fixes(name),
    }

    # ruleset (force push protection via non_fast_forward rule)
    audit["ruleset_id"] = get_ruleset(name)
    audit["has_force_push_ruleset"] = audit["ruleset_id"] is not None

    if audit["ruleset_id"]:
        details = get_ruleset_details(name, audit["ruleset_id"])
        bypass = (details or {}).get("bypass_actors") or []
        has_admin_bypass = any(
            a.get("actor_type") == "RepositoryRole" and a.get("actor_id") == 5
            for a in bypass
        )
        audit["ruleset_admin_bypass"] = has_admin_bypass
    else:
        audit["ruleset_admin_bypass"] = False

    # branch protection
    prot, reason = get_branch_protection(name)
    if prot:
        audit["protection_enabled"] = True
        audit["protection_available"] = True
        pr_reviews = prot.get("required_pull_request_reviews", {})
        audit["prot_review_count"] = pr_reviews.get("required_approving_review_count")
        audit["prot_dismiss_stale"] = pr_reviews.get("dismiss_stale_reviews")
        audit["prot_code_owners"] = pr_reviews.get("require_code_owner_reviews")
        audit["prot_force_pushes"] = prot.get("allow_force_pushes", {}).get("enabled")
        audit["prot_allow_deletions"] = prot.get("allow_deletions", {}).get("enabled")
        audit["prot_enforce_admins"] = prot.get("enforce_admins", {}).get("enabled")
        audit["prot_linear_history"] = prot.get("required_linear_history", {}).get("enabled")
        audit["prot_conversation_resolution"] = prot.get(
            "required_conversation_resolution", {}
        ).get("enabled")
        audit["prot_signatures"] = get_required_signatures(name)
    else:
        audit["protection_enabled"] = False
        audit["protection_available"] = reason != "unavailable"

    return audit


def compute_issues(a):
    """Return a list of non-compliance issue strings for a single audit dict."""
    if "error" in a:
        return [f"audit_error: {a['error']}"]

    issues = []

    for k, target in REPO_SETTINGS.items():
        current = a.get(k)
        if current != target:
            issues.append(f"{k}={current}(want {target})")

    if not a.get("dependabot_alerts"):
        issues.append("dependabot_alerts=off")
    if not a.get("dependabot_updates"):
        issues.append("dependabot_updates=off")

    # secret scanning / branch protection / ruleset are only enforced on public repos
    # (private repos on GitHub Free don't support them)
    if not a.get("private") and a.get("protection_available", True):
        if a.get("secret_scanning") != "enabled":
            issues.append(f"secret_scanning={a.get('secret_scanning')}")
        if a.get("push_protection") != "enabled":
            issues.append(f"push_protection={a.get('push_protection')}")

        if not a.get("protection_enabled"):
            issues.append("branch_protection=off")
        else:
            if a.get("prot_review_count") != 1:
                issues.append(f"prot_review_count={a.get('prot_review_count')}")
            if a.get("prot_dismiss_stale") is not True:
                issues.append("prot_dismiss_stale=off")
            if a.get("prot_conversation_resolution") is not True:
                issues.append("prot_conversation_resolution=off")
            if a.get("prot_signatures") is not True:
                issues.append("prot_signatures=off")

        if not a.get("has_force_push_ruleset"):
            issues.append("ruleset_non_fast_forward=missing")
        elif not a.get("ruleset_admin_bypass"):
            issues.append("ruleset_admin_bypass=missing")

    return issues


def print_audit_table(audits):
    """Print a summary table of audit results."""
    print(f"\n{'REPO':<40} {'VIS':<8} {'DEL-BR':<7} {'AUTO-M':<7} {'WIKI':<5} "
          f"{'PROJ':<5} {'SEC-SC':<7} {'PUSH-P':<7} {'DEP-AL':<7} {'DEP-UP':<7} "
          f"{'PROT':<5} {'NO-FP':<6} {'STALE':<6} {'SIGS':<5}")
    print("-" * 155)
    for a in audits:
        if "error" in a:
            print(f"{a['name']:<40} ERROR: {a['error']}")
            continue
        prot = "Y" if a["protection_enabled"] else ("N/A" if not a["protection_available"] else "N")
        no_fp = "Y" if a.get("has_force_push_ruleset") else "N"
        print(
            f"{a['name']:<40} "
            f"{a['visibility']:<8} "
            f"{'Y' if a['delete_branch_on_merge'] else 'N':<7} "
            f"{'Y' if a['allow_auto_merge'] else 'N':<7} "
            f"{'Y' if a['has_wiki'] else 'N':<5} "
            f"{'Y' if a['has_projects'] else 'N':<5} "
            f"{(a.get('secret_scanning') or 'N/A')[:7]:<7} "
            f"{(a.get('push_protection') or 'N/A')[:7]:<7} "
            f"{'Y' if a['dependabot_alerts'] else 'N':<7} "
            f"{'Y' if a['dependabot_updates'] else 'N':<7} "
            f"{prot:<5} "
            f"{no_fp:<6} "
            f"{str(a.get('prot_dismiss_stale', '-'))[:6]:<6} "
            f"{str(a.get('prot_signatures', '-'))[:5]:<5}"
        )

    total = len(audits)
    protected = sum(1 for a in audits if a.get("protection_enabled"))
    unavailable = sum(1 for a in audits if not a.get("protection_available", True))
    public = sum(1 for a in audits if not a.get("private"))
    private = sum(1 for a in audits if a.get("private"))
    forks = sum(1 for a in audits if a.get("fork"))

    print(f"\nSummary: {total} repos ({public} public, {private} private, {forks} forks)")
    print(f"Branch protection: {protected} enabled, {unavailable} unavailable (private)")


def print_noncompliance_report(audits):
    """Print a list of non-compliant repos with their specific issues."""
    noncompliant = []
    for a in audits:
        issues = compute_issues(a)
        if issues:
            noncompliant.append((a["name"], issues))

    print("\n=== NON-COMPLIANCE REPORT ===\n")
    if not noncompliant:
        print("All repos are compliant.")
        return 0

    for name, issues in sorted(noncompliant):
        print(f"  {name} ({len(issues)}):")
        for issue in issues:
            print(f"    - {issue}")

    print(f"\nTotal non-compliant: {len(noncompliant)}/{len(audits)}")
    return len(noncompliant)


def phase1_audit(repo_filter=None):
    """Phase 1: Audit all repos."""
    print("Phase 1: Auditing all repositories...")
    repos = list_repos()
    print(f"Found {len(repos)} repos")

    if repo_filter:
        repos = [r for r in repos if r["name"] == repo_filter]
        if not repos:
            print(f"Repo '{repo_filter}' not found")
            sys.exit(1)

    audits = []
    for i, repo in enumerate(repos):
        name = repo["name"]
        sys.stdout.write(f"\r  Auditing {i+1}/{len(repos)}: {name:<40}")
        sys.stdout.flush()
        audit = audit_repo(name, repo)
        audits.append(audit)

    print("\r" + " " * 80)
    print_audit_table(audits)

    out_path = "/tmp/gh_hardening_audit_before.json"
    with open(out_path, "w") as f:
        json.dump(audits, f, indent=2)
    print(f"\nAudit saved to {out_path}")

    return audits


def phase2_repo_settings(audits, dry_run=False):
    """Phase 2: Apply repo settings."""
    print(f"\nPhase 2: {'[DRY-RUN] ' if dry_run else ''}Applying repo settings...")
    changed = 0
    skipped = 0

    for a in audits:
        name = a["name"]
        if "error" in a:
            print(f"  {name}: SKIP (audit error)")
            skipped += 1
            continue

        diffs = {}
        for key, target in REPO_SETTINGS.items():
            current = a.get(key)
            if current != target:
                diffs[key] = (current, target)

        if not diffs:
            skipped += 1
            continue

        changes_str = ", ".join(f"{k}: {old} -> {new}" for k, (old, new) in diffs.items())
        print(f"  {name}: {changes_str}")

        if not dry_run:
            body = {k: v for k, (_, v) in diffs.items()}
            result = gh_api_json(f"/repos/{OWNER}/{name}", method="PATCH", body=body)
            if result:
                changed += 1
            else:
                print(f"    FAILED to apply settings")
        else:
            changed += 1

    print(f"\nPhase 2 complete: {changed} changed, {skipped} already compliant")


def phase3_security(audits, dry_run=False):
    """Phase 3: Apply security settings."""
    print(f"\nPhase 3: {'[DRY-RUN] ' if dry_run else ''}Applying security settings...")
    changed_sec = 0
    changed_dep = 0

    for a in audits:
        name = a["name"]
        if "error" in a:
            continue

        if not a["private"]:
            needs_scanning = a.get("secret_scanning") != "enabled"
            needs_push_prot = a.get("push_protection") != "enabled"

            if needs_scanning or needs_push_prot:
                changes = []
                if needs_scanning:
                    changes.append("secret_scanning")
                if needs_push_prot:
                    changes.append("push_protection")
                print(f"  {name}: enabling {', '.join(changes)}")

                if not dry_run:
                    body = {"security_and_analysis": {}}
                    if needs_scanning:
                        body["security_and_analysis"]["secret_scanning"] = {"status": "enabled"}
                    if needs_push_prot:
                        body["security_and_analysis"]["secret_scanning_push_protection"] = {
                            "status": "enabled"
                        }
                    result = gh_api_json(f"/repos/{OWNER}/{name}", method="PATCH", body=body)
                    if result:
                        changed_sec += 1
                    else:
                        print(f"    FAILED")
                else:
                    changed_sec += 1
        else:
            if a.get("secret_scanning") != "enabled":
                print(f"  {name}: SKIP secret scanning (private repo, GitHub Free)")

        if not a.get("dependabot_alerts"):
            print(f"  {name}: enabling dependabot alerts")
            if not dry_run:
                rc, _, err = gh_api(
                    f"/repos/{OWNER}/{name}/vulnerability-alerts", method="PUT"
                )
                if rc == 0:
                    changed_dep += 1
                else:
                    print(f"    FAILED: {err[:80]}")
            else:
                changed_dep += 1

        if not a.get("dependabot_updates"):
            print(f"  {name}: enabling dependabot security updates")
            if not dry_run:
                rc, _, err = gh_api(
                    f"/repos/{OWNER}/{name}/automated-security-fixes", method="PUT"
                )
                if rc == 0:
                    changed_dep += 1
                else:
                    print(f"    FAILED: {err[:80]}")
            else:
                changed_dep += 1

    print(f"\nPhase 3 complete: {changed_sec} secret scanning, {changed_dep} dependabot changes")


def phase4_branch_protection(audits, dry_run=False):
    """Phase 4: Apply branch protection rules and force-push ruleset."""
    print(f"\nPhase 4: {'[DRY-RUN] ' if dry_run else ''}Applying branch protection...")
    changed = 0
    skipped = 0

    for a in audits:
        name = a["name"]
        if "error" in a:
            skipped += 1
            continue

        if a["private"]:
            print(f"  {name}: SKIP (private repo, GitHub Free)")
            skipped += 1
            continue

        diffs = []

        needs_protection = False
        if not a["protection_enabled"]:
            needs_protection = True
            diffs.append("creating protection")
        else:
            checks = [
                (a.get("prot_dismiss_stale"), True, "dismiss_stale"),
                (a.get("prot_allow_deletions"), False, "allow_deletions"),
                (a.get("prot_conversation_resolution"), True, "conversation_resolution"),
                (a.get("prot_review_count"), 1, "review_count"),
            ]
            for current, target, label in checks:
                if current != target:
                    needs_protection = True
                    diffs.append(f"{label}: {current} -> {target}")

        needs_signatures = a.get("prot_signatures") is not True
        if needs_signatures:
            diffs.append(f"signatures: {a.get('prot_signatures')} -> True")

        needs_ruleset = not a.get("has_force_push_ruleset")
        needs_admin_bypass = a.get("has_force_push_ruleset") and not a.get("ruleset_admin_bypass")

        if needs_ruleset:
            diffs.append("creating non_fast_forward ruleset")
        elif needs_admin_bypass:
            diffs.append("adding admin bypass to existing ruleset")

        if not diffs:
            skipped += 1
            continue

        print(f"  {name}: {', '.join(diffs)}")

        if not dry_run:
            if needs_protection or needs_signatures:
                rc, out, err = gh_api(
                    f"/repos/{OWNER}/{name}/branches/{DEFAULT_BRANCH}/protection",
                    method="PUT",
                    body=BRANCH_PROTECTION_BODY,
                )
                if rc != 0:
                    print(f"    FAILED protection: {err[:100]}")
                    continue

            if needs_signatures:
                rc, out, err = gh_api(
                    f"/repos/{OWNER}/{name}/branches/{DEFAULT_BRANCH}/protection/required_signatures",
                    method="POST",
                )
                if rc != 0:
                    print(f"    FAILED signatures: {err[:100]}")
                    continue

            if needs_ruleset:
                rc, out, err = gh_api(
                    f"/repos/{OWNER}/{name}/rulesets",
                    method="POST",
                    body=RULESET_BODY,
                )
                if rc != 0:
                    print(f"    FAILED ruleset: {err[:100]}")
                    continue
            elif needs_admin_bypass:
                # Update existing ruleset to add admin bypass
                rs_id = a.get("ruleset_id")
                rc, out, err = gh_api(
                    f"/repos/{OWNER}/{name}/rulesets/{rs_id}",
                    method="PUT",
                    body=RULESET_BODY,
                )
                if rc != 0:
                    print(f"    FAILED ruleset update: {err[:100]}")
                    continue

            changed += 1
        else:
            changed += 1

    print(f"\nPhase 4 complete: {changed} changed, {skipped} skipped")


def phase5_report(repo_filter=None):
    """Phase 5: Re-audit and generate comparison report."""
    print("Phase 5: Re-auditing and generating comparison report...")

    try:
        with open("/tmp/gh_hardening_audit_before.json") as f:
            before = {a["name"]: a for a in json.load(f)}
    except FileNotFoundError:
        print("ERROR: No before audit found. Run --phase 1 first.")
        sys.exit(1)

    repos = list_repos()
    if repo_filter:
        repos = [r for r in repos if r["name"] == repo_filter]

    after_list = []
    for i, repo in enumerate(repos):
        name = repo["name"]
        sys.stdout.write(f"\r  Auditing {i+1}/{len(repos)}: {name:<40}")
        sys.stdout.flush()
        after_list.append(audit_repo(name, repo))

    print("\r" + " " * 80)

    after = {a["name"]: a for a in after_list}

    with open("/tmp/gh_hardening_audit_after.json", "w") as f:
        json.dump(after_list, f, indent=2)

    print("\n=== CHANGES REPORT ===\n")
    fields_to_compare = [
        "delete_branch_on_merge", "allow_auto_merge", "has_wiki", "has_projects",
        "secret_scanning", "push_protection", "dependabot_alerts", "dependabot_updates",
        "protection_enabled", "prot_dismiss_stale", "has_force_push_ruleset",
        "ruleset_admin_bypass", "prot_conversation_resolution", "prot_signatures",
    ]

    repos_changed = 0
    for name in sorted(after.keys()):
        b = before.get(name, {})
        a = after[name]
        diffs = []
        for field in fields_to_compare:
            old = b.get(field)
            new = a.get(field)
            if old != new:
                diffs.append(f"{field}: {old} -> {new}")
        if diffs:
            repos_changed += 1
            print(f"  {name}:")
            for d in diffs:
                print(f"    {d}")

    if repos_changed == 0:
        print("  No changes detected (all repos already compliant or no before data)")

    print(f"\n=== FINAL STATUS ===\n")
    print_audit_table(after_list)
    print(f"\nRepos changed: {repos_changed}/{len(after_list)}")
    print(f"After audit saved to /tmp/gh_hardening_audit_after.json")


def main():
    parser = argparse.ArgumentParser(description="Harden GitHub repos for rios0rios0")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3, 4, 5], help="Run specific phase")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--repo", type=str, help="Target a single repo")
    parser.add_argument(
        "--fail-on-noncompliant",
        action="store_true",
        help="After auditing, exit 1 if any repo is non-compliant. Intended for CI usage.",
    )
    args = parser.parse_args()

    if args.dry_run and args.phase:
        print("--dry-run runs all phases 1-4 in dry-run mode. Ignoring --phase.")

    if args.dry_run:
        audits = phase1_audit(args.repo)
        phase2_repo_settings(audits, dry_run=True)
        phase3_security(audits, dry_run=True)
        phase4_branch_protection(audits, dry_run=True)
        return

    if not args.phase:
        print("Please specify --phase (1-5) or --dry-run")
        parser.print_help()
        sys.exit(1)

    if args.phase == 1:
        audits = phase1_audit(args.repo)
        noncompliant_count = print_noncompliance_report(audits)
        if args.fail_on_noncompliant and noncompliant_count > 0:
            print(f"\nFAIL: {noncompliant_count} repo(s) non-compliant", file=sys.stderr)
            sys.exit(1)
    elif args.phase == 2:
        audits = phase1_audit(args.repo)
        phase2_repo_settings(audits)
    elif args.phase == 3:
        audits = phase1_audit(args.repo)
        phase3_security(audits)
    elif args.phase == 4:
        audits = phase1_audit(args.repo)
        phase4_branch_protection(audits)
    elif args.phase == 5:
        phase5_report(args.repo)


if __name__ == "__main__":
    main()
