# CI/CD and Automation

## Overview

Claude Code is not limited to interactive use in a terminal. It can be embedded into CI pipelines, invoked from scripts, and extended with custom commands and lifecycle hooks that automate repetitive workflows. This document covers the practical mechanisms — slash commands, hooks, GitHub Actions, and headless mode — that let you build Claude Code into your team's development automation. The goal is to handle routine tasks automatically so developers can focus on decisions that require human judgment.

## Custom Slash Commands

Slash commands are reusable prompt templates stored as markdown files. They let you encode complex workflows into a single command that any team member can run consistently.

### File Structure

Slash commands live in `.claude/commands/` inside your project. Each `.md` file becomes a command:

```
.claude/
  commands/
    deploy-check.md        →  /project:deploy-check
    changelog.md           →  /project:changelog
    onboard.md             →  /project:onboard
    review.md              →  /project:review
    explain.md             →  /project:explain
```

The file content becomes the prompt that Claude receives when you invoke the command. You can use `$ARGUMENTS` as a placeholder for any arguments passed after the command name.

### Example: Pre-Deployment Verification

**`.claude/commands/deploy-check.md`**:

```markdown
Run a pre-deployment verification for the current branch. Do each step and
report the results:

1. **Uncommitted changes**: Run `git status` and confirm the working tree
   is clean. If there are uncommitted changes, stop and warn.

2. **Test suite**: Run `npm test` and report the results. If any tests
   fail, list them and stop.

3. **Type checking**: Run `npx tsc --noEmit` and report any type errors.

4. **Lint**: Run `npx eslint src/` and report any errors (warnings are OK).

5. **Build**: Run `npm run build` and confirm it succeeds.

6. **Migration check**: Run `npm run migration:status` and confirm there
   are no pending migrations.

7. **Environment diff**: Compare `.env.example` against the current
   environment variables and flag any that are missing from .env.example
   but referenced in code.

Report a final PASS/FAIL status with a summary of any issues found.
```

Run it with `/project:deploy-check` before deploying.

### Example: Changelog Generation

**`.claude/commands/changelog.md`**:

```markdown
Generate a changelog entry for the upcoming release.

1. Run `git log --oneline $(git describe --tags --abbrev=0)..HEAD` to get
   all commits since the last tag.

2. Group the changes into these categories:
   - **Features**: New functionality
   - **Fixes**: Bug fixes
   - **Improvements**: Enhancements to existing features
   - **Breaking Changes**: Anything that requires migration or changes
     existing behavior

3. Write each entry in user-facing language. Skip internal refactors,
   dependency bumps, and CI changes unless they affect users.

4. Format as markdown with today's date and the next version number
   (based on whether there are breaking changes → major, features → minor,
   or only fixes → patch).

Output the changelog entry only — do not modify any files unless I ask.
```

### Example: Project Onboarding

**`.claude/commands/onboard.md`**:

```markdown
Explain this project to a new developer. Cover:

1. **What it does**: Read the README and key source files to give a 2-3
   sentence summary of the project's purpose.

2. **Architecture**: Describe the high-level architecture. What are the
   main components? How do they communicate? Include a simple ASCII
   diagram if helpful.

3. **Tech stack**: List the key technologies, frameworks, and tools.
   Note any unusual choices and why they might have been made.

4. **Directory structure**: Explain what each top-level directory contains
   and the organizational pattern (e.g., by feature, by layer).

5. **Getting started**: What commands does a new developer need to run?
   Check package.json scripts, Makefile, docker-compose, etc.

6. **Key patterns**: What recurring patterns should the developer
   understand? Check CLAUDE.md and any CONTRIBUTING docs for conventions.

7. **Common tasks**: How to run tests, start the dev server, create a
   migration, add a new API endpoint, etc.

Keep it practical. Skip obvious things ("JavaScript is a programming
language"). Focus on what a senior developer needs to be productive in
this specific codebase.
```

### Example: Implementing a Feature from a Spec

**`.claude/commands/implement-spec.md`**:

```markdown
Read the feature spec at: $ARGUMENTS

Before writing any code:
1. Read and understand the full scope of the feature from the spec
2. Explore the codebase to understand existing patterns and architecture
3. Propose a staged implementation plan where each stage is independently
   reviewable and testable
4. Flag ambiguities, missing details, or potential conflicts with existing code
5. Wait for plan approval before implementing

After approval, implement one stage at a time. Run relevant tests after each
stage. Pause for review between stages.
```

Run it with `/project:implement-spec docs/specs/notifications.md`. This is the core workflow for PRD-driven development — the spec carries the full context, Claude proposes the decomposition, and the developer steers at the plan level rather than crafting individual prompts. See [Prompting Strategies](03-prompting-strategies.md) for more on this pattern.

