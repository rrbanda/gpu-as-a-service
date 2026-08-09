# Customize Presentation

Step-by-step workflow for forking this presentation for a specific customer, event, or audience.

## When to Use

- Preparing for a customer engagement with their specific GPU fleet data
- Tailoring for a conference talk with a specific time slot
- Adjusting for an audience with a particular focus (inference-only, training-heavy, FinOps)

## Workflow

### 1. Understand the Context

Gather information about:
- **Audience**: Who will be watching? (platform engineers, data scientists, executives, mixed)
- **Time**: How long is the slot? (15 min = ~5 sections, 30 min = ~10, 60 min = all)
- **Focus**: What matters most? (cost savings, inference latency, training scale, governance)
- **Customer data**: Do they have specific GPU fleet numbers, team structure, utilization metrics?

### 2. Select and Reorder Sections

Edit `presentation.json` to include only relevant sections and reorder for the audience:

**For inference-focused audiences:**
```
hero → gpu101 → vocab → discovery → mechanisms → maas → patterns → decision → stack → nextsteps
```

**For training-focused audiences:**
```
hero → gpu101 → vocab → discovery → training → governance → loops → finops → stack → nextsteps
```

**For executive / FinOps audiences:**
```
hero → gpu101 → discovery → challenges → results → finops → patterns → roadmap → nextsteps
```

**For 15-minute lightning talk:**
```
hero → gpu101 → challenges → layers → nextsteps
```

### 3. Customize Content

#### Discovery Section (Customer Fleet Data)

If you have the customer's actual GPU data, edit `sections/discovery.html`:
- Replace the `wb-editable` field default values with real numbers
- Update GPU types to match their fleet (e.g., replace A100 with H100)
- Update team names and utilization percentages

#### Next Steps Section (Implementation Roadmap)

Edit `sections/nextsteps.html` to reorder the 10-step plan based on customer priorities:
- If they already have Kueue, skip step 3
- If inference is urgent, move steps 4-6 to the top
- If FinOps is the driver, lead with steps 7-8

#### Decision Tree

Edit `sections/decision.html` if the customer's workload mix is already known -- you can pre-select answers or simplify the tree.

### 4. Update Agenda

Update the `agenda` array in `presentation.json` to reflect the selected sections. Maximum 6 cards. Each card needs:
- `num`: display number (01-06)
- `title`: short title
- `desc`: one-line description
- `target`: section id to link to
- `accent`: color token matching the section's theme

### 5. Update Presenter Groups

Adjust `presenterGroups` in `presentation.json` so that arrow-key navigation in presenter mode groups sections logically for your flow.

### 6. Verify

- [ ] `presentation.json` sections array contains only intended sections
- [ ] All section `id` values in agenda/presenterGroups match entries in sections array
- [ ] Customer-specific data in discovery section is accurate (if applicable)
- [ ] Nextsteps section reflects customer priorities (if applicable)
- [ ] Test locally: all sections load, navigation works, presenter mode works
- [ ] Footer text is appropriate for the audience
