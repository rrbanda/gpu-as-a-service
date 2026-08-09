# GPU-as-a-Service on RHOAI — Expert Knowledge Base

> Presenter's deep-reference guide. Organized by the **seven knowledge layers** an expert must command end-to-end.

---

## Layer 1 — The Business Case

### The GPU Crisis in Numbers

| Metric | Source | Value |
|--------|--------|-------|
| Global AI infra spending (2026) | Gartner | **$401 billion** |
| Average enterprise GPU utilization | Cast AI 2026 Kubernetes Report | **5%** (20x overprovisioned) |
| Enterprises running GPUs at ≤50% capacity | VentureBeat survey of 573 tech leaders | **86%** |
| Run:AI annual revenue before acquisition | Industry estimates | **$200M+** |
| Run:AI commercial pricing | NVIDIA AI Enterprise | **$4,500/GPU/year** |

### Why Utilization Is So Low

The root cause is a self-reinforcing procurement loop:

1. **FOMO-driven over-commitment** — teams hoard GPUs because supply is scarce; nobody releases capacity because the shortage that drives prices up is exactly why no team will give capacity back.
2. **Container architecture mismatch** — GPUs sit idle while waiting for CPU preprocessing, data loading, or network I/O. High activity does not equal high productivity.
3. **No utility layer** — unlike electricity (generation → grid → meter → billing), there is no equivalent abstraction for GPUs. Organizations buy generators (GPUs) but have no grid, no meter, and no bill.

### Four Strategic Goals of GPUaaS

| Goal | What It Means | Key Metric |
|------|---------------|------------|
| Maximize GPU Utilization | See allocated, active, and productive utilization across the fleet | Idle GPU-hours while queue has pending demand → low |
| Ensure Fair Sharing | GPU access converges to agreed policy of entitlement, priority, and borrowing | Per-team usage converges to entitlement; starvation rate → zero |
| Seamless Self-Service | Users choose intent-based compute with cost, availability, and queue visibility | Time to first GPU workload < 2 min; % launched without admin ticket |
| Support Chargeback | Map GPU consumption to accountable cost centers | Per-team GPU consumption reports available; disputed invoice rate → low |

### Customer Pain Points (UX Research)

| Job-to-be-Done | Pain Point | Real Customer Quote |
|----------------|------------|---------------------|
| **Monitor** | No unified view of capacity, utilization, or health | "18 free GPUs across 7 nodes, need 4 on same node — 78% idle but cannot satisfy request" |
| **Self-Service** | Requesting GPUs without filing a ticket | "How to get GPUs?" — Data scientists manually estimate requirements via trial-and-error |
| **Troubleshoot** | GPU errors, preemption, and fragmentation invisible | "Preemption events invisible — users complain about randomly killed jobs" |
| **FinOps** | No consumption tracking, showback, or chargeback | "Today it's a manual process. We don't have an automated way of determining this." |

### Customer Archetypes

**Direct platform users** — Internal AI/ML platform teams. Platform admins provision GPU infra for data science and ML engineering teams. Need visibility into utilization, fair scheduling, and quota controls.
- Examples: Taikang, Bank of America, Hitachi (250+ projects), CEZ

**Token providers / AI Grid operators** — Build GPU infra for others to consume as a managed service. Require per-tenant isolation, chargeback, and self-service onboarding. Hard requirement for usage export and multi-tenant quota controls.
- Examples: NeoCloud, Verizon (AI Grid), T-Mobile, FoxConn, Zero Latency

---

## Layer 2 — Physical GPU Fleet

### GPU Comparison Table (2026 Pricing)

