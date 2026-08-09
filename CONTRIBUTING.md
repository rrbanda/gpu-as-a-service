# Contributing

This presentation is designed for AI-assisted contribution. An AI coding assistant can handle structure, conventions, and accuracy validation automatically by reading the instructions in `AGENTS.md` and the workflow guides in `skills/`.

## AI-Assisted Contribution (Recommended)

Open this repo in any AI-capable code editor. The agent instructions and skills work with any AI coding assistant.

### Add a new topic

Tell your AI assistant:

> "Add a section about GPU operator lifecycle management. Read skills/add-section.md for the workflow."

The assistant will research the topic, create the section file following conventions, update `presentation.json`, and register all claims in `SOURCES.md`.

### Update existing content

> "Update the DRA section -- DRA is now GA in OCP 4.22. Read skills/edit-section.md."

The assistant will verify the claim against upstream docs, update the section, and update `SOURCES.md`.

### Verify accuracy

> "Verify the accuracy of the roadmap section. Read skills/verify-accuracy.md."

The assistant will cross-reference every claim against `SOURCES.md` and upstream documentation, flagging anything stale or changed.

### Customize for a customer or event

> "Customize this presentation for a 30-minute slot focused on inference optimization. Read skills/customize-presentation.md."

The assistant will select and reorder sections, update the agenda, and adjust presenter groups.

---

## Manual Contribution

If contributing without an AI assistant, read `AGENTS.md` for all conventions, then follow the steps below.

### File Structure

```
index.html              Thin shell -- do not add content here
css/main.css            Styles -- use var() tokens, never hex colors
js/loader.js            Section loader -- rarely needs editing
js/interactions.js      Interactive behaviors -- rarely needs editing
presentation.json       Section order, nav labels, agenda, presenter groups
sections/*.html         Content lives here -- one file per topic
KNOWLEDGE_BASE.md       Deep reference organized by knowledge layer
SOURCES.md              Source registry for every factual claim
SPEAKER_NOTES.md        Presenter talking points
```

### Add a New Section

1. Copy `skills/section-template.html` to `sections/{id}.html`
2. Replace placeholders with content following CSS class conventions in `AGENTS.md`
3. Add an entry to the `sections` array in `presentation.json`
4. Register all factual claims in `SOURCES.md` with source URLs
5. Test locally: `python3 -m http.server 8000`

### Modify Existing Content

1. Edit the relevant `sections/*.html` file
2. Use existing CSS classes (see `AGENTS.md` for the complete reference)
3. Use `var()` tokens from `:root` block, never raw color values
4. Update `SOURCES.md` if factual claims changed
5. Test at both desktop and mobile widths

### Add a CSS Component

1. Add styles to `css/main.css` following existing organization
2. Use CSS custom properties from the `:root` block
3. Test at 768px breakpoint and add responsive overrides to the `@media` block

### Style Conventions

- All colors use CSS custom properties (`var(--token)`)
- Border radius uses `var(--radius)` (12px) or `var(--radius-sm)` (8px)
- Transitions use `var(--transition)`
- Font sizes use `rem` or `clamp()` for responsive scaling
- No `!important` except in print and presenter-mode styles

### Local Development

```bash
python3 -m http.server 8000
# Open http://localhost:8000
```

No build step required. The presentation uses `fetch()` to load sections, so it requires an HTTP server (not `file://`).

### Pull Requests

1. Fork the repo
2. Create a feature branch
3. Make changes following conventions in `AGENTS.md`
4. Verify all factual claims are registered in `SOURCES.md`
5. Test locally at desktop and mobile widths
6. Submit a PR with a description of what changed and why

---

## Key Files for Contributors

| File | Purpose |
|------|---------|
| `AGENTS.md` | Complete agent instructions -- HTML conventions, CSS classes, accuracy rules |
| `skills/add-section.md` | Workflow for adding a new topic |
| `skills/edit-section.md` | Workflow for updating content |
| `skills/verify-accuracy.md` | Workflow for fact-checking |
| `skills/customize-presentation.md` | Workflow for forking for a specific audience |
| `SOURCES.md` | Source registry -- every claim mapped to a URL |
| `KNOWLEDGE_BASE.md` | Deep reference guide organized by knowledge layer |
