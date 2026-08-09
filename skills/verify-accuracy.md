# Verify Accuracy

Step-by-step workflow for fact-checking presentation content against upstream documentation.

## Scope

Run this skill on a single section, a group of sections, or the entire presentation.

## Workflow

### 1. Extract Claims

Read the target section file(s) from `sections/` and identify every factual claim:

| Claim Type | Examples |
|------------|----------|
| Version number | "GA in OCP 4.21", "Kueue v1.3", "RHOAI 3.5" |
| Statistic | "5% utilization", "$401B spending", "86% of enterprises" |
| Feature availability | "Tech Preview in 3.5", "targeted 3.7", "GA since 4.19" |
| API/CRD name | "ResourceClaim", "TrainJob", "InferencePool" |
| Project status | "CNCF Sandbox", "CNCF Incubating", "K8s SIG" |
| Hardware spec | "7 MIG slices", "80GB HBM3", "NVLink" |
| Architecture claim | "prefix-aware KV-cache routing", "disaggregated prefill/decode" |

### 2. Cross-Reference SOURCES.md

For each claim found in step 1:

1. Look up the claim in `SOURCES.md`
2. Check if a source URL exists
3. Check the "Last Verified" date
4. Flag claims that are:
   - **Missing**: not in SOURCES.md at all
   - **Stale**: last verified more than 90 days ago
   - **Unsourced**: in SOURCES.md but no URL

### 3. Re-Verify Flagged Claims

For each flagged claim, web-search the authoritative source:

- **Red Hat product versions/features**: search `site:docs.redhat.com` or `site:access.redhat.com`
- **Kubernetes features**: search `site:kubernetes.io` or check KEP status at `github.com/kubernetes/enhancements`
- **CNCF project status**: check `cncf.io/projects` or the project's GitHub About section
- **Industry statistics**: search for the named report (e.g., "Cast AI 2026 Kubernetes Report")
- **Hardware specs**: check vendor documentation (NVIDIA, AMD, Intel)

### 4. Produce Report

Output a structured verification report with these categories:

```
## Verification Report: [section name(s)]
Date: YYYY-MM-DD

### ✅ Verified (N claims)
| Claim | Value | Source | Confirmed |
|-------|-------|--------|-----------|

### ⚠️ Updated (N claims)
| Claim | Old Value | New Value | Source | Action Needed |
|-------|-----------|-----------|--------|---------------|

### ❌ Unverified (N claims)
| Claim | Value | Issue |
|-------|-------|-------|

### 🕐 Stale (N claims)
| Claim | Value | Last Verified | Days Old |
|-------|-------|---------------|----------|
```

### 5. Apply Fixes

For claims in the "Updated" category:
1. Follow the `skills/edit-section.md` workflow to update the content
2. Update `SOURCES.md` with the corrected value and today's date

For claims in the "Unverified" category:
1. Add `<!-- UNVERIFIED: [claim] -->` comment in the HTML
2. Add the claim to `SOURCES.md` with an empty URL and "UNVERIFIED" in the date column

### 6. Summary Checklist

- [ ] All claims in target section(s) identified
- [ ] Each claim cross-referenced against SOURCES.md
- [ ] Stale claims (>90 days) re-verified via web search
- [ ] Verification report produced
- [ ] Corrections applied where needed
- [ ] SOURCES.md updated with all new verification dates