| GPU | Memory | Bandwidth | FP8 TFLOPS | On-Demand $/hr | Best For |
|-----|--------|-----------|------------|----------------|----------|
| NVIDIA L40S | 48 GB GDDR6 | 864 GB/s | 362 | $0.50–1.50 | Small models (≤13B), dev/test |
| NVIDIA A100 SXM | 80 GB HBM2e | 2 TB/s | 624 | $1.40–2.40 | Cost-effective training, 70B inference |
| NVIDIA H100 SXM | 80 GB HBM3 | 3.35 TB/s | 1,979 | $2.50–3.50 | Production inference, large training |
| NVIDIA H200 SXM | 141 GB HBM3e | 4.8 TB/s | 1,979 | $2.60–4.39 | Memory-bound 70B+ models |
| NVIDIA B200 SXM | 192 GB HBM3e | 8 TB/s | ~4,000 | $4.50–8.00 | Frontier models (405B+), MoE |
| AMD MI300X | 192 GB HBM3 | 5.3 TB/s | ~2,600 | Varies | Multi-vendor strategy, large models |
| Intel Gaudi 3 | 128 GB HBM2e | 3.7 TB/s | ~1,800 | Varies | Cost-efficient training |

**Key insight:** Optimize for cost-per-token, not hourly rate. B200 at $5.98/hr beats multi-GPU H100 configurations for 405B+ models because it eliminates tensor parallelism overhead.

### Multi-Vendor Accelerator Support in OpenShift

| Vendor | Operator | Partitioning | Resource Name | RHOAI Status |
|--------|----------|-------------|---------------|--------------|
| NVIDIA | NVIDIA GPU Operator | MIG, Time-slicing, MPS, VFIO, DRA | `nvidia.com/gpu` | GA |
| AMD | AMD GPU Operator | DCM (CPX + NPS4) | `amd.com/gpu` | GA |
| Intel | Intel Gaudi Base Operator | N/A (full device) | `habana.ai/gaudi` | GA |

### Topology and Interconnects

| Level | Interconnect | Bandwidth | Latency |
|-------|-------------|-----------|---------|
| Same NVLink domain | NVLink | 900 GB/s (NVL72) | Nanoseconds |
| Same rack (InfiniBand) | NDR | 400 Gb/s | Microseconds |
| Same rack (Ethernet) | RoCE v2 | 100–400 Gb/s | Low milliseconds |
| Cross-rack | Leaf-spine fabric | Shared | Higher milliseconds |

**GPUDirect RDMA on OpenShift AI** — Demonstrated 3x training speedup (5 hours → 1 hour 40 minutes) for distributed fine-tuning by bypassing CPU and going GPU-to-GPU over RoCE.

### Node Feature Discovery (NFD)

NFD Operator auto-labels GPU nodes with hardware attributes. The GPU Operator then uses these labels for scheduling. Install NFD first, then the GPU operator for your vendor.

---

## Layer 3 — Device Exposure and Partitioning

### Dynamic Resource Allocation (DRA)

**Status:** GA in OpenShift 4.21 / Kubernetes 1.34 (enabled by default).

DRA replaces the device plugin's count-based model (`nvidia.com/gpu: 1`) with structured, attribute-based resource requests using CEL expressions.

**Core API objects:**

| Object | Purpose |
|--------|---------|
| `ResourceSlice` | Driver publishes available devices with attributes (memory, architecture, compute capability) |
| `DeviceClass` | Defines a category of devices (e.g., `gpu.nvidia.com`) |
| `ResourceClaim` | User's request for specific device(s) with CEL selectors |
| `ResourceClaimTemplate` | Per-pod claim template, Kubernetes creates claims automatically |

**Example — Request a GPU with >40GB memory:**

```yaml
apiVersion: resource.k8s.io/v1
kind: ResourceClaimTemplate
metadata:
  name: large-gpu
  namespace: gpu-example
spec:
  spec:
    devices:
      requests:
      - name: gpu
        exactly:
          deviceClassName: gpu.nvidia.com
          selectors:
          - cel:
              expression: |
                device.capacity['gpu.nvidia.com'].memory.isGreaterThan(quantity("40Gi"))
```

**Example — Request Hopper architecture with 80GB+:**

```yaml
selectors:
- cel:
    expression: |
      device.attributes['gpu.nvidia.com'].architecture == 'Hopper'
      &&
      device.capacity['gpu.nvidia.com'].memory.isGreaterThan(quantity("80Gi"))
```

