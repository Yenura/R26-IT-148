---
name: RecruitAI Course-Web Site
description: Static exam answer-sheet themed showcase for SLIIT final-year research project R26-IT-148.
colors:
  paper: "#F4EDDE"
  paper-deep: "#E9DFC7"
  card: "#FFFDF4"
  ink: "#22304A"
  ink-panel: "#2C3D5C"
  ink-line: "#46587E"
  ink-soft: "#4B5A7A"
  muted-dark: "#C4CEE6"
  examiner-red: "#C8102E"
  red-deep: "#9A0B23"
  graphite: "#8A8FA0"
  pencil-rule: "#D3C8A8"
  highlighter: "#F2C230"
  pass-green: "#1E7A46"
  stamp-amber: "#A85B08"
typography:
  display:
    fontFamily: "\"Segoe UI\", system-ui, sans-serif"
    fontSize: "clamp(2.4rem, 6vw, 4.2rem)"
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "\"Segoe UI\", system-ui, sans-serif"
    fontSize: "2rem"
    fontWeight: 800
    lineHeight: 1.15
  body:
    fontFamily: "\"Segoe UI\", system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  mono-label:
    fontFamily: "Consolas, Menlo, monospace"
    fontSize: "0.72rem"
    fontWeight: 700
    letterSpacing: "0.08em"
rounded:
  sm: "6px"
  md: "8px"
  lg: "10px"
  card: "14px"
spacing:
  section: "2.8rem 1.2rem"
  container: "1150px"
  gap: "0.9rem"
components:
  button-primary:
    backgroundColor: "{colors.examiner-red}"
    textColor: "{colors.card}"
    rounded: "{rounded.md}"
    padding: "0.7rem 1.3rem"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "0.7rem 1.3rem"
  chip-tag:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "999px"
    padding: "0.35rem 0.8rem"
---

# Design System: RecruitAI Course-Web Site

## Overview

**Creative North Star: "The Marked Answer Sheet"**

The site is an exam answer sheet being marked live: the hiring pipeline reads as scan, mark, tally, rank. A warm paper ground carries blue-black ink, examiner-red marks, graphite rules, and exactly one highlighter-yellow reserved for the live score. Density alternates between quiet paper stretches and deep-ink blocks like cut sheets stacked with air between them. Motion is a single authored moment, the optical reader's scan bar traveling the hero card. Nothing glows, nothing floats without a shadow that has somewhere to land.

**Key Characteristics:**
- Paper ground with ink borders, never cards on dark slate.
- Mono serials and stamped badges carry metadata; prose stays in workhorse sans.
- Red marks celebration (ticks, stamps, scores), never correction.

## Colors

Committed-field strategy: paper owns the page, ink owns alternating sections, red marks only what matters.

