# Source Registry

Every factual claim in this presentation is tracked here with its authoritative source.
When editing content, update this file. When verifying, check the URLs and dates.

---

## Statistics

| Claim | Value | Section | Source | URL | Last Verified |
|-------|-------|---------|--------|-----|---------------|
| Average GPU utilization | 5% | hero, results | Cast AI 2026 State of Kubernetes Optimization Report | https://cast.ai/reports/kubernetes-optimization-report/ | 2026-08-09 |
| GPU overprovisioning factor | 20x | hero, gpu101 | Cast AI 2026 Report (5% util = 20x overprovisioned) | https://cast.ai/press-release/2026-state-of-kubernetes-optimization-report/ | 2026-08-09 |
| Enterprises at ≤50% GPU capacity | 86% | hero, results | VentureBeat Research survey (573 tech leaders, June 2026) | https://venturebeat.com/orchestration/wall-street-is-debating-the-ai-buildout-enterprises-just-answered-86-say-their-gpus-run-at-half-capacity-or-less | 2026-08-09 |
| Global AI infra spending 2026 | $401B (construction add-on) | results | Gartner Jan 2026 forecast -- $401B is the additional construction spending, total AI infra is $1.37T | https://cxotoday.com/media-coverage/gartner-says-worldwide-ai-spending-will-total-2-5-trillion-in-2026/ | 2026-08-09 |
| MIG density improvement | 7x (7 models on 1 A100) | results, mechanisms | Architecture capability (7 MIG 1g.10gb slices on A100 80GB) | https://docs.nvidia.com/datacenter/tesla/mig-user-guide/ | 2026-08-09 |
| Idle capacity recoverable (scale-to-zero) | 85% | results, mechanisms | Architecture estimate (20 models, 3 active = 85% idle) | Presentation calculation -- see mechanisms section | 2026-08-09 |
| Training speedup with GPUDirect RDMA | 3x | results, training | Red Hat on RoCE/InfiniBand (5h → 1h40m) | Presentation claim -- needs authoritative Red Hat source | 2026-08-09 |
| MIG SM utilization for content safety | 42–88% | mechanisms | Architecture claim for 2g.20gb slices | Presentation claim -- needs benchmark source | 2026-08-09 |
| Cold-start reduction (shared NAS + accelerated loader) | 5–30 min → 30–90 sec | mechanisms | Architecture estimate for 70B model | Presentation estimate | 2026-08-09 |
| Run:AI pricing | $4,500/GPU/year | appendix | NVIDIA AI Enterprise commercial pricing | Industry estimates | 2026-08-09 |
| H100 on-demand equivalent rate | $3.20/hr | discovery | On-demand cloud equivalent pricing | https://cast.ai/blog/gpu-cloud-pricing/ | 2026-08-09 |
| A100 on-demand equivalent rate | $1.90/hr | discovery | On-demand cloud equivalent pricing | https://cast.ai/blog/gpu-cloud-pricing/ | 2026-08-09 |
| FOCUS specification version | v1.4 | finops | FinOps Foundation | https://focus.finops.org/ | 2026-08-09 |

### Anonymized Production Results (llm-d Inference Optimization)

These results are from enterprise llm-d deployments. They are inference optimization results — fewer GPUs needed to serve the same traffic with better latency. Per policy: no customer names. Results may be shown without attribution.

| Claim | Value | Slide Context | Original Source | Notes | Added |
|-------|-------|---------------|-----------------|-------|-------|
| GPU reduction from llm-d | 61% (256 → 99 GPUs) | Slide 17 stats, Slide 35 stats | Enterprise LLM serving deployment on H200 | llm-d inference optimization, not fleet management | 2026-08-09 |
| KV-cache hit rate | 93% | Slide 17 stats | Enterprise LLM deployment on H200 | Prefix-aware routing via EPP + KV-Cache Indexer | 2026-08-09 |
| TTFT improvement | 10–30x | Slide 17 stats | Enterprise deployment on A100 | KV-cache-aware routing + prefix caching | 2026-08-09 |
| Throughput increase | +40% | Slide 17 stats | Enterprise deployment on H200 | Disaggregated prefill/decode | 2026-08-09 |
| GPU reduction (compliance workload) | 80%, p99 < 500ms | Not used in slides | Enterprise compliance checking deployment | 2,000 checks/min sustained | 2026-08-09 |

