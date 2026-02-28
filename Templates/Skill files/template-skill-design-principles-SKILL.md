---
name: design-principles
description: Global design principles and technical constraints that govern all implementation. Use when writing any code, making architectural decisions, or reviewing implementation approaches. These are rules, not suggestions.
---

# Design Principles

These principles are extracted from the Product TDD and apply to all
implementation work. They are non-negotiable constraints.

<!-- Replace these placeholders with your project's actual design principles. -->
<!-- These are the architectural rules that Claude Code must never violate. -->
<!-- Keep this skill small — it should be loaded quickly and frequently. -->
<!-- The full Product TDD stays in the repo for session-level loading. -->

- [Your performance principle, e.g., "Display speed is paramount — denormalize for read speed"]
- [Your data integrity principle, e.g., "Idempotent writes — all sync uses UPSERT"]
- [Your editability principle, e.g., "Editability is explicit — never make fields editable unless the PRD says so"]
- [Your caching principle, e.g., "Fields marked with † require a caching/denormalization strategy in the TDD"]
- [Add your project's design principles here]

## Setup

<!-- After copying this template into .claude/skills/design-principles/: -->
<!-- 1. Replace the placeholders above with principles from your Product TDD -->
<!-- 2. Delete these setup comments -->
<!-- 3. If a principle must apply to EVERY task without exception, also add it to CLAUDE.md -->
