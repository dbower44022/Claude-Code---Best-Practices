# Project Setup

This methodology uses two tools at different phases: **Claude.ai** for requirements development and design, and **Claude Code** for implementation. Each needs its own configuration. Getting both set up correctly means Claude understands your methodology, your conventions, and your codebase — and doesn't lose context between sessions or tools.

This guide covers Claude.ai project configuration first (since requirements work precedes implementation), then Claude Code configuration: CLAUDE.md files, the .claude/ directory, MCP servers, permission modes, and .claudeignore.

---

## Configuring Claude.ai for PRD Development

Claude.ai is where all requirements thinking happens — creating PRDs, TDDs, decomposing entities, refining action catalogs, and reviewing Implementation Guides. A well-configured Claude.ai Project ensures that every conversation starts with the right context and follows the methodology consistently.

### Create a Dedicated Project

Create a Claude.ai Project for your product's requirements work. This gives you a persistent workspace where project instructions, uploaded knowledge files, and conversation history are scoped to your product. All PRD development conversations should happen within this project rather than in general Claude.ai conversations.

### Repository Access

Claude.ai can clone and interact with your Git repository directly during conversations, eliminating the manual cycle of downloading files, editing them, and re-uploading. This is especially valuable for PRD development, where you're frequently reading existing documents and producing updated versions.

**Add the repo URL to Project Instructions.** Include a line like `GitHub repository: https://github.com/username/project-name` so Claude.ai always knows where to find your documents. For public repositories, this is all that's needed — Claude.ai can clone the repo at the start of any session.

**For private repositories, provide a Personal Access Token (PAT).** Claude.ai cannot authenticate to private repos without a token. You have two options:

- **Paste the PAT at the start of each session.** More secure — the token doesn't persist in your project configuration — but requires you to provide it every time. Claude.ai will configure Git authentication for the duration of that session.
- **Include the PAT in Project Instructions.** More convenient — Claude.ai can access the repo in every conversation without prompting. But the PAT lives in your project's system prompt. If you choose this approach, use a fine-grained token scoped to the specific repository with minimal permissions (Contents: Read and write).

To create a GitHub PAT: click your profile photo (top right) → Settings → Developer settings (bottom of the left sidebar) → Personal access tokens → Fine-grained tokens. Scope it to your project repository with Contents read/write permission.

**The recommended workflow:** Claude.ai pulls from the repo to read current documents, works on updates in the conversation, and pushes finalized changes back to the repo when you approve. This keeps Git as the single source of truth and avoids version drift between the repo and uploaded project knowledge files.

### Project Instructions (System Prompt)

The Project Instructions field is always in context — every message Claude.ai reads includes these instructions. Keep them concise and directive. Their job is to define Claude.ai's role and working rules, not to repeat the methodology guide.

**Example Project Instructions:**

```
You are a product requirements analyst working on [Product Name].

## Your Role
- Help the product owner develop, decompose, and refine product requirements
- Create and update documents following the PRD Methodology Guide (uploaded to project knowledge)
- Always use the appropriate template from project knowledge when creating new documents

## Working Rules
- Never mix product requirements (what) with technical decisions (how) in the same document
- When creating a new document, identify the correct document type (Entity Base PRD, Action Sub-PRD, TDD, Functional Area PRD, etc.) and use its template
- Maintain task list IDs using the entity prefix convention (e.g., CONT-01, COMP-01)
- When a field is added to an Entity Base PRD, always specify Editable, Sortable, and Filterable metadata
- Mark subquery-backed sortable fields with † and note the TDD caching requirement
- When an action is too complex for the action catalog, recommend creating a Sub-PRD
- Preserve existing document content when making updates — make surgical edits, not rewrites
- Use terminology from the glossary consistently; when introducing a new term, add it to the glossary
- Track version numbers in all documents and update the PRD Index after every session

## Key References in Project Knowledge
- prd-methodology-guide.md — the methodology (document types, hierarchy, workflows, conventions)
- template-*.md files — templates for each document type
- glossary.md — authoritative term definitions; use these terms consistently in all documents
- [product]-prd-index.md — current document registry and status (upload when available)

## Repository
- GitHub repository: https://github.com/[username]/[project-name]
- PRD documents are in the PRDs/ directory; templates are in PRDs/Templates/
```

Adapt this to your product. The `[Product Name]` and entity prefixes should reflect your actual project. Add product-specific rules as you discover recurring issues — for example, if Claude.ai keeps making UI PRD decisions that belong in the GUI Standards, add a rule about that boundary.

**Project Instructions vs. User Preferences:** Project Instructions should contain rules specific to the methodology and product — things that would apply to anyone working on this project. Personal behavioral preferences — communication style, formatting rules, interaction patterns (e.g., "never use the popup menu widget," "always ask clarifying questions before answering") — belong in Claude.ai's User Preferences (Settings > Profile), where they apply across all your conversations regardless of project. Don't clutter Project Instructions with personal preferences that aren't project-specific.