**Cross-check note (from PM review):** Some llm-d POC results are not GPUaaS-specific. The 61% GPU reduction is an llm-d inference optimization result, not a GPUaaS fleet management metric. The deck correctly attributes these as "distributed inference optimization" results.

### FinOps Dashboard Mock Data

| Claim | Value | Slide Context | Source | Added |
|-------|-------|---------------|--------|-------|
| Total allocated cost (monthly) | $93,400 | Slide 28 table | Internal GPUaaS knowledge guide — July 2026 showback mock | 2026-08-09 |
| Total active compute cost | $54,490 | Slide 28 table | Internal GPUaaS knowledge guide | 2026-08-09 |
| Total idle allocation cost | $38,910 | Slide 28 table | Derived: $93,400 - $54,490 | 2026-08-09 |
| Fleet average efficiency | 58% | Slide 28 table | Derived: $54,490 / $93,400 | 2026-08-09 |
| Data Science efficiency | 25% | Slide 28 table | Internal GPUaaS knowledge guide | 2026-08-09 |

### New Content from Gap Analysis (Aug 2026)

| Claim | Value | Slide Context | Source | Added |
|-------|-------|---------------|--------|-------|
| Inference dominates GPU demand | 55–67% of AI compute in 2026; 80–90% over model lifecycle | Slide 3 note | Deloitte TMT Predictions 2026; Presenc AI research; Lenovo CEO at CES 2026 | 2026-08-09 |
| Shadow IT risk from slow GPU provisioning | 3–5 day ServiceNow wait drives data scientists to cloud | Slide 5 icon | Red Hat AI GPU-as-a-Service Business deck p.7 | 2026-08-09 |
| Scale-to-zero objection — "loading on demand creates queues" | Counter-framing: busy models stay warm, only tail powers down | Slide 24 bullet | Internal GPUaaS Use Cases document p.2 | 2026-08-09 |
| MultiKueue dispatching strategies | All-at-once, Incremental, External | Slide 26 bullet | MultiKueue in RHACM document p.6 | 2026-08-09 |
| WorkloadPriorityClass vs Pod priority | Kueue has own priority system separate from K8s Pod priority | Slide 15 bullet | DRA, Kueue, and OpenShift Scheduling document p.14 | 2026-08-09 |
| InstaSlice / Dynamic Accelerator Slicer | DRA-powered on-demand MIG slicing | Slide 14 bullet | Red Hat AI GPU-as-a-Service Business deck p.33-34 | 2026-08-09 |
| Three metering layers | Metering → Rating → Allocation | New slide (Enterprise Scale) | Internal GPUaaS knowledge guide | 2026-08-09 |
| Internal catalog pricing tiers | Shared dev, guaranteed shared, dedicated GPU, reserved cluster | New slide (Reference Solution) | Internal GPUaaS knowledge guide | 2026-08-09 |

### Accuracy Notes

