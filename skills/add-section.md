# Add a New Section

Step-by-step workflow for adding a new topic to the presentation.

## Prerequisites

Read `AGENTS.md` in the repo root for full HTML conventions and CSS class reference.

## Workflow

### 1. Determine Placement

- Review `presentation.json` to understand the current section flow
- Identify where the new topic fits in the narrative (the presentation follows a logical progression: problem → architecture → mechanisms → workloads → operations → implementation)
- Pick a short, lowercase `id` (e.g., `gpu-operator`, `networking`, `security`)

### 2. Research the Topic

- Search authoritative sources for the topic (see priority list in `AGENTS.md`)
- Cross-reference with `KNOWLEDGE_BASE.md` for existing context
- Collect specific version numbers, API names, and measurable claims
- For each fact, note the source URL

### 3. Create the Section File

- Copy `skills/section-template.html` to `sections/{id}.html`
- Replace placeholders:
  - `SECTION_LABEL` → short category (e.g., "GPU Operations")
  - `SECTION_TITLE` → descriptive title
  - `SECTION_INTRO` → one paragraph framing the topic
  - `INSIGHT_TEXT` → single key takeaway
- Add content using only the CSS classes documented in `AGENTS.md`
- Never hardcode colors — use `var(--token)` custom properties
- Never add `<section>` wrappers — the loader does this
- Never add `onclick` handlers — use `data-*` attributes for interactive elements

### 4. Update presentation.json

Add an entry to the `sections` array at the desired position:

```json
{ "id": "your-id", "file": "sections/your-id.html", "navLabel": "Short Label" }
```

If the section should appear in the agenda grid, add an `agenda` entry (max 6 cards total).

If the section should reveal alongside another section in presenter mode, add it to a `presenterGroups` array.

### 5. Register Sources

For every factual claim in the new section, add a row to `SOURCES.md`:

```markdown
| Claim text | Value | Source name | URL | YYYY-MM-DD |
```

### 6. Update Knowledge Base

If the section introduces concepts not covered in `KNOWLEDGE_BASE.md`, add them under the appropriate layer.

### 7. Verify

- [ ] Section file is a pure HTML fragment (no `<html>`, `<body>`, `<section>` wrapper)
- [ ] Starts with `<span class="section-label">` and `<h2>`
- [ ] Ends with `<div class="insight-box">`
- [ ] All colors use CSS custom properties
- [ ] All statistics have source attribution (`stat-source` or inline citation)
- [ ] All claims registered in `SOURCES.md` with URLs
- [ ] No inline `onclick` or event handlers
- [ ] Test locally: `python3 -m http.server 8000`, confirm section loads and navigation works