**Key DRA capabilities in OCP 4.21:**
- **Partitionable devices** — drivers advertise overlapping logical partitions; MIG created on-demand
- **Device taints and tolerations** — mark degraded devices, workloads must explicitly tolerate
- **Shared counters** — prevent allocation of overlapping MIG slices on same physical GPU
- **Device binding conditions** — for network-attached and fabric-attached accelerators

### GPU Sharing Mechanisms

| Method | Isolation | Flexibility | Overhead | Best For |
|--------|-----------|-------------|----------|----------|
| Full GPU passthrough | Complete | None | None | Training, prod inference |
| MIG (static) | Memory + fault | Fixed profiles | Low | Stable multi-tenant prod |
| MIG (dynamic via DRA) | Memory + fault | On-demand | Low | Elastic multi-tenant |
| Time-slicing | None (shared memory) | Any GPU, any count | Context-switch | Dev/test, light inference |
| MPS | Partial (CUDA contexts) | Medium | Low | Concurrent small workloads |
| MIG + Time-slicing | MIG isolation + oversubscription | Stacked | Medium | Maximum density |

**MIG profiles on A100-40GB:**

| Profile | Compute | Memory | Max instances |
|---------|---------|--------|---------------|
| 1g.5gb | 1/7 | 5 GB | 7 |
| 2g.10gb | 2/7 | 10 GB | 3 |
| 3g.20gb | 3/7 | 20 GB | 2 |
| 7g.40gb | 7/7 | 40 GB | 1 |

### InstaSlice / Dynamic Accelerator Slicer (DAS)

Operator that dynamically partitions NVIDIA GPUs using MIG on demand:
- Pod requests a MIG resource (e.g., `nvidia.com/mig-3g.20gb`)
- DAS creates the slice just before the container starts
- DAS destroys the slice when the pod terminates
- Kubernetes-native: standard resource requests, no SSH, no manual config

**Future:** DAS is planned for deprecation in favor of native DRA partitionable devices (upstream Kubernetes).

### AMD Partitioning with Device Config Manager (DCM)

AMD Instinct MI300X supports GPU partitioning via CPX (Compute Partition X) and NPS (NUMA Per Socket):
- SPX (default): 8 GPUs, no partitioning
- CPX + NPS4: 8 physical GPUs → **64 schedulable resources** (8x density)
- Configured via `ConfigMap` with partition profiles applied by the DCM component of the AMD GPU Operator

---

## Layer 4 — Scheduling, Quotas, and Fair Sharing

### Red Hat Build of Kueue (RHBoK)

**Version:** 1.3 (April 2026), OCP 4.19+ operator. Sits alongside kube-scheduler as an admission layer.

**Core concepts:**

```
Cohort (group of ClusterQueues that can borrow from each other)
├── ClusterQueue A (team-a)
│   ├── ResourceFlavor: "gpu-h100" (label: nvidia.com/gpu.product=H100)
│   ├── ResourceFlavor: "gpu-a100" (label: nvidia.com/gpu.product=A100)
│   ├── nominal quota: 40 GPUs
│   └── LocalQueue (namespace: team-a-ns)
│       └── Jobs submitted here
└── ClusterQueue B (team-b)
    ├── ResourceFlavor: "gpu-h100"
    ├── nominal quota: 40 GPUs
    └── LocalQueue (namespace: team-b-ns)
        └── Jobs submitted here
```

**Key capabilities:**

| Feature | Description |
|---------|-------------|
| Fair sharing | Admission Fair Sharing (AFS) — orders workloads by historical usage; queues with lower usage admitted first |
| Priority & preemption | WorkloadPriorityClass — suspend and requeue lower-priority work for urgent jobs |
| Gang scheduling | All-or-nothing admission for multi-GPU training (JobSet, TrainJob) |
| Cohort borrowing | Borrow unused capacity within cohorts; prevent idle GPUs |
| Resource fungibility | If one flavor is full, admit on a different flavor automatically |
| Opt-in model | Manage only specific namespaces with labels |