### Project Knowledge (Uploaded Files)

Project knowledge files are available to Claude.ai in every conversation within the project. Upload these files as your methodology foundation:

**Always upload:**

- `prd-methodology-guide.md` — the complete methodology reference. Claude.ai uses this to understand document types, hierarchy, naming conventions, and workflows.
- All `template-*.md` files — the templates for every document type. When you ask Claude.ai to create a new Entity Base PRD or Action Sub-PRD, it should work from the actual template rather than improvising a structure.
- Your product glossary — the single authoritative source of terminology. Upload this so Claude.ai uses your exact terms when creating and updating documents, rather than inventing its own names for concepts. Without it, terminology drifts across PRDs and eventually into code.

**Upload as you go:**

- Your PRD Index — once it exists, keep it updated in project knowledge so Claude.ai can reference the current state of all documents.
- Entity Base PRDs and TDDs relevant to the current phase of work. When decomposing the Company entity, upload the Company Entity Base PRD and its TDD so Claude.ai has context. You don't need every document uploaded at once — scope it to what's active.
- GUI Standards — upload when working on UI PRDs so Claude.ai can reference component patterns and conventions.
- Implementation Guides — upload when iterating on previously built features so Claude.ai understands what was actually implemented.

Re-upload the glossary whenever new terms are added. It grows with every PRD — each new entity, action, and UI concept introduces terminology that should be captured centrally.

**Don't upload:**

- Source code files — those belong in Claude Code's context, not Claude.ai's.
- Documents you're not actively working on — unnecessary files dilute the knowledge base and can cause Claude.ai to reference stale context.

### Keeping Project Knowledge Current

The uploaded files in project knowledge are static snapshots. When you update a document (version a methodology guide, revise a PRD, update the index), you must re-upload the updated file to project knowledge. The canonical versions of your documents should live in your Git repository; the project knowledge copies are deployed snapshots for Claude.ai's use.

If you've configured repository access (see above), this sync burden is reduced — Claude.ai can pull the latest documents directly from Git at the start of each session. Project knowledge uploads are still useful for the methodology guide and templates (which Claude.ai benefits from having always available without a fetch step), but active PRDs and TDDs can be read from the repo on demand.

If not using Git integration, establish a habit: after any session that produces updated documents, push to Git first (source of truth), then re-upload to project knowledge. This prevents drift between what's in the repo and what Claude.ai sees.

### Recommended Claude.ai Settings

These settings affect how Claude.ai behaves in your project conversations:

- **Memory (Search and reference past chats)** — Enable. This allows Claude.ai to recall context from previous PRD sessions within the project, reducing the need to re-explain decisions.
- **Generate memory from chat history** — Enable. This builds Claude.ai's awareness of your product over time — entity names, design patterns you've established, recurring preferences.
- **Artifacts** — Enable. Useful for reviewing document drafts inline before committing to final versions.
- **Web Search** — Enable selectively. Useful when researching competitive products or technical approaches during PRD development, but not needed for routine document work.
- **Code Execution and File Creation** — Enable if you want Claude.ai to produce downloadable document files. Disable if you prefer to copy content from the conversation directly.

### Session Workflow

At the start of each Claude.ai PRD session:

1. Open the project (not a general conversation)
2. If using Git integration, have Claude.ai pull the latest from the repository
3. State the goal: "We're decomposing the Company entity today" or "I need to create an Action Sub-PRD for email import"
4. Reference the PRD Index if one exists: "Check the PRD Index for current status"
5. Work iteratively — review Claude.ai's output, refine, and approve before moving to the next document

At the end of each session:

1. Review all produced or modified documents
2. Push finalized documents to Git (either have Claude.ai push directly, or push manually)
3. If not using Git integration, re-upload any changed documents to project knowledge
4. Update the PRD Index to reflect what was accomplished

---

## Configuring Claude Code for Implementation

Getting Claude Code productive on your codebase starts with configuration. A well-configured project means Claude Code understands your conventions, knows how to build and test, and avoids wasting time on irrelevant files. This section covers the setup that matters most: CLAUDE.md files, the .claude/ directory, MCP servers, permission modes, and .claudeignore.

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

- [PRD Methodology Guide](../prd-methodology-guide.md) — the complete methodology for document types, hierarchy, and workflows
- [Context Management](02-context-management.md) — manage the context window so Claude stays effective on large codebases
- [Team Workflows](09-team-workflows.md) — share Claude Code configuration across a team
- [CI/CD and Automation](08-cicd-and-automation.md) — use Claude Code in headless pipelines and automated workflows