### Personal vs. Project Commands

Commands in `.claude/commands/` are project-level and should be committed to version control so the entire team can use them. For personal commands, use `~/.claude/commands/` instead — these are available in every project but not shared.

## Hooks System

Hooks are shell commands that Claude Code runs automatically at specific points in its lifecycle. They let you enforce quality checks, run formatters, and trigger external tools without relying on the developer to remember.

### Hook Types

| Hook | When It Runs | Common Uses |
|------|-------------|-------------|
| `PreToolUse` | Before Claude calls a tool | Block dangerous operations, validate parameters |
| `PostToolUse` | After a tool call completes | Run linters, formatters, tests on changed files |
| `Notification` | When Claude sends a notification | Forward to Slack, desktop notifications, logging |
| `Stop` | When Claude finishes a response | Run final validation, summary checks |

### Configuration

Hooks are configured in `.claude/settings.json` (project-level) or `~/.claude/settings.json` (user-level):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "bash -c 'npx prettier --write \"$CLAUDE_FILE_PATH\" 2>/dev/null || true'"
      }
    ]
  }
}
```

The `matcher` field is a regex matched against the tool name. The `command` is a shell command with access to environment variables that Claude Code sets based on the context.

### Example: Auto-Format on Save

Run Prettier on every file Claude writes or edits:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "bash -c 'EXT=\"${CLAUDE_FILE_PATH##*.}\"; if [[ \"$EXT\" =~ ^(ts|tsx|js|jsx|json|css|md)$ ]]; then npx prettier --write \"$CLAUDE_FILE_PATH\" 2>/dev/null; fi'"
      }
    ]
  }
}
```

### Example: Run Tests on Change

Run related tests after Claude modifies source files:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "bash -c 'if [[ \"$CLAUDE_FILE_PATH\" == *.ts && \"$CLAUDE_FILE_PATH\" != *.test.ts ]]; then npx jest --findRelatedTests \"$CLAUDE_FILE_PATH\" --passWithNoTests 2>&1 | tail -10; fi'"
      }
    ]
  }
}
```

### Example: Block Dangerous Commands

Prevent Claude from running certain commands, even if permissions would otherwise allow it:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "bash -c 'if echo \"$CLAUDE_BASH_COMMAND\" | grep -qE \"rm -rf /|DROP TABLE|git push.*--force.*main\"; then echo \"BLOCKED: This command is not allowed by project hooks\" >&2; exit 1; fi'"
      }
    ]
  }
}
```

A non-zero exit code from a `PreToolUse` hook prevents the tool from executing.

### Hook Tips

- Keep hooks fast. Hooks that take more than a few seconds will slow down every interaction.
- Use `|| true` for non-critical hooks so failures do not break the workflow.
- Use `tail` or `head` to limit output — Claude sees hook output, and verbose output wastes context.
- Test hooks outside of Claude Code first to make sure they work correctly.

## GitHub Actions Integration

Claude Code can run in CI pipelines using the official `anthropics/claude-code-action` GitHub Action, enabling automated PR review, issue triage, and code fixes.

### Automated PR Review

This workflow runs Claude Code to review every pull request when it is opened or updated:

```yaml
name: Claude PR Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            Review this pull request. Check for:
            1. Logic errors and bugs
            2. Security vulnerabilities
            3. Missing error handling
            4. Test coverage gaps
            5. Breaking API changes

            Be specific. Reference file names and line numbers.
            Skip nitpicks about style — our linter handles that.
            Focus on issues that could cause production problems.

            Post your review as a PR comment with findings organized
            by severity: Critical, Warning, Suggestion.
```

### Issue Triage and Labeling

Automatically label and triage new issues:

```yaml
name: Issue Triage
on:
  issues:
    types: [opened]

jobs:
  triage:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
    steps:
      - uses: actions/checkout@v4

      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            Analyze this GitHub issue. Based on the description:
            1. Suggest appropriate labels (bug, feature, docs, etc.)
            2. Identify which area of the codebase it likely affects
            3. Estimate complexity (small, medium, large)
            4. If it's a bug report, check if you can identify the
               likely source of the problem in the codebase

            Post a comment with your analysis.
```

### Automated Fixes for Simple Issues

For issues labeled as "good-first-issue" or "auto-fix", Claude can attempt a fix automatically:

```yaml
name: Auto Fix
on:
  issues:
    types: [labeled]

jobs:
  fix:
    if: contains(github.event.label.name, 'auto-fix')
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4

      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            Read issue #${{ github.event.issue.number }}.
            Implement the fix described in the issue.
            Run the existing tests to verify your fix.
            Create a new branch and open a pull request with your changes.
            Reference the issue in the PR description.
          allowed_tools: "Bash,Read,Write,Edit"
```

### Security Considerations for CI