- **86% vs 83%**: VentureBeat corrected their original article (July 14, 2026 update) from 86% to 83%. The article title still says "86%" but the body text says "83%". The slides no longer cite this stat directly — the 5% utilization (Cast AI) is used as the anchor stat instead.
- **$401B**: This is specifically the *additional construction spending* driven by AI infrastructure buildout, not the total AI infrastructure spending ($1.37T). The presentation's stat-source says "Gartner" which is correct.
- **3x training speedup**: Confirmed by Red Hat Developer article (April 2025) — baseline OVN: 5h, GPUDirect RDMA: 1h40m. Source: https://developers.redhat.com/articles/2025/04/29/accelerate-model-training-openshift-ai-nvidia-gpudirect-rdma
- **61% GPU reduction**: This is a benchmark-validated result (10 GPUs round-robin → 3.9 GPUs with llm-d P/D disaggregation). Previously labeled as "anonymized enterprise deployment" — corrected to "benchmark-validated."
- **+40% throughput / P/D scale threshold**: Disaggregated P/D shows net-positive gains at 16–32 GPUs for typical chat workloads; below 8 GPUs, chunked prefill on colocated instances is more efficient (Groundy analysis, 2026). AWS validated 1P:1D on 16 H100s with Llama-3.3-70B showing flat decode latency under load. llm-d v0.5 validated ~3,100 tokens/s per B200 decode GPU on a 16×16 topology. Sources: https://groundy.com/articles/prefill-decode-disaggregation-the-architecture-shift-redefining-llm-serving-at-scale/, https://aws.amazon.com/blogs/machine-learning/disaggregated-prefill-and-decode-for-llm-inference-on-sagemaker-hyperpod/ — Verified 2026-08-10.
- **10x concurrent users (REMOVED)**: The vLLM PagedAttention paper shows 2–4x throughput improvement vs Orca, up to 24x vs naive frameworks. The "10x" figure had no benchmark support. Corrected to "2–4x higher throughput."
- **93% cache hit rate (CORRECTED to 87%+)**: Published llm-d benchmarks show 87.4% cache hit rate. The 93% figure did not appear in any public benchmark.
- **42–88% SM utilization (REMOVED)**: No public benchmark supports this specific range. Replaced with qualitative statement.
- **llm-d GA timing (CORRECTED)**: llm-d went GA in RHOAI 3.3 (March 2026), not 3.5 (August 2026) as previously stated. Source: Red Hat Customer Portal release components article.
- **vLLM model count (CORRECTED)**: Updated from "100+" to "200+" per current official vLLM documentation and GitHub README.
- **InstaSlice (CORRECTED)**: InstaSlice/DAS does NOT use DRA. It uses its own AllocationClaim CRD and scheduler plugin. DRA partitionable devices (beta K8s 1.36) will supersede it.
- **FIPS/FedRAMP (TIGHTENED)**: OpenShift runs in FIPS mode via validated RHEL crypto modules (not OCP itself holding validation). FedRAMP High is for ROSA on GovCloud, not self-managed OCP.
- **Run:AI pricing (CLARIFIED)**: $4,500/GPU/year is the NVIDIA AI Enterprise (NVAIE) bundle price that includes Run:AI, not a standalone Run:AI price.
- **60–90% fragmentation (CORRECTED to 60–80%)**: Per the original PagedAttention paper (UC Berkeley).

---

## Version Numbers and Feature Availability

| Component | Claim | Section | Source | URL | Last Verified |
|-----------|-------|---------|--------|-----|---------------|
| DRA | GA in K8s 1.34 | mechanisms, layers | Kubernetes blog | https://kubernetes.io/blog/2025/09/01/kubernetes-v1-34-dra-updates/ | 2026-08-09 |
| DRA API version | resource.k8s.io/v1 | mechanisms | Kubernetes docs | https://kubernetes.io/docs/concepts/scheduling-eviction/dynamic-resource-allocation/ | 2026-08-09 |
| DRA RHOAI GA target | 3.6/3.7 | layers, stack | RHOAI internal roadmap | Internal strategy document | 2026-08-09 |
| Kueue API version | v1beta2 | governance | Kueue GitHub | https://github.com/kubernetes-sigs/kueue/ | 2026-08-09 |
| Kueue latest release | v0.19.0 | governance | Kueue GitHub releases | https://github.com/kubernetes-sigs/kueue/releases | 2026-08-09 |
| MaaS | GA in RHOAI 3.4 | maas | RHOAI internal roadmap | Internal strategy document | 2026-08-09 |
| RHOAI 3.5 features | GPU Topology Dashboard, Kueue in Workbenches, MLflow GA, llm-d observability | roadmap | RHOAI internal roadmap | Internal strategy document | 2026-08-09 |
| RHOAI 3.6 features | Kueue Quota Dashboard, DRA DP, KEDA GA for llm-d, Compute Profiles v1 | roadmap | RHOAI internal roadmap | Internal strategy document | 2026-08-09 |
| RHOAI 3.7 features | Scheduling explainability, GPU cost attribution, Advanced Compute Profiles | roadmap | RHOAI internal roadmap | Internal strategy document | 2026-08-09 |
| RHOAI 3.8 features | Self-service GPU pool wizard, idle GPU reclamation | roadmap | RHOAI internal roadmap | Internal strategy document | 2026-08-09 |
| Compute Profiles | Targeted RHOAI 3.7 | vocab, stack | RHOAI internal roadmap | Internal strategy document | 2026-08-09 |
| NVIDIA DRA GPU driver donated to CNCF | KubeCon Europe 2026 | layers | KubeCon Europe 2026 announcement | Needs specific announcement URL | 2026-08-09 |
| Kubeflow Trainer v2 API | trainer.kubeflow.org/v1alpha1, release v2.2.0 GA but API is alpha | training | Kubeflow Trainer docs | https://github.com/kubeflow/trainer | 2026-08-09 |
| KServe latest release | v0.20.0 (as of Aug 2026) | stack | KServe GitHub | https://github.com/kserve/kserve/releases | 2026-08-09 |
| MaaSSubscription API | maas.opendatahub.io/v1alpha1 | maas | RHOAI internal API | Internal | 2026-08-09 |
| LLMInferenceService API | serving.kserve.io/v1alpha1 | maas | KServe/llm-d | https://github.com/llm-d/llm-d | 2026-08-09 |

