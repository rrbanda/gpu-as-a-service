# GPU-as-a-Service on RHOAI — Speaker Notes

---

## Section: Hero

### Talking Points

- **Open strong with the problem:** "Every enterprise I talk to has the same story — they bought GPUs, they're spending millions, and half the time those GPUs are sitting idle."
- **Frame the narrative arc:** This talk is about turning GPUs from expensive fixed assets into a shared, elastic, governed service — the same journey we took with compute and storage a decade ago.
- **Anchor the business case immediately:** $401B in AI infrastructure spending in 2026 (Gartner), yet Cast AI reports the average GPU utilization is just 5%. That is an enormous gap between investment and value.
- **Position Red Hat's angle:** We are not building a proprietary scheduler or a closed platform. We are bringing proven open-source primitives — DRA, Kueue, llm-d — into an enterprise-supported, opinionated stack.
- **Set expectations:** By the end of this session you will have a concrete mental model of the layers, the mechanisms, and the decision framework to adopt GPU-as-a-Service in your organization.

### Audience Hooks

- **C-Suite:** Lead with the $401B spend and 5% utilization stat. Frame as capital efficiency.
- **Platform Eng:** Emphasize that this is built on upstream Kubernetes — no lock-in, no proprietary agents.
- **Data Scientists:** Promise that the goal is *faster access* to GPUs, not more YAML to write.
- **Solution Architects:** Highlight the layered architecture — each layer is independently adoptable.

### Transition Line

"So let's start at the foundation — what actually makes a GPU different from a CPU, and why does that matter for how we schedule and share them?"

---

## Section: GPU 101

### Talking Points

- **Demystify the hardware:** A modern data-center GPU (H100, MI300X) is not just a faster CPU. It is a massively parallel processor with its own memory hierarchy, its own interconnects (NVLink, NVSwitch), and its own failure modes.
- **Explain why scheduling is hard:** Unlike CPUs, GPUs have non-fungible characteristics — different memory sizes, different compute capabilities, different interconnect topologies. You cannot just say "give me 1 GPU."
- **Introduce the memory wall:** The biggest bottleneck in LLM inference is not compute — it is memory bandwidth. This single fact drives the entire architecture of modern serving systems.
- **Highlight multi-tenancy challenges:** GPUs were originally designed for exclusive access. Sharing them safely requires hardware support (MIG, SR-IOV, time-slicing) and software coordination.
- **Connect to the business:** Every idle GPU-second at current market rates costs real money. Understanding the hardware is prerequisite to understanding why utilization is so low.

### Audience Hooks

- **C-Suite:** "Think of GPUs like factory equipment — expensive, specialized, and devastating when idle."
- **Platform Eng:** Focus on NVLink topology and why pod placement matters for multi-GPU jobs.
- **Data Scientists:** Emphasize memory capacity — why your model OOMs on one card but not another.
- **Solution Architects:** Draw the analogy to storage classes — different GPUs serve different workload profiles.

### Transition Line

"Now that we have the hardware mental model, let's establish a shared vocabulary for the rest of this talk."

---

## Section: Vocab

### Talking Points

