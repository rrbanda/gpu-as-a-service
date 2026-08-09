# Agent Instructions

This file provides instructions for AI coding assistants working on this repository.
Read this file before making any changes.

## Project Overview

This is a modular, zero-dependency web presentation on **GPU as a Service** architecture on Red Hat OpenShift AI. It runs on GitHub Pages with no build step.

### File Structure

```
index.html              Thin shell (head, nav, main, footer, script tags)
css/main.css            All styles -- dark theme, CSS custom properties
js/loader.js            Fetches presentation.json, loads section fragments, builds nav
js/interactions.js      Scroll reveal, presenter mode, flashcards, counters, decision tree
presentation.json       Section order, nav labels, agenda cards, presenter groups, footer
sections/*.html         One HTML fragment per topic (21 files)
KNOWLEDGE_BASE.md       Deep-reference guide organized by seven knowledge layers
SOURCES.md              Every factual claim mapped to its authoritative source + verification date
SPEAKER_NOTES.md        Presenter talking points per section
CHEAT_SHEET.md          Quick-reference for Q&A
skills/                 Agent workflow guides for common contribution tasks
```

### How the Presentation Loads

1. `js/loader.js` fetches `presentation.json` at runtime
2. It reads the `sections` array and fetches each `.html` fragment in parallel
3. Each fragment is wrapped in `<section id="..." class="section">` with auto-generated navigation arrows
4. The `agenda` array populates the hero's 6-card grid
5. `presenterGroups` controls which sections reveal together in presenter mode (arrow keys)
6. After all sections are injected, `js/interactions.js` is loaded to attach behaviors

---

## Section HTML Conventions

Section files in `sections/` are **pure HTML fragments**. They contain only the inner content -- the loader wraps them in `<section>` tags and appends navigation arrows automatically.

### Required Structure

Every section file must start with:

```html
  <span class="section-label">CATEGORY LABEL</span>
  <h2>Section Title</h2>
```

And should end with an insight box:

```html
  <div class="insight-box">
    <strong>Key takeaway:</strong> One-sentence summary of the section's main point.
  </div>
```

### Available CSS Classes

Use only these existing classes from `css/main.css`. Never add inline styles for things that have a class. Never hardcode hex colors -- use CSS custom properties.

#### Layout

| Class | Purpose |
|-------|---------|
| `grid-2` | Two-column responsive grid (min 320px per column) |
| `grid-3` | Three-column responsive grid (min 280px per column) |
| `grid-4` | Four-column responsive grid (min 240px per column) |
| `card` | Surface-colored card with border, radius, hover lift |
| `insight-box` | Cyan-tinted callout box for key takeaways |

#### Statistics

| Class | Purpose |
|-------|---------|
| `stat-grid` | Grid container for stat cards |
| `stat-card` | Individual statistic card |
| `stat-number` | Large number display. Add `.green`, `.amber`, or `.red` for color. Use `data-target`, `data-suffix`, `data-prefix` for animated counters. |
| `stat-label` | Description text below the number |
| `stat-source` | Small attribution text (source name) |

#### Code & YAML

| Class | Purpose |
|-------|---------|
| `code-block` | Monospace code display with syntax highlighting spans (`.str`, `.num`, `.key`, `.comment`) |
| `details.yaml-toggle` | Collapsible YAML block with `<summary>` label |

#### Tables

| Class | Purpose |
|-------|---------|
| `table-wrap` | Scrollable table container |
| Standard `<table>`, `<th>`, `<td>` | Styled automatically |

#### Architecture Components

| Class | Purpose |
|-------|---------|
| `layer-card` | Expandable card for architecture layers. Use `data-layer="1"` through `data-layer="5"` for color coding. Contains `.layer-header` and `.layer-detail`. |
| `component-pills` | Flex container for technology pill tags |
| `component-pill` | Individual technology pill |
| `flow-diagram` | Horizontal flow with `.flow-node` and `.flow-arrow` |
| `flow-node` | Node in flow diagram. Add `.cyan`, `.pink`, `.purple`, `.blue`, `.amber` for color. |

#### Interactive Elements

| Class | Purpose |
|-------|---------|
| `flashcard` | Flip card (event delegation handles click). Contains `.flashcard-inner` > `.flashcard-front` + `.flashcard-back` |
| `flashcard-grid` | Grid container for flashcards |
| `decision-tree` | Container for decision questions |
| `decision-node` | Single question block |
| `decision-option` | Clickable answer. Use `data-question="q1"` and `data-value="yes"` attributes (no onclick). |
| `toggle-btn` | Pattern toggle button. Use `data-pattern="..."` attribute. |
| `pattern-view` | Content pane shown when its toggle is active |

#### GPU Visualizations

| Class | Purpose |
|-------|---------|
| `gpu-bars` | Container for GPU utilization bars |
| `mig-viz` | MIG slicing visualization (before → after) |
| `control-loops-visual` | Animated concentric rings + loop cards |

#### Personas & Use Cases

| Class | Purpose |
|-------|---------|
| `persona-card` | Card with `.persona-icon`, `.persona-waste`, `.persona-fix` |
| `mapping-persona` | Use case mapping block with vote buttons |
| `tech-card` | Technology stack card with `.tech-name`, `.tech-org`, `.tech-desc` |

#### Presenter Mode

| Class | Purpose |
|-------|---------|
| `wb-editable` | Inline-editable field (active in presenter mode). Use `data-field="..."`. |
| `wb-sticky-board` | Container for audience sticky notes |
| `wb-vote-btn` | Vote button (auto-injected by JS, visible only in presenter mode) |