---

## CNCF Project Status

| Project | Status | Accepted Date | Section | Source | URL | Last Verified |
|---------|--------|---------------|---------|--------|-----|---------------|
| KServe | CNCF Incubating | Sep 29, 2025 | vocab, stack | CNCF project page | https://www.cncf.io/projects/kserve/ | 2026-08-09 |
| llm-d | CNCF Sandbox | Mar 12, 2026 | vocab, layers, maas, stack | CNCF project page | https://www.cncf.io/projects/llm-d/ | 2026-08-09 |
| KEDA | CNCF Graduated | Aug 22, 2023 | stack | CNCF project page | https://www.cncf.io/projects/keda/ | 2026-08-09 |
| Kueue | K8s SIG Scheduling (kubernetes-sigs) | N/A | vocab, stack | Kueue homepage | https://kueue.sigs.k8s.io/ | 2026-08-09 |
| vLLM | Community (UC Berkeley origin) | N/A | stack | vLLM GitHub | https://github.com/vllm-project/vllm | 2026-08-09 |
| KubeRay | CNCF / Ray Community | N/A | vocab, stack | KubeRay GitHub | https://github.com/ray-project/kuberay | 2026-08-09 |

### llm-d Founding Contributors

Verified: Red Hat, Google Cloud, IBM Research, CoreWeave, NVIDIA (source: CNCF blog, March 24, 2026).
Additional contributors: AMD, Cisco, Hugging Face, Intel, Lambda, Mistral AI, UC Berkeley, University of Chicago.

---

## Architecture Claims