- **Define the key terms upfront** to avoid confusion: MIG (Multi-Instance GPU), DRA (Dynamic Resource Allocation), Kueue (not "queue" — it's a Kubernetes-native job queueing system), llm-d (disaggregated LLM serving daemon).
- **Distinguish scheduling from allocation:** Scheduling decides *when* a workload runs. Allocation decides *what resources* it gets. DRA handles allocation; Kueue handles scheduling.
- **Clarify "GPU sharing" vs "GPU partitioning":** Time-slicing shares a full GPU across workloads (with contention). MIG partitions a GPU into isolated instances (no contention, fixed sizes).
- **Introduce the "GPU-as-a-Service" framing:** It is not a product name — it is an operating model. GPUs are pooled, governed, and consumed as a service with quotas, fairness, and observability.
- **Set the acronym baseline:** OCP (OpenShift Container Platform), RHOAI (Red Hat OpenShift AI), NFD (Node Feature Discovery), GPU Operator.

### Audience Hooks

- **C-Suite:** Keep it high-level — "MIG means 7 workloads on 1 GPU instead of 1."
- **Platform Eng:** Precision matters here — clarify DRA vs device plugin model, ResourceClaim vs ResourceQuota.
- **Data Scientists:** Frame in terms they care about — "You request a GPU profile, not a raw device."
- **Solution Architects:** Map each term to an architecture layer they will design around.

### Transition Line

"With a shared language established, let's look at what we actually discover when we audit GPU infrastructure in the field."

---

## Section: Discovery

### Talking Points

- **Lead with the data:** 86% of enterprises report GPU utilization at or below 50% (VentureBeat 2026). The median is far worse than the mean — many clusters run at 5-15% effective utilization.
- **Explain why utilization is low:** It is not laziness. It is structural: exclusive allocation, no preemption, no borrowing, no scale-to-zero, no right-sizing. The tooling enforces waste.
- **Show the discovery process:** Walk through what a typical GPU audit reveals — stranded resources, over-provisioned notebooks, zombie jobs, no chargeback visibility.
- **Quantify the waste:** A single idle H100 at cloud rates costs ~$25K/year. A 100-GPU cluster at 5% utilization is wasting $2.3M annually.
- **Position the opportunity:** This is not a "nice to have" optimization. For most enterprises, improving GPU utilization from 5% to 40% is equivalent to buying 8x more GPUs — without spending a dollar on hardware.

### Audience Hooks

- **C-Suite:** Lead with dollars wasted. $2.3M/year per 100 GPUs at 5% utilization. That gets attention.
- **Platform Eng:** Show the ops burden — manual namespace quotas, ticket-based GPU requests, no fair-sharing.
- **Data Scientists:** "Your job is queued for 6 hours because someone else's notebook is idle but allocated."
- **Solution Architects:** Frame as a maturity model — where are they today, where could they be?

### Transition Line

"So the waste is real, it's measurable, and it's structural. Let's talk about *why* existing approaches fail to solve it."

---

## Section: Challenges

### Talking Points

- **The device plugin model is broken:** `nvidia.com/gpu: 1` is a boolean — you get a whole GPU or nothing. No partial allocation, no topology awareness, no late binding.
- **Scheduling is first-come, first-served:** Without Kueue, Kubernetes has no concept of fairness, priority preemption across namespaces, or borrowing unused quota.
- **No right-sizing feedback loop:** Data scientists request "the biggest GPU available" because there is no penalty for over-requesting and no tooling to recommend the right size.
- **Multi-cluster is an afterthought:** Most enterprises have 3-10 GPU clusters with no unified view of capacity, no cross-cluster scheduling, and no shared governance.
- **Vendor lock-in is real:** Run:AI charges $4,500/GPU/year and requires proprietary agents. That is $450K/year for a 100-GPU cluster — more than many organizations spend on the GPUs themselves over 3 years.

### Audience Hooks

- **C-Suite:** "You're paying for GPUs twice — once for the hardware, again for the software to manage them."
- **Platform Eng:** Validate their pain — "You've probably built custom scripts to work around these gaps."
- **Data Scientists:** "You've probably waited hours for a GPU that was sitting idle in another team's namespace."
- **Solution Architects:** Position as technical debt — the longer you wait, the harder it gets.

### Transition Line

"These challenges are not unique to any one organization. They are systemic. And they require a layered, systematic solution."

---

## Section: Layers

### Talking Points

- **Introduce the architecture as a layer cake:** Hardware → Discovery → Partitioning → Allocation → Scheduling → Serving → Governance → FinOps. Each layer is independently valuable but compounds with the others.
- **Explain the bottom-up adoption path:** You don't need all layers on day one. Start with discovery and partitioning (MIG), add allocation (DRA), then scheduling (Kueue), then serving (llm-d).
- **Map to Red Hat products:** GPU Operator (discovery + drivers), DRA (allocation), Kueue (scheduling), RHOAI (serving + governance), OpenShift (platform).
- **Emphasize the open-source foundation:** Every layer is upstream Kubernetes or CNCF. Red Hat adds enterprise support, lifecycle management, and opinionated integration.
- **Show the value at each layer:** MIG alone gives you 7x density on H100. DRA alone gives you topology-aware placement. Kueue alone gives you fair-sharing. Combined, they are transformational.

### Audience Hooks

- **C-Suite:** "Each layer has independent ROI. You don't need to boil the ocean."
- **Platform Eng:** This maps to their operational model — different teams own different layers.
- **Data Scientists:** "Each layer makes your experience better — faster access, right-sized resources, less waiting."
- **Solution Architects:** This is their blueprint. They will design implementations around these layers.

### Transition Line

"Let's go deeper on the three core feedback loops that make this system intelligent rather than just static."

---

## Section: Loops

### Talking Points

- **Introduce three feedback loops:** (1) Right-sizing loop — observe actual usage, recommend smaller allocations. (2) Scheduling loop — observe queue depth, adjust priorities, preempt if needed. (3) Scaling loop — observe demand patterns, scale-to-zero when idle, scale-up on arrival.
- **Explain why loops matter:** Static allocation is the root cause of waste. Dynamic, feedback-driven allocation is what turns a GPU cluster into a GPU *service*.
- **Right-sizing loop in detail:** Prometheus metrics → VPA recommendations → developer nudges → smaller requests → higher bin-packing → more jobs served.
- **Scheduling loop in detail:** Kueue observes fair-share ratios → borrows unused quota → preempts lower-priority workloads when owners return → guarantees SLOs without waste.
- **Scaling loop in detail:** llm-d observes request rates → scales replicas based on KV-cache pressure → drains gracefully → scales to zero when idle → cold-starts in seconds with disaggregated prefill.

### Audience Hooks

- **C-Suite:** "The system continuously optimizes itself — like auto-scaling for GPUs but smarter."
- **Platform Eng:** Focus on the observability stack required — what metrics, what dashboards, what alerts.
- **Data Scientists:** "Your job gets preempted gracefully with checkpointing, not killed with no warning."
- **Solution Architects:** Map loops to control theory — sensor, controller, actuator for each loop.

### Transition Line

"These loops are powered by specific Kubernetes mechanisms. Let's look at the three most important ones."

---

## Section: Mechanisms

### Talking Points

- **DRA (Dynamic Resource Allocation):** GA in Kubernetes 1.34 / OCP 4.21. Replaces the device plugin model with structured, typed resource claims. Enables topology-aware allocation, late binding, and partial GPU assignment.
- **Kueue (Kubernetes-native Job Queueing):** v1.3, supported on OCP 4.19+. Provides ClusterQueues, LocalQueues, fair-sharing with borrowing, priority-based preemption, and cohort-level resource sharing.
- **llm-d (Disaggregated LLM Serving):** Separates prefill (compute-bound) from decode (memory-bound) phases. Routes requests based on KV-cache locality. Enables independent scaling of each phase.
- **How they compose:** DRA allocates the right GPU slice → Kueue decides when to schedule → llm-d optimizes how inference workloads use the allocated resources.
- **Maturity and timeline:** DRA is GA. Kueue is stable (v1.3). llm-d is rapidly maturing as part of the RHOAI serving stack. These are not experiments — they are production-ready.

### Audience Hooks

- **C-Suite:** "These are the specific technologies that close the utilization gap."
- **Platform Eng:** Deep-dive opportunity — ResourceClaim YAML, ClusterQueue CRDs, llm-d gateway config.
- **Data Scientists:** "DRA means you describe *what* you need, not *which specific device* to use."
- **Solution Architects:** Discuss failure modes, HA, upgrade paths for each mechanism.

### Transition Line

"Mechanisms without governance become chaos. Let's talk about how we wrap these in policy."

---

## Section: Governance

### Talking Points

- **Define GPU governance:** Who can use which GPUs, how much, for how long, at what priority, with what accountability. Without governance, you just have a faster way to waste resources.
- **Quota and fair-sharing:** Kueue ClusterQueues define nominal quotas per team. Borrowing allows teams to use idle capacity. Lending limits prevent starvation. This is self-balancing.
- **Priority classes:** Map to business value — production inference > development training > exploratory notebooks. Preemption follows priority with configurable grace periods.
- **Namespace isolation:** DRA ResourceClaims are namespace-scoped. Combined with RBAC, this gives you multi-tenant isolation without separate clusters.
- **Audit and compliance:** Every allocation decision is logged. Chargeback is possible per-namespace, per-team, per-project. This feeds FinOps.

### Audience Hooks

- **C-Suite:** "Governance ensures your $10M GPU investment serves business priorities, not whoever submits first."
- **Platform Eng:** Show the CRD hierarchy — ClusterQueue → Cohort → LocalQueue → Workload. This is their domain.
- **Data Scientists:** "You always get your fair share. And when others are idle, you get more. Automatically."
- **Solution Architects:** Discuss integration with existing RBAC, OPA/Gatekeeper, and compliance frameworks.

### Transition Line

"Governance tells us who gets what. FinOps tells us what it costs and whether it's worth it."

---

## Section: FinOps

### Talking Points

- **Frame the FinOps challenge for GPUs:** Traditional cloud FinOps tools don't understand GPU utilization, MIG slices, or shared inference endpoints. You need GPU-native cost attribution.
- **Chargeback model:** Attribute costs per namespace/team based on actual GPU-seconds consumed (not requested). This changes behavior — teams that over-request see it in their bill.
- **Show-back vs charge-back:** Start with show-back (visibility) to build trust. Move to charge-back (accountability) once the data is credible. Don't skip the trust-building phase.
- **ROI calculation framework:** Compare (GPUs needed at current utilization) vs (GPUs needed at target utilization). The delta times hardware cost is your annual savings. At 5% → 40% utilization, that's an 8x capacity multiplier.
- **Tie to Run:AI displacement:** If you're paying $4,500/GPU/year for Run:AI and you have 200 GPUs, that's $900K/year. The open-source stack eliminates that line item entirely.

### Audience Hooks

- **C-Suite:** This is their language. Speak in TCO, ROI, payback period, and cost-per-inference.
- **Platform Eng:** Show the metrics pipeline — Prometheus → cost model → dashboard → alert on waste.
- **Data Scientists:** "Visibility helps you — when leadership sees utilization is high, they approve more GPUs."
- **Solution Architects:** Design the metering architecture — what to instrument, where to store, how to report.

### Transition Line

"With governance and FinOps in place, let's look at the common deployment patterns we see in the field."

---

## Section: Patterns

### Talking Points

- **Pattern 1 — Shared Training Cluster:** Multiple teams share a large GPU pool. Kueue provides fair-sharing. Jobs are queued, prioritized, and preempted. Best for organizations with bursty training workloads.
- **Pattern 2 — Inference-as-a-Service:** Centralized inference endpoints with llm-d. Teams consume via API, not by deploying their own models. Amortizes GPU cost across many consumers. Scale-to-zero for low-traffic models.
- **Pattern 3 — MIG-Partitioned Development:** Use MIG to carve H100s into 7 slices for notebooks and small experiments. Developers get instant access to a "GPU slice" without waiting. 7x developer density per GPU.
- **Pattern 4 — Tiered Priority:** Production inference at highest priority, scheduled training at medium, interactive development at lowest. Preemption flows downward. SLOs are met without over-provisioning.
- **Pattern 5 — Hybrid Burst:** On-prem GPUs for baseline demand, cloud burst for peaks. Kueue cohorts span clusters. DRA claims are portable. Cost optimization through placement policy.

### Audience Hooks

- **C-Suite:** "Which pattern matches your organization? Most start with Pattern 3 (fastest ROI) or Pattern 2 (widest impact)."
- **Platform Eng:** These are reference architectures. Each has a deployment guide and Helm chart.
- **Data Scientists:** Pattern 3 means instant GPU access for development. Pattern 2 means no MLOps burden for inference.
- **Solution Architects:** Discuss when to combine patterns — most production deployments use 2-3 simultaneously.

### Transition Line

"With these patterns in mind, how do you decide which to adopt first? Let's talk about the decision framework."

---

## Section: Decision

### Talking Points

- **Introduce the decision matrix:** Two axes — (1) Workload type (training vs inference vs development) and (2) Organizational maturity (ad-hoc → managed → optimized → autonomous).
- **Start where the pain is:** If developers are waiting hours for GPUs → start with MIG partitioning. If utilization is low → start with Kueue fair-sharing. If inference costs are exploding → start with llm-d.
- **Crawl-Walk-Run adoption:** Crawl = GPU Operator + MIG + basic monitoring. Walk = DRA + Kueue + quotas + chargeback. Run = llm-d + autoscaling + cross-cluster federation + full FinOps.
- **Prerequisites for each stage:** Crawl needs OCP 4.17+, GPU Operator. Walk needs OCP 4.19+ (Kueue), OCP 4.21+ (DRA GA). Run needs RHOAI 3.5+ and operational maturity.
- **Timeline guidance:** Crawl is achievable in 2-4 weeks. Walk takes 1-2 months. Run is a 3-6 month transformation with organizational change management.

### Audience Hooks

- **C-Suite:** "You don't need to commit to the full vision. Each stage has measurable ROI."
- **Platform Eng:** Map to their sprint capacity — "Crawl is a single sprint. Walk is a quarter. Run is two quarters."
- **Data Scientists:** "Even Crawl gives you 7x more GPU access through MIG. Walk gives you fair-sharing."
- **Solution Architects:** This is their engagement framework. Help them scope the customer's starting point.

### Transition Line

"Let's look at what organizations that have adopted this approach have actually achieved."

---

## Section: Results

### Talking Points

- **Lead with outcomes, not technology:** Organizations adopting GPU-as-a-Service patterns report 3-8x improvements in effective utilization, 60-80% reduction in GPU wait times, and elimination of six-figure vendor licensing.
- **MIG density gains:** A single H100 running 7 MIG instances serves 7 concurrent notebook users. That's 7x developer density with zero additional hardware cost.
- **Kueue fair-sharing impact:** Teams report 90%+ cluster utilization while maintaining SLOs. The key insight: borrowing unused quota is free. You only preempt when the owner returns.
- **llm-d inference efficiency:** Disaggregated prefill/decode reduces P99 latency by 30-50% compared to monolithic serving. KV-cache-aware routing eliminates redundant computation.
- **TCO comparison:** A 200-GPU deployment saving $900K/year in Run:AI licensing, achieving 5x utilization improvement (equivalent to 800 additional GPUs worth of capacity), with 6-month payback on implementation effort.

### Audience Hooks

- **C-Suite:** Frame as return on existing investment. "You don't need more GPUs. You need to use the ones you have."
- **Platform Eng:** Show the operational simplification — fewer tickets, fewer manual interventions, self-service model.
- **Data Scientists:** "Average wait time drops from hours to minutes. Notebook startup with MIG is instant."
- **Solution Architects:** Provide reference metrics for sizing engagements and setting customer expectations.

### Transition Line

"These results are built on a specific technology stack. Let me show you how the pieces fit together."

---

## Section: Stack

### Talking Points

- **Bottom-up stack overview:** OCP (platform) → GPU Operator + NFD (hardware discovery) → DRA (allocation) → Kueue (scheduling) → RHOAI (model serving, pipelines, notebooks) → llm-d (inference optimization).
- **Version alignment matters:** DRA GA requires OCP 4.21 / K8s 1.34. Kueue v1.3 requires OCP 4.19+. llm-d is integrated in RHOAI 3.5+. Planning upgrades is essential.
- **RHOAI roadmap:** 3.5 (August 2026) — llm-d GA, DRA integration. 3.6 (November 2026) — advanced FinOps, multi-cluster Kueue. 3.7 (~Q1 2027) — autonomous scaling, cross-cloud federation.
- **What Red Hat supports vs upstream:** Red Hat provides lifecycle support, CVE patching, certified operators, and integration testing across the full stack. Upstream components are usable independently but without these guarantees.
- **Integration points:** RHOAI integrates with Kueue for notebook and pipeline scheduling. DRA integrates with the GPU Operator for resource discovery. llm-d integrates with RHOAI model serving for inference routing.

### Audience Hooks

- **C-Suite:** "This is a supported, enterprise-grade platform — not a science project."
- **Platform Eng:** Show the operator dependency graph and upgrade sequencing. This is their bread and butter.
- **Data Scientists:** "RHOAI is your interface. The infrastructure complexity is hidden below."
- **Solution Architects:** Provide the BOM (bill of materials) for solution proposals.

### Transition Line

"Let's get concrete about who uses this and what it looks like for their specific workflows."

---

## Section: Use Cases

### Talking Points

- **LLM Fine-Tuning:** Teams need multi-GPU jobs with NVLink affinity. DRA ensures topology-aware placement. Kueue handles gang scheduling. Checkpointing enables graceful preemption.
- **Real-Time Inference:** Production models need guaranteed latency. Priority classes protect inference workloads. llm-d optimizes token generation. Scale-to-zero saves capacity during off-peak.
- **Notebook-Based Experimentation:** Data scientists need immediate access to small GPUs. MIG provides instant 10GB slices. No waiting, no over-provisioning, no waste.
- **Batch Processing / Data Pipelines:** ETL and feature engineering with GPU acceleration. Low priority, preemptible, but high volume. Fills cluster gaps like Tetris pieces.
- **Multi-Model Serving:** Serve 10-50 models on a shared GPU pool. llm-d routes based on KV-cache state. LoRA adapters enable model multiplexing on shared base weights.

### Audience Hooks

- **C-Suite:** Map use cases to their AI strategy — which of these are they doing today? Which are they planning?
- **Platform Eng:** Each use case has different SLO requirements — discuss the operational implications.
- **Data Scientists:** Speak to their daily workflow — notebooks, experiments, training runs, model deployment.
- **Solution Architects:** Each use case is a deployment pattern with specific resource requirements and scaling characteristics.

### Transition Line

"Different personas interact with this platform differently. Let's look at who does what."

---

## Section: Personas

### Talking Points

- **Platform Engineer:** Configures ClusterQueues, sets quotas, manages GPU Operator upgrades, defines ResourceClaimTemplates, monitors cluster-wide utilization. Their goal: self-service with guardrails.
- **Data Scientist / ML Engineer:** Submits training jobs, launches notebooks, deploys models. Interacts via RHOAI dashboard or Jupyter. Should never need to know about DRA or Kueue internals.
- **Infrastructure / FinOps Lead:** Reviews cost attribution dashboards, sets budget alerts, approves capacity expansions. Needs visibility without operational responsibility.
- **Application Developer:** Consumes inference endpoints via API. Does not deploy or manage models. Cares about latency SLOs and rate limits, not GPU topology.
- **AI/ML Leader (Director/VP):** Prioritizes workloads across teams, allocates budget, sets organizational GPU strategy. Needs executive dashboards showing utilization, cost, and business value delivered.

### Audience Hooks

- **C-Suite:** Show the organizational model — clear responsibilities, clear escalation, clear value attribution.
- **Platform Eng:** Validate their role as the enablers. Show how the tooling reduces their ticket burden.
- **Data Scientists:** "Your workflow doesn't change. You get faster access with less friction."
- **Solution Architects:** Map personas to RACI for implementation planning.

### Transition Line

"So where do we go from here? Let me leave you with concrete next steps."

---

## Section: Next Steps

### Talking Points

- **Immediate action (this week):** Audit your current GPU utilization. Deploy Prometheus GPU metrics if you haven't. Quantify the waste — this builds the business case.
- **Short-term (30 days):** Deploy MIG on your H100/A100 clusters. This is low-risk, high-reward, and requires no application changes. Immediate 7x density for notebooks.
- **Medium-term (60-90 days):** Deploy Kueue for fair-sharing. Define ClusterQueues per team. Enable borrowing. Watch utilization climb from 5% to 30-50% without additional hardware.
- **Long-term (6 months):** Full GPU-as-a-Service with DRA, llm-d, FinOps dashboards, and cross-cluster federation. This is the end state — autonomous, efficient, governed.
- **Engagement model:** Red Hat consulting can run a GPU Efficiency Assessment (2-week engagement). Solution Architects can co-design the target architecture. TAMs provide ongoing optimization guidance.

### Audience Hooks

- **C-Suite:** "The ROI is measurable at every stage. Start small, prove value, expand."
- **Platform Eng:** "We have quickstart guides, Helm charts, and reference architectures. You can start this sprint."
- **Data Scientists:** "Within 30 days you'll have instant GPU access via MIG. Within 90 days, fair-sharing eliminates wait times."
- **Solution Architects:** "Red Hat has a prescriptive engagement model. We will co-design the architecture with your team."

### Transition Line

*(Final section — close with energy)*: "The GPU utilization gap is not a technology problem — it's an operating model problem. And now you have the blueprint to solve it. Let's talk."

---

---

## Q&A Preparation

### Technical Architecture Questions

**Q: How does DRA differ from the existing device plugin model?**
A: Device plugins offer a flat counter (`nvidia.com/gpu: 1`) with no topology awareness, no partial allocation, and early binding. DRA introduces structured ResourceClaims with typed attributes (memory, compute capability, interconnect), late binding (scheduler decides placement at pod scheduling time), and support for partial GPU allocation (MIG slices, SR-IOV VFs). It is GA in Kubernetes 1.34 / OCP 4.21.

**Q: Does Kueue replace the default Kubernetes scheduler?**
A: No. Kueue sits above the scheduler. It *gates* workload admission — deciding *when* a workload is allowed to be scheduled. The default scheduler still handles pod-to-node placement. Kueue adds queuing, fair-sharing, borrowing, preemption, and quota management that the default scheduler lacks.

**Q: How does llm-d know which GPU has the KV-cache for a given request?**
A: llm-d maintains a distributed KV-cache registry. When a prefill completes, the cache location is registered. Subsequent decode requests for the same session are routed to the GPU holding the relevant cache entries. This is implemented via a custom gateway that inspects request metadata before routing.

**Q: Can MIG slices be changed dynamically without draining the node?**
A: MIG reconfiguration requires the GPU to be idle (no active workloads on that GPU). However, with DRA and proper drain policies, you can gracefully evict workloads, reconfigure MIG profiles, and reschedule — without draining the entire node. Only the specific GPU being reconfigured needs to be idle.

**Q: What happens when a preempted job loses its GPU mid-training?**
A: Kueue supports configurable preemption policies with grace periods (e.g., 5 minutes). Best practice is to configure checkpointing at intervals shorter than the grace period. The preempted job is re-queued and resumes from its last checkpoint when capacity becomes available.

**Q: How does gang scheduling work with Kueue for multi-GPU training jobs?**
A: Kueue's Workload abstraction represents the entire job (all pods). Admission is all-or-nothing — either all requested GPUs are available and the workload is admitted, or it waits. This prevents partial scheduling where some pods run and others are pending indefinitely.

### Competitive Questions

**Q: How does this compare to Run:AI?**
A: Run:AI provides a proprietary scheduler overlay with similar goals (fair-sharing, fractional GPUs, quotas). Key differences: (1) Cost — Run:AI charges $4,500/GPU/year; the open-source stack is $0 in licensing. (2) Lock-in — Run:AI requires proprietary agents; DRA/Kueue are upstream Kubernetes. (3) Ecosystem — Run:AI was acquired by NVIDIA; its future as a multi-vendor solution is uncertain. (4) Support — Red Hat provides enterprise support for the full open-source stack.

**Q: Why not just use cloud-native GPU scheduling (GKE Autopilot, EKS with Karpenter)?**
A: Cloud-native solutions are viable for cloud-only workloads. However: (1) Most enterprise GPU workloads are on-prem or hybrid for data gravity, latency, and cost reasons. (2) Cloud solutions don't federate across environments. (3) Cloud GPU costs are 3-5x owned hardware over 3 years. (4) DRA and Kueue work identically across on-prem, cloud, and hybrid.

**Q: How does this compare to KubeRay for ML workloads?**
A: KubeRay is a Ray-specific operator. It's excellent if your organization is standardized on Ray. However: (1) It only serves Ray workloads, not PyTorch, JAX, or inference. (2) It does not provide cross-framework fair-sharing. (3) Kueue integrates *with* KubeRay — you can use both. Kueue manages the queue; KubeRay manages the Ray cluster lifecycle.

**Q: What about NVIDIA DGX Cloud / Base Command?**
A: DGX Cloud is a managed service with strong hardware-software integration. Trade-offs: (1) Vendor lock-in to NVIDIA hardware and software stack. (2) No hybrid/multi-cloud portability. (3) Premium pricing. (4) Limited governance customization. For organizations wanting open standards, multi-vendor flexibility, and on-prem support, the RHOAI stack is the alternative.

### Business Questions

**Q: What's the ROI timeline?**
A: MIG partitioning delivers ROI in week 1 (7x density, no app changes). Kueue fair-sharing delivers ROI in month 1-2 (utilization jumps from 5% to 30-50%). Full stack ROI is typically realized within 6 months. Payback period for implementation effort is 2-4 months for most organizations with 50+ GPUs.

**Q: Is there additional licensing cost for these capabilities?**
A: DRA, Kueue, and llm-d are open-source with no per-GPU licensing. They are included in RHOAI subscriptions. The RHOAI subscription is per-node or per-core, not per-GPU. There is no incremental licensing cost for GPU-as-a-Service capabilities on existing RHOAI deployments.

**Q: What's the pricing model compared to Run:AI at $4,500/GPU/year?**
A: RHOAI is priced per-node (or per-core), not per-GPU. A node with 8 GPUs pays the same RHOAI subscription as a node with 1 GPU. For a 200-GPU cluster, this typically represents 80-90% savings compared to Run:AI's per-GPU pricing, depending on node density.

**Q: When will these features be GA and fully supported?**
A: Kueue: GA now, supported on OCP 4.19+. DRA: GA in OCP 4.21 (available now). llm-d: GA in RHOAI 3.5 (August 2026). Full integration with FinOps dashboards: RHOAI 3.6 (November 2026). Cross-cluster federation: RHOAI 3.7 (~Q1 2027).

### Implementation Questions

**Q: What are the prerequisites to get started?**
A: Minimum: OCP 4.19+ with GPU Operator and NFD deployed. Recommended: OCP 4.21+ for DRA GA support. GPUs: NVIDIA A100/H100 for MIG support (MIG requires Ampere or later). Monitoring: Prometheus + Grafana for utilization metrics.

**Q: How much effort is the initial deployment?**
A: Crawl stage (MIG + monitoring): 2-4 weeks, 1 platform engineer. Walk stage (Kueue + DRA + quotas): 4-8 weeks, 2 platform engineers. Run stage (full stack): 3-6 months, cross-functional team. These estimates assume existing OCP expertise.

**Q: Do we need to rewrite our ML pipelines?**
A: No. Existing workloads continue to work unchanged. DRA is backwards-compatible — old `nvidia.com/gpu: 1` requests still work. Benefits accrue incrementally: switch to ResourceClaims for topology awareness, add Kueue labels for fair-sharing, adopt llm-d for inference optimization. Each is opt-in.

**Q: What's the ordering? What do we deploy first?**
A: Recommended order: (1) GPU Operator + NFD (if not already deployed). (2) MIG configuration on H100/A100 nodes. (3) Kueue operator + ClusterQueue definitions. (4) DRA (after OCP 4.21 upgrade). (5) llm-d (with RHOAI 3.5+). Each step is independently valuable.

**Q: Can we run this in a disconnected/air-gapped environment?**
A: Yes. All components are available as OCP operators deployable via OperatorHub in disconnected mode. Container images can be mirrored to internal registries. No phone-home or external API dependencies at runtime.

---

## Objection Handling

### "We already have Run:AI"

- **Acknowledge:** "Run:AI was a reasonable choice when it was the only option for GPU scheduling and fair-sharing. It solved a real gap."
- **Reframe:** "The question is whether a proprietary, per-GPU-licensed overlay is the right long-term architecture now that these capabilities are native to Kubernetes. Run:AI was acquired by NVIDIA — its roadmap is now tied to a single hardware vendor's strategy."
- **Evidence:** At $4,500/GPU/year, a 200-GPU cluster pays $900K/year for scheduling software. DRA and Kueue deliver equivalent fair-sharing, quotas, and preemption at zero licensing cost, with upstream community momentum and Red Hat enterprise support.
- **Bridge:** "We're not asking you to rip and replace overnight. Run the open-source stack alongside Run:AI on a subset of clusters. Compare operational experience and cost. Let the data decide."

### "Kubernetes can schedule GPUs fine with device plugins"

- **Acknowledge:** "Device plugins work. They've served the community well for basic GPU allocation since Kubernetes 1.8."
- **Reframe:** "The question is not whether you *can* schedule GPUs — it's whether you're scheduling them *efficiently*. Device plugins give you a GPU counter. They don't give you topology awareness, partial allocation, late binding, or structured resource types."
- **Evidence:** Organizations using device plugins report 5-15% effective GPU utilization because the model forces whole-GPU, early-bound, topology-unaware allocation. DRA enables MIG slices, NUMA-aware placement, and right-sized allocation — the same GPU hardware serves 3-7x more workloads.
- **Bridge:** "DRA is backwards-compatible. Your existing workloads keep working. You gain new capabilities incrementally by switching to ResourceClaims."

### "Our utilization is already high"

- **Acknowledge:** "That's great — you're ahead of most organizations. Let's validate the number and see if there's still opportunity."
- **Reframe:** "High *allocation* is not the same as high *utilization*. Most organizations report 'high utilization' based on GPU allocation rate (how many GPUs are assigned) rather than SM occupancy or memory bandwidth utilization (how much compute is actually being consumed)."
- **Evidence:** Cast AI's 2026 data shows the average is 5% *compute* utilization even when *allocation* utilization is 80%+. The gap between 'allocated' and 'actually computing' is where the waste lives. MIG and right-sizing close that gap.
- **Bridge:** "Let's deploy GPU-native metrics (DCGM exporter) and measure SM activity and memory bandwidth. If your utilization is genuinely high, we'll find other optimization vectors like inference latency."

### "We're a single-vendor NVIDIA shop, why multi-vendor?"

- **Acknowledge:** "NVIDIA dominates the market for good reason — their hardware and CUDA ecosystem are unmatched. Standardizing on one vendor simplifies operations."
- **Reframe:** "The risk is not today — it's tomorrow. AMD MI300X is price-competitive. Intel Gaudi 3 serves specific workloads well. Hyperscalers are building custom silicon. An architecture that only works with NVIDIA locks you into their pricing power indefinitely."
- **Evidence:** DRA's structured resource model is vendor-agnostic by design. You describe what you *need* (memory, compute capability), not what vendor provides it. This means your workloads are portable even if your hardware isn't — yet. And when AMD or Intel GPUs make sense for specific workloads, you can mix without re-architecting.
- **Bridge:** "Today, this gives you leverage in NVIDIA negotiations. Tomorrow, it gives you hardware flexibility. The architecture should not constrain future choices."

### "Kueue is too new / not enterprise ready"

- **Acknowledge:** "Kueue is relatively new compared to tools like SLURM or PBS that have decades of history in HPC scheduling."
- **Reframe:** "Kueue v1.3 is stable, well-tested, and backed by Google and Red Hat with full enterprise support on OpenShift. It was designed from the ground up for Kubernetes-native workloads, not retrofitted from a different era."
- **Evidence:** Kueue is used in production at Google (GKE), Red Hat (RHOAI), and dozens of enterprises. It's a Kubernetes SIG-Scheduling subproject with broad community investment. On OCP 4.19+, it is a supported operator with SLA-backed support from Red Hat. v1.3 has been stable since early 2026.
- **Bridge:** "Start with a non-production cluster. Run your training workloads through Kueue for 30 days. Measure the fair-sharing behavior. The proof is in the operational data."

### "We can't afford downtime to migrate"

- **Acknowledge:** "Zero downtime is a legitimate requirement. GPU workloads — especially production inference — cannot tolerate unplanned interruption."
- **Reframe:** "This is not a forklift migration. Every component is additive and backwards-compatible. MIG can be enabled on idle GPUs without touching running workloads. Kueue gates *new* workloads without affecting existing ones. DRA coexists with device plugins."
- **Evidence:** The recommended adoption path is incremental: deploy alongside existing infrastructure, migrate workload-by-workload, validate at each step. There is no "big bang" cutover. You can run device plugins and DRA simultaneously on different node pools indefinitely.
- **Bridge:** "Let's design a migration plan with explicit rollback points. We'll start with net-new workloads and migrate existing ones only when you're confident."

### "Scale-to-zero cold-start is too slow for production"

- **Acknowledge:** "Cold-start latency is a valid concern for latency-sensitive production inference. Loading a 70B parameter model from disk takes meaningful time."
- **Reframe:** "llm-d's disaggregated architecture specifically addresses this. Prefill can begin on a shared, always-warm instance while a dedicated decode instance scales up. And with KV-cache-aware routing, frequently-accessed models maintain warm cache state across the fleet."
- **Evidence:** llm-d with pre-loaded model weights on NVMe (not network storage) achieves cold-start under 10 seconds for 7B models and under 30 seconds for 70B models. For production endpoints with SLOs, maintain a minimum replica of 1 and scale-to-zero only for development/staging models where cost savings outweigh latency.
- **Bridge:** "Scale-to-zero is not binary. You configure it per-model based on traffic patterns and SLO requirements. High-traffic production models stay warm. Long-tail models scale to zero and accept the cold-start trade-off."

### "Our data scientists don't want to change their workflow"

- **Acknowledge:** "Workflow disruption is the #1 adoption killer for platform initiatives. If data scientists have to learn new tools or write new YAML, adoption will stall."
- **Reframe:** "The explicit design goal is *zero workflow change* for data scientists. They continue using Jupyter notebooks in RHOAI, submitting training jobs via the same interfaces, and consuming inference endpoints via the same APIs. The optimization happens below their abstraction layer."
- **Evidence:** MIG is invisible to the user — they request a GPU, they get a MIG slice. Kueue is invisible — their job is queued and admitted automatically. DRA is invisible — their ResourceClaim is fulfilled without them knowing which physical GPU they received. The only visible change is *faster access and shorter wait times*.
- **Bridge:** "Run a pilot with a friendly team. Show them that their workflow is unchanged but their experience is better — faster access, less waiting, same familiar tools. Let them be your internal advocates."

---

## Demo Scripts

### Demo 1: DRA ResourceClaim Demo

**Objective:** Show the difference between legacy device plugin requests and structured DRA ResourceClaims.

**Time Estimate:** 8-10 minutes

**Setup Commands:**

```bash
# Ensure OCP 4.21+ with DRA enabled
oc get clusterversion
oc get crd resourceclaims.resource.k8s.io

# Show available GPU resources via DRA
oc get resourceslices -o wide

# Create demo namespace
oc new-project dra-demo
```

**What to Show:**

1. **Legacy approach** — Create a pod with `nvidia.com/gpu: 1`. Show that you get *any* GPU with no control over type, memory, or topology.

```yaml
# legacy-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: legacy-gpu-pod
spec:
  containers:
  - name: workload
    image: nvcr.io/nvidia/cuda:12.6-base-ubi9
    command: ["nvidia-smi"]
    resources:
      limits:
        nvidia.com/gpu: 1
```

2. **DRA approach** — Create a ResourceClaimTemplate requesting specific attributes (e.g., MIG 3g.40gb profile, minimum 40GB memory).

```yaml
# dra-claim.yaml
apiVersion: resource.k8s.io/v1
kind: ResourceClaimTemplate
metadata:
  name: gpu-claim-template
spec:
  spec:
    devices:
      requests:
      - name: gpu
        deviceClassName: gpu.nvidia.com
        selectors:
        - cel:
            expression: "device.attributes['gpu.nvidia.com'].migProfile == '3g.40gb'"
```

3. **Show the difference** — The DRA pod gets exactly a 3g.40gb MIG slice with guaranteed isolation. The legacy pod got a random full GPU.

**What to Say:**

"Notice the difference. The legacy approach is like ordering 'a car' — you might get a compact or an SUV. The DRA approach is like ordering 'a sedan with at least 300 horsepower and AWD.' You describe what you need, and the system finds the right match. This is the foundation of GPU-as-a-Service — declarative, typed, topology-aware resource allocation."

**Expected Output:**

```
# Legacy pod - gets full GPU (80GB H100)
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 560.35.03    Driver Version: 560.35.03    CUDA Version: 12.6     |
| GPU  Name       Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
|  0   H100 80GB HBM3      On  | 00000000:3B:00.0  Off |                    0 |
+-----------------------------------------------------------------------------+

# DRA pod - gets exactly a 3g.40gb MIG slice
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 560.35.03    Driver Version: 560.35.03    CUDA Version: 12.6     |
| MIG 3g.40gb     Device  0: H100 80GB HBM3 (UUID: MIG-xxxxx)                |
| 40960MiB / 40960MiB memory | 42 Multiprocessors                            |
+-----------------------------------------------------------------------------+
```

---

### Demo 2: Kueue Fair Sharing Demo

**Objective:** Show two teams with quotas, demonstrate borrowing of idle capacity and preemption when the owner returns.

**Time Estimate:** 12-15 minutes

**Setup Commands:**

```bash
# Install Kueue operator (if not already installed)
oc get csv -n openshift-operators | grep kueue

# Create namespace per team
oc new-project team-alpha
oc new-project team-beta

# Apply Kueue configuration
oc apply -f - <<EOF
apiVersion: kueue.x-k8s.io/v1beta1
kind: ResourceFlavor
metadata:
  name: h100-flavor
spec:
  nodeLabels:
    nvidia.com/gpu.product: H100-SXM5-80GB
---
apiVersion: kueue.x-k8s.io/v1beta1
kind: ClusterQueue
metadata:
  name: gpu-cluster-queue
spec:
  cohort: "gpu-pool"
  resourceGroups:
  - coveredResources: ["nvidia.com/gpu"]
    flavors:
    - name: h100-flavor
      resources:
      - name: "nvidia.com/gpu"
        nominalQuota: 8
        borrowingLimit: 4
        lendingLimit: 4
---
apiVersion: kueue.x-k8s.io/v1beta1
kind: LocalQueue
metadata:
  name: team-alpha-queue
  namespace: team-alpha
spec:
  clusterQueue: gpu-cluster-queue
---
apiVersion: kueue.x-k8s.io/v1beta1
kind: LocalQueue
metadata:
  name: team-beta-queue
  namespace: team-beta
spec:
  clusterQueue: gpu-cluster-queue
EOF
```

**What to Show:**

1. **Baseline:** Team Alpha has nominal quota of 4 GPUs, Team Beta has nominal quota of 4 GPUs. Total cluster: 8 GPUs.
2. **Borrowing:** Team Alpha submits 6 GPU jobs. They use their 4 + borrow 2 from Beta's idle quota. All 6 jobs run immediately.
3. **Preemption:** Team Beta submits 4 GPU jobs. Kueue preempts 2 of Alpha's borrowed jobs (lowest priority first) to return capacity to Beta. Beta's jobs start; Alpha's preempted jobs re-queue.

```bash
# Step 1: Team Alpha submits 6 jobs (exceeds nominal quota of 4)
for i in $(seq 1 6); do
  oc -n team-alpha create -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: alpha-training-$i
  labels:
    kueue.x-k8s.io/queue-name: team-alpha-queue
spec:
  template:
    spec:
      containers:
      - name: train
        image: nvcr.io/nvidia/cuda:12.6-base-ubi9
        command: ["sleep", "300"]
        resources:
          limits:
            nvidia.com/gpu: 1
      restartPolicy: Never
EOF
done

# Show all 6 admitted (4 nominal + 2 borrowed)
oc -n team-alpha get workloads

# Step 2: Team Beta submits 4 jobs
for i in $(seq 1 4); do
  oc -n team-beta create -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: beta-training-$i
  labels:
    kueue.x-k8s.io/queue-name: team-beta-queue
spec:
  template:
    spec:
      containers:
      - name: train
        image: nvcr.io/nvidia/cuda:12.6-base-ubi9
        command: ["sleep", "300"]
        resources:
          limits:
            nvidia.com/gpu: 1
      restartPolicy: Never
EOF
done

# Show preemption: Alpha goes from 6→4, Beta gets its 4
watch "oc get workloads -A --sort-by=.metadata.creationTimestamp"
```

**What to Say:**

"Watch what happens. Team Alpha asked for 6 GPUs but only owns 4. Because Team Beta is idle, Kueue *lends* Beta's unused capacity to Alpha. No manual intervention. No tickets. Now when Beta submits their own jobs, Kueue automatically preempts Alpha's *borrowed* capacity — not their owned capacity. Alpha keeps 4, Beta gets 4. This is fair-sharing in action. No one waits unnecessarily, but everyone gets their guaranteed share when they need it."

**Expected Output:**

```
# After Alpha submits 6 jobs:
NAMESPACE    NAME                STATUS    QUOTA USED
team-alpha   alpha-training-1    Admitted  1 GPU (nominal)
team-alpha   alpha-training-2    Admitted  1 GPU (nominal)
team-alpha   alpha-training-3    Admitted  1 GPU (nominal)
team-alpha   alpha-training-4    Admitted  1 GPU (nominal)
team-alpha   alpha-training-5    Admitted  1 GPU (borrowed)
team-alpha   alpha-training-6    Admitted  1 GPU (borrowed)

# After Beta submits 4 jobs (preemption occurs):
team-alpha   alpha-training-5    Evicted   (returned borrowed GPU)
team-alpha   alpha-training-6    Evicted   (returned borrowed GPU)
team-beta    beta-training-1     Admitted  1 GPU (nominal)
team-beta    beta-training-2     Admitted  1 GPU (nominal)
team-beta    beta-training-3     Admitted  1 GPU (nominal)
team-beta    beta-training-4     Admitted  1 GPU (nominal)
```

---

### Demo 3: llm-d Routing Demo

**Objective:** Show KV-cache-aware routing improving latency for multi-turn conversations and repeated prompts.

**Time Estimate:** 10-12 minutes

**Setup Commands:**

```bash
# Ensure RHOAI 3.5+ with llm-d enabled
oc get csv -n redhat-ods-operator | grep rhods

# Create inference namespace
oc new-project llmd-demo

# Deploy llm-d with disaggregated prefill/decode
oc apply -f - <<EOF
apiVersion: serving.kserve.io/v1alpha1
kind: ServingRuntime
metadata:
  name: llmd-runtime
  namespace: llmd-demo
spec:
  multiModel: false
  supportedModelFormats:
  - name: vllm
    version: "1"
  containers:
  - name: kserve-container
    image: registry.redhat.io/rhoai/llmd-serving:3.5
    args:
    - --disaggregated-mode=full
    - --kv-cache-routing=enabled
    - --prefill-replicas=2
    - --decode-replicas=4
    resources:
      limits:
        nvidia.com/gpu: 1
---
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: llama-3-8b
  namespace: llmd-demo
spec:
  predictor:
    model:
      modelFormat:
        name: vllm
      runtime: llmd-runtime
      storageUri: "pvc://model-store/llama-3-8b"
EOF

# Wait for deployment
oc -n llmd-demo wait --for=condition=Ready inferenceservice/llama-3-8b --timeout=300s

# Get the inference endpoint
ENDPOINT=$(oc -n llmd-demo get inferenceservice llama-3-8b -o jsonpath='{.status.url}')
```

**What to Show:**

1. **Baseline without KV-cache routing:** Send a multi-turn conversation. Each request gets routed to a random decode instance. No cache reuse. Show P99 latency.
2. **With KV-cache routing enabled:** Same conversation. Requests route to the decode instance holding the KV-cache from prior turns. Show improved P99 latency (30-50% reduction).
3. **Dashboard view:** Show the llm-d gateway metrics — cache hit rate, prefill/decode split, per-instance utilization.

```bash
# Multi-turn conversation WITHOUT cache routing (random routing)
echo "--- Without KV-cache routing (random) ---"
for turn in 1 2 3 4 5; do
  time curl -s -X POST "$ENDPOINT/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "x-llmd-routing: random" \
    -d '{
      "model": "llama-3-8b",
      "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain GPU memory hierarchy in detail."},
        {"role": "assistant", "content": "GPU memory hierarchy consists of..."},
        {"role": "user", "content": "How does this affect transformer inference specifically?"}
      ],
      "max_tokens": 200
    }' | jq '.usage.completion_tokens, .usage.total_tokens'
done

# Same conversation WITH KV-cache routing
echo "--- With KV-cache routing (session-affinity) ---"
SESSION_ID=$(uuidgen)
for turn in 1 2 3 4 5; do
  time curl -s -X POST "$ENDPOINT/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "x-llmd-session-id: $SESSION_ID" \
    -H "x-llmd-routing: kv-cache-aware" \
    -d '{
      "model": "llama-3-8b",
      "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain GPU memory hierarchy in detail."},
        {"role": "assistant", "content": "GPU memory hierarchy consists of..."},
        {"role": "user", "content": "How does this affect transformer inference specifically?"}
      ],
      "max_tokens": 200
    }' | jq '.usage.completion_tokens, .usage.total_tokens'
done

# Show routing metrics
echo "--- Gateway Metrics ---"
curl -s "$ENDPOINT/metrics" | grep -E "llmd_cache_hit_rate|llmd_routing_decisions|llmd_prefill_latency|llmd_decode_latency"
```

**What to Say:**

"Watch the latency difference. In the first run, every request recomputes the KV-cache for the entire conversation history — the prefill happens from scratch each time. In the second run, llm-d routes the request to the decode instance that already has the KV-cache from prior turns. The prefill is skipped entirely for cached tokens. For a 5-turn conversation, this saves 60-80% of the prefill compute. At scale — thousands of concurrent conversations — this is the difference between needing 10 GPUs and needing 4. That's the power of disaggregated, cache-aware inference serving."

**Expected Output:**

```
--- Without KV-cache routing (random) ---
Turn 1: real 0m1.847s  (full prefill, 2048 tokens processed)
Turn 2: real 0m1.923s  (full prefill again, no cache reuse)
Turn 3: real 0m1.891s  (full prefill again)
Turn 4: real 0m1.956s  (full prefill again)
Turn 5: real 0m1.912s  (full prefill again)

--- With KV-cache routing (session-affinity) ---
Turn 1: real 0m1.834s  (full prefill, cache stored)
Turn 2: real 0m0.743s  (cache hit, only new tokens prefilled)
Turn 3: real 0m0.698s  (cache hit, incremental prefill)
Turn 4: real 0m0.721s  (cache hit, incremental prefill)
Turn 5: real 0m0.709s  (cache hit, incremental prefill)

--- Gateway Metrics ---
llmd_cache_hit_rate{model="llama-3-8b"} 0.82
llmd_routing_decisions_total{strategy="kv-cache-aware"} 1547
llmd_prefill_latency_seconds{quantile="0.99"} 0.234
llmd_decode_latency_seconds{quantile="0.99"} 0.089
```

---

## Timing Guide

| Section | Duration | Cumulative |
|---------|----------|------------|
| Hero | 2 min | 2 min |
| GPU 101 | 4 min | 6 min |
| Vocab | 3 min | 9 min |
| Discovery | 4 min | 13 min |
| Challenges | 4 min | 17 min |
| Layers | 5 min | 22 min |
| Loops | 4 min | 26 min |
| Mechanisms | 6 min | 32 min |
| Governance | 4 min | 36 min |
| FinOps | 4 min | 40 min |
| Patterns | 5 min | 45 min |
| Decision | 4 min | 49 min |
| Results | 3 min | 52 min |
| Stack | 4 min | 56 min |
| Use Cases | 4 min | 60 min |
| Personas | 3 min | 63 min |
| Next Steps | 3 min | 66 min |
| Q&A Buffer | 14 min | 80 min |

**Total: ~80 minutes** (adjust by trimming GPU 101 or Patterns for shorter slots)
