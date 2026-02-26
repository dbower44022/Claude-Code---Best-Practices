# Claude Code Best Practices for Large Application Development

## Overview

This guide is for experienced developers who want to get the most out of Claude Code when working on large, real-world software projects. It covers the full project lifecycle — from initial setup and architecture through implementation, testing, and CI/CD — with practical patterns that scale beyond toy examples.

The core workflow for large applications is **PRD-driven development**: store feature specs in your repository, point Claude at a spec in plan mode, let Claude propose a staged implementation plan, review and adjust the plan, then implement stage by stage with review checkpoints. This scales from small features to complex multi-service changes because Claude handles the decomposition — the developer steers at the plan level, not at the prompt level.

These documents are meant to be read in order for newcomers, but each stands alone as a reference for its topic.

## Documents

### Getting Started
- [Project Setup](01-project-setup.md) — Configure CLAUDE.md, project structure, MCP servers, and permission modes for your codebase
- [Context Management](02-context-management.md) — Manage the context window effectively so Claude stays useful on large codebases

### Working with Claude Code
- [Prompting Strategies](03-prompting-strategies.md) — PRD-driven development, effective prompting, plan mode, and iteration
- [Architecture and Design](04-architecture-and-design.md) — Use Claude Code for design decisions, architecture reviews, and documenting choices
- [Implementation Patterns](05-implementation-patterns.md) — Strategies for writing code: incremental changes, multi-file coordination, refactoring, and worktrees

### Quality and Testing
- [Testing and Debugging](06-testing-and-debugging.md) — TDD workflows, test generation, debugging strategies, and understanding failures
- [Code Review and Quality](07-code-review-and-quality.md) — Automated reviews, standards enforcement, security patterns, and quality gates

### Automation and Teams
- [CI/CD and Automation](08-cicd-and-automation.md) — Slash commands, hooks, GitHub Actions integration, and automated workflows
- [Team Workflows](09-team-workflows.md) — Shared conventions, onboarding, consistent prompting, and knowledge sharing

### Reference
- [Common Pitfalls](10-common-pitfalls.md) — Anti-patterns to avoid: over-reliance, context exhaustion, gold-plating, and more

## How to Use This Guide

**If you're new to Claude Code:** Start with [Project Setup](01-project-setup.md) and [Context Management](02-context-management.md), then read through in order.

**If you're already using Claude Code:** Jump to the topic most relevant to your current challenge. Each document has a "See Also" section linking to related topics.

**If you're setting up Claude Code for a team:** Start with [Project Setup](01-project-setup.md), then go directly to [Team Workflows](09-team-workflows.md) and [CI/CD and Automation](08-cicd-and-automation.md).
