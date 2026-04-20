Review the AI-assistant guidance files in this repository against the actual code and update them **only if they have meaningfully drifted** from the current state of the codebase.

Two files are in scope, both optional:

- `CLAUDE.md` at the repo root — guidance for Claude Code sessions.
- `.github/copilot-instructions.md` — guidance for GitHub Copilot sessions.

## Your task

1. **Read each file if it exists.** Start with whichever already exists. Do not create either file unless the repository clearly benefits from it.
2. **Skim the repo** to gather truth:
   - `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md` (recent `[Unreleased]` entries are often the most reliable signal of drift).
   - The manifest/build files that define the project's language and commands: `package.json`, `pyproject.toml`, `go.mod`, `build.gradle`, `Makefile`, `Taskfile.yaml`, `Dockerfile`.
   - Top-level source directories to get a feel for architecture.
   - Any `.github/workflows/` files if CI commands are documented.
3. **Compare** each existing file against that reality.
4. **Decide, per file:**
   - If every factual claim still holds and nothing materially new has been added, **make no edits to that file**.
   - If a claim is wrong, a load-bearing piece of context is missing, or a documented command no longer works, **rewrite the affected sections only**. Keep the rest intact.
   - If the file does not exist but the repo would clearly benefit (it has custom build commands, non-obvious architecture, or specific conventions), create it following the structure below. If the repo is trivial or the existing `README.md` already covers everything, do not create the file.

## Rules for `CLAUDE.md`

- **Always start with this banner** (exact text) when creating:
  ```
  # CLAUDE.md

  This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
  ```

## Rules for `.github/copilot-instructions.md`

- The file is loaded automatically by GitHub Copilot Chat and inlined into prompts. Keep it focused and under a few hundred lines.
- No banner is required — start directly with content.
- Content should overlap in substance with `CLAUDE.md` (both serve the same purpose for different assistants) but phrase it for GitHub Copilot's context model. Do not duplicate text verbatim — cross-reference or summarize.

## Shared rules for what goes into either file

- Focus on the **big picture** that takes reading multiple files to understand: architectural invariants, dependency direction, non-obvious coupling between modules.
- Include **build / test / lint commands** that are commonly used, including how to run a single test.
- Include **conventions specific to this repo** — things a reader would get wrong by following generic best practices.

## What NOT to include

- Generic development advice ("write tests", "use meaningful names", "handle errors").
- Obvious file-structure descriptions that `ls` would reveal.
- Made-up sections like "Common Development Tasks", "Tips for Development", or "Support and Documentation" unless they already exist in the repo's own docs.
- Restatements of what `README.md` already covers well — link or summarize, don't duplicate.
- Per-language conventions that come from the user's global rules (those are already in the assistant's context).

## Commit discipline

- If and only if you modify `CLAUDE.md` or `.github/copilot-instructions.md`, the host workflow will detect the diff and open a PR. You do not need to run git commands yourself.
- If you decide both files are accurate (or should not be created), do nothing. Weekly no-op runs are expected and correct.
- Never edit any file other than `CLAUDE.md` or `.github/copilot-instructions.md`. Never run destructive commands. Never push, tag, or merge.

## Tone

- Terse and declarative. Short sentences. No filler.
- Match the style of the existing file if one is present.
- When in doubt about a claim, leave it out rather than guess.
