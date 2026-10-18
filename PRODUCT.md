# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary: SLIIT course-web evaluators marking the R26-IT-148 website assessment. Their job is to verify every required structural element (Home, Domain, Milestones with drop-down, Documents, Presentations, About Us, Contact Us) quickly and award full marks. Secondary: general visitors and future students discovering the RecruitAI research project.

## Product Purpose

Single-page static showcase for final-year research project R26-IT-148 (AI-Driven Recruitment Ecosystem). It exists to satisfy the course-web website deliverable and to present the project's domain evidence, timeline, documents, team, and contacts. Success means full website-assessment marks plus a credible public face for the research.

## Positioning

Unlike generic senior-project sites, this one is backed by verifiable ML results (90.49% CV accuracy, NDCG@1 0.9784, 91.50% hireability) and a fully offline-safe static build with zero external dependencies.

## Operating Context

Evaluated as a zipped upload to the SLIIT course web with a 20 MB cap; opened in a desktop or mobile browser with possibly no internet. Maintained by the 3-member student team up to final submission (28 Oct 2026). Document/slide links are Google Drive URLs swapped into placeholder anchors.

## Capabilities and Constraints

- Static HTML + CSS with tiny progressive-enhancement JS (works with JS disabled). No frameworks, no external fonts/scripts/images.
- Total size must stay under 20 MB; images kept local and compressed.
- Required tabs and behaviors preserved: Home, Domain (survey/gap/problem/objectives/methodology/tech), Milestones with assessment drop-down, Documents (links only), Presentations incl. future slots, About Us, Contact Us.
- Confirmed facts: 3 members (IT22089236 Comp 1, IT22306272 Comp 2, IT22027610 Comp 3+4); supervisors Mrs. Buddhima Attanayaka / Mrs. Narmada Gamage; AIMS research group; 2026 Regular Batch deadlines; ICDMIS 2026 poster achievement.
- Open: member photos, LinkedIn URLs, Drive links for documents/slides.

## Brand Commitments

Name RecruitAI, tagline AI-Driven Recruitment Ecosystem, project code R26-IT-148, SLIIT affiliation. Optical-mark identity (answer paper, blue-black ink, examiner red, single highlighter yellow) recorded in DESIGN.md. No other binding visual commitments.

## Evidence on Hand

- Site lives at `D:\GitHub\website\` (moved out of the repo 11 Oct 2026): `index.html`, `styles.css`, `script.js`.
- Local assets: supervisor portraits, 15 tech SVG logos in `website/assets/`.
- Verification: serves HTTP 200 on local static server; ~1.1 MB total.
- Absent (must not be fabricated): member photos, LinkedIn URLs, document/slide Drive links.

## Product Principles

1. Compliance first: every required element present and reachable within one scroll or click.
2. Evidence over adjectives: metrics, dates, and links carry the claims.
3. Offline-safe by default: nothing the evaluator needs may depend on the network.
4. Student-maintainable: plain files, obvious placeholders, documented handoff in `website/README.md`.

## Accessibility & Inclusion

No product-specific standard established. Baseline: semantic HTML, keyboard-reachable nav, alt text on images, readable contrast on body copy.
