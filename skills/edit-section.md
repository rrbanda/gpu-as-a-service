# Edit a Section

Step-by-step workflow for updating existing presentation content.

## Prerequisites

Read `AGENTS.md` in the repo root for full HTML conventions and CSS class reference.

## Workflow

### 1. Identify What Changed

Common triggers:
- Version number update (e.g., "RHOAI 3.5" → "RHOAI 3.6")
- Feature status change (e.g., "Tech Preview" → "GA")
- Statistic refresh (e.g., new utilization data)
- Accuracy correction
- Content expansion or clarification

### 2. Verify the New Information

Before editing, confirm the new information is correct:

1. Check `SOURCES.md` for the existing claim and its source URL
2. Visit the source URL to confirm it still says what we claim
3. If the claim is changing, web-search the authoritative source to verify the new value
4. For Red Hat product claims, check: docs.redhat.com release notes
5. For Kubernetes claims, check: kubernetes.io changelog or KEP status
6. For CNCF project status, check: cncf.io/projects or the project's GitHub repo

### 3. Make the Edit

- Open the relevant `sections/*.html` file
- Update the content following existing conventions (see `AGENTS.md`)
- Preserve existing CSS classes and structure
- If updating a `stat-number`, update both the display text and `data-target` attribute
- If updating a `stat-source`, use the new source name

### 4. Update SOURCES.md

For every changed claim:

1. Find the existing row in `SOURCES.md`
2. Update the value, source URL, and verification date to today
3. If it's a new claim, add a new row

### 5. Update KNOWLEDGE_BASE.md

If the edit changes a concept described in `KNOWLEDGE_BASE.md`, update it there too. Keep both files in sync.

### 6. Verify

- [ ] The new information has been verified against an authoritative source
- [ ] `SOURCES.md` is updated with the new source URL and today's date
- [ ] `KNOWLEDGE_BASE.md` is updated if applicable
- [ ] No CSS classes were removed or renamed
- [ ] No inline styles replaced existing class-based styles
- [ ] Test locally if the change affects layout or interactivity