- Store your API key in GitHub Secrets, never in workflow files.
- Limit `allowed_tools` in CI to only what the workflow needs.
- Use `permissions` to restrict what the GitHub token can do.
- Be cautious with workflows triggered by `pull_request_target` from forks, as they run with write access to the repository.
- Review Claude's proposed changes through the PR process, just as you would with any automated tool.

## Automated PR Descriptions

Claude can generate clear, structured PR descriptions from your commit history and code changes, saving time and improving consistency.

### Manual Workflow

From within a Claude Code session on your feature branch:

```
Generate a PR description for the current branch. Compare against main.
Include:
- A one-line summary
- A detailed description of what changed and why
- A list of notable implementation decisions
- Testing notes: what was tested and how to verify
- Any migration or deployment steps needed
```

### One-Liner for Scripting

```bash
claude --print "$(cat <<'EOF'
Generate a pull request description for the current branch.

Run `git log --oneline main..HEAD` and `git diff main...HEAD --stat` to
understand the changes. Then read the changed files if you need more context.

Format:
## Summary
One paragraph explaining what this PR does and why.

## Changes
Bullet list of specific changes, grouped by area.

## Testing
How the changes were tested. What to verify during review.

## Notes
Anything reviewers should know — tradeoffs, follow-up work, risks.
EOF
)"
```

### Automated in CI

Add PR description generation as a step in your PR workflow:

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    prompt: |
      Generate a description for this pull request based on the
      commits and diff. Update the PR body with the description.
      Use this format:

      ## Summary
      [What and why in 1-2 sentences]

      ## Changes
      [Bullet list of changes]

      ## Testing
      [What was tested]
```

## Headless Mode and Non-Interactive Use

Claude Code's `--print` flag (short form: `-p`) runs a single prompt and outputs the result to stdout, making it suitable for scripting, pipelines, and automation.

### Basic Usage

```bash
# Simple question
claude --print "What testing framework does this project use?"

# Pipe input to Claude
git diff main...HEAD | claude --print "Summarize these changes in one paragraph"

# Read from a file
claude --print "Review this file for security issues" < src/auth/middleware.ts
```

### The --print Flag

When you use `--print`, Claude Code:
- Runs non-interactively (no TUI, no interactive prompts)
- Outputs the response to stdout
- Still has access to tools (file reading, bash) unless restricted
- Exits after completing the single prompt

### Useful One-Liners

**Explain a function:**
```bash
claude --print "Explain what the processPayment function in src/services/payment.ts does, including edge cases it handles"
```

**Generate a commit message:**
```bash
claude --print "Write a concise commit message for the currently staged changes. Follow conventional commits format."
```

**Check for TODO comments:**
```bash
claude --print "Find all TODO and FIXME comments in the codebase. List each with file, line number, and the comment text. Flag any that look stale or important."
```

**Estimate complexity:**
```bash
claude --print "Analyze the codebase and identify the 5 most complex files by cyclomatic complexity, coupling, or general difficulty to maintain. Explain why each is complex."
```

### Environment Variables

Configure Claude Code behavior through environment variables, useful in CI and automation:

| Variable / Flag | Purpose |
|-----------------|---------|
| `ANTHROPIC_API_KEY` | API key for authentication (env var) |
| `--max-turns N` | Limit the number of agentic turns in a session (CLI flag) |
| `CLAUDE_CODE_USE_BEDROCK` | Use Amazon Bedrock as the provider (env var) |
| `CLAUDE_CODE_USE_VERTEX` | Use Google Vertex AI as the provider (env var) |

### Combining with Other Tools

Claude Code's headless mode integrates well with standard Unix tooling:

```bash
# Review only files changed in the last commit
git diff HEAD~1 --name-only | xargs -I{} claude --print "Review {} for bugs and suggest improvements"

# Generate documentation for all public APIs
claude --print "List all exported functions in src/api/ and generate JSDoc comments for any that are missing them"

# Pre-commit check
claude --print "Check the staged changes for console.log statements, hardcoded secrets, and commented-out code. Output only issues found, one per line."
```

### Scripting Tips

- Use `--print` for any non-interactive automation. Without it, Claude Code starts the interactive TUI.
- Long prompts are easier to maintain in files: `claude --print "$(cat prompts/review.txt)"`
- For CI, use `--max-turns N` to prevent runaway sessions that burn through API credits.
- Combine with `jq`, `grep`, and other tools to post-process Claude's output for downstream automation.

## See Also

- [Code Review and Quality](07-code-review-and-quality.md) — Review patterns and quality standards that complement automation
- [Project Setup](01-project-setup.md) — CLAUDE.md configuration and project structure
- [Team Workflows](09-team-workflows.md) — Shared conventions and workflows for teams using Claude Code