**Example — ClusterQueue with borrowing:**

```yaml
apiVersion: kueue.x-k8s.io/v1beta1
kind: ClusterQueue
metadata:
  name: team-a-queue
spec:
  cohort: shared-gpu-pool
  resourceGroups:
  - coveredResources: ["nvidia.com/gpu"]
    flavors:
    - name: gpu-h100
      resources:
      - name: "nvidia.com/gpu"
        nominalQuota: 8
        borrowingLimit: 4
        lendingLimit: 8
  preemption:
    withinClusterQueue: LowerPriority
    reclaimWithinCohort: Any
```

**Example — WorkloadPriorityClass:**

```yaml
apiVersion: kueue.x-k8s.io/v1beta1
kind: WorkloadPriorityClass
metadata:
  name: production
value: 1000
description: "Production workloads — preempts dev workloads"
---
apiVersion: kueue.x-k8s.io/v1beta1
kind: WorkloadPriorityClass
metadata:
  name: development
value: 100
description: "Development workloads — preemptible by production"
```

**Supported workload integrations:**
BatchJob, JobSet, TrainJob (KFTv2), PaddleJob, PyTorchJob, TFJob, XGBoostJob, MPIJob, JAXJob, Pod, RayCluster, RayJob, AppWrapper, Deployment, StatefulSet, LeaderWorkerSet

### MultiKueue (Multi-Cluster)

Extends Kueue across clusters via Manager/Worker topology:

- **Manager cluster** — holds the MultiKueueConfig, receives all job submissions
- **Worker clusters** — execute the actual workloads

**Dispatching strategies:**
- **All-at-once** — race across all worker clusters; fastest admission wins
- **Incremental** — try clusters in a predefined order
- **External** — delegate to external controllers (e.g., OCM/RHACM)

### RHACM MultiKueue Add-on

Automates vanilla MultiKueue's manual management:

1. **Automated deployment** — RHBoK add-on deploys Kueue to managed clusters automatically
2. **Dynamic topology** — AdmissionCheckController converts Placement decisions (GPU, CPU, GoldClass) into MultiKueue topologies dynamically
3. **Self-updating configs** — MultiKueue config updates automatically as clusters join/leave; eliminates manual kubeconfig rotation
4. **RHOAI integration** — data scientists submit jobs through RHOAI to hub LocalQueues; RHACM dispatches to best available cluster

---

## Layer 5 — AI Workload Surface

### Training and Fine-tuning

**Kubeflow Trainer v2 (TrainJob API)** — GA with native Kueue integration:

```yaml
apiVersion: trainer.kubeflow.org/v1
kind: TrainJob
metadata:
  name: llama-finetune
  labels:
    kueue.x-k8s.io/queue-name: team-a-queue
    kueue.x-k8s.io/priority-class: production
spec:
  runtimeRef:
    name: torch-distributed
  trainer:
    image: quay.io/rhoai/training:latest
    numProcPerNode: "4"
    resourcesPerNode:
      requests:
        nvidia.com/gpu: "4"
        memory: "128Gi"
```

**JIT Checkpointing** — automatic state save on preemption:

1. SIGTERM handler registered by TransformersTrainer SDK
2. Training pauses safely after current optimizer step
3. Model state saved asynchronously (CUDA streams) to PVC or S3
4. Sentinel file ensures incomplete checkpoints are detected
5. On restart, training automatically resumes from latest valid checkpoint

Key SDK parameters:
- `enable_jit_checkpoint=True` — saves on SIGTERM
- `PeriodicCheckpointConfig(save_steps=500, save_total_limit=3)` — regular saves
- `S3CheckpointConfig(bucket="checkpoints", region="us-east-1")` — S3 backend

**CodeFlare SDK + KubeRay** — Python-native distributed workload submission:

