# GPU as a Service — Interactive Architecture Deep Dive

An interactive, single-page whiteboard experience that walks through GPU-as-a-Service architecture on Kubernetes. From "why are enterprise GPUs 30-50% idle?" to a production-ready implementation roadmap.

**[Live Demo](https://rrbanda.github.io/gpu-as-a-service/)**

---

## What This Is

A self-contained, zero-dependency interactive page designed for:

- **Whiteboarding sessions** with enterprise customers evaluating GPU infrastructure
- **Technical deep dives** into GPU scheduling, partitioning, and governance on OpenShift AI
- **Reusable sales engineering asset** — fork, customize colors/content, present

Built with vanilla HTML, CSS, and JavaScript. No frameworks, no build step, no npm.

## Quick Start

```bash
git clone https://github.com/rrbanda/gpu-as-a-service.git
cd gpu-as-a-service
open index.html    # macOS
# or: xdg-open index.html (Linux)
# or: start index.html (Windows)
```

That's it. No install, no build, no server.

## Content Sections

The page follows a logical whiteboarding flow — each section builds on the last:

| # | Section | What It Covers |
|---|---------|----------------|
| 1 | **Opening Hook** | "30-50% idle" stat + embedded session agenda |
| 2 | **Vocabulary** | 11 interactive flip cards (MIG, DRA, Kueue, llm-d, KServe, etc.) |
| 3 | **Three Problems** | Why generic IaaS doesn't work for AI GPUs |
| 4 | **Enterprise Environment** | Realistic GPU fleet walkthrough — 86 GPUs, 4 teams, $540K/yr waste |
| 5 | **AI Challenges** | 7 AI-specific scheduling problems |
| 6 | **Five-Layer Architecture** | Expandable layer cards from physical GPUs to self-service |
| 7 | **Control Loops** | Three concentric loops: scheduling, serving, governance |
| 8 | **GPU Mechanisms** | MIG slicing visualization, GPU utilization bars, DRA examples |
| 9 | **Governance** | Kueue configuration — when to use it and when not to |
| 10 | **GPU FinOps** | Metering pipeline, showback dashboards, chargeback comparison |
| 11 | **Architecture Patterns** | Dedicated vs. shared vs. hybrid — toggle between them |
| 12 | **Decision Tree** | 3-question interactive quiz → personalized architecture recommendation |
| 13 | **Validated Results** | Animated production metrics (61% utilization improvement, etc.) |
| 14 | **Tech Stack** | Open-source components with provenance (KServe, llm-d, Kueue, etc.) |
| 15 | **Use Case Mapping** | Persona → Use Case → Capability → RHOAI Feature table |
| 16 | **Persona Summary** | 4 team personas with waste patterns and fixes |
| 17 | **Solution Roadmap** | 10-step implementation plan ordered by dependency and ROI |

## Project Structure

```
gpu-as-a-service/
├── index.html              # Page content (HTML only — no inline CSS/JS)
├── css/
│   ├── tokens.css          # Design tokens (colors, fonts, spacing)
│   ├── base.css            # Reset, typography, section layout, grids
│   ├── navigation.css      # Side nav dots, progress bar, scroll arrows
│   ├── hero.css            # Landing screen, hook, agenda timeline
│   ├── cards.css           # All card types, flashcards, mapping tables
│   ├── visualizations.css  # GPU bars, MIG animation, rings, dashboards
│   ├── interactive.css     # Pattern toggle, YAML collapsibles, decision tree
│   ├── roadmap.css         # Solution timeline, phase labels, step cards
│   └── responsive.css      # Mobile breakpoints + print styles
├── js/
│   ├── scroll.js           # Reading progress bar
│   ├── reveal.js           # Scroll-triggered section reveals + nav tracking
│   ├── animations.js       # GPU bars, MIG slices, animated counters
│   ├── interactions.js     # Layer cards expand, pattern toggle
│   └── decision-tree.js    # 3-question decision tree → recommendation
├── images/
│   └── og-preview.png      # Social share preview image
├── README.md
├── CONTRIBUTING.md
├── LICENSE                  # Apache 2.0
└── .github/
    └── workflows/
        └── pages.yml        # GitHub Pages auto-deploy
```

## Customization Guide

### Change Colors

Edit `css/tokens.css`. All 23 design tokens are CSS custom properties:

```css
:root {
  --bg: #080b14;           /* Page background */
  --surface: #0f1420;      /* Card backgrounds */
  --text: #f1f5f9;         /* Primary text */
  --l1-fleet: #3b82f6;     /* Layer 1 accent (blue) */
  --l2-mechanisms: #06b6d4; /* Layer 2 accent (cyan) */
  --red: #ef4444;          /* Warning / waste indicators */
  --green: #10b981;        /* Success / fix indicators */
  /* ... see file for all tokens */
}
```

### Add a New Section

1. Add HTML in `index.html` using the `<section id="your-id" class="section">` pattern
2. Add a nav dot in `<nav id="side-nav">`: `<a href="#your-id" data-label="Your Label"></a>`
3. Add a `↓` arrow in the preceding section: `<a href="#your-id" class="section-arrow">↓</a>`
4. Style new components in the appropriate CSS file

### Modify Content

All content lives in `index.html`. Search for section IDs to find what you need:
- `#hero` — Opening hook and agenda
- `#discovery` — Enterprise environment narrative
- `#nextsteps` — Solution roadmap (10 steps)

### Add Customer-Specific Data

The enterprise environment section (`#discovery`) uses generic data. To customize:
1. Replace GPU counts, types, and team names in the `#discovery` section
2. Update the waste calculations in the insight box
3. Adjust the Solution Roadmap steps to match the customer's priorities

## Deployment

### GitHub Pages (recommended)

The included workflow (`.github/workflows/pages.yml`) auto-deploys on push to `main`.

1. Go to **Settings → Pages** in your repo
2. Set Source to **GitHub Actions**
3. Push to `main` — the site deploys automatically

### Any Static Host

Copy the entire repo to any web server. No build step required. Works on:
- Netlify (drag-and-drop)
- Vercel (import repo)
- AWS S3 + CloudFront
- Any nginx/Apache server

### Embed in MkDocs

Add to your `mkdocs.yml` navigation:

```yaml
nav:
  - GPUaaS Deep Dive: https://rrbanda.github.io/gpu-as-a-service/
```

## Technical Details

- **Zero dependencies** — no npm, no build tools, no frameworks
- **~148 KB total** — loads instantly, works offline after first visit
- **Accessible** — semantic HTML, keyboard navigable, print stylesheet included
- **Dark theme** — designed for projection in meeting rooms
- **Mobile responsive** — side nav hides, grids reflow, touch-friendly cards
- **Print friendly** — `@media print` stylesheet strips animations and backgrounds

## License

[Apache License 2.0](LICENSE)
