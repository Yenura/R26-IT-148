# RecruitAI Design System

## Architecture

Three-layer token system: **Primitive → Semantic → Component**

```
Primitive tokens (raw values, never used in components)
       ↓
Semantic tokens (purpose aliases: --color-primary, --color-fg)
       ↓
Component tokens (--btn-bg, --card-border, --input-shadow-focus)
```

### Files

| File | Purpose |
|------|---------|
| `design-tokens.css` | All three token layers + backward-compat aliases |
| `components.css` | Component styles using tokens |
| `index.css` | Imports both (entry point) |
| `chartTheme.js` | Recharts theme config reading from tokens |

## Token Naming Convention

```
--p-{category}-{variant}    Primitive   (e.g. --p-purple-500)
--color-{purpose}           Semantic    (e.g. --color-primary)
--{component}-{property}    Component   (e.g. --btn-bg)
```

## Usage Rules

1. **Never use primitive tokens in components** — always go through semantic or component tokens
2. **Never use hardcoded hex/rgb** in component styles — reference tokens
3. **Dark theme** is default (`:root`), light theme is `[data-theme="light"]`
4. **Backward compat aliases** (`--accent`, `--bg`, etc.) exist in `:root` — migrate to `--color-*` names over time

## Adding a New Component

1. Define component tokens in `:root` inside `design-tokens.css`
2. Add light-theme overrides in `[data-theme="light"]`
3. Write styles in `components.css` using only `--color-*` or `--{component}-*` tokens

## Color Palette

| Role | Dark | Light | Primitives |
|------|------|-------|------------|
| Primary | `#7c6cff` | `#6c5ce7` | purple-500 / purple-600 |
| Success | `#00e4b8` | `#00b894` | teal-400 / teal-500 |
| Warning | `#ffb347` | `#d97706` | amber-500 / amber-600 |
| Danger | `#ff5c7a` | `#e11d48` | rose-500 / rose-600 |
| Info | `#60a5fa` | `#3b82f6` | blue-400 / blue-500 |

## Spacing Scale

4px base: `--p-space-1` (4) → `--p-space-2` (8) → `--p-space-3` (12) → `--p-space-4` (16) → `--p-space-5` (20) → `--p-space-6` (24) → `--p-space-8` (32) → `--p-space-10` (40) → `--p-space-12` (48) → `--p-space-16` (64)

## Typography Scale

| Token | Size | Usage |
|-------|------|-------|
| `--p-text-xs` | 11px | Labels, captions |
| `--p-text-sm` | 12px | Secondary text, badges |
| `--p-text-base` | 13px | Body text (default) |
| `--p-text-md` | 14px | Body large |
| `--p-text-lg` | 15px | Card titles |
| `--p-text-xl` | 16px | Section headings |
| `--p-text-2xl` | 20px | Page subheadings |
| `--p-text-3xl` | 24px | Stat values |
| `--p-text-4xl` | 28px | Page titles |

## Component States

Every interactive component follows: **default → hover → active → disabled → focus-visible**

| Component | Default | Hover | Active | Disabled | Focus |
|-----------|---------|-------|--------|----------|-------|
| Button | `--btn-bg` | `--btn-bg-hover` | `--btn-bg-active` | opacity 0.5 | `--color-focus-ring` |
| Card | `--card-border` | `--card-border-hover` | — | — | — |
| Card-interactive | `--card-border` | `--card-border-active` + glow + lift(-1px) | translateY(0) | — | — |
| Input | `--input-border` | — | — | opacity 0.5 | `--input-border-focus` + `--input-shadow-focus` |
| Nav-item | `--sidebar-item-fg` | bg + fg change | — | — | — |
| Chip | `--chip-border` | `--chip-border-hover` | — | — | — |

## Layout

- **App shell**: flex, sidebar (240px sticky) + main content (max 1280px)
- **Grid system**: `.grid` (16px gap), `.grid-2/3/4` (responsive, collapses at 900px)
- **Sidebar**: sticky, full height, collapsible via state
- **Responsive**: mobile breakpoint at 600px (sidebar overlay), content breakpoint at 900px (grid collapse)

## Z-Index Scale

| Token | Value | Usage |
|-------|-------|-------|
| `--p-z-base` | 0 | Default |
| `--p-z-dropdown` | 100 | Dropdowns, tooltips |
| `--p-z-sticky` | 200 | Sticky sidebar |
| `--p-z-overlay` | 300 | Mobile sidebar overlay |
| `--p-z-modal` | 400 | Modal dialogs |
| `--p-z-toast` | 500 | Toast notifications |

## Animations

| Name | Duration | Usage |
|------|----------|-------|
| `fadeIn` | 400ms ease-out | Page entrance |
| `shimmer` | 1.5s ease-in-out | Skeleton loading |
| `pulse-danger` | 2s infinite | Error status dot |
| `toast-in` | 200ms ease | Toast slide-in |

## Migration Guide

Old tokens still work via backward-compat aliases in `:root`. To migrate:

```
--accent      → --color-primary
--accent-2    → --color-success
--accent-warn → --color-warning
--accent-danger → --color-danger
--bg          → --color-bg
--text        → --color-fg
--text-secondary → --color-fg-secondary
--text-muted  → --color-fg-muted
--border      → --color-border
--border-light → --color-border-strong
--card        → --card-bg
```