| Claim | Section | Type | Verification |
|-------|---------|------|-------------|
| MIG carves A100 into up to 7 isolated slices | vocab, mechanisms | Hardware spec | Verified -- NVIDIA MIG User Guide |
| MIG provides dedicated compute, memory, and cache per slice | vocab, mechanisms | Hardware spec | Verified -- NVIDIA MIG User Guide |
| A100 80GB supports MIG profiles including 1g.10gb | mechanisms | Hardware spec | Verified -- NVIDIA MIG User Guide |
| llm-d provides KV-cache-aware routing via EPP | vocab, layers, maas | Architecture | Verified -- llm-d GitHub, CNCF blog |
| llm-d supports disaggregated prefill/decode | layers, maas | Architecture | Verified -- llm-d CNCF blog |
| llm-d KV transfer uses NIXL (zero-copy GPU-to-GPU RDMA) | patterns | Architecture | Verified -- llm-d CNCF blog, patterns section |
| WVA scales on queue depth, KV-cache pressure, token throughput | vocab, layers, loops | Architecture | Verified -- llm-d documentation |
| WVA supports minReplicas: 0 for scale-to-zero | vocab, mechanisms | Architecture | Verified -- llm-d documentation |
| DRA uses CEL expressions for device selection | mechanisms | API spec | Verified -- Kubernetes DRA docs |
| DRA supports partitionable devices, device taints, shared counters | mechanisms | API spec | Verified -- beta in K8s 1.36 (KEP 4815, 5055), not part of 1.34 GA core |
| InstaSlice (Dynamic Accelerator Slicer) creates/destroys MIG slices dynamically via DRA | mechanisms | Architecture | Internal Red Hat AI GPUaaS Business deck -- InstaSlice DRA integration |
| WorkloadPriorityClass is Kueue's own priority system, separate from K8s Pod priority | governance | API spec | Verified -- Kueue docs, DRA/Kueue scheduling document |
| MultiKueue dispatching: all-at-once, incremental, external strategies | multi-cluster | Architecture | Verified -- MultiKueue in RHACM document p.6 |
| Kueue supports nominalQuota, borrowingLimit, preemption, fairSharing | governance | API spec | Verified -- Kueue docs |
| Kueue Resource Transformations for GPU credit normalization | governance | API spec | Verified -- Kueue Configuration API |
| KServe provides scale-to-zero via Knative-based autoscaling | vocab, mechanisms | Architecture | Verified -- KServe docs |
| JIT checkpointing intercepts SIGTERM for preemption-safe training | training | Architecture | Architecture pattern -- needs specific implementation reference |
| AMD MI300X supports DCM (CPX + NPS4) = 8→64 resources | stack | Hardware spec | AMD documentation |
| Intel Gaudi 3: full device only (no partitioning) | stack | Hardware spec | Intel Gaudi documentation |
| NVLink bandwidth: 900 GB/s between 8 GPUs (H100 SXM) | layers, challenges | Hardware spec | NVIDIA H100 datasheet |
| llm-d supports NVIDIA CUDA, AMD ROCm, Intel Gaudi, IBM Spyre | stack | Multi-vendor | Verified -- CNCF project page, llm-d docs |
| Red Hat AI Inference: standalone product, runs on OCP or managed K8s | appendix | Product | Red Hat product page |
| OpenShift has FedRAMP High authorization | vocab | Compliance | Red Hat compliance documentation |
| FIPS 140-2 validated cryptography in OpenShift | vocab | Compliance | Red Hat security documentation |

---

## Red Hat Product Claims

| Product | Claim | Section | Source | Last Verified |
|---------|-------|---------|--------|---------------|
| Red Hat OpenShift AI | Core AI platform: workbenches, training, serving, monitoring, MaaS | appendix | Red Hat product page | 2026-08-09 |
| Red Hat AI Inference | Standalone inference (vLLM + llm-d), runs on OCP or managed K8s (AKS, CKS) | appendix | Red Hat product page | 2026-08-09 |
| Red Hat AI Factory with NVIDIA | Co-engineered stack: RHOAI + NVIDIA AI Enterprise | appendix | Red Hat product page | 2026-08-09 |
| Red Hat Build of Kueue | Batch scheduling, quotas, fair sharing | appendix | Red Hat product page | 2026-08-09 |
| Red Hat Advanced Cluster Management | Multi-cluster GPU fleet management, MultiKueue add-on | stack, appendix | Red Hat product page | 2026-08-09 |
| OpenShift Container Platform | Foundation: GPU Operator, DRA, node management, Prometheus | appendix | Red Hat product page | 2026-08-09 |

---

## Competitor/Landscape Claims

| Claim | Section | Source | Last Verified |
|-------|---------|--------|---------------|
| Run:AI pricing at $4,500/GPU/year | appendix | NVIDIA AI Enterprise pricing (industry estimates) | 2026-08-09 |
| Run:AI GPU vendors: NVIDIA-only post-acquisition | appendix | Industry analysis | 2026-08-09 |
| KAI Scheduler: proprietary + OSS core | appendix | Run:AI/NVIDIA announcements | 2026-08-09 |
| KAI enforced memory isolation NOT open-sourced | appendix | Industry analysis -- verify with latest KAI releases | 2026-08-09 |

---

## How to Use This File

1. **Adding a claim**: Add a row to the appropriate table with the claim text, value, section, source name, URL, and today's date.
2. **Updating a claim**: Find the row, update the value and URL, set the date to today.
3. **Verifying**: For any claim with a "Last Verified" date older than 90 days, re-check the URL and update.
4. **Missing URLs**: Claims with "Internal strategy document" or "Needs specific URL" should be replaced with public URLs as they become available.
5. **Corrections**: If a source changes (like VentureBeat's 86%→83% correction), note it in the "Accuracy Notes" section and decide whether to update the presentation.
