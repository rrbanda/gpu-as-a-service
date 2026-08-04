# Contributing

This is a reusable whiteboard asset. The most common contribution is forking it for a specific customer engagement.

## Fork for a Customer Session

1. **Fork** this repo (or create a private copy)
2. **Customize the environment section** (`#discovery` in `index.html`) — replace the generic fleet data with the customer's actual GPU inventory, team structure, and utilization patterns
3. **Reorder the Solution Roadmap** (`#nextsteps`) to match the customer's priorities
4. **Adjust the Decision Tree** (the `selectDecision` function in `js/main.js`) if the customer's workload mix differs
5. **Deploy** to GitHub Pages or any static host

## Modify Content

All content is in `index.html`. The page is structured as 18 `<section>` elements, each with a unique `id`. To find a section, search for its ID:

```
#hero        — Opening hook, agenda, and pain-point cards
#gpu101      — GPU 101 (hotel analogy for beginners)
#vocab       — Flash card vocabulary
#problems    — Three GPU problems
#discovery   — Enterprise environment narrative
#challenges  — Seven AI challenges
#layers      — Five-layer architecture
#loops       — Three control loops
#mechanisms  — GPU mechanisms deep dive
#governance  — Kueue configuration
#finops      — GPU FinOps
#patterns    — Architecture patterns (Dedicated Inference Pool / Shared Cluster)
#decision    — Decision tree
#results     — Industry data
#stack       — Technology stack
#usecases    — Use case mapping (with voting)
#personas    — Persona summary
#nextsteps   — Solution roadmap
```

## Add a New CSS Component

1. Add styles to `css/main.css` following existing section organization
2. Use `var()` tokens from the `:root` block at the top, not raw color values
3. Test at `768px` breakpoint and add responsive overrides to the `@media` block at the bottom

## Style Conventions

- All colors use CSS custom properties from the `:root` block in `css/main.css`
- Border radius uses `var(--radius)` (12px) or `var(--radius-sm)` (8px)
- Transitions use `var(--transition)` for consistency
- Font sizes use `rem` or `clamp()` for responsive scaling
- No `!important` except in print and presenter-mode styles

## Testing Locally

```bash
open index.html
```

No build step. For live reload during development, use any static file server:

```bash
# Python
python3 -m http.server 8000

# Node (if available)
npx serve .
```

## Pull Requests

If you have improvements to the core content, architecture accuracy, or UX:

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Test locally at both desktop and mobile widths
5. Submit a PR with a clear description of what changed and why
