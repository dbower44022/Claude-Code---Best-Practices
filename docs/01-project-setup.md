# Project Setup

Getting Claude Code productive on your codebase starts with configuration. A well-configured project means Claude understands your conventions, knows how to build and test, and avoids wasting time on irrelevant files. This guide covers the setup that matters most: CLAUDE.md files, the .claude/ directory, MCP servers, permission modes, and .claudeignore.

## Writing an Effective CLAUDE.md

The CLAUDE.md file is the single most impactful thing you can configure. Claude reads it at the start of every conversation, so it functions as persistent memory and standing instructions. The goal is to give Claude the context it needs to work autonomously without bloating the context window.

### What to Include

- **Build, test, and lint commands** — Claude will guess wrong otherwise, especially on monorepos or non-standard setups
- **Project conventions** — naming patterns, file organization rules, import ordering, error handling approaches
- **Architecture overview** — just enough to understand the system's shape (2-5 sentences, not a design doc)
- **Key file paths** — entry points, config files, shared utilities, database schemas
- **Feature specs location** — where PRDs and design docs live (e.g., `docs/specs/`) so Claude can read them when implementing features
- **Common gotchas** — things that trip up newcomers ("always run migrations before tests", "the legacy API uses a different auth scheme")

### What to Skip

- Anything Claude can discover by reading the code (function signatures, type definitions, standard library usage)
- Verbose explanations of well-known frameworks ("React uses a virtual DOM...")
- Full API documentation — link to it instead
- Changelog or historical context that doesn't affect current work

### Example CLAUDE.md

Here is a realistic CLAUDE.md for a mid-size TypeScript application:

```markdown
# CLAUDE.md

## Build & Test
- `pnpm install` — install dependencies
- `pnpm build` — full production build
- `pnpm test` — run full test suite (Jest)
- `pnpm test -- --testPathPattern=<pattern>` — run a single test file
- `pnpm lint` — ESLint + Prettier check
- `pnpm lint:fix` — auto-fix lint issues
- `pnpm db:migrate` — run pending database migrations
- `pnpm db:generate` — regenerate Prisma client after schema changes

## Architecture
Monorepo with three packages:
- `packages/api` — Express REST API (entry: src/server.ts)
- `packages/web` — Next.js frontend (entry: src/app/layout.tsx)
- `packages/shared` — shared types, validators, and utilities

## Conventions
- Use Zod schemas for all API request/response validation
- Error handling: throw AppError subclasses, never raw Error
- Database queries go in `*.repository.ts` files, never in route handlers
- Tests live next to source files: `foo.ts` → `foo.test.ts`
- Use named exports, not default exports
- Import order: node builtins → external packages → @shared/ → relative

## Key Files
- `packages/api/src/routes/` — all API route definitions
- `packages/shared/src/schemas/` — Zod schemas shared between API and frontend
- `prisma/schema.prisma` — database schema (source of truth for data model)
- `docker-compose.yml` — local dev services (Postgres, Redis)

## Feature Specs
PRDs and feature specs live in `docs/specs/`. Read the relevant spec before
implementing any feature work. Each spec defines the scope, requirements,
and acceptance criteria for a feature.

## Gotchas
- Always run `pnpm db:generate` after changing prisma/schema.prisma
- The `packages/web` build depends on `packages/shared` being built first
- Redis is required for running the API locally (sessions + job queue)
- CI runs `pnpm test -- --ci --coverage` — tests must pass with coverage thresholds
```

### CLAUDE.md Hierarchy

Claude loads CLAUDE.md files from multiple locations, and they stack:

1. **Project root CLAUDE.md** — loaded for every conversation in the project. Put universal information here.
2. **`.claude/` directory CLAUDE.md** — same scope as project root, useful if you want to keep the root directory clean.
3. **Nested CLAUDE.md in subdirectories** — loaded only when Claude is working with files in or below that directory. Use these for package-specific or module-specific instructions.