### Color Tokens

Always use CSS custom properties, never hex values:

| Token | Use For |
|-------|---------|
| `var(--l1-fleet)` | Layer 1 / Fleet Discovery (blue) |
| `var(--l2-mechanisms)` | Layer 2 / GPU Mechanisms (cyan) |
| `var(--l3-governance)` | Layer 3 / Governance (purple) |
| `var(--l4-ai-aware)` | Layer 4 / AI-Aware Scheduling (pink) |
| `var(--l5-self-service)` | Layer 5 / Self-Service (amber) |
| `var(--red)` | Warning / negative stats |
| `var(--green)` | Positive / success |
| `var(--amber)` | Caution / neutral stats |
| `var(--surface)` | Card backgrounds |
| `var(--raised)` | Elevated surfaces |
| `var(--bg)` | Page background |
| `var(--border)` | Standard borders |
| `var(--text)` | Primary text |
| `var(--text-secondary)` | Body / paragraph text |
| `var(--text-muted)` | Labels, captions |

### Source Attribution Rules

Every factual claim must have attribution:

- **Statistics** displayed in `stat-card`: add `<div class="stat-source">Source Name</div>`
- **Inline claims**: add parenthetical source, e.g., `(Cast AI 2026 Kubernetes Report)`
- **Tables with data**: include a "Source" column
- After adding any claim, update `SOURCES.md` with the source URL and verification date

---

## presentation.json Configuration

```json
{
  "sections": [
    { "id": "section-id", "file": "sections/filename.html", "navLabel": "Nav Tooltip" }
  ],
  "agenda": [
    { "num": "01", "title": "Card Title", "desc": "Card description", "target": "section-id", "accent": "var(--token)" }
  ],
  "presenterGroups": [
    ["leader-section", "follower1", "follower2"]
  ],
  "footer": {
    "title": "Footer title",
    "text": "Footer text with HTML entities allowed"
  }
}
```

### Editing Rules

- **Section order** in the `sections` array determines navigation flow, side-nav order, and arrow links
- **Adding a section**: create `sections/{id}.html` and add an entry to the `sections` array at the desired position
- **Removing a section**: remove its entry from the array (the HTML file can remain)
- **Agenda cards**: the `agenda` array populates the hero section's 6-card grid; `target` must match a section `id`; `accent` should be a color token
- **Presenter groups**: sections in the same array are revealed together when pressing arrow keys in presenter mode; the first element is the "leader"

---

## Accuracy Requirements

This presentation is used for technical audiences. Every factual claim must be verifiable.

### What Counts as a Factual Claim

- Version numbers (e.g., "GA in OCP 4.21", "Kueue v1.3")
- Statistics (e.g., "5% average utilization", "$401B")
- Feature availability (e.g., "TP in RHOAI 3.5", "targeted 3.7")
- API/CRD names (e.g., "ResourceClaim", "TrainJob", "InferencePool")
- Project status (e.g., "CNCF Sandbox", "CNCF Incubating")
- Hardware specifications (e.g., "7 MIG slices on A100", "80GB HBM3")
- Architecture descriptions (e.g., "llm-d uses prefix-aware KV-cache routing")

### Before Committing Any Content Change

1. Verify every factual claim against its authoritative source (see `SOURCES.md`)
2. If modifying a claim, web-search the authoritative source to confirm the new value
3. Update `SOURCES.md` with the verified source URL and today's date
4. If a claim cannot be verified, mark it with `<!-- UNVERIFIED -->` in the HTML

### Authoritative Sources (in priority order)

1. **Red Hat documentation**: docs.redhat.com, access.redhat.com
2. **Kubernetes official docs**: kubernetes.io, github.com/kubernetes/enhancements
3. **CNCF project repos**: github.com/kubernetes-sigs/kueue, github.com/kserve, github.com/llm-d
4. **Upstream project docs**: vllm.readthedocs.io, ray.io/docs
5. **Vendor documentation**: NVIDIA, AMD, Intel official docs
6. **Industry reports**: named reports with publication dates (Gartner, IDC, Cast AI)

---

## Available Skills

The `skills/` directory contains step-by-step workflow guides for common tasks:

| Skill | File | Use When |
|-------|------|----------|
| Add Section | `skills/add-section.md` | Creating a new topic/section for the presentation |
| Edit Section | `skills/edit-section.md` | Updating existing content, fixing versions, refreshing stats |
| Verify Accuracy | `skills/verify-accuracy.md` | Fact-checking sections against upstream documentation |
| Customize Presentation | `skills/customize-presentation.md` | Forking for a specific customer, event, or audience |

Read the relevant skill file before performing that task. Each skill contains a checklist, conventions, and validation steps.

---

## Quick Reference

### Add a New Section

1. Read `skills/add-section.md`
2. Create `sections/{id}.html` following the HTML conventions above
3. Add entry to `presentation.json` `sections` array
4. Add all factual claims to `SOURCES.md`
5. Update `KNOWLEDGE_BASE.md` if the topic introduces new concepts

### Update Content

1. Read `skills/edit-section.md`
2. Verify the new information against authoritative sources
3. Edit the section file
4. Update `SOURCES.md` with new verification dates

### Verify Accuracy

1. Read `skills/verify-accuracy.md`
2. Cross-reference section claims against `SOURCES.md`
3. Web-search to re-verify any claim older than 90 days
4. Output a verification report

### Local Development

```bash
python3 -m http.server 8000
# Open http://localhost:8000
```

No build step. The presentation loads via fetch() so it requires an HTTP server (not file://).
