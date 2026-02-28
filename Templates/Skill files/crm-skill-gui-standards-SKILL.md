---
name: gui-standards
description: CRMExtender UI design system — application shell, navigation, layout patterns, interaction paradigms, window types, display modes, card architecture, and visual design tokens. Use when implementing any user interface component — list views, detail panels, forms, modals, entity bar, action panel, content panel, grid, toolbar, search, or any visual element. Covers information density, view-optimized rendering, section-based editing, responsive breakpoints, and keyboard shortcuts.
---

# CRMExtender GUI Standards

This skill provides the UI design system for CRMExtender. Load it whenever
you're building or modifying user interface components.

For the complete specification, see [gui-functional-requirements-prd.md](gui-functional-requirements-prd.md).
For the preview card amendment, see [gui-preview-card-amendment.md](gui-preview-card-amendment.md).

## Core Design Principles (always apply)

### Information Density Over Whitespace
- The UI is designed for large screens (4K 27") — maximize data visibility, minimize clicks
- No empty field placeholders — if a field has no data, suppress it entirely
- Sections with 0 items are suppressed completely (no header, no empty placeholder)
- When sections are suppressed, adjacent sections expand to claim the freed space
- Compact spacing is the default density (32-36px row height, 4-8px padding)

### View-Optimized Rendering
- Default state is always view mode — optimized for reading and scanning
- Edit mode is a deliberate, section-level opt-in triggered by a pencil icon
- Field values render as formatted text, not input controls
- Compound fields (address, name) render as single formatted blocks
- Boolean fields render as descriptive text or icons, not checkboxes
- Relation fields render as clickable entity names, not dropdowns
- Date fields use Contextual Date Formatting (Today/Yesterday/Day name/Month Day/Month Day Year)

### Content-Proportional Space Allocation
- Sections dynamically allocate vertical space based on data volume
- 0 items = suppressed, 1-3 items = compact, 10+ items = expanded with scroll

### Contextual Purity
- Each entity workspace is dedicated entirely to that entity type
- Cross-cutting features (notifications, dashboards, activity) live on the Home screen

## Workspace Layout
- Four vertical zones: Entity Bar, Action Panel, Content Panel, Detail Panel
- Two horizontal bars: Application Tool Bar (top), Application Status Bar (bottom)
- All zones visible simultaneously on large screens
- Splitter bars between zones for user-adjustable widths

## Visual Design Tokens
- Typography: system font stack, H1-H4 headings, body, caption, monospace
- Spacing: 4px base unit, scale of 4/8/12/16/24/32/48
- Border radius: small (4px), medium (8px), large (12px)
- Iconography: monochrome, 24×24 standard / 16×16 compact
- Density: Compact (default) / Standard / Comfortable — user-selectable three-tier cascade
- Dark mode: architecture supports theme switching, implementation deferred

## Window Types
- Docked Window (detail panel)
- Modal Full Overlay Window
- Modal Partial Overlay Window
- Floating Modal / Floating Unmodal
- Undocked Window (second monitor support)
- Search Window

## Display Modes
- Preview Mode — summary, compact, read-only
- View Mode — full read-only display
- Edit Mode — section-based editing with pencil icon trigger