For a monorepo, this hierarchy is particularly useful:

```
my-project/
  CLAUDE.md                    # shared build commands, repo-wide conventions
  packages/
    api/
      CLAUDE.md                # API-specific patterns, test commands, env vars
    web/
      CLAUDE.md                # frontend conventions, component patterns
    shared/
      CLAUDE.md                # rules for the shared package (e.g., "no runtime deps")
```

Each nested file should contain only what is specific to that subtree. Do not repeat information from the root CLAUDE.md.

## The .claude/ Directory

The `.claude/` directory holds project-level Claude Code configuration that goes beyond the CLAUDE.md file.

### settings.json

The `.claude/settings.json` file configures project-level settings like allowed and denied tools, MCP servers, and custom permissions. This file is checked into version control and shared across the team.

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test*)",
      "Bash(npm run lint*)",
      "Bash(npx prisma*)"
    ],
    "deny": [
      "Bash(rm -rf /)*",
      "Bash(git push --force)*"
    ]
  }
}
```

The `allow` list pre-approves specific commands so Claude does not ask for confirmation every time. The `deny` list blocks commands you never want Claude to run, regardless of permission mode. Glob patterns work in both lists.

### Custom Slash Commands

Markdown files in `.claude/commands/` become project-specific slash commands accessible as `/project:command-name`. This is one of the most underused features of Claude Code. Good candidates for custom commands include workflows your team repeats frequently.

**Example: `.claude/commands/add-api-endpoint.md`**

```markdown
Create a new API endpoint based on the user's description.

Follow these steps:
1. Create the Zod request/response schemas in packages/shared/src/schemas/
2. Create the route handler in packages/api/src/routes/
3. Create the repository file if database access is needed
4. Register the route in packages/api/src/routes/index.ts
5. Write integration tests for the new endpoint
6. Run `pnpm test` to verify everything passes

Use existing endpoints as reference for patterns and conventions.
The user's prompt will describe what the endpoint should do: $ARGUMENTS
```

The team invokes this with `/project:add-api-endpoint GET /users/:id/preferences — returns user notification and display preferences`. The `$ARGUMENTS` placeholder is replaced with whatever the user types after the command name.

**Example: `.claude/commands/debug-test.md`**

```markdown
Help debug a failing test.

1. Run the failing test with verbose output: `pnpm test -- --verbose $ARGUMENTS`
2. Read the test file and the source file it tests
3. Analyze the failure — is it a test bug or a source bug?
4. Propose a fix with an explanation of the root cause
5. Apply the fix and re-run the test to confirm it passes
```

### Memory Files

Claude Code also uses `.claude/` to store conversation memory when you ask it to "remember" something. These are managed automatically — you generally do not need to edit them by hand, but it is useful to know they exist. If Claude starts behaving oddly based on stale memory, check `.claude/` for outdated memory entries.

## MCP Server Configuration

Model Context Protocol (MCP) servers extend Claude's capabilities by giving it access to external systems through structured tool interfaces. They are most valuable when Claude needs to interact with something beyond the filesystem and shell.

### When MCP Servers Help

- **Database access** — querying a database directly instead of writing and running ad-hoc scripts
- **API integrations** — interacting with project management tools, CI systems, or internal services
- **Specialized search** — semantic code search, documentation search, or knowledge base access
- **Browser and UI testing** — tools like Playwright MCP for interacting with web applications

### Configuration

MCP servers are configured in `.mcp.json` at the project root (recommended for project-scoped servers) or in `~/.claude.json` for user-scoped servers:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://localhost:5432/myapp_dev"
      ]
    },
    "playwright": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic/mcp-server-playwright"
      ]
    }
  }
}
```

### Practical Example: Database MCP

With a Postgres MCP server configured, Claude can directly query your development database when debugging issues or exploring data. Instead of asking Claude to write a script, run it, and parse the output (which consumes context and is error-prone), Claude calls the MCP tool and gets structured results.