```python
from codeflare_sdk import RayJob, ManagedClusterConfig

job = RayJob(
    entrypoint="python train.py",
    cluster_config=ManagedClusterConfig(
        num_workers=4,
        worker_cpu_requests=8,
        worker_gpu_requests=1,
        worker_memory_requests="32Gi",
    ),
    local_queue="team-a-queue",
    priority_class="production",
)
job.submit()
```

### Inference and Serving

**llm-d — Disaggregated Inference:**

Architecture separates compute-intensive prefill from latency-sensitive decode:

```
Request → Gateway → EPP (Endpoint Picker) → Prefill Pool → KV Cache Transfer → Decode Pool → Response
```

- **EPP scheduler** checks every model server pod for:
  - Existing prefix cache (KV-cache locality)
  - Queue depth per pod
  - Current utilization
- **Prefill pool** — compute-optimized resources for initial token generation
- **Decode pool** — latency-optimized resources for autoregressive generation
- **NIXL** — NVIDIA Inference Transfer Library for high-speed GPU-to-GPU KV cache transfer

**LLMInferenceService CR:**

```yaml
apiVersion: serving.kserve.io/v1alpha1
kind: LLMInferenceService
metadata:
  name: qwen3-8b
spec:
  replicas: 2
  model:
    uri: hf://RedHatAI/Qwen3-8B-FP8-dynamic
    name: RedHatAI/Qwen3-8B-FP8-dynamic
  router:
    route: {}
    gateway: {}
    scheduler: {}
  template:
    containers:
    - name: main
      resources:
        limits:
          nvidia.com/gpu: "1"
          memory: 32Gi
```

**WVA (Workload Variant Autoscaler):**
- SLO-driven scaling based on inference-specific metrics (ITL, KV cache saturation, queue depth)
- Computes optimal replica count via `wva_desired_replicas` metric
- Actuator (HPA or KEDA) applies the count as a direct pass-through

### Models-as-a-Service (MaaS) — GA in RHOAI 3.4

**Governance model:**

```
Request → MaaS API Gateway
            ├── MaaSAuthPolicy check (403 if group not authorized for model)
            ├── MaaSSubscription check (403 if no subscription for model)
            └── Token rate limit check (429 if quota exceeded)
         → Inference Server (vLLM / llm-d)
```

**MaaSSubscription** — defines per-group token quotas:

```yaml
apiVersion: maas.opendatahub.io/v1alpha1
kind: MaaSSubscription
metadata:
  name: team-a-premium
  namespace: models-as-a-service
spec:
  owners:
  - kind: Group
    name: team-a
  models:
  - name: llama-3-70b
    namespace: model-serving
    rateLimits:
    - window: 1h
      maxTokens: 100000
  - name: qwen3-8b
    namespace: model-serving
    rateLimits:
    - window: 24h
      maxTokens: 1000000
```

**MaaSAuthPolicy** — defines model access per group (independent from quota).

### GenAI Studio

- **AI Hub** — centralized discovery of models, tools, MCP servers
- **Playground** — interactive, stateless environment for prompt testing and parameter tuning
- **MCP Catalog** — curated catalog of MCP servers; discover, deploy, manage directly on OpenShift
- **MCP Lifecycle Operator** — Kubernetes operator for declarative MCP server deployment (`MCPServer` CR)
- **MCP Gateway** — unified runtime endpoint with identity-aware routing and per-tool metrics

---

## Layer 6 — Observability and FinOps

### Current State (RHOAI 3.5)

| Capability | Component | Status |
|-----------|-----------|--------|
| GPU utilization, memory, temperature, ECC | DCGM Exporter via Prometheus | GA |
| GPU Topology and Utilization Dashboard | RHOAI Dashboard | GA (new in 3.5) |
| Kueue scheduling info in Workbenches | RHOAI Dashboard | GA (new in 3.5) |
| MaaS observability (token usage, costs) | RHOAI Dashboard | TP (new in 3.5) |
| llm-d metrics (EPP, vLLM, prefix cache) | Prometheus + Grafana | GA |
| Distributed tracing for llm-d | OpenTelemetry + Tempo + Jaeger | DP |
| Experiment tracking and agent tracing | MLflow | GA (since 3.4) |
| Model registry | RHOAI Model Registry | GA |

