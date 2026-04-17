Review the current `CLAUDE.md` in this repository against the actual code and update it **only if it has meaningfully drifted** from the current state of the codebase. The file already lives at the repo root if it exists — read it first before doing anything else.

## Your task

1. **Read `CLAUDE.md`** at the repo root if it exists. If it does not, create it.
2. **Skim the repo** to gather truth:
   - `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md` (recent `[Unreleased]` entries are often the most reliable signal of drift).
   - The manifest/build files that define the project's language and commands: `package.json`, `pyproject.toml`, `go.mod`, `build.gradle`, `Makefile`, `Taskfile.yaml`, `Dockerfile`.
   - Top-level source directories to get a feel for architecture.
   - Any `.github/workflows/` files if CI commands are documented.
3. **Compare** the current `CLAUDE.md` against the reality above.
4. **Decide:**
   - If every factual claim in `CLAUDE.md` still holds and nothing materially new has been added to the codebase, **make no edits**. Exit silently.
   - If a claim is wrong, a load-bearing piece of context is missing, or a documented command no longer works, **rewrite the affected sections only**. Keep the rest of the file intact.
   - If `CLAUDE.md` does not exist, create a new one following the structure below.

## Rules for what goes into `CLAUDE.md`

Follow these strictly. The file is read by future Claude Code instances; it is not a README for humans.

- **Always start with this banner** (exact text):
  ```
  # CLAUDE.md

  This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
  ```
- Focus on the **big picture** that takes reading multiple files to understand: the architectural invariants, the dependency direction, the non-obvious coupling between modules.
- Include **build / test / lint commands** that are commonly used, including how to run a single test.
- Include **conventions specific to this repo** — things a reader would get wrong by following generic best practices.

## What NOT to include

- Generic development advice (“write tests”, “use meaningful names”, “handle errors”).
- Obvious file-structure descriptions that `ls` would reveal.
- Made-up sections like “Common Development Tasks”, “Tips for Development”, or “Support and Documentation” unless they already exist in the repo's own docs.
- Restatements of what `README.md` already covers well — link or summarize, don't duplicate.
- Per-language conventions that come from the user's global rules (those are already in the assistant's context).

## Commit discipline

- If and only if you modify `CLAUDE.md`, the host workflow will detect the diff and open a PR. You do not need to run git commands yourself.
- If you decide the file is accurate, do nothing. Daily no-op runs are expected and correct.
- Never edit any file other than `CLAUDE.md`. Never run destructive commands. Never push, tag, or merge.

## Tone

- Terse and declarative. Short sentences. No filler.
- Match the style of the existing `CLAUDE.md` if one is present.
- When in doubt about a claim, leave it out rather than guess.
