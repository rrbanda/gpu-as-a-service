# GPU-as-a-Service on RHOAI — Cheat Sheet

> Quick-reference for live Q&A sessions. All numbers, YAML, and commands in one place.

---

## Quick Stats

| Metric | Value | Source |
|--------|-------|--------|
| Global AI infra spending (2026) | **$401 billion** | Gartner |
| Average enterprise GPU utilization | **5%** | Cast AI 2026 Kubernetes Report |
| Enterprises at ≤50% GPU capacity | **86%** | VentureBeat (573 tech leaders) |
| Run:AI pricing | **$4,500/GPU/year** | NVIDIA AI Enterprise |
| Average overprovisioning factor | **20x** | Cast AI 2026 |
| MIG max slices (A100) | **7 slices** | NVIDIA |
| GPUDirect RDMA training speedup | **3x** (5h → 1h40m) | Red Hat demo |
| Scale-to-zero idle recovery | **85%** idle capacity recovered | Platform capability |

---

## GPU Hardware Comparison

| GPU Model | Memory | Bandwidth | FP8 TFLOPS | On-Demand $/hr | Best For |
|-----------|--------|-----------|------------|----------------|----------|
| NVIDIA L40S | 48 GB GDDR6 | 864 GB/s | 362 | $0.50–1.50 | Small models (≤13B), dev/test |
| NVIDIA A100 SXM | 80 GB HBM2e | 2 TB/s | 624 | $1.40–2.40 | Cost-effective training, 70B inference |
| NVIDIA H100 SXM | 80 GB HBM3 | 3.35 TB/s | 1,979 | $2.50–3.50 | Production inference, large training |
| NVIDIA H200 SXM | 141 GB HBM3e | 4.8 TB/s | 1,979 | $2.60–4.39 | Memory-bound 70B+ models |
| NVIDIA B200 SXM | 192 GB HBM3e | 8 TB/s | ~4,000 | $4.50–8.00 | Frontier models (405B+), MoE |
| AMD MI300X | 192 GB HBM3 | 5.3 TB/s | ~2,600 | Varies | Multi-vendor strategy, large models |
| Intel Gaudi 3 | 128 GB HBM2e | 3.7 TB/s | ~1,800 | Varies | Cost-efficient training |

---

## GPU Sharing Comparison

| Method | Isolation | Flexibility | Overhead | Best For |
|--------|-----------|-------------|----------|----------|
| Full passthrough | Complete | None | None | Training, prod inference |
| MIG (static) | Memory + fault | Fixed profiles | Low | Stable multi-tenant prod |
| MIG (dynamic/DRA) | Memory + fault | On-demand | Low | Elastic multi-tenant |
| Time-slicing | None (shared memory) | Any GPU, any count | Context-switch | Dev/test, light inference |
| MPS | Partial (CUDA contexts) | Medium | Low | Concurrent small workloads |

---

## MIG Profiles (A100 80GB)

| Profile | Compute | Memory | Max Instances |
|---------|---------|--------|---------------|
| 1g.10gb | 1/7 | 10 GB | 7 |
| 2g.20gb | 2/7 | 20 GB | 3 |
| 3g.40gb | 3/7 | 40 GB | 2 |
| 4g.40gb | 4/7 | 40 GB | 1 |
| 7g.80gb | 7/7 | 80 GB | 1 |

---

## YAML Snippets

### 1. DRA ResourceClaimTemplate — GPU with >40GB memory

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

### 2. DRA ResourceClaimTemplate — Hopper architecture

```yaml
apiVersion: resource.k8s.io/v1
kind: ResourceClaimTemplate
metadata:
  name: hopper-gpu
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
                device.attributes['gpu.nvidia.com'].architecture == 'Hopper'
                &&
                device.capacity['gpu.nvidia.com'].memory.isGreaterThan(quantity("80Gi"))
```

### 3. Kueue ResourceFlavor — H100

```yaml
apiVersion: kueue.x-k8s.io/v1beta1
kind: ResourceFlavor
metadata:
  name: gpu-h100
spec:
  nodeLabels:
    nvidia.com/gpu.product: H100
```

### 4. Kueue ClusterQueue with cohort borrowing

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

### 5. Kueue WorkloadPriorityClass (production + development)

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

### 6. TrainJob with Kueue integration

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

### 7. LLMInferenceService CR for llm-d

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

### 8. MaaSSubscription with token quotas

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

### 9. Time-slicing ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: time-slicing-config
  namespace: nvidia-gpu-operator
data:
  any: |-
    version: v1
    sharing:
      timeSlicing:
        renameByDefault: false
        resources:
        - name: nvidia.com/gpu
          replicas: 4
```

### 10. MIG Manager ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mig-parted-config
  namespace: nvidia-gpu-operator
data:
  config.yaml: |
    version: v1
    mig-configs:
      all-1g.10gb:
        - device-filter: ["0x233110DE", "0x232210DE", "0x20B210DE"]
          devices: all
          mig-enabled: true
          mig-devices:
            "1g.10gb": 7
      all-3g.40gb:
        - device-filter: ["0x233110DE", "0x232210DE", "0x20B210DE"]
          devices: all
          mig-enabled: true
          mig-devices:
            "3g.40gb": 2
```

---

## CLI Commands