### Enabling GPU Monitoring

```yaml
# In ClusterPolicy (NVIDIA GPU Operator)
dcgm:
  enabled: true
dcgmExporter:
  enabled: true
  serviceMonitor:
    enabled: true  # Exposes metrics to OpenShift Prometheus
```

```yaml
# In OdhDashboardConfig
spec:
  dashboardConfig:
    observabilityDashboard: true  # Enables Observe & Monitor menu
```

### RHOAI Roadmap for GPUaaS

| Release | Target Date | Key Deliverables |
|---------|-------------|------------------|
| **RHOAI 3.5** | Aug 2026 | GPU Topology Dashboard (Admin), Kueue info in Workbenches |
| **RHOAI 3.6** | Nov 2026 | Kueue Quota Dashboard, Workload Observability, DRA support (DP), Per-tenant GPU usage export, Compute Profiles v1 |
| **RHOAI 3.7** | ~Q1 2027 | Scheduling explainability ("why am I pending?"), Self-service GPU allocation via calendar view, GPU cost attribution per team |
| **RHOAI 3.8** | ~Q2 2027 | Self-service GPU pool wizard, GPU slice provisioning with quota enforcement, Idle GPU detection + reclamation |

### FinOps Approach

**Start with showback, then graduate to chargeback:**

1. **90-day showback program** — establish trusted data before financial consequences
2. **Label taxonomy** — enforce `app.kubernetes.io/name`, `team`, `cost-centre` via OPA Gatekeeper
3. **DCGM + K8s metadata correlation** — attribute GPU-hours to teams/projects
4. **Three cost models:**
   - Request-based: charge for what teams reserved (simple, penalizes hoarding)
   - Utilization-based: charge for actual GPU compute used (fair, harder to implement)
   - Hybrid: charge for max(reserved, utilized) — prevents hoarding AND incentivizes right-sizing

**FOCUS v1.4 specification** — FinOps Open Cost and Usage Specification. Standardized billing format for multi-cloud/K8s cost attribution. Version 1.5 will add AI token-level cost breakdown.

---

## Layer 7 — Self-Service and Product Evolution

### Hardware Profiles → Compute Profiles

| Aspect | Hardware Profile (Today) | Compute Profile (Target) |
|--------|------------------------|------------------------|
| Hardware config | GPU count, tolerations, node selectors | GPU model, memory, architecture, MIG slice |
| Software stack | None | Default runtime, compatible workbench images |
| Access policy | None | Allowed groups, team-scoped visibility |
| Cost & billing | None | Per-GPU-hour rate, chargeback code |
| Queue & quota | None | ClusterQueue assignment, availability ("2/8 used"), priority |

### Strategic Framework: See → Govern → Act

**See** — Make GPUs visible
- GPU utilization (cluster, tenant, user)
- Workload observability
- Per-tenant usage export for chargeback

**Govern** — Establish policy
- Kueue/quota scheduling policy creation and management
- Multi-tenant onboarding
- Preemption visibility and auto-resume

**Act** — Enable self-service
- Hardware Profiles → Compute Profiles
- Granular compute requests (DRA)
- Idle GPU detection + reclamation

### Deployment Scenarios

| Scenario | Complexity | Description | Example Customers |
|----------|-----------|-------------|-------------------|
| Single cluster, single tenant | Simplest | One team, one cluster | Early PoC, small deployments |
| Single cluster, multi-tenant | Core challenge | Fair sharing, quotas, isolation between teams | Hitachi (250+ projects), CEZ, Taikang |
| Multiple clusters | Hardest | Centralized visibility and cross-cluster governance | Verizon (AI Grid), JCCM, EMEA CCSP |

---

## Competitive Positioning

### vs. Run:AI / KAI Scheduler