### Primary
- **Answer Paper** (#F4EDDE): page ground; every light section sits on it.
- **Examiner Red** (#C8102E): primary actions, marks, ticks, stamps, focus rings on light ground.

### Secondary
- **Blue-Black Ink** (#22304A): text, borders, alternating section grounds, navigation rules.
- **Highlighter Yellow** (#F2C230): the live score only (fusion strip, scan bar, active states, focus on dark ground).

### Tertiary
- **Pass Green** (#1E7A46): completed-milestone ticks on paper; lightened to mint (#7BDFA2) for ticks on ink grounds.
- **Stamp Amber** (#A85B08): slide file badges and pending states, edged darker (#7A4205).
### Neutral
- **Card Paper** (#FFFDF4): raised surfaces on the ground; portraits use pure white (#FFFFFF) photo beds edged in ink.
- **Deep Paper** (#E9DFC7): inset wells and photo beds.
- **Ink Soft** (#4B5A7A): secondary text on paper.
- **Pale Ink** (#C4CEE6): secondary text on ink grounds.
- **Graphite** (#8A8FA0): placeholders, inactive marks.
- **Pencil Rule** (#D3C8A8): hairlines, graph grid, double rules.

### Named Rules
**The One Highlighter Rule.** Yellow appears only where a score is live or being read. Its rarity is the point; decorative yellow is banned.

## Typography

**Display Font:** Segoe UI ExtraBold via system stack (with system-ui fallback)
**Body Font:** Segoe UI via system stack (with system-ui fallback)
**Label/Mono Font:** Consolas, Menlo, monospace

**Character:** Institutional and unsentimental; display shouts in uppercase with tight tracking while mono serials whisper the metadata. No webfonts ship (offline-safe constraint), so weight, case, and spacing do the expressive work.

### Hierarchy
- **Display** (800, clamp(2.4rem, 6vw, 4.2rem), 1.15): hero headline only, uppercase.
- **Headline** (800, 2rem, 1.15): section titles, uppercase.
- **Title** (700, 1.05–1.1rem, 1.15): card and panel headings.
- **Body** (400, 1rem, 1.6): prose, max measure ~70ch.
- **Label** (700 mono, 0.7–0.78rem, 0.08em tracking, uppercase): serials, tags, badges, table headers.

### Named Rules
**The Case Rule.** Uppercase is reserved for display, headlines, badges, and mono labels. Body copy and card titles never shout.

## Layout

Single centered column (1150px container), sections alternate paper and full-bleed ink. The hero pairs a masthead column with the optical-reader card beside it; domain content grids 4→2→1; milestones run a 5-up timetable collapsing to 2-up then stacked. Spacing rhythm is section air (2.8rem) with tight intra-card groups. Breakpoints at 1000px, 720px, 640px; tables scroll horizontally inside wrappers rather than reflowing.

## Elevation & Depth

Depth is real paper stacking: 2px ink borders with small offset plus soft blur. Ink-ground sections go flat (border tonal instead of shadow).

### Shadow Vocabulary
- **Sheet lift** (`box-shadow: 3px 4px 12px rgba(34,48,74,.18)`): stat, domain, document, and panel cards on paper.
- **Cover lift** (`box-shadow: 5px 7px 22px rgba(34,48,74,.35)`): hero optical-reader card.
- **Portrait lift** (`box-shadow: 4px 5px 14px rgba(34,48,74,.20)`): team and supervisor cards.

### Named Rules
**The Blur Rule.** Every offset shadow carries blur. Zero-blur block shadows never ship.

## Shapes

Slightly rounded sheets (8–10px cards, 14px portraits) with 2px ink outlines; pills reserved for chips, timeline marks, and the table-of-contents rail; stamps (badges, achievement year) use tighter radii with rotation (−2 to −6deg) and double borders. Perforation and torn edges are not used.

## Components

### Buttons
- **Shape:** rounded rectangles (8px), 2px borders.
- **Primary:** examiner red fill and deep-red edge, paper text, soft cover shadow; hover deepens to red-deep.
- **Hover / Focus:** focus ring is 3px red on paper, highlighter on ink grounds.
- **Secondary / Ghost:** transparent with 2px ink outline; hover inverts to ink fill with paper text.

### Chips
- **Style:** paper tags, 2px ink outline, pill radius, 18px brand glyph + semibold label.
- **State:** static metadata only; no selected variant exists.

### Cards / Containers
- **Corner Style:** 8–10px sheets, 14px portraits.
- **Background:** card paper on light sections, ink-panel on ink sections.
- **Shadow Strategy:** sheet lift on paper; flat tonal borders on ink.
- **Border:** 2px ink (paper) or 2px ink-line (dark).
- **Internal Padding:** 0.9–1.2rem.

### Inputs / Fields
- **Style:** card-paper fill, 2px ink stroke, 8px radius; graphite placeholders.
- **Focus:** red outline ring; no glow.

### Navigation
- Sticky paper bar under a 4px double ink rule; links semibold with highlighter-wash hover; dropdowns are bordered paper slips; mobile collapses behind a bordered toggle button stacking full-width links.

### Optical Reader (signature component)
Ink panel staging the live pipeline: numbered dashed readout rows with pass-mint scanned ticks, a highlighter fusion strip for the final score, segmented ten-cell meters per component (fill driven by score, mono value at right), and one traveling scan bar (7s linear loop, removed under reduced motion).

## Do's and Don'ts

### Do:
- **Do** keep yellow exclusive to live scores and active states (The One Highlighter Rule).
- **Do** set metadata (dates, serials, tags, badges) in uppercase mono with wide tracking.
- **Do** use examiner red for celebration marks: ticks, stamps, primary actions.
- **Do** alternate paper and ink sections to pace long scrolls.

### Don't:
- **Don't** ship kickers/eyebrows above headings; headings carry their own weight.
- **Don't** use gradient text or zero-blur offset shadows.
- **Don't** add webfonts, external images, or scripts; the system is offline-safe by constraint.
- **Don't** invent new accent colors; the palette is closed at red, yellow, green, amber.