```bash
# Check GPU resources on nodes
oc get nodes -o json | jq '.items[] | {name:.metadata.name, gpus:.status.allocatable["nvidia.com/gpu"]}'

# List DRA ResourceClaims
oc get resourceclaims -A

# Check Kueue queue status
oc get clusterqueues -o wide

# List pending workloads in Kueue
oc get workloads -A --field-selector=status.conditions[0].type!=Admitted

# Check GPU utilization via DCGM
oc exec -n nvidia-gpu-operator $(oc get pods -n nvidia-gpu-operator -l app=nvidia-dcgm-exporter -o name | head -1) -- dcgm-exporter -r

# Deploy llm-d InferenceService
oc apply -f llminferenceservice.yaml -n model-serving

# Check MIG status on a node
oc debug node/<node-name> -- chroot /host nvidia-smi mig -lgi

# List hardware profiles in RHOAI
oc get hardwareprofiles -A
```

---

## Competitive Comparison Tables

### vs Run:AI / KAI Scheduler

| Dimension | Run:AI | RHOAI |
|-----------|--------|-------|
| GPU vendors | NVIDIA-only | NVIDIA + AMD + Intel |
| Scheduling | KAI Scheduler (proprietary + OSS core) | Kueue (K8s-native, CNCF) |
| GPU isolation | Proprietary memory isolation (NOT open-sourced) | MIG (hardware), DRA, namespace isolation |
| Dashboard | Full GPU dashboard | GPU Topology Dashboard (3.5), expanding 3.6+ |
| Hierarchical quotas | Departments → Projects with borrowing | Cohort-based borrowing (flat) |
| Chargeback | Consumption reports across org units | Showback (3.5 TP), export in 3.6 |
| Pricing | $4,500/GPU/year | Included with RHOAI subscription |
| AI lifecycle | GPU scheduling only | Full: notebooks → training → serving → monitoring |
| Lock-in | NVIDIA HW + proprietary control plane | Open source, multi-vendor, K8s-native |

### vs Cloud-native (EKS/AKS/GKE)

| Dimension | Cloud-native | RHOAI |
|-----------|-------------|-------|
| Portability | Cloud-specific APIs | Same platform on-prem, cloud, edge |
| Data sovereignty | Data in cloud provider regions | Keep data on-premises |
| Vendor lock-in | Cloud-specific GPU mgmt tools | No proprietary lock-in |
| Consistent ops | Different RBAC/monitoring per cloud | Same RBAC, monitoring, CI/CD everywhere |

---

## RHOAI Product Portfolio

| Product | Role in GPUaaS |
|---------|----------------|
| **Red Hat OpenShift AI** | Core AI platform: workbenches, training, serving, monitoring, MaaS |
| **Red Hat AI Inference** | Standalone inference (vLLM + llm-d), runs on OCP or managed K8s |
| **Red Hat AI Factory with NVIDIA** | Co-engineered: RHOAI + NVIDIA AI Enterprise, optimized for NVIDIA HW |
| **Red Hat Build of Kueue** | Batch scheduling, quotas, fair sharing, multi-tenancy |
| **Red Hat Advanced Cluster Management** | Multi-cluster GPU fleet management, MultiKueue add-on |
| **OpenShift Container Platform** | Foundation: GPU Operator, DRA, node management, Prometheus |

---

## RHOAI Roadmap

| Release | Target Date | Key Deliverables |
|---------|-------------|------------------|
| **3.5** | Aug 2026 | GPU Topology Dashboard, Kueue info in Workbenches |
| **3.6** | Nov 2026 | Kueue Quota Dashboard, Workload Observability, DRA support (DP), Per-tenant GPU usage export, Compute Profiles v1 |
| **3.7** | ~Q1 2027 | Scheduling explainability ("why am I pending?"), Self-service GPU allocation, GPU cost attribution per team |
| **3.8** | ~Q2 2027 | Self-service GPU pool wizard, GPU slice provisioning with quota enforcement, Idle GPU detection + reclamation |

---

## Customer Archetypes

**Direct platform users** — Internal AI/ML platform teams provisioning GPUs for data science and ML engineering. Need visibility, fair scheduling, quota controls.
- Taikang, Bank of America, Hitachi (250+ projects), CEZ

**Token providers / AI Grid operators** — Build GPU infra for others as a managed service. Require per-tenant isolation, chargeback, self-service onboarding, usage export.
- NeoCloud, Verizon (AI Grid), T-Mobile, FoxConn, Zero Latency

---

## Acronym Reference

| Acronym | Meaning |
|---------|---------|
| ACM | Advanced Cluster Management |
| DAS | Dynamic Accelerator Slicer (InstaSlice) |
| DCM | Device Config Manager (AMD) |
| DCGM | Data Center GPU Manager |
| DRA | Dynamic Resource Allocation |
| EPP | Endpoint Picker Policy (llm-d) |
| FOCUS | FinOps Open Cost and Usage Specification |
| KFTv2 | Kubeflow Trainer v2 |
| KEDA | Kubernetes Event-Driven Autoscaler |
| MaaS | Models-as-a-Service |
| MIG | Multi-Instance GPU |
| MPS | Multi-Process Service |
| NFD | Node Feature Discovery |
| NIXL | NVIDIA Inference Transfer Library |
| NVLink | NVIDIA high-speed GPU interconnect |
| RDMA | Remote Direct Memory Access |
| RHBoK | Red Hat Build of Kueue |
| RHOAI | Red Hat OpenShift AI |
| RoCE | RDMA over Converged Ethernet |
| WVA | Workload Variant Autoscaler |