| Dimension | Run:AI | RHOAI |
|-----------|--------|-------|
| GPU vendors | NVIDIA-only (post-acquisition) | NVIDIA + AMD + Intel |
| Scheduling | KAI Scheduler (proprietary + open-source core) | Kueue (Kubernetes-native, CNCF) |
| GPU isolation | Enforced memory isolation (proprietary, NOT open-sourced) | MIG (hardware), DRA, namespace isolation |
| Dashboard | Full GPU dashboard with allocation, utilization, idle detection | GPU Topology Dashboard (3.5), expanding in 3.6-3.7 |
| Hierarchical quotas | Departments → Projects with borrowing | Cohort-based borrowing (flat, not hierarchical yet) |
| Chargeback | Consumption reports across org units | Showback dashboard (3.5 TP), export in 3.6 |
| Pricing | $4,500/GPU/year | Included with RHOAI subscription |
| AI lifecycle | GPU scheduling only | Full lifecycle: notebooks → training → serving → monitoring |
| Lock-in | NVIDIA hardware + proprietary control plane | Open source, multi-vendor, Kubernetes-native |

**RHOAI structural advantages:**
- AI lifecycle integration (Run:AI/Rafay are GPU-only or infra-only)
- Multi-vendor accelerator support
- Kubernetes-native — no proprietary control plane
- The product gap is not primitives — it's UX

### vs. Cloud-native (EKS/AKS/GKE)

- **Portability** — same platform across on-prem, cloud, edge
- **Data sovereignty** — keep data on-premises
- **No vendor lock-in** — avoid cloud-specific GPU management tools
- **Consistent operations** — same RBAC, monitoring, CI/CD everywhere

---

## Red Hat Product Portfolio for GPUaaS

| Product | Role in GPUaaS |
|---------|----------------|
| **Red Hat OpenShift AI** | Core AI platform: workbenches, training, serving, monitoring, MaaS |
| **Red Hat AI Inference** | Standalone inference stack (vLLM + llm-d), runs on OCP or any managed K8s (AKS, CKS) |
| **Red Hat AI Factory with NVIDIA** | Co-engineered stack: RHOAI + NVIDIA AI Enterprise, optimized for NVIDIA hardware |
| **Red Hat Build of Kueue** | Batch scheduling, quotas, fair sharing, multi-tenancy |
| **Red Hat Advanced Cluster Management** | Multi-cluster GPU fleet management, MultiKueue add-on |
| **OpenShift Container Platform** | Foundation: GPU Operator, DRA, node management, Prometheus |

---

## Key References

| Topic | URL |
|-------|-----|
| RHOAI 3.5 Docs | https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.5/ |
| DRA on OCP 4.21 | https://developers.redhat.com/articles/2026/03/25/dynamic-resource-allocation-goes-ga-red-hat-openshift-421-smarter-gpu |
| llm-d + KServe | https://developers.redhat.com/articles/2026/04/21/kserve-llm-d-optimized-gen-ai-inference |
| Kueue upstream | https://kueue.sigs.k8s.io/ |
| KAI Scheduler | https://kai-scheduler.dev/ |
| GPUaaS blog (Red Hat) | https://www.redhat.com/en/blog/gpu-service-ai-scale-practical-strategies-red-hat-openshift-ai |
| GPU utilization crisis | https://venturebeat.com/infrastructure/5-gpu-utilization-the-401-billion-ai-infrastructure-problem-enterprises-cant-keep-ignoring |
| Multi-tenant DRA + MIG | https://developers.redhat.com/articles/2026/08/03/multitenant-ai-inference-dynamic-resource-allocation-openshift |
| JIT Checkpointing | https://developers.redhat.com/articles/2026/05/21/guide-jit-checkpointing-kubeflow-trainer-openshift-ai |
| MaaS Governance | https://www.redhat.com/en/blog/models-service-maas-governance-managing-ai-access-and-token-quotas |
| FOCUS Spec | https://focus.finops.org/focus-specification/ |
| Red Hat AI Factory | https://docs.nvidia.com/ai-enterprise/deployment/red-hat-ai-factory/latest/index.html |
