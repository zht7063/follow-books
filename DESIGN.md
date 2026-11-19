---
version: alpha
name: Follow Books — Dan Koe study edition
description: A compact, unofficial reading companion with visible evidence boundaries.
colors:
  primary: "#2349a0"
  background: "#edf2f8"
  surface: "#ffffff"
  text: "#1d2b43"
  muted: "#4d6078"
  border: "#c7d3e3"
typography:
  display:
    fontFamily: '"Palatino Linotype", "Book Antiqua", Palatino, serif'
  sans:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", sans-serif'
  mono:
    fontFamily: 'ui-monospace, "Cascadia Mono", monospace'
rounded:
  DEFAULT: "0.75rem"
spacing:
  section-gap: "3rem"
  page-max: "78rem"
components:
  navigation: {owner: "scripts/build_site.py: shell"}
  source: {owner: "scripts/build_site.py: source_card"}
  search: {owner: "web/search.js"}
---

# Follow Books Design System

## Overview

### Creative North Star

An annotated study edition: a blue cloth cover, a visible contents leaf, and generous white reading pages. The signature is the book-spine rail with chapter tabs, which gives a finite collection a beginning, middle and end. This is a reading companion, not an imitation of Dan Koe's brand.

### Product context and register

The task brief is the product authority. Readers want to understand one author's themes and open the original sources without mistaking an index for a complete book. This is a content site with local search, not an account-based application. English editorial and controls; Chinese seed abstracts retain their original language and carry `lang="zh-Hans"`. No Japan-market assumption. Desktop study and phone reading are equally supported. Avoid generic SaaS cards, decorative statistics, and faux archival claims.

### Token ownership/runtime mapping

`web/reader.css` owns runtime tokens; the frontmatter mirrors its six palette tokens and font stacks. The builder copies this file into `site/assets/`. Contract tests check the mapping and responsive rules. All pages share the same shell, metadata, chapter navigation and source cards.

## Colors

Blue is navigation and emphasis, pale slate is the desk surface, white is the reading leaf. Ink and muted text stay dark enough on both surfaces. Status labels include words; color never carries evidence alone. Focus uses the primary blue. Scrollbar thumb uses muted, track uses background. Forced colors use system settings. One light theme keeps the prototype predictable.

## Typography

Palatino gives editorial headings a book-like cadence; system sans keeps controls and mixed Chinese/English sources familiar. Monospace is reserved for source ids. Reader prose is 1.125rem with 1.85 line height and a 66ch measure. No remote fonts or font swap.

## Layout

At wide widths the contents rail is 16rem and the reading leaf takes the remaining space. At 760px and below the rail joins document flow, chapters become wrapped links, and the reading area uses 1rem padding. All children have `min-width: 0`; URLs wrap. Document scrolling owns the whole page. No viewport-height clipping or hidden mobile navigation. Full catalog lists are deliberately rendered for this finite 63-entry edition and grouped by chapter.

## Elevation & Depth

A quiet border separates the white page from the blue desk. No modal, floating action, drop-shadow stack or sticky header. Status text and results occupy normal document flow.

## Shapes

A 0.75rem reading-leaf radius softens the outer cover; source entries use rules and spacing rather than nested cards. Controls have at least 44px target height.

## Components

### Foundational visual states

Native links and buttons provide keyboard semantics. Hover underlines, focus rings and current-chapter text distinguish states. All content remains available without JavaScript. Local search adds a results region only after initialization; no remote loading state is necessary. No-results text suggests clearing or changing the query. Search errors preserve the complete browse list.

### Buttons and actions

One primary reading link; ordinary navigation uses underlined text. Clear search is a visible, labelled button when a query is present. No destructive actions, authentication, purchases or data entry.

### Navigation and data display

The same shell links contents, chapters and catalog on every page. Previous/next links follow the editorial chapter order. Source entries always show attribution, dates and provenance, fetch/read status, a short seed abstract when permitted, and the original link. X entries remain URL-only and videos remain unwatched.

### Forms and overlays

Search is local, IME-safe, and updates `?q=`. Explicit submit commits the query; clear restores focus. A `<noscript>` message explains browsing. No select, dialog or overlay is needed.

### Iconography

Text labels are primary. No icon dependencies or external images.

### Motion

No animation is required; reduced motion disables any future smooth scrolling.

### Content and data visualization

Editorial identifies the evidence it uses. Counts distinguish requests, sources and reviewed pages. This edition is incomplete and unaffiliated. No inferred publication dates, watched-video claims or reproduced article bodies.

## Do's and Don'ts

- Do preserve a calm prose measure and visible source trails.
- Do keep all navigation usable on a 375px viewport.
- Don't use fetched as a synonym for read.
- Don't turn inaccessible sources into invented chapters or summaries.