This is especially useful for tasks like:

- "What does the users table look like for the account that reported this bug?"
- "Show me all orders in the last 24 hours with a failed payment status"
- "Check if the migration actually added the new column"

Without the MCP server, each of these would require Claude to write a SQL script, run it via psql, and parse the text output. With the MCP server, it is a single tool call.

### Team Sharing

Since MCP configuration lives in `.claude/settings.json`, it is shared through version control. Make sure connection strings reference local development resources (localhost, dev databases) — never production credentials.

## Permission Modes

Claude Code has three permission modes that control how much autonomy Claude has. Choose based on your situation.

### Ask Mode

Claude asks for confirmation before every file write and every shell command. This is the default and the most conservative option.

**When to use it:** When exploring an unfamiliar codebase, when running Claude on code you do not fully understand, or when working in a sensitive area of the project. Also appropriate when you are new to Claude Code and want to understand what it does before trusting it.

### Auto-Edit Mode

Claude writes and edits files freely but still asks before running shell commands (except those explicitly allowed in settings.json).

**When to use it:** This is the recommended mode for most day-to-day development work. Claude spends a lot of time editing files, and confirming each edit slows the workflow significantly. File edits are low-risk because you can review the diff and revert with git. Shell commands are higher-risk (installing packages, running scripts with side effects), so approval there is still valuable.

Start here for most projects. Add frequently-used safe commands (test runners, linters, build commands) to the `allow` list in `.claude/settings.json` to reduce confirmation prompts further.

### Plan Mode

Claude analyzes and proposes approaches but cannot write files or run commands. It is restricted to read-only operations.

**When to use it:** Complex architecture decisions, exploring unfamiliar codebases before making changes, or any time you want to align on an approach before implementation. Enter with Shift+Tab (press twice from default mode) or start with `claude --permission-mode plan`. Exit plan mode (Shift+Tab to cycle back) before asking Claude to implement.

### Dangerously Full Auto Mode

Claude runs everything without asking — file edits, shell commands, all of it.

**When to use it:** Headless CI/CD pipelines, automated code generation workflows, or throwaway environments where there is nothing to break. Not recommended for interactive development work on a real codebase. Despite the name, it is not inherently dangerous if used in the right context (containers, ephemeral environments, sandboxed CI jobs).

## .claudeignore

The `.claudeignore` file works like `.gitignore` — it tells Claude Code to skip matching files and directories entirely. Claude will not read, search, or index anything that matches.

### What to Exclude

- **Build output** — `dist/`, `build/`, `.next/`, `out/`
- **Vendored dependencies** — `node_modules/`, `vendor/`
- **Generated code** — API client stubs, protobuf output, ORM-generated types
- **Large data files** — test fixtures over a few KB, seed data, SQL dumps
- **Binary files** — images, compiled assets, fonts
- **Environment files** — `.env.local`, `.env.production` (also prevents accidental exposure of secrets)

### Example .claudeignore

```
# Build output
dist/
build/
.next/
out/
*.min.js
*.min.css

# Dependencies
node_modules/

# Generated code
src/generated/
packages/api/src/prisma-client/
*.pb.ts

# Large data
fixtures/large/
seed-data/
*.sql.gz

# Binary and media
*.png
*.jpg
*.gif
*.woff2
*.ico

# Environment and secrets
.env*
!.env.example

# IDE and OS
.idea/
.vscode/
.DS_Store
```

This keeps Claude focused on the code that matters and prevents it from wasting context window space on files it cannot usefully process.

## See Also

- [Context Management](02-context-management.md) — manage the context window so Claude stays effective on large codebases
- [Team Workflows](09-team-workflows.md) — share Claude Code configuration across a team
- [CI/CD and Automation](08-cicd-and-automation.md) — use Claude Code in headless pipelines and automated workflows
