# GPU as a Service — Interactive Architecture Deep Dive

An interactive, modular whiteboard experience that walks through GPU-as-a-Service architecture on Kubernetes. From "why are enterprise GPUs at 5% utilization?" to a production-ready implementation roadmap.

**[Live Demo](https://rrbanda.github.io/gpu-as-a-service/)**

---

## What This Is

A zero-dependency interactive presentation designed for:

- **Technical deep dives** into GPU scheduling, partitioning, and governance on OpenShift AI
- **Whiteboarding sessions** with enterprise platform engineers, ML engineers, and architects
- **Reusable asset** — fork, swap section files, edit the config, present

Built with vanilla HTML, CSS, and JavaScript. No frameworks, no build step, no npm.

## Quick Start

Since the presentation loads section files via `fetch()`, you need an HTTP server for local development:

```bash
git clone https://github.com/rrbanda/gpu-as-a-service.git
cd gpu-as-a-service

# Any of these work:
python3 -m http.server 8000        # Python (built-in)
npx serve .                        # Node.js (npx, no install)
php -S localhost:8000               # PHP (built-in)
```

Open `http://localhost:8000` in your browser. The live GitHub Pages deployment works without any server setup.

## Architecture

The presentation is **config-driven**. A single `presentation.json` file defines section order, navigation labels, agenda cards, and presenter mode groupings. Sections are individual HTML fragment files loaded at runtime.

```
gpu-as-a-service/
├── index.html              # Thin shell (~45 lines) — head, nav, main, footer
├── presentation.json       # Section order, nav labels, agenda, presenter groups
├── sections/               # One HTML fragment per topic
│   ├── hero.html           #   Opening hook + agenda grid placeholder
│   ├── gpu101.html         #   GPU fundamentals
│   ├── vocab.html          #   11 interactive flashcards
│   ├── discovery.html      #   Example environment + waste analysis
│   ├── challenges.html     #   7 AI-specific scheduling challenges
│   ├── layers.html         #   Five-layer architecture (expandable cards)
│   ├── loops.html          #   Three concentric control loops
│   ├── mechanisms.html     #   MIG, DRA, scale-to-zero deep dive
│   ├── governance.html     #   Kueue configuration + YAML examples
│   ├── maas.html           #   MaaS, GenAI Studio, llm-d
│   ├── training.html       #   KFTv2, JIT checkpointing, CodeFlare
│   ├── finops.html         #   GPU FinOps + showback dashboards
│   ├── patterns.html       #   Architecture patterns (toggle view)
│   ├── decision.html       #   Interactive 3-question decision tree
│   ├── stack.html          #   Technology stack components
│   ├── results.html        #   Industry benchmark data
│   ├── usecases.html       #   Use case → capability → feature mapping
│   ├── personas.html       #   Team persona summary
│   ├── roadmap.html        #   RHOAI 3.5–3.8 product roadmap
│   ├── nextsteps.html      #   10-step implementation plan
│   └── appendix.html       #   Collapsible landscape comparison + product portfolio
├── css/
│   └── main.css            # Global styles — tokens, layout, components, responsive, print
├── js/
│   ├── loader.js           # Reads config, fetches sections, builds nav/arrows/agenda
│   └── interactions.js     # Scroll reveal, animations, presenter mode, decision tree
├── images/
│   └── og-preview.png      # OpenGraph preview image
├── KNOWLEDGE_BASE.md       # Consolidated research reference (7 layers)
├── SPEAKER_NOTES.md        # Talking points + Q&A preparation
├── CHEAT_SHEET.md          # Quick-reference stats, YAML snippets, CLI commands
├── AGENTS.md               # AI coding assistant instructions (agent-agnostic)
├── SOURCES.md              # Source registry — every claim tracked with URLs
├── skills/                 # Agent workflow guides
│   ├── add-section.md      #   Add a new topic
│   ├── edit-section.md     #   Update existing content
│   ├── verify-accuracy.md  #   Fact-check against upstream docs
│   ├── customize-presentation.md  # Fork for a customer/event
│   └── section-template.html      # Starting point for new sections
├── CONTRIBUTING.md
├── LICENSE                 # Apache 2.0
└── .github/
    └── workflows/
        └── pages.yml       # GitHub Pages auto-deploy
```

## How It Works

1. `index.html` loads `js/loader.js`
2. `loader.js` fetches `presentation.json` for the config
3. All section HTML files are fetched in parallel via `Promise.all`
4. The loader builds the side-nav, wraps each fragment in `<section>` tags, appends navigation arrows, populates agenda cards and footer
5. After DOM is populated, `js/interactions.js` is loaded to initialize scroll animations, observers, presenter mode, and the decision tree

## Customization Guide

### Reorder Sections

Edit `presentation.json` — change the array order in `sections`. Navigation, section arrows, and the entire flow update automatically.

### Add a New Topic

1. Create `sections/newtopic.html` with your content (pure HTML fragment, no `<section>` wrapper)
2. Add an entry to the `sections` array in `presentation.json`:
   ```json
   { "id": "newtopic", "file": "sections/newtopic.html", "navLabel": "New Topic" }
   ```
3. Done — the loader handles the `<section>` wrapper, nav dot, and navigation arrow

### Remove a Topic

Delete the entry from `presentation.json`. The section file can stay on disk.

### Change Navigation Labels

Edit the `navLabel` field in `presentation.json`.

### Change Agenda Cards

Edit the `agenda` array in `presentation.json`. Each card has: `num`, `title`, `desc`, `target` (section ID to link to), and `accent` (CSS color variable).

### Change Presenter Groups

Edit the `presenterGroups` array in `presentation.json`. Sections in a group are revealed together with a single arrow key press.

### Change Colors

Edit `css/main.css`. All design tokens are CSS custom properties at the top:

```css
:root {
  --bg: #080b14;           /* Page background */
  --surface: #0f1420;      /* Card backgrounds */
  --text: #f1f5f9;         /* Primary text */
  --l1-fleet: #3b82f6;     /* Layer 1 accent (blue) */
  --l2-mechanisms: #06b6d4; /* Layer 2 accent (cyan) */
  /* ... see file for all tokens */
}
```

### Fork for a Different Talk

Copy the repo, swap section files, edit the config. The same shell, CSS, and JS work with completely different content.

## Presenter Mode

Press **P** to enter Presenter Mode:

- **Progressive reveal:** Sections hidden until → (right arrow). Related sections reveal in groups.
- **Pain-point cards:** 8 common pain points in the hero. Click **"+ Add Your Own"** live.
- **Editable environment:** Click highlighted numbers in the discovery section — idle counts auto-update.
- **Use case voting:** ▲ buttons on use cases for audience polling. Top-voted items highlight.
- **Decision tree:** 3 interactive questions generate a personalized architecture recommendation.

Press **P** again to exit.

## Deployment

### GitHub Pages (recommended)

The included workflow auto-deploys on push to `main`. Go to **Settings → Pages**, set Source to **GitHub Actions**, and push.

### Any Static Host

Copy the entire repo to any web server. Works on Netlify, Vercel, AWS S3 + CloudFront, nginx, Apache — no build step.

## Technical Details

- **Zero dependencies** — no npm, no build tools, no frameworks
- **Modular** — 21 independent section files, config-driven assembly
- **Config-driven** — reorder, add, remove sections via JSON
- **Dark theme** — designed for projection in meeting rooms
- **Mobile responsive** — side nav hides, grids reflow, touch-friendly
- **Print friendly** — `@media print` stylesheet strips animations
- **Accessible** — semantic HTML, keyboard navigable

## Contributing

This repo is built for AI-assisted contribution. Any AI coding assistant can add sections, update content, verify accuracy, and customize the presentation by reading `AGENTS.md` and the workflow guides in `skills/`. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Every factual claim is tracked in [SOURCES.md](SOURCES.md) with authoritative source URLs and verification dates, ensuring 100% technical accuracy.

## License

[Apache License 2.0](LICENSE)
