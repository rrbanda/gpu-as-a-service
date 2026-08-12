# Speaker Notes — GPU as a Service on Red Hat OpenShift AI

## Narrative Framework: Pyramid Principle with SCQA Opening

**Framework:** Pyramid Principle (Barbara Minto / McKinsey) with SCQA opening — the industry-standard structure for enterprise architecture presentations targeting FSI audiences.

**SCQA:** Situation → Complication → Question (implicit) → Answer
**Pyramid:** Governing thought (journey map) supported by MECE pillars, each backed by evidence slides
**Assertion-Evidence:** Every slide title is a complete-sentence assertion, body is visual evidence

**Build order:**
```
SCQA Opening (slides 1-5)
  → Situation: ACME's $20M GPU fleet
  → Complication: Five hidden problems (dashboard)
  → Answer: GPUaaS journey map (conclusion first — Minto Pyramid)

Pillar 1: GPU Reality (slides 6-11)
  → Physical → fungibility → topology → packing → conflict → paradigm shift bridge

The Analogy (slides 12-13)
  → 401(k) quote + fund-by-fund table
  → Appears ONLY here until closing callback

Pillar 2: Architecture Deep Dive (slides 14-27)
  → vLLM → MIG → DRA → Kueue → LLM signals → llm-d (organic build order)
  → LLM signals placed AFTER Kueue — sets up llm-d's routing intelligence
  → Pure technical — NO analogy language

Pillar 3: Platform Architecture (slides 28-37)
  → Five-layer stack → dedicated/shared → prod/elastic → Kueue pool
  → WVA explained → control loops → WVA vs Kueue fairness
  → Request flow → component table → multi-tenant isolation

Pillar 4: FinOps and Operations (slides 38-45)
  → Metering → pricing → monthly bill → charge model
  → Showback dashboard → WVA in action → KubeRay+Kueue → multi-cluster

Reference Solution + Close (slides 46-52)
  → Team callback → before/after → implementation → roadmap → analogy callback
```

---

## Analogy Usage Rules

1. **Slides 12-13 only:** Full analogy language — 401(k), funds, fractional shares, etc.
2. **Slides 14-45:** ZERO analogy language. Pure technical.
3. **Slide 51 (closing narrative):** Analogy callbacks — "Remember the 401(k)?"
4. **During delivery:** You MAY verbally say "remember the mental model?" but slide content stays technical.

---

## Diagram Animation Notes

All 25 diagram slides use animated D3.js visualizations that render when you navigate to the slide. Nodes fade in, arrows draw, and labels appear with staggered timing. This creates a "build" effect that helps the audience follow the diagram's logic step by step.

- **First visit:** Animations play automatically when you arrive at the slide
- **Re-visiting:** Diagrams stay rendered (no repeat animation)
- **Compare slides:** Traditional vs AI-Aware and WVA vs Kueue show side-by-side panels
- **Tip:** Pause briefly on diagram slides to let the animation complete (~2 seconds)

---

## Slide-by-Slide Notes

### Slide 1: Title Slide (Title)

This is your first impression. Don't rush it. Let the room settle.

"Good morning, everyone. Thank you for being here. I know GPU time is expensive — and so is yours — so I want to make a promise upfront. By the time we're done today, you'll understand something that took me a long time to learn: managing a GPU fleet is NOTHING like managing a CPU fleet. The scheduling is different. The economics are different. The failure modes are different. And if you try to apply traditional infrastructure patterns to GPUs, you'll waste millions of dollars — quietly, invisibly, with a dashboard that tells you everything is fine."

--- pause ---

"We're going to walk through a concrete reference architecture for GPU as a Service on Red Hat OpenShift AI. Not theory — production patterns. Not a product pitch — an engineering deep dive. And I'll use a real scenario throughout: a financial services firm with 500 GPUs and a $20 million problem they don't know they have."

"Let's start with that problem."

---


### Slide 2: Agenda — What We Will Cover Today

Set the roadmap. The audience needs to see the full journey before diving in.

"Before we jump in, let me give you the map for the next hour. We're covering six sections, and each one builds on the last."

"First — The Challenge. We'll look at ACME Financial Services' $20 million GPU fleet and uncover five problems that their operations dashboard completely hides."

"Then — GPU Reality. We'll open the hood on GPU hardware and understand why GPU scheduling is fundamentally different from anything you've done with CPUs. Heterogeneity, topology, the packing problem."

"After that — Architecture Deep Dive. Five technologies, in the exact order organizations adopt them: vLLM for inference efficiency, MIG for GPU slicing, DRA for smart selection, Kueue for governance, and llm-d for intelligent routing. Each one solves a specific problem that the previous one couldn't."

"Then we'll zoom out to Platform Architecture — how these five technologies compose into one production system with control loops, deployment patterns, and a complete component map."

"FinOps and Operations — because technology without economics is just engineering for its own sake. We'll cover metering, pricing, showback dashboards, and the training lifecycle."

"And finally — Reference Solution. A concrete 12-week implementation roadmap that takes ACME from 5% utilization to 75%+. Same 500 GPUs, no new procurement."

"By the end, you'll have everything you need to evaluate, design, and start implementing GPU as a Service in your own environment."

"Let's start with the challenge."

---


### Slide 3: ACME's $20M GPU Fleet (Stats) — SITUATION

This slide sets the emotional stakes. The audience needs to feel the scale of waste before they'll care about solutions.

"So let's talk about ACME Financial Services. They've invested $20 million in GPUs. 500 of them. Mix of H100s at $30,000 a pop, A100s at $15,000. That's real capital. That's a line item the CFO is watching."

"And here's what the industry data tells us: across enterprise Kubernetes fleets — this is Cast AI's data from over 23,000 clusters — average GPU utilization is about 5%. Five percent. If ACME is anywhere near that average, they're running $19 million worth of idle silicon."

--- pause for effect ---

"Now think about what it takes to actually GET a GPU at ACME today. A data scientist needs a notebook with a GPU. She opens a ServiceNow ticket. Three to five DAYS later — if she's lucky — she gets access. In a world where her competitor is iterating on models hourly."

"And this isn't just an ACME problem. Gartner estimates $401 billion globally on AI infrastructure this year. The waste at this scale is staggering."

"So what's actually going on behind ACME's dashboard? Let me show you."

---


### Slide 4: Five Hidden Problems (Dashboard Diagram) — COMPLICATION

This is THE complication slide. The audience needs to feel the gap between what leadership sees and what's actually happening.

"Here's what ACME's operations dashboard looks like. Top row — everything's green. 95% of GPUs allocated. Check. $20 million spent, all accounted for. Check. 500 GPUs in the fleet, all online. Check. All systems normal."

--- pause ---

"Now look at the bottom row. This is what's ACTUALLY happening."

"First: 'GPU allocated' does NOT mean 'GPU computing.' ACME's actual compute utilization is 12%. Those GPUs are sitting in pods that are reserved but doing nothing. It's like paying for a hotel room 365 days a year because you visit twice."

"Second: Finance sees one line on the P&L — '$20 million on GPUs.' No per-team breakdown, no cost attribution, no idea which team is efficient and which is burning money."

"Third: 42% of GPUs are idle right now, but they can't be shared. They're allocated. Other teams that need GPUs are queuing for days while allocated GPUs sit idle."

"Fourth: there's no priority system. A three-day training run launches on Saturday and grabs everything. Monday morning, the production inference service that handles customer-facing transactions can't get a single GPU. Training starved inference."

"And fifth — and this is the one that keeps the CISO up at night — that 3-to-5-day wait for a GPU? It drives shadow IT. Data scientists spin up personal cloud GPU accounts outside the security perimeter. Models trained on uncontrolled infrastructure. Sensitive data leaving the organization."

"Add it up: ACME is bleeding roughly $8 million a year in idle capacity, with zero visibility into who's using what, and growing security exposure from shadow GPU usage."

"So the question is: how do you turn this into a governed, shared service? Here's the map."

---


### Slide 5: The Complete GPUaaS Journey (Diagram) — ANSWER

This is the governing thought — the Pyramid Principle answer. Show the full map AFTER the problem is established.

"This is the answer. And I'm showing it to you now — not at the end — because I want you to have this map in your head as we go through each piece."

"Six layers, bottom to top. Physical GPU fleet — the hardware reality we're about to explore. GPU mechanisms — MIG slicing, DRA, the primitives. Then Kubernetes plus Kueue for scheduling and governance. Above that, the GPUaaS control plane — llm-d, WVA, the AI-aware intelligence layer. Then the AI platform itself — OpenShift AI with model serving, training pipelines. And at the top: self-service. A data scientist picks from a dropdown, the platform handles everything else."

"We're going to build this from the bottom up today. Every technology, every pattern, every decision point. By the end, you'll understand every layer and — more importantly — why each layer exists and what goes wrong if you skip it."

"Keep this picture in your head. When I say 'we're at layer 3' or 'this is the governance layer,' this is what I'm referencing."

"Let's start at the bottom. What's actually inside ACME's GPU servers?"

---


### Slide 6: Data Center GPU Servers (Diagram) — GPU REALITY

**[Section transition]** "Now let's open the hood on GPU hardware and understand why this is fundamentally different from anything you've done with CPUs."

This slide grounds everything in physical reality. If the audience doesn't understand the hardware, nothing else will make sense.

"Alright, let's open the hood. This is what a GPU server actually looks like inside ACME's data center."

"Each server has 8 GPUs — typically all the same model — connected via NVLink and NVSwitch. That NVSwitch fabric is critical: it gives you 900 GB/s of bandwidth between any two GPUs in the same server. Think of it as a private highway between the GPUs. That highway is what makes multi-GPU training fast."

"Now, when someone requests '4 H100s for training,' what SHOULD happen is the platform abstracts away which rack, which server, which slots. The user shouldn't care — they should just get 4 GPUs with the right interconnect. That's what GPUaaS means."

"But today at ACME? There's no such abstraction. Teams literally know which servers they're on. They have preferences. Some teams hoard entire servers because they got burned once by a bad placement. It's the infrastructure equivalent of people keeping cash under their mattress because they don't trust the bank."

"And that's just within a single server. Let's zoom out and talk about what happens when your fleet has DIFFERENT types of GPUs."

---


### Slide 7: GPU Heterogeneity (Diagram)

This slide is the most important concept in the entire GPU Reality section. If the audience gets this, everything else clicks.

"Here's the thing nobody tells you about GPUs when you're coming from a CPU world. When someone on your team says 'I need 8 GPUs' — that's like saying 'I need 8 vehicles.' A motorcycle, a pickup truck, and a semi-trailer are all vehicles, but you would NEVER use them interchangeably."

"GPUs have at least six dimensions that matter for every request:"

"GPU model — an H100 and an A100 are not the same. H100 has 3x the FP8 throughput. Memory — 80 GB HBM3 vs 40 GB HBM2. For a 70-billion-parameter model, this is the difference between fitting in one GPU or needing two. Topology — are the GPUs on the same NVSwitch domain or across a network hop? Network — InfiniBand vs RoCE matters for distributed training. Precision — does your workload need FP16, FP8, INT8? Software — which CUDA version, which driver?"

"An H100 with NVLink on the same switch domain is a fundamentally different resource than an A100 across a network hop. But traditional IaaS? It treats all GPUs as identical. You request nvidia.com/gpu: 4, and the scheduler picks randomly. THAT is the root cause of misallocation."

"Let me make this concrete. Think about what happens when your scheduler puts a 500-megabyte sentiment model on a $30,000 H100. You've just allocated $30,000 worth of hardware to a workload that could run on a $3,000 MIG slice. Multiply that by 40 models and you see how ACME ends up at 5% utilization."

"Let me show you how topology specifically affects real performance."

**IF SOMEONE ASKS:** "Does Kubernetes support heterogeneous GPU scheduling natively?" — "Not well, until Dynamic Resource Allocation. We'll cover DRA in about 15 minutes, and it's the direct answer to this problem."

---


### Slide 8: Topology Matters (Diagram)

This slide makes topology visceral with a concrete performance comparison.

"Same request: '8 GPUs.' Two very different outcomes."

"Option A: all 8 GPUs are on the same NVSwitch domain. They talk to each other at 900 gigabytes per second. For a distributed training job doing all-reduce across 8 GPUs, this is the fast path. The GPUs spend most of their time computing, not waiting for data."

"Option B: 4 GPUs on one server, 4 on another, connected across a network hop — even a fast one like InfiniBand. Now your all-reduce has to cross that network boundary on every iteration. We're talking orders of magnitude slower for communication-heavy workloads."

"And here's the kicker — both Options look identical to the scheduler. nvidia.com/gpu: 8. Same request. Wildly different performance. Your training job might take 4 hours in Option A and 16 hours in Option B. Same cost in GPU-hours, 4x longer wall-clock time."

"For inference it matters too, just differently. Tensor parallelism across GPUs in the same domain is fine. Across a network hop, you add latency to every single token generation."

"This is why topology-aware scheduling isn't optional — it's a correctness requirement. And it's something DRA solves, as we'll see shortly."

"But topology is just one dimension of the problem. Let me show you the REAL scheduling challenge."

---


### Slide 9: The Packing Problem (Diagram)

This slide makes the scheduling complexity concrete.

"Now you understand that GPUs are heterogeneous and topology-sensitive. But here's what makes GPU scheduling truly hard: look at these four workloads."

"A Jupyter notebook — needs a quarter of a GPU for about 4 hours while a data scientist experiments. A fine-tuning job — needs 4 GPUs for 2 hours. A full training run — 64 GPUs for 72 hours, continuous. And a production LLM — 8 GPUs, always on, serving real-time traffic."

"These workloads have wildly different shapes. Different GPU counts, different durations, different priorities, different failure modes. The notebook can be interrupted — the data scientist will just restart. The training run CAN be interrupted if you have checkpointing, but you'll lose time. The production LLM? Interrupt that and customer transactions fail."

"THIS is the packing problem. You have a fixed number of GPUs, and you need to fit all these different shapes into them, while respecting priority, topology, and isolation constraints. No traditional scheduler was designed for this. Not Kubernetes' default scheduler, not YARN, not Slurm in its out-of-the-box configuration."

"Every architectural decision we make for the rest of this session is driven by this packing problem. It's the reason MIG exists, the reason Kueue exists, the reason we need DRA instead of simple integer-based GPU requests."

"And it gets worse — because these workloads don't just have different shapes. They have fundamentally different characteristics."

---


### Slide 10: Training vs Inference (Diagram)

This slide introduces the fundamental conflict that drives the entire GPU scheduling challenge.

"Let's look at what happens in a real GPU fleet over a week."

"Saturday night — someone launches a large training job. Within an hour, it's consumed 90% of the cluster's GPU capacity. Training jobs are greedy by nature — they'll take everything they can get, and they run for hours or days."

"Monday morning — the trading desk opens. Customer-facing inference services need to scale up. But there are no GPUs available. Training took everything. And here's the thing about inference: it can't wait. It has millisecond SLOs. A customer is on the other end of that API call. You can't tell them 'please hold, your fraud detection model is queued behind a training job.'"

"These two workload types are fundamentally different. Training is batch — you can queue it, you can preempt it, you care about throughput over hours. Inference is real-time — it's always on, it has strict latency requirements, and it directly affects customer experience."

"Industry-wide, Deloitte's 2026 data shows inference now accounts for 55 to 67 percent of all AI compute. And that share only grows — over a model's lifecycle, training is a one-time cost but inference runs forever. 80 to 90 percent of a model's total compute goes to inference."

"So the platform HAS to be able to handle both — and more importantly, it has to be able to dynamically rebalance between them. Training yields to inference when demand spikes. Inference releases capacity back to training when traffic drops."

"That dynamic rebalancing? It's what separates traditional GPU management from what we're building today."

---


### Slide 11: Traditional vs AI-Aware GPUaaS (Compare Diagram) — BRIDGE

This is the paradigm shift slide. It bridges from problems to solutions.

"So let me make the shift we need to make crystal clear. Look at these two sides."

"On the left — traditional GPUaaS. The user says 'give me 8 H100s.' The platform says 'here you go.' The user manages EVERYTHING — model serving, scaling, memory, routing. The platform has no idea what's running on those GPUs. It's a raw hardware allocation service. It's IaaS for GPUs."

"On the right — AI-aware GPUaaS. The user says 'deploy Llama 70B at 500 requests per second.' The platform figures out: which GPUs, how many, which topology, how to route, how to scale, when to add replicas, when to scale to zero. The user focuses on the MODEL. The platform handles the INFRASTRUCTURE intelligence."

"This is NOT a small difference. This is the difference between giving someone a raw kitchen and giving them a restaurant. Both involve food. But the level of intelligence, automation, and abstraction is completely different."

"The rest of this session shows you exactly how to build the right side. Five technologies, in the exact order you'd adopt them. Let me give you a mental model first."

---


### Slide 12: The 401(k) Analogy (Quote) — THE ANALOGY

**[Section transition]** "We've seen the GPU reality — heterogeneity, topology, the packing problem, the conflict between training and inference. Now I want to give you a mental model that ties all of this together."

Slow down here. This is the emotional reset before the deep dive. Let the analogy breathe.

"Before we dive into the technologies, I want to give you a mental model. Something to anchor everything we're about to cover."

--- pause, read the quote slowly ---

"Imagine your 401(k) — $20 million across four funds. 95% of your money is sitting in a zero-interest checking account. You can't rebalance without a 5-day paper form. And your quarterly statement doesn't even show which funds actually grew."

--- pause ---

"That's how ACME manages its GPU fleet today. The money is there — $20 million. But it's not working. It's sitting in the wrong places, it can't move, and nobody can see what's happening."

"Now, you'd never manage an actual 401(k) this way. You'd have a fund manager optimizing returns. You'd have fractional shares so you can invest $100, not $600,000. You'd have automatic rebalancing. You'd have a monthly statement."

"Every single one of those investing concepts maps to a specific GPU technology. We'll make those connections explicit later. For now, just hold this picture in your mind: a poorly managed retirement portfolio with $20 million in it."

"Let me show you the four funds."

---


### Slide 13: Fund-by-Fund Table (The Analogy)

Walk through each fund's PROBLEM only. Do NOT name the technologies. Build anticipation.

"Here are ACME's four funds — four different ways the money is stuck."

"Fund A: the Inference Endowment. 120 H100s allocated 24 hours a day, 7 days a week. But actual trading happens 6 hours a day. That's like paying for a full-time financial advisor who only works during market hours but charges you around the clock. 90 GPUs sitting idle every single night."

"Fund B: the Small Model Portfolio. 40 A100s running small compliance models — sentiment analysis, entity extraction. Each model uses 1 to 3 gigabytes on an 80 gigabyte GPU. That's like buying a $600,000 position when you need $100 of exposure. Massive over-allocation."

"Fund C: the Team Silo Allocation. Each team has its own GPU allocation. No rebalancing, no sharing. If the Gen AI team has 30 idle GPUs and the ML Engineering team is in a queue — too bad. No cross-pollination. It's like four separate brokerage accounts with no ability to transfer between them."

"Fund D: the Invisible Portfolio. No showback, no chargeback, no monthly statement. The CTO can't tell which team generated value and which burned money. You wouldn't accept that from your 401(k) provider. Why accept it from your GPU platform?"

"Each of these investing mistakes has a fix. A specific technology. Let's learn them one by one."

**CRITICAL:** Do NOT say "fund manager = vLLM" here. That mapping happens on slide 26 (Rosetta Stone) AFTER the audience has learned all five technologies.

---


### Slide 14: Architecture Deep Dive — Five Technologies Preview (Diagram)

**[Section transition]** "We've seen the GPU reality and the mental model. Now let's dive into the five technologies that transform this broken portfolio into a managed one."

Brief pause. Let the diagram animate — it shows all five technologies as cards with their key metrics.

--- pause ---

"Here's what's important: these aren't five random tools. They come in a specific order — the exact order organizations adopt them. Each one solves a problem that the previous one couldn't. vLLM makes each GPU efficient. MIG splits GPUs for small workloads. DRA lets you request the RIGHT GPU. Kueue governs who gets capacity. And llm-d routes requests intelligently across everything."

"Each builds on the last. You can't do smart GPU selection if you haven't sliced them first. You can't govern sharing if you don't know what's available. It's a stack, and we're going to build it from the bottom up."

"Let's start with vLLM."

---


### Slide 15: vLLM (Diagram)

This is where you establish deep technical credibility. Take your time with the diagram animation.

"vLLM is where every organization starts. You have a model — say Llama 70B — and you need to serve it. The question is: how do you get maximum throughput from each GPU?"

"Look at the left side of this diagram. This is traditional model serving. Fixed memory blocks, pre-allocated. You set aside memory for each request upfront. What happens? Fragmentation. 60 to 80 percent of GPU memory is wasted on gaps between allocations. It's like assigning each hotel guest an entire floor even though they only need one room."

"Now look at the center. PagedAttention — this is vLLM's breakthrough. Instead of fixed blocks, memory is allocated in pages, just like virtual memory in an operating system. Pages can be shared across requests with common prefixes — think of it like a shared system prompt. And when a request finishes, pages are released instantly. No fragmentation. This alone gives you 2 to 4x throughput improvement on the same hardware."

"The right side shows continuous batching — and this is worth spending a moment on because it's one of the most misunderstood concepts. Look at the time-step grid. At T0, requests A and B are active. At T1, request C joins the batch — it doesn't have to wait. At T2, request A finishes and its slot is immediately filled by request D. Every time step, the GPU is working on a full batch. Compare this to static batching — where the GPU processes a batch of, say, 4 requests, then WAITS until ALL four finish before starting the next batch. If one request generates 10 tokens and another generates 500, the GPU sits idle for 490 tokens on that first request's slot. Continuous batching eliminates that waste entirely. The result: the GPU never sits idle between decode steps."

"Now, notice the bottom left — prefill versus decode. These two phases of LLM inference compete on the same GPU. Prefill is compute-heavy — processing the entire prompt. Decode is memory-bandwidth-heavy — generating one token at a time. They have opposite resource profiles, and running them together creates contention. We're going to resolve this with llm-d later, but I want you to hold onto this tension."

"Bottom right — vLLM runs on NVIDIA, AMD, Intel, and Google TPUs. Same codebase, same API. No vendor lock-in at the serving layer."

"So vLLM makes each GPU dramatically more efficient. But here's the thing — if you have 40 small models, each using 1 to 3 gigabytes on an 80 GB GPU, efficiency per model isn't the problem. The problem is that you're dedicating an entire GPU to a tiny workload."

**IF SOMEONE ASKS:** "How does vLLM compare to TensorRT-LLM or Triton?" — "vLLM focuses on LLM-specific optimizations like PagedAttention and continuous batching. TensorRT-LLM is NVIDIA-specific and optimizes at the kernel level. In practice, many teams use vLLM for flexibility and multi-vendor support, and TensorRT-LLM when they need maximum performance on NVIDIA hardware. They're not mutually exclusive — you can use TensorRT as a backend within vLLM."

---


### Slide 16: MIG (Diagram)

The before/after transformation is the emotional hook here. Lead with the waste.

"So here's the compliance team's problem. 40 A100s running small models — sentiment analysis, entity extraction, fraud scoring. Each model uses about 2 gigabytes of VRAM on an 80 gigabyte GPU. That's 2.5% utilization per GPU. Look at those tiny red bars on the left — that's real money evaporating."

"MIG — Multi-Instance GPU — solves this by partitioning a single physical GPU into up to 7 isolated slices. Each slice has its own dedicated memory, dedicated compute units, and dedicated L2 cache. They're not sharing. They're not interfering. If one slice's model crashes with an out-of-memory error, the others don't even notice."

"Watch the transformation in the center. 40 GPUs → 6 GPUs with 42 MIG slices. 34 GPUs freed. At $30,000 per GPU-year, that's over a million dollars in recovered capacity. From ONE optimization. And those 34 freed GPUs? They can go to the inference team or the training team."

"Now, important distinction at the bottom. MIG gives you hardware isolation — dedicated memory, compute, L2 cache. No noisy neighbors, guaranteed performance. Time-slicing is the alternative for dev and test environments — multiple workloads share the SAME GPU resources by taking turns. It's cheaper but dangerous: an out-of-memory in one workload crashes everyone on that GPU. Use MIG for production, time-slicing for dev only."

"One challenge with MIG today: reconfiguring slices requires draining the GPU and restarting. InstaSlice — a project Red Hat contributes to — aims to make MIG profiles dynamically configurable. Not GA yet, but it's coming."

**IF SOMEONE ASKS:** "Which GPU models support MIG?" — "A100 and H100 support 7-way MIG. H200 and B200 continue to expand on it. L40S does NOT support MIG — it's designed for inference and graphics. Always check the NVIDIA MIG user guide for the latest slice profiles."

---


### Slide 17: MIG Slicing Diagram

Visual reinforcement of the MIG concept.

"Let me zoom in on what one partitioned GPU actually looks like. One physical H100 — three isolated MIG slices."

"Each slice gets its own memory partition, its own compute engines, its own L2 cache. Slice 1 might be running a 20-billion-parameter model. Slice 2 is running a 7-billion-parameter model. Slice 3 is doing sentiment classification. They're on the same chip, but they're as isolated as separate GPUs."

"This is also the billing boundary. Each MIG slice can be billed as a separate SKU. So your FinOps team can charge the compliance team for three 1g.10gb slices at $4,500 each instead of one full A100 at $15,000. The economics suddenly work."

"But here's the natural next question: if you have MIG slices of different sizes AND full GPUs of different models, how does the scheduler know which one to give to a workload? Today's answer — nvidia.com/gpu: 1 — is useless. You need something smarter."

---


**ABSORBED FROM MIG STATS SLIDE (merged):**
Quick validation with numbers. Let these land.

"Let me ground this in numbers. 7x density — that's how many workloads one GPU can serve with MIG versus dedicating one GPU per workload. 85% of overnight idle capacity is recoverable when you combine MIG with scale-to-zero. And the cold-start trade-off? 30 to 90 seconds for a 70-billion-parameter model to reload from object storage. For overnight idle recovery, that's a completely acceptable trade-off."

"These aren't theoretical numbers. They're from production deployments running RHOAI."

"MIG gives us density. But now we have a new problem: we have full GPUs, MIG slices, different memory sizes, different compute profiles — and the Kubernetes scheduler treats them all as nvidia.com/gpu: 1. We need a way to request the RIGHT GPU."

---

**Key stat talking points:** 7x density (40 GPUs collapsed to 6 for small models), 85% overnight idle capacity recoverable via scale-to-zero, SM utilization above 2.5% on right-sized MIG slices, 30-90s cold-start for 70B model.


---

### Slide 18: DRA (Diagram)

DRA is the bridge from hardware primitives to intelligent scheduling.

"This is Dynamic Resource Allocation — DRA — and it's the most important Kubernetes API for GPU workloads that most people haven't heard of."

"Look at the top row. This is how GPU scheduling works TODAY. Your pod spec says nvidia.com/gpu: 1. The scheduler picks a GPU — any GPU. A 500-megabyte compliance model might land on a $30,000 H100. You've just wasted $29,500 worth of hardware because the scheduler can't tell the difference between a MIG slice and a full GPU."

"Now look at the bottom row. With DRA, you write a ResourceClaim using CEL expressions — common expression language. 'I need a GPU with at least 10 gigabytes of VRAM, A100 or H100 family, MIG is fine.' The scheduler checks the ResourceSlice inventory — what's actually available — matches your claim to the best fit, and places your workload. That 500 MB model lands on a MIG 1g.10gb slice. The H100 stays free for workloads that actually need it."

"There are four APIs here, and they're elegantly designed. ResourceClaim — what I need. ResourceSlice — what's available. DeviceClass — categories like 'training-gpu' or 'inference-small.' ClaimTemplate — reusable patterns so your data scientists don't write CEL every time."

"GA in Kubernetes 1.34. Shipping in OpenShift 4.21. And here's a significant moment — NVIDIA donated the DRA GPU driver to the CNCF at KubeCon Europe 2026. The GPU vendor themselves is saying 'this is the right abstraction.'"

"We can now slice GPUs with MIG, and request the right slice with DRA. But who decides which team gets capacity when four teams want 154 GPUs but only 100 exist?"

**IF SOMEONE ASKS:** "What about GPU Operator vs DRA?" — "GPU Operator handles driver installation and device plugin registration. DRA handles the scheduling and matching logic. They're complementary — you need both. Think of GPU Operator as the plumbing and DRA as the water routing system."

---


### Slide 19: Kueue Governance (Diagram)

Kueue is the governance pillar. Take your time with the three panels.

"Kueue is the job queueing and resource governance system for Kubernetes. And I want to be precise about what it does, because people confuse it with the default Kubernetes scheduler. The default scheduler asks 'where does this pod fit?' Kueue asks a DIFFERENT question: 'SHOULD this workload be admitted at all?'"

"Look at the left panel. ACME has 100 GPUs and four teams wanting a total of 154. Gen AI wants 40. ML Engineering wants 30. Data Science wants 60. Applied AI wants 24. There are NOT enough GPUs for everyone."

"Kueue solves this with quotas and borrowing. Each team gets a guaranteed quota — solid bars. Gen AI gets 30 guaranteed. But if ML Engineering's 25 GPUs are idle at midnight, Gen AI can borrow up to 10 more — the transparent extensions. When ML Engineering comes back Monday morning, those borrowed GPUs are returned. No manual intervention."

"Center panel — the preemption flow. Saturday night, training consumes 80 GPUs. Monday morning, inference demand spikes 10x. Kueue preempts the training jobs — they checkpoint their state and yield. Inference gets capacity within 60 seconds. When inference demand drops Tuesday evening, training resumes from its checkpoint. Zero lost work."

"Right panel — GPU credits. Here's a subtle but important problem: how do you compare an H100 to an A100 to a MIG slice? Kueue normalizes with credits. H100 = 100 credits, A100 = 60 credits, MIG 1g.10gb = 10 credits. A team with 600 credits can spend them on 6 H100s, or 10 A100s, or 60 MIG slices. Same budget, maximum flexibility."

"And at the bottom — WorkloadPriorityClass. This is Kueue's OWN priority system, separate from Kubernetes pod priority. Why? Because the platform team needs to control BUSINESS priority without affecting pod scheduling. 'Production inference is priority 1000. Experimental training is priority 10.' The platform team sets this, not the data scientists."

"One more nuance. Default Kueue behavior when no priorities are configured is FIFO — first in, first out. But it's not STRICT FIFO. If a large job is waiting for 8 GPUs and a small job only needs 1 GPU that's available, Kueue schedules the small job. This fills resource gaps rather than leaving GPUs idle. It's more efficient than strict FIFO."

**IF SOMEONE ASKS: "How do we ensure production always wins over development?"**
"PriorityClass resources. Create a cluster-scoped PriorityClass called 'production' with value 100, and 'development' with value 10. Then configure Kueue's withinClusterQueue preemption to LowerPriority. When a production workload is pending and all GPUs are occupied by development workloads, Kueue suspends the lowest-priority development workload."

**IF SOMEONE ASKS:** "How is Kueue different from Volcano?" — "Volcano is a batch scheduling system — it focuses on gang scheduling and pod groups. Kueue is a quota and admission control system — it focuses on which workloads get to enter the cluster at all. They actually complement each other, and there's work to make them interoperate."

---


### Slide 20: Kueue's Three Decisions (Diagram)

Make the three-step decision tree concrete with examples.

"Kueue's logic boils down to three decisions, and they happen in order."

"Decision one: is the workload WITHIN the team's quota? If yes — admitted immediately. Your pod starts. No waiting."

"Decision two: the workload EXCEEDS the team's quota, BUT other teams have idle GPUs. Can we borrow? Kueue checks borrowing rules — is this team allowed to borrow? Is the lending team okay with it? If yes — admitted via borrowing. The workload runs, but with a lower priority than quota-based workloads. If the lending team needs their GPUs back, the borrowing workload is the first to be preempted."

"Decision three: the workload exceeds quota AND no peers have idle capacity. The workload is queued. It waits. And Kueue manages the queue — WorkloadPriorityClass determines which queued workloads get admitted first when capacity frees up."

"This three-tier model — quota, borrowing, queueing — is what prevents the 'land grab' problem where one team monopolizes the cluster. It's also what makes multi-tenancy actually work on shared GPU clusters."

"Now, Kueue controls WHO gets GPUs. But how does the system know WHICH vLLM instance to actually route an inference request to? That's a completely different optimization problem."

---


### Slide 21: Kueue Workload Coverage (Diagram)

This slide answers the number one misconception: "Kueue is just for training."

"I want to address something I hear in almost every conversation. People think Kueue is a training scheduler. It's not. Kueue is the admission control layer for EVERY GPU workload type in the cluster."

"Look at the left side — five workload types, each a different technology. LLM inference via KServe and vLLM. Distributed training via Kubeflow Trainer v2. Ray jobs via KubeRay. Interactive workbenches — JupyterLab, RStudio. AI pipelines via Kubeflow Pipelines 2.0."

"Every single one of these goes through the same admission gate in the center. Same Kueue policies. Same quotas. Same borrowing rules. Same priority classes. The label is the same — kueue.x-k8s.io/queue-name — regardless of workload type."

"Why does this matter? Because without this, you'd have inference consuming GPUs outside of quota. A data scientist with a Jupyter notebook holding onto a GPU for three days. A pipeline step grabbing an H100 for a 5-minute preprocessing task. No governance. Kueue closes every back door."

"On the right — the GPU resource pools. H100s, A100s, MIG slices, and the elastic burst pool. Every workload competes through the same admission gate, governed by the same policy engine."

"And notice the four policy modes: FIFO, Priority, Gang, and Fair-Share. FIFO is the default — oldest job first. Priority lets production preempt development. Gang ensures distributed training gets ALL its GPUs or none. Fair-share distributes capacity proportionally across teams."

**IF SOMEONE ASKS: "What about gang scheduling?"**
"Gang scheduling is critical for distributed training. If a TrainJob requests 4 GPUs across 4 nodes, Kueue waits until ALL 4 are available. Without this, you get partial allocation — 3 GPUs sitting idle waiting for the 4th. Kueue admits the job atomically: all or nothing."

---


### Slide 22: Fair-Share Admission (Diagram)

A concrete micro-example to make fair-sharing tangible.

"Let me make this really concrete with a simple scenario. Two GPUs just became available. Three teams are waiting."

"Team A submitted first, wants 1 GPU. Team B submitted second, wants 1 GPU. Team C submitted third, wants 1 GPU. Who gets in?"

"Kueue doesn't just do first-come-first-served — that would let aggressive teams monopolize the cluster by always submitting first. Instead, Kueue looks at fair-share: how much has each team used relative to their quota? Team A has used 60% of their quota. Team B has used 40%. Team C has used 90%."

"Result: A gets one GPU — admitted. B gets the other — admitted. C? Queued. Not because they submitted last, but because they've already used the most. Fair-share means the team that's consumed the least, relative to their quota, gets priority."

"This is how you prevent the 'squeaky wheel gets the GPU' problem. Governance by policy, not by politics."

"Alright — we can now slice GPUs, request the right one, and govern who gets them. But we still haven't addressed HOW the system knows which vLLM instance to route to. That's where we need to understand what signals an AI-aware platform even has to work with."

---


### Slide 23: 9 LLM Inference Signals (Diagram)

This slide sets up llm-d by showing what intelligence is available.

"Here's something that blew my mind when I first learned it. Traditional infrastructure monitoring gives you CPU utilization, memory usage, network I/O. That's it. And it's COMPLETELY inadequate for LLM inference."

"LLM inference has NINE optimization signals that traditional IaaS never sees. Model replicas — how many instances of each model are running. KV cache pressure — how full is each instance's key-value cache? Prefill vs decode — is the GPU doing the compute-heavy prompt processing or the memory-bound token generation? Batch saturation — how many requests are being processed simultaneously? Token throughput — tokens per second per instance. TTFT — time to first token, the latency your user feels. GPU memory — how much VRAM is actually being used. Model weights — where are they loaded? And LoRA adapters — which fine-tuned variants are hot on each instance?"

"Traditional IaaS sees exactly ONE of these: GPU utilization percentage. And even that's misleading — a GPU at 80% utilization doing nothing useful because of memory fragmentation looks the same as a GPU at 80% utilization cranking through tokens."

"These nine signals are the levers that the NEXT technology — llm-d — uses to make intelligent routing decisions. Without these signals, you're flying blind. With them, you can do things like route a request to the instance that already has its system prompt cached. Which is exactly what llm-d does."

---


### Slide 24: llm-d KV-Cache Routing (Diagram)

This is the most technically impressive slide. Let the animation tell the story.

"llm-d is where everything comes together. This is the technology that makes your inference fleet intelligent — routing each request to the RIGHT vLLM instance based on those nine signals we just discussed."

"Watch the flow at the top. A request arrives — 'Analyze this transaction for compliance violations.' It hits the Gateway, then the Endpoint Picker — EPP. The EPP doesn't round-robin. It checks: which vLLM instance has the relevant system prompt prefix already in its KV cache? Replica 1 has prompt-A cached. Replica 2 has prompt-B. Replica 3 has our compliance prompt cached. Route to Replica 3. The prefill step — which normally takes 200 milliseconds — is SKIPPED entirely because the KV cache already has it."

"Look at the middle left. This is the KV-cache economics that most people miss. Call 1 to your compliance endpoint pays full prefill — 200 milliseconds. But Call 2 through Call 10 — same system prompt prefix — they're all cache hits. 18 milliseconds each. For an agentic compliance chain — 10 calls with the same context — you pay full cost ONCE. The other 9 calls are essentially free in terms of prefill compute."

"Middle right — disaggregated prefill and decode. Remember that tension between prefill and decode I mentioned in the vLLM slide? Here's the resolution. Run prefill on H100s — they have the compute power for the heavy prompt processing. Run decode on A100s — they have the memory bandwidth for token generation. NIXL — that's the zero-copy GPU-to-GPU KV transfer protocol — moves the KV cache between the pools without touching the CPU."

"And at the bottom — this isn't a Red Hat science project. llm-d is co-created by Red Hat, Google Cloud, IBM Research, CoreWeave, and NVIDIA. It's in the CNCF Sandbox. GA in Red Hat OpenShift AI 3.3. This is production software."

**IF SOMEONE ASKS:** "How does llm-d compare to SGLang's router?" — "SGLang optimizes at the engine level — it's excellent at intra-engine scheduling. llm-d operates at the fleet level — routing ACROSS multiple vLLM instances with KV-cache awareness. They're different layers. You could theoretically run SGLang as the engine and llm-d as the fleet router."

---


### Slide 25: llm-d Routing Diagram

This is the "aha" diagram. Walk through it slowly.

"I want to make sure this really lands because this is the single most impactful optimization in the entire architecture."

"Call 1: a user submits 'Analyze this transaction for compliance...' The system prompt is 2,000 tokens. The query is 500 tokens. Full prefill: 2,500 tokens processed, 200 milliseconds. The KV cache for those 2,000 system prompt tokens is now stored on Replica 3."

"Call 2: different user, same endpoint. Same 2,000-token system prompt, different 500-token query. EPP routes to Replica 3. Cache hit. Only the 500 new query tokens need prefill. Time: 20 milliseconds instead of 200."

"Calls 3 through 10: same pattern. Each one pays only for its unique query tokens. The shared prefix is free."

"Now imagine an agentic workflow. A compliance pipeline that runs 10 sequential calls — each building on the last, each sharing the same system context. Without llm-d, that's 10 times 200 milliseconds of prefill — 2 seconds of compute. With llm-d, it's 200 milliseconds plus 9 times 20 milliseconds — 380 milliseconds total. 5x faster, using dramatically fewer GPU cycles."

"For ACME's compliance team running thousands of these chains per hour, the GPU savings are enormous. This is how you get 61% fewer GPUs needed to serve the same traffic."

---


### Slide 26: llm-d Stats (Stats)

Let the numbers speak. Pause between each one. Be ready for the scale question.

"Four numbers. Let me give you a moment with each."

"61% fewer GPUs needed to serve the same inference traffic. Same throughput, same latency SLOs, 61% less hardware. In the benchmark, 10 GPUs with round-robin routing went down to 3.9 GPUs with llm-d's prefix-aware routing and P/D disaggregation. At ACME's scale, that's potentially hundreds of GPUs freed up for other workloads."

--- pause ---

"87%+ KV cache hit rate. That means 87% of requests skip prefill entirely. They go straight to decode. Your users feel this as dramatically lower time-to-first-token."

--- pause ---

"10 to 30x improvement in TTFT — time to first token. From 200 milliseconds to under 20 milliseconds for cached requests. For real-time applications like chatbots and compliance checks, this is the difference between 'snappy' and 'sluggish.'"

--- pause ---

"+40% token throughput increase with disaggregated prefill/decode — and notice the fine print: 16+ GPUs. That's the scale threshold. Below 8 GPUs, co-located serving with chunked prefill wins — the overhead of KV cache transfer between nodes isn't worth it. At 16 to 32 GPUs, disaggregation breaks even and becomes net-positive for typical chat workloads. At 50+ GPUs, you unlock full phase-specific parallelism. For ACME with 500 GPUs, they're well above that threshold. But if someone is running a small deployment, I'd tell them: start with colocated vLLM, and disaggregate when you scale."

"These numbers are from published benchmarks — AWS validated 1P:1D on 16 H100s running Llama-3.3-70B with flat decode latency under load. The llm-d project validated 3,100 tokens/second per B200 decode GPU on a 16x16 topology."

"Now — you've learned all five technologies. Let me connect them back to that 401(k) we talked about earlier."

**IF SOMEONE ASKS: "Does this mean I need 16 GPUs minimum?"**
"Not for llm-d itself — you can run llm-d with prefix-aware routing at any scale and get the KV-cache hit benefits (that's where the 87% hit rate and 10-30x TTFT comes from). It's specifically the disaggregated prefill/decode split that needs 16+ GPUs to be worth the network overhead. Most enterprises running production LLM serving are already at that scale."

**IF SOMEONE ASKS: "What about the per-token cost reduction?"**
"Think about it this way: if you serve the same traffic with 61% fewer GPUs, your per-token cost drops by more than half. At $2/GPU-hour for H100s, that's real money — potentially millions annually at scale. The +40% throughput increase from disaggregation stacks on top of the routing savings."

---


### Slide 27: 401(k) Rosetta Stone (Table)

The audience finally gets the payoff for the analogy. Make this a satisfying "aha."

"Remember the 401(k) with the four broken funds? Now that you know all five technologies, let's connect the dots."

"Fund manager — the expert who maximizes returns from each investment. That's vLLM. It squeezes maximum throughput from each GPU."

"Fractional shares — the ability to invest $100 instead of buying a $600,000 position. That's MIG. You get a slice of a GPU instead of dedicating the whole thing."

"Smart order book — the system that matches buy orders to the right exchange at the right price. That's DRA. It matches your workload to the right GPU based on actual attributes, not just 'give me one.'"

"Allocation limits — the rules that prevent any single fund from taking over your entire portfolio. That's Kueue. Quotas, fair-sharing, borrowing limits."

"Smart order routing — the algorithm that routes each trade to the exchange with the best liquidity. That's llm-d. It routes each request to the vLLM instance with the best KV cache."

"Every investing mistake had a technology fix. And just like a well-managed portfolio, these technologies work TOGETHER — they're not independent tools."

"The analogy ends here. From now on, it's pure architecture. Let's see how these five technologies compose into one production system."

---


### Slide 28: Five-Layer Stack (Diagram) — PLATFORM ARCHITECTURE

**[Section transition]** "We've covered the five individual technologies. Now let's see how they compose into one production architecture."

Fulfill the promise from slide 5.

"Remember the journey map from the opening? Here's the five-layer architecture in detail."

"Layer 1 — physical GPUs. The hardware reality. NVLink, NVSwitch, heterogeneous models, topology. Everything we covered in GPU Reality."

"Layer 2 — mechanisms. MIG slicing, DRA for smart selection. These are the primitives that make GPUs manageable."

"Layer 3 — governance. Kueue for quotas, fair-sharing, borrowing, preemption. This is the policy layer."

"Layer 4 — AI-aware intelligence. llm-d for routing, WVA for autoscaling. This is the layer that understands WHAT'S running on the GPUs, not just that they're allocated."

"Layer 5 — self-service. Compute Profiles, model catalogs, one-click deployment. This is what the data scientist actually sees."

"Each layer adds intelligence. Skip a layer and you create gaps. Try to go straight from physical GPUs to self-service and you get ACME's current state — shadow IT and ServiceNow tickets."

"Let's start at the top: what's the simplest deployment pattern?"

---


### Slide 29: Dedicated vs Shared Clusters (Diagram)

Start with the simplest pattern to ground the audience.

"The first architectural decision every organization faces: dedicated clusters or shared clusters?"

"On the left — Pattern A: dedicated inference. One team, one model family, one cluster. You run vLLM and llm-d. You DON'T need Kueue because there's nobody to share with. This is the simplest pattern. If you're just starting your GPUaaS journey and you have one team running inference, start here. Get the serving layer right before you add multi-tenancy."

"On the right — Pattern B: shared cluster. Multiple teams, mixed workloads — inference AND training on the same hardware. NOW you need Kueue. Inference gets 60% quota, training gets 40%. But training can borrow inference's idle GPUs overnight. Inference reclaims them Monday morning. This is where the real savings happen — 40% or more compared to dedicated clusters — because idle capacity doesn't go to waste."

"Here's the practical guidance: most organizations start with dedicated clusters per team. They consolidate to shared clusters as their platform maturity grows and they build trust in the governance layer. Don't try to go straight to shared multi-tenant — you'll fight political battles before you've proven the technology works."

"In both patterns, though, you face the same question: which GPUs are guaranteed for production, and which are available for everyone to share?"

**IF SOMEONE ASKS:** "What about having separate clusters for training vs inference?" — "That's a valid intermediate pattern. Training clusters run Kueue but not llm-d. Inference clusters run llm-d but may not need Kueue if they're single-tenant. The risk is fragmented utilization — you can't share capacity across the boundary. MultiKueue addresses this, which we'll cover later."

---


### Slide 30: Guaranteed + Elastic Capacity (Diagram)

Make the fleet splitting concrete.

"Regardless of whether you choose dedicated or shared clusters, every organization needs to answer this question: what's guaranteed, and what's elastic?"

"Think of it like a budget. Your GPU fleet splits into two pools. The prod reservation — this is inference capacity managed by llm-d and WVA. These GPUs are GUARANTEED to be available for production workloads. Your customer-facing fraud detection model gets these GPUs no matter what. They don't get preempted, they don't get borrowed."

"Then there's the elastic pool — everything else. Training, fine-tuning, notebooks, batch jobs. Kueue governs this pool. Teams get quotas, they borrow from each other, workloads queue when capacity is full."

"The beauty of this split is that the elastic pool can EXPAND into the prod reservation's idle capacity — and shrink back when production demand returns. The prod pool always has priority. But when inference traffic drops at night, those reserved GPUs don't sit idle — they flow into the elastic pool for training."

"The elastic pool needs a gatekeeper — someone who decides 'you may or may not have those GPUs.' That's Kueue's role at the pool level, and it's subtly different from what we saw earlier."

---


### Slide 31: Kueue Pool (Diagram)

Show Kueue in its pool governance role — distinct from the earlier quota explanation.

"Here's Kueue at the pool level. 32 H100s in this example. Three teams: Team A running Llama inference, Team B running Mistral inference, Team C running a training job."

"The autoscaler — whether that's WVA for inference or KEDA for training — says 'I WANT 2 more GPUs.' The autoscaler's job is to detect demand. But WANTING GPUs and GETTING GPUs are two very different things."

"Kueue's job is to decide: does this team's quota allow it? Is there capacity available? If another team's GPUs are idle, can we borrow? If not, does this workload wait, or does it preempt something lower-priority?"

"Demand does NOT equal entitlement. This is the single most important principle in shared GPU management. Just because your model is popular doesn't mean your team gets unlimited GPUs. The platform enforces policy — not popularity."

"Now, Kueue controls WHO gets GPUs. But who decides HOW MANY replicas each model actually needs? That's a different question entirely — and it requires an autoscaler that understands AI workloads, not just CPU metrics."

---


### Slide 32: WVA Explained (Diagram)

This is the WVA introduction. The audience is meeting a new component — be thorough.

"So we have a gap. Kueue governs WHO gets GPUs — it's the policy layer. But somebody needs to decide HOW MANY replicas each model needs at any given moment. That's WVA — the Workload Variance Autoscaler."

"Look at the left panel. WVA sits right between llm-d and Kueue in the architecture. llm-d routes individual requests. WVA decides how many vLLM instances to run. Kueue decides whether WVA is allowed to have the GPUs it's requesting."

"Now here's why WVA exists instead of just using HPA or KEDA. Look at the right panel. HPA and KEDA see CPU utilization and memory usage. That's it. But for LLM inference, CPU and memory are the WRONG signals. A GPU might be at 30% compute utilization but have a saturated KV cache — it's full and can't accept new requests. HPA would say 'everything's fine.' WVA would say 'we need more replicas.'"

"WVA uses LLM-specific signals: queue depth — how many requests are waiting? KV-cache pressure — how full are the caches? TTFT — is time-to-first-token degrading? Token throughput — are tokens per second dropping? These signals tell you what's ACTUALLY happening with your inference workload, not just what the hardware meters say."

"At the bottom — four behaviors. Scale UP when demand signals spike — meet your SLOs. Scale DOWN when demand drops — consolidate to fewer GPUs, save money. Scale to ZERO when there's no traffic for N minutes — release the GPUs entirely for other teams. And right-SIZE — match the GPU type to the model. A 7B model doesn't need an H100; a MIG slice will do."

"Now you know all the actors. llm-d routes each request. WVA decides how many replicas. Kueue decides whether WVA gets the GPUs. Let me show you how they compose into three nested control loops."

**IF SOMEONE ASKS:** "Is WVA the same as KEDA with custom metrics?" — "Conceptually similar, but WVA is purpose-built for LLM inference. KEDA requires you to write custom scalers and metric adapters. WVA natively understands vLLM's metrics endpoint and makes scaling decisions based on LLM-specific signals like KV-cache pressure and TTFT. It's the difference between building a custom car from parts versus buying one designed for the track."

---


### Slide 33: Three Control Loops (Diagram)

Systems thinking. Show how the pieces compose without fighting each other.

"This is the slide that separates people who've deployed this in production from people who've only read about it. Three control loops, three different timescales, and the CRITICAL thing is that each one trusts the one above it."

"Innermost loop — llm-d's EPP, the Endpoint Picker. Timescale: milliseconds. Every single request gets routed to the optimal vLLM instance. This is the fastest loop — it reacts in real time to cache state, queue depth, and load."

"Middle loop — WVA and KEDA. Timescale: seconds to minutes. How many replicas should each model have? WVA watches the aggregate signals — if queue depth is rising across all instances, add a replica. If most instances are idle, consolidate. This loop doesn't route requests — it adjusts the FLEET size."

"Outer loop — Kueue. Timescale: minutes to hours for quota enforcement. In a shared cluster, Kueue is the ceiling. WVA says 'I want 2 more replicas.' Kueue says 'your team's quota allows 1 more.' WVA gets 1. Not 2."

"And underneath all of this — kube-scheduler handles GPU placement on nodes. It's the slowest loop, dealing with physical topology and node selection."

"The reason this works is that each loop TRUSTS the one above it. llm-d doesn't try to add replicas — that's WVA's job. WVA doesn't try to override quotas — that's Kueue's job. If you collapse these loops into one system, you get oscillation — the system fights itself. Separation of concerns isn't just good engineering here — it's a correctness requirement."

"Now, WVA and Kueue both use the word 'fairness.' But they mean very different things."

---


### Slide 34: WVA vs Kueue Fairness (Compare Diagram)

Disambiguate the most common source of confusion.

"This is the slide I wish I'd had six months ago, because this confusion cost us a LOT of debugging time."

"WVA Fairness asks: 'Which model replicas best use available accelerators?' It looks at model demand, KV cache pressure, queue depth, hardware variants, inference SLOs. It's optimizing for PERFORMANCE. 'Given these GPUs, how do I get the best inference throughput?'"

"Kueue Fairness asks: 'Which tenants are ENTITLED to GPUs?' It looks at tenants, quotas, resource flavors, borrowing rules, priority levels. It's enforcing POLICY. 'Team A is at 90% of their quota, Team B is at 40% — the next GPU goes to Team B.'"

"These are two completely different questions. WVA is inference-aware optimization — it doesn't know or care about team quotas. Kueue is platform-level governance — it doesn't know or care about KV cache hit rates. They operate at different levels, on different signals, with different goals."

"Never conflate the two. If someone on your team says 'we need fairness,' the first question is: 'Fairness of WHAT? Model placement or team allocation?' The answer determines which system handles it."

---


**IF SOMEONE ASKS about demand vs entitlement (absorbed from fighting slide):**
A concrete scenario that shows WVA and Kueue interacting.

"Let me make this real. Two inference services, one shared cluster."

"Llama wants 6 more GPUs — traffic is spiking. Mistral wants 4 more — also busy. But only 8 GPUs are free in the cluster. Total demand: 10. Available: 8. Someone's not getting everything they want."

"Step one — WVA optimizes. Based on inference signals — queue depth, latency, cache hit rates — WVA calculates the optimal split. Llama gets 5, Mistral gets 3. That's 8 total, fits within available capacity. Purely from an inference performance standpoint, this is the best allocation."

"Step two — Kueue applies governance. Team A, which runs Llama, has a quota of 10 GPUs. They're already using 6. Kueue says: 'You can have 4 more, not 5. Your quota is the ceiling.' So Llama gets 4, Mistral gets 3. One GPU remains unallocated — it could go to a queued training job."

"Demand does NOT equal entitlement. WVA proposes. Kueue disposes. This is the WVA plus Kueue interaction in a nutshell, and it's what makes shared clusters actually governable."

---

---

### Slide 35: One Request, Five Systems (Diagram)

The full end-to-end request flow. Show how everything connects.

"Let me trace a single inference request through the entire architecture. This is the end-to-end flow."

"A request arrives — 'Analyze this transaction for compliance violations.' It hits the Kubernetes Ingress, then llm-d's EPP. The EPP checks which vLLM instance has the relevant prefix in its KV cache. Routes to Replica 3."

"But wait — did WVA recently scale up? Did it add Replica 3 in the first place? Yes. WVA detected rising queue depth and added it 30 seconds ago."

"And did Kueue allow WVA to add that replica? In a shared cluster, yes — the team's quota had headroom. In a dedicated cluster, this question doesn't arise."

"Finally, kube-scheduler placed that new replica on a physical GPU — the one with the right topology, the right memory, the right NVLink domain."

"Five systems, five questions. Each one answers exactly ONE question. No overlap, no gaps. llm-d: which instance? WVA: how many instances? Kueue: is this team allowed? kube-scheduler: which physical GPU? And vLLM: how to serve efficiently?"

"Let me show you the full component reference."

---


### Slide 36: Component Table (Table)

Reference table. Don't read every row — highlight the pattern and the new KubeRay entry.

"Here's the full component reference — nine components, nine questions, no overlap, no gaps."

"I won't read every row, but notice the pattern. Each component answers exactly one question. vLLM: how to serve efficiently? MIG: how to partition? DRA: how to match? Kueue: who gets capacity? llm-d: where to route? WVA: how many replicas? kube-scheduler: which node?"

"One I want to call out specifically — KubeRay plus Ray Serve. This is the distributed workload orchestration layer. Its question: how to orchestrate distributed training AND multi-model serving? RayCluster for the compute fabric, RayJob for training, RayService for serving. All governed by Kueue. We'll go deeper on this one in a few slides."

"This clean separation is by design. If two components answered the same question, they'd fight each other. If a question had no component, you'd have a gap. This is a well-factored system."

"You can take a photo of this slide if you want — it's a useful reference when you're wiring this up."

"One more architectural point before we move to FinOps: vendor independence."

---


**IF SOMEONE ASKS about multi-vendor GPU support (absorbed from vendor slide):**
Quick but important. Frame as a procurement advantage.

"This entire architecture runs on NVIDIA, AMD, Intel, and Google TPUs. Same codebase, same APIs, same management plane. vLLM abstracts the hardware at the serving layer. DRA abstracts it at the scheduling layer. Kueue and llm-d don't care what's underneath."

"Why does this matter practically? Two reasons. First, procurement leverage. When your NVIDIA allocation is constrained — and it IS constrained for most enterprises right now — you have alternatives. AMD MI300X is a credible option for inference. Intel Gaudi3 is emerging. You're not locked in."

"Second, future-proofing. GPU architectures evolve fast. B200, B300 are coming. Custom silicon from cloud providers is expanding. If your platform is hardware-agnostic, you adopt new hardware without re-architecting."

"This is an architecture decision, not an operations afterthought. Build for multi-vendor from day one."

"Alright — we've covered the architecture. Now let's talk about what everyone REALLY wants to know: who pays for what? Let's get into FinOps."

---

---

### Slide 37: Multi-Tenant Isolation Stack (Diagram)

This is THE enterprise governance slide. Let the layers build visually.

"Let me consolidate everything we've talked about — quotas, priorities, fair-share, hardware profiles, MaaS — into one picture. Seven layers of GPU isolation, building from the bottom up."

"Start at the base. Node isolation — taints and tolerations. This is optional, for teams that need hard GPU pool separation. Most organizations don't need this, so it's gray. It's available but not required."

"Layer two — project isolation. OpenShift namespaces with RBAC and NetworkPolicy. Every team gets their own namespace. This is day one configuration."

"Layer three — GPU quota. Kueue ClusterQueue with nominalQuota. This is also day one. Each team gets a guaranteed GPU allocation. ML Engineering gets 40 GPUs. Applied AI gets 80. These are hard guarantees."

"Now we start adding governance layers. Layer four — fair-share with Kueue cohorts. Weighted proportional sharing across teams. When GPUs are contended, the Dominant Resource Share algorithm decides who gets admitted. This goes in around week five."

"Layer five — priority tiers. PriorityClass resources. Production workloads at priority 100 preempt development workloads at priority 10. When a fraud detection model needs GPUs at 2 AM, the overnight training job yields. Also week five."

"Layer six — hardware abstraction. Hardware Profiles in the RHOAI dashboard. Data scientists don't see nvidia.com/gpu: 1 — they see 'Small development GPU' or 'Large model fine-tuning.' The platform team defines what each profile maps to."

"Top layer — model governance. MaaS subscriptions with AuthPolicies. Per-team model access. Per-model token rate limits. This is the capstone — deployed around week nine."

"Look at the timeline on the right. Each layer is additive. You don't need all seven on day one. Start simple — namespaces and quotas. Add governance as teams mature. This is exactly the 12-week roadmap we showed earlier."

**IF SOMEONE ASKS: "Do we need all seven layers?"**
"No. Layers 1-3 (node isolation, project isolation, GPU quota) cover 80% of use cases. Fair-share and priority tiers add elasticity. Hardware Profiles and MaaS are for teams that want self-service and model governance. Each layer is optional and additive."

---


### Slide 38: Metering at Three Layers (Diagram) — FINOPS & OPERATIONS

**[Section transition]** "We've built the architecture. Now let's talk about the economics — because technology without financial governance is just engineering for its own sake."

Frame FinOps as something most organizations get wrong.

"FinOps for GPUs. This is where I see organizations make the most expensive mistakes, because they try to jump to chargeback before they can even METER correctly."

"There are three layers, and they must happen in order. Layer 1: Metering — what was consumed? GPU-hours, VRAM-hours, tokens processed. You need to MEASURE before you can price. And GPU metering is harder than CPU metering because you have to track not just 'was the GPU allocated' but 'was the GPU actually COMPUTING?' Those are very different numbers."

"Layer 2: Rating — what rate applies? Is this an H100 or a MIG slice? Is it production or dev/test? Is it within quota or burst capacity? The rate card matters because GPU costs vary by 10x depending on the hardware."

"Layer 3: Allocation — which cost center pays? This is where organizational politics meets technical metering. Does the platform team pay for idle capacity? Does the team that reserved GPUs pay whether they used them or not?"

"Here's my strong advice: start with metering. Get 90 days of clean data before you even THINK about chargeback. Too many organizations launch chargeback on day one, the data is wrong, teams revolt, and the whole initiative loses credibility."



"And let me be specific about what metrics we actually collect at layer one. DCGM Exporter — NVIDIA Data Center GPU Manager — runs as a DaemonSet via the GPU Operator. It exposes per-GPU Prometheus metrics. The key ones: DCGM_FI_DEV_GPU_UTIL gives you compute utilization as a percentage. DCGM_FI_DEV_FB_USED tells you how much framebuffer — VRAM — is consumed in megabytes. DCGM_FI_DEV_MEM_COPY_UTIL shows memory bandwidth utilization. DCGM_FI_DEV_POWER_USAGE reports power draw in watts. You access these in OpenShift Console under Observe > Metrics, or via the Prometheus API."

---


### Slide 39: Memory Pricing (Diagram)

This is a subtle but critical pricing trap.

"Here's a pricing trap that catches almost everyone. A workload is using 25% of the GPU's compute but 50% of its VRAM. Which do you charge for?"

"If you charge for compute usage — 25% — you're massively undercharging. That workload is BLOCKING 50% of the GPU's memory. No other workload can use that memory. The GPU is half-occupied even though its compute engine is mostly idle."

"The correct formula: billable GPU-equivalent equals the MAXIMUM of compute utilization and memory utilization. In this case, max of 25% and 50% equals 50%. Charge for 50%."

"For AI workloads, VRAM is frequently the binding constraint, not compute. A large model's weights sit in memory 24/7 even when no requests are coming in. If you only meter compute, you'll dramatically undercount the actual resource consumption."

"This is especially important for MIG slicing — a MIG slice is defined by its memory partition. A 1g.10gb slice has 10 GB of memory. If your model uses 8 GB, it's consuming 80% of that slice's memory regardless of compute."

---


### Slide 40: ACME's Monthly GPU Bill (Table)

Make the numbers personal. This is the "CFO slide."

"Let's look at ACME's actual monthly GPU bill. This is the table the CFO has been asking for — and never received until now."

"Total allocated: $233,500 per month across 8 teams. Total ACTIVE — meaning GPUs that were actually computing: $136,225. Total IDLE — GPUs that were reserved but doing nothing: $97,275. That's $97K per month in idle capacity. Nearly $1.2 million per year."

"Now look at the per-team breakdown. Data Science: $103,500 allocated, $25,875 active. That's 25% efficiency. They're paying $77,625 per month for GPUs that sit idle 75% of the time. Why? Because they over-request. They ask for 8 GPUs 'just in case,' use 2, and the rest sit there."

"Gen AI: 72% efficiency. Not bad, but that's still $18,000 per month in idle. ML Engineering: 62%. Applied AI: 59%."

"You cannot govern what you cannot measure. This table is the first step. Once teams can SEE their idle cost, behavior changes. Not through punishment — through visibility."

---


### Slide 41: Charge for Allocation (Two-Column)

The charging philosophy. This is where policy meets engineering.

"Here's the charging philosophy, and it's counterintuitive enough that I want to walk through the reasoning."

"Left column — what you CHARGE for. Charge for allocated GPU-hours, not utilization. Why? Because an allocated GPU that's idle is STILL blocking other teams from using it. The incentive should be: don't reserve what you won't use. If teams only pay for utilization, they'll over-reserve because it's free to hold idle GPUs."

"Burst capacity — when a team exceeds their quota and borrows from idle peers — charge a 1.5 to 2x premium. This creates a natural incentive to right-size your quota. Burst is available when you need it, but it costs more than your base allocation."

"Token-based API billing for inference-as-a-service. If teams consume models via API rather than managing their own deployments, charge per token. This is the model that cloud LLM APIs use, and it works because the platform absorbs the infrastructure complexity."

"Right column — what you SHOW but don't charge for. Queue wait time — the time your workload spent waiting for GPUs. Show it in dashboards so teams can see contention, but don't charge for it. Nobody should pay for WAITING. Idle allocation — show it prominently so teams can see their waste, but initially don't penalize it. Failed placements — show how many times placement failed, but don't charge."

"Unused fleet capacity is a SHARED cost. IT carries the idle-capacity risk in the burst pool. Teams consume elastically. For team reservations — where a team explicitly reserves GPUs — the TEAM carries the risk. They pay whether they use them or not."

"Start with 90-day showback — show teams their costs but don't charge. Let them adjust behavior. THEN graduate to chargeback once the data is trusted and teams have had time to optimize."

**IF SOMEONE ASKS:** "What about teams that game the system by requesting minimum and always bursting?" — "That's why burst pricing is 1.5-2x. If a team's burst is consistently high, it's cheaper for them to increase their quota. The pricing structure creates a natural feedback loop."

---


### Slide 42: Showback Dashboard — Team Breakdown (Diagram)

This is the "monthly statement." Make it tangible.

"Here's what the showback dashboard actually looks like. This is what the CTO opens on the first Monday of each month."

"Team Model Engineering, July. Allocated: $42,000. Active: $24,000. Idle: $18,000. Right away you can see — 43% of their GPU spend was idle. But that's not the whole story."

"GPU utilization: 57%. Memory utilization: 81%. See the gap? Their GPUs are memory-bound, not compute-bound. They're running large models that fill VRAM but don't saturate compute. This tells you the team might benefit from MIG — split those GPUs and run more models per GPU."

"Queue wait: 320 GPU-hours. That's how much time their workloads spent waiting for GPUs. This is the contention signal — it tells you whether the team's quota is too small or whether they need to schedule more efficiently."

"THIS is the monthly statement the CTO has been asking for. And it didn't exist before GPU-level metering was implemented. Teams are no longer arguing about whether they need more GPUs — the data speaks for itself."



"And for MaaS inference specifically, you get token-level tracking through Limitador. Three key metrics: authorized_hits counts tokens consumed per successful request, broken down by subscription and model. authorized_calls counts API requests. limited_calls counts rate-limited 429 responses — teams hitting their token ceiling. The RHOAI Perses dashboard pulls from these metrics. CSV export is available for monthly showback reports."

"One caveat: this observability dashboard is designed for showback — visibility, not billing. If you need billing-grade metering for actual chargeback, access the Limitador metrics endpoint directly and build your own aggregation."

---


**IF SOMEONE ASKS about scale-to-zero (absorbed from scale-to-zero slide):**
This is the single biggest capacity recovery mechanism.

"Now let me show you the single biggest quick win in the entire GPU economy. Scale to zero."

"ACME's Gen AI team has 120 H100s allocated for production inference. But actual traffic? Six hours a day — market hours for the trading desk. The other 18 hours? 90 H100s sit completely idle. That's $2.7 million per year in idle overnight capacity."

"KServe combined with WVA gives you minReplicas: 0. When no requests arrive for a configured window — say 15 minutes — WVA scales the inference service down to zero replicas. The GPUs are released back to the elastic pool. Kueue can hand them to training jobs, fine-tuning jobs, or other teams."

"The trade-off? Cold-start. When the first request arrives the next morning, the model needs to load from object storage back into GPU memory. For a 70-billion-parameter model, that's 30 to 90 seconds depending on storage bandwidth and model format."

"For ACME, a 30-90 second cold-start at 6 AM is COMPLETELY acceptable. The trading desk doesn't open for another hour. Meanwhile, 90 H100s ran training jobs all night that would have otherwise required procurement of ADDITIONAL hardware."

"This is the kind of optimization that pays for the entire GPUaaS platform implementation in the first quarter."

---

---

### Slide 43: WVA Autoscaling (Diagram)

Show WVA in action with a specific scaling event.

"Here's WVA in action. Llama 70B, running 4 replicas. Queue depth starts rising. TTFT — time to first token — degrades from 50 milliseconds to 200 milliseconds. WVA detects the trend."

"WVA's decision: scale from 4 to 6 replicas. Add 2 more vLLM instances. It submits the request to Kueue — 'I need 2 more H100s.' Kueue checks Team A's quota — they have headroom. Admitted. kube-scheduler places the new replicas on nodes with available GPUs in the right topology."

"60 seconds later, 6 replicas are running. Queue depth drops. TTFT returns to 50 milliseconds. And here's the important part: all of this happened within Kueue's quota ceiling. WVA didn't override governance. It scaled within policy."

"When traffic drops again that evening, WVA scales back to 4 — or even to zero. Those 2 GPUs return to the elastic pool. No manual intervention. No PagerDuty alerts. Just AI-aware autoscaling working as designed."

---


### Slide 44: KubeRay + Kueue — Distributed Workloads (Diagram)

KubeRay isn't just for training — it's the distributed workload orchestration layer for both training AND multi-model inference.

"This is a slide that changes how people think about KubeRay. Most people associate it with distributed training — and that's correct, but it's only half the story. KubeRay plus Kueue is the distributed workload orchestration layer in RHOAI. It handles training AND multi-model serving."

"Let's take the left panel first — training. You submit a RayJob or a Kubeflow TrainJob. Kueue runs admission — does this team have quota? Is there capacity? Once admitted, GPUDirect RDMA gives you 3x speedup on distributed fine-tuning by transferring data directly GPU-to-GPU, bypassing the CPU entirely. And when an inference spike hits, the training job doesn't crash. Kueue sends SIGTERM, the job does a JIT checkpoint — saves state after the current training step — and releases the GPUs. When capacity returns, it resumes from that checkpoint. Zero lost work."

"Now the right panel — this is what most people miss. RayService deploys Ray Serve with vLLM as the backend. That's multi-model serving on a shared cluster. You can run Llama, Mistral, and a custom fine-tuned model on the same RayCluster. Ray Serve handles routing. And you get THREE levels of autoscaling working together: Ray Serve manages replica counts, Ray's autoscaler adds or removes worker pods, and Kueue governs the overall quota ceiling. Elastic borrowing means if another team's GPUs are idle, your RayService can grab them. When they need them back, Kueue preempts gracefully."

"Zero-downtime upgrades are built in. RayService does a rolling deployment — new version spins up, old version drains, no traffic dropped. For ACME, that's critical. They can update their fraud detection model mid-day without impacting transaction scoring."

"And at the bottom — CodeFlare SDK. This is the Python-native interface. Data scientists don't write YAML or run kubectl. They use a Python API from their Jupyter notebook to submit training jobs or deploy models. Same SDK for both training and serving."

"One thing to be clear about: RHOAI gives you three serving patterns. KServe with vLLM for single-model, single-node — that's the simplest path. KubeRay with RayService for multi-model, multi-node — that's what we're looking at here. And llm-d for disaggregated inference at massive scale. They're not competitors — they're different tools for different scales."

**IF SOMEONE ASKS: When should I use KubeRay + RayService vs llm-d?**
"Use KubeRay + RayService when you need multi-model serving — multiple models on the same cluster, with per-model autoscaling, and you want the unified training + serving orchestration layer. Use llm-d when you have one model at massive scale — hundreds of GPUs, disaggregated prefill and decode, KV-cache routing across a fleet. Think of it this way: RayService is your multi-model workstation, llm-d is your single-model hyperscaler."

**IF SOMEONE ASKS: What about KServe? Is it deprecated?**
"Absolutely not. KServe with vLLM is the simplest, most straightforward path for single-model serving. InferenceService CR, KEDA autoscaling, done. If you have one model per endpoint and don't need multi-model orchestration, KServe is the right choice. The three patterns are complementary."

---


### Slide 45: Multi-Cluster Fleet Management (Diagram)

Scale beyond a single cluster.

"Everything we've discussed so far has been within a single cluster. But ACME has NINE clusters across SIX environment types — production, UAT, dev, training, edge, and GovCloud. Each cluster is an island. One has idle H100s. Another is maxed out. There's no fleet-wide visibility."

"Red Hat Advanced Cluster Management plus MultiKueue solves this. Single pane of glass across all nine clusters. Submit a job ONCE. MultiKueue evaluates: which cluster has the capacity, the right GPU type, and the appropriate environment? Three dispatching strategies: all-at-once — submit to all clusters, first one that admits wins. Incremental — try preferred clusters first, fail over to others. External — delegate the decision to an OCM controller."

"MaaS — Model as a Service — GA in RHOAI 3.4. This is multi-tenant LLM governance. ACME's teams consume models via API. Token quotas per team. RBAC. Usage tracking. Audit trails. The data scientist doesn't manage infrastructure — they call an API."

"And for regulated industries — FIPS 140-2 and 140-3 mode via validated RHEL crypto modules. Air-gapped installation with mirror registries and oc-mirror v2. Cosign signature verification via sigstore — ClusterImagePolicy CRDs. ROSA on GovCloud has FedRAMP High Authorization for both classic and hosted control planes. For ACME, these aren't optional features — they're NON-NEGOTIABLE requirements."

---


### Slide 46: Team Callback — Four Teams Revisited (Table) — REFERENCE SOLUTION

**[Section transition]** "We've covered the technology, the architecture, and the economics. Now let's put it all together into something ACME can actually implement."

This is the structural payoff. Every problem now has a named solution.

"Remember these four teams from the opening? Let me show you what changes."

--- pause for recognition ---

"Gen AI — 90 idle H100s overnight. The fix: scale-to-zero with WVA. When trading hours end, models scale down. Those 90 GPUs flow to the elastic pool for overnight training. We covered this on slides 48 and 49."

"ML Engineering — 77 gigabytes of unused VRAM per GPU on those small compliance models. The fix: MIG slicing. One A100 becomes 7 isolated slices. 34 GPUs freed. Over a million dollars recovered. Slide 16."

"Applied AI — 75% idle because they over-request. The fix: DRA right-sizing with CEL-based claims, plus Kueue borrowing so they only reserve what they use and borrow when they need more. Slides 21 and 22."

"Data Science — idle notebooks clogging the cluster. The fix: notebook culling policies with Kueue governance. If a notebook hasn't been active for 2 hours, Kueue reclaims the GPU. The data scientist restarts in 30 seconds. Slide 19."

"Every single problem from the opening now has a named solution, a specific technology, and a slide number you can reference. This isn't theory — it's a deployment plan."

---


### Slide 47: Before/After (Two-Column)

Quantify the transformation. Make it concrete.

"Let me put the before and after side by side."

"Day 0 — where ACME is today. 38% average utilization. $97,000 per month in idle capacity — that's $1.2 million per year. 3 to 5 day wait for a GPU notebook. Teams hoarding resources. Shadow IT growing. No cost visibility."

"Day 90 — after implementing the reference architecture. 75% or higher utilization. $58,000 per month recovered — $700K annually. Self-service GPU access in minutes, not days. Per-team showback dashboards. Dynamic sharing with governance."

"And notice what DIDN'T change: same 500 GPUs. Same $20 million investment. No new hardware procurement. The gains come entirely from better management of existing resources."

"So how do you actually get from Day 0 to Day 90? Let me walk you through the 12-week implementation."

---


### Slide 48: Twelve Weeks to Governed Sharing (Content)

This is the "how to actually do it" slide. Be specific about sequencing and risk.

"Here's the implementation roadmap, and I want to be specific about sequencing because order matters."

"Days 1 through 7: idle culling plus MIG. This is the quick win with zero risk. Identify GPUs that have been allocated but idle for more than 48 hours. Notify the owning team. If no response, reclaim. Then take those compliance models on full A100s and move them to MIG slices. Result: 34 GPUs recovered in the first week. No new software needed — just policy and MIG configuration."

"Weeks 2 through 4: DRA. Replace nvidia.com/gpu: 1 with attribute-based ResourceClaims. Now workloads request 'A100 or MIG, at least 10 GB VRAM' instead of 'one GPU, any GPU.' The scheduler starts placing workloads on appropriate hardware. Misallocation drops immediately."

"Weeks 5 through 8: llm-d plus scale-to-zero. Deploy llm-d for KV-cache-aware routing. Configure WVA with minReplicas: 0 for non-production hours. Result: 90 H100s recovered overnight. This is the biggest single capacity win."

"Weeks 9 through 12: Kueue fair-share plus GPU showback. Implement Kueue quotas per team. Enable GPU metering and build the showback dashboard. Teams start seeing their costs. Behavior change begins. This is the foundation for eventual chargeback."

"Notice the order: quick wins first to build credibility, then infrastructure changes, then governance. Don't lead with governance — that's a political fight. Lead with 'we just recovered 34 GPUs and nobody noticed' — that builds trust."

**IF SOMEONE ASKS:** "What's the team size needed for this?" — "Two to three platform engineers, a FinOps analyst, and an executive sponsor. The technology is Kubernetes-native — if your team can manage OpenShift, they can deploy this. The hard part is organizational change management, not the technology."

---


### Slide 49: Self-Service Profile (Diagram)

Show the end-state experience. Make it feel effortless.

"This is what Day 90 actually FEELS like for a data scientist."

"She opens the OpenShift AI dashboard. She sees a dropdown: 'Compute Profile.' Options: Small development — 1 GPU, 16 GB, good for experimentation. Medium inference — 2 GPUs, 40 GB, for serving a mid-size model. Large model fine-tuning — 4 H100s, 80 GB each, with NVLink topology."

"She picks 'Large model fine-tuning.' Clicks submit."

"Behind the scenes, the platform translates that into: 4 H100s, 80 GB each, in the same NVSwitch domain, appropriate node pool, Kueue queue assignment, quota check, DRA ResourceClaim. If capacity is available — admitted. If not — queued with an estimated wait time."

"She doesn't write YAML. She doesn't open a ServiceNow ticket. She doesn't know which cluster she's on. She doesn't care about NVLink topology. She just picks from a dropdown and starts working."

"THAT is the difference between 'GPU as a raw resource' and 'GPU as a Service.' The complexity is still there — all five technologies are working underneath — but the data scientist sees a dropdown."

---


### Slide 50: Platform Maturity Themes (Diagram)

This is NOT a release schedule. It's a maturity model. Let the four cards build left to right.

"I want to show you something different from a typical product roadmap. Instead of dates and version numbers, let's talk about the four themes of platform maturity — because EVERY organization follows this same journey, regardless of which quarter they start."

"Theme one — SEE. Visibility. Before you can manage anything, you need to see it. Look at the problems this theme solves: GPU utilization is invisible, there's no fleet-wide view, and you can't justify a $20 million GPU spend to your CFO. The capabilities here are all about measurement — GPU topology dashboards, DCGM metrics flowing into Prometheus, Kueue queue visibility, llm-d observability. This is the foundation. Everything else builds on this."

"Theme two — GOVERN. Policy and quota. Now that you can see the fleet, you discover the problem: teams are hoarding GPUs, there are no sharing rules, it's a land-grab culture. The capabilities are enforcement mechanisms — Kueue quota dashboards, DRA for smart GPU selection, fair-share with preemption, and Hardware Profiles so data scientists pick from a dropdown instead of writing YAML."

"Theme three — ACT. Self-service. You've got visibility and governance, but your data scientists are still filing ServiceNow tickets and waiting 5 days for a GPU. The capabilities here remove friction — Compute Profiles, scheduling explainability so teams understand WHY their job is queued, GPU cost attribution so teams see their spend, and one-click model deployment."

"Theme four — AUTOMATE. Platform intelligence. This is the capstone. The platform starts making decisions autonomously — a GPU pool wizard that suggests optimal configurations, idle GPU auto-reclamation, predictive scaling that anticipates traffic before it hits, ML-driven right-sizing recommendations."

"Notice the arrow between each card: each theme builds on the previous one. You literally CANNOT skip. If you try to automate without governance, you'll auto-scale workloads that shouldn't be running. If you try to self-serve without visibility, you'll give teams GPUs you don't have."

"Where would ACME be in this journey? After twelve weeks of the implementation we just walked through, they'd be solidly in ACT — with the foundation for AUTOMATE laid."

**IF SOMEONE ASKS: "When do these capabilities ship?"**
"The themes map to RHOAI releases, but the exact timing depends on Red Hat's release cadence. What I'd encourage you to focus on is the maturity model — which theme are YOU in today? Most organizations are somewhere between SEE and GOVERN. The path forward is always the same: measure first, then enforce, then empower, then automate."

**IF SOMEONE ASKS: "Can we get specific release dates?"**
"Check the RHOAI lifecycle page for GA dates. Red Hat confirms dates closer to release. But the capability ordering is committed — visibility first, governance second, self-service third, automation fourth. That sequence doesn't change."

---


### Slide 51: 401(k) Callback — Every Dollar Working (Content)

The analogy returns. Full circle. This should feel like coming home.

"Remember the 401(k) with 95% in a zero-interest checking account? Let me tell you how that story ends."

--- pause ---

"Same $20 million. Same 500 GPUs. But now every dollar is working."

"The data scientist picks 'Medium GPU' from a dropdown. Behind the scenes, DRA selects a MIG slice — the fractional share she actually needs. She didn't have to know about MIG, DRA, or ResourceClaims. She just picked from a dropdown. That's the fractional share, delivered as a Compute Profile."

"The Gen AI team's Llama service scales to zero at 8 PM. 90 H100s flow to the elastic pool. Training jobs pick them up within minutes. At 6 AM, traffic returns, WVA scales Llama back up, Kueue preempts the training jobs — they checkpoint and yield. That's the auto-rebalancing that was missing from the broken portfolio."

"And the CTO? She opens the showback dashboard on the first Monday of every month. Team-by-team costs. GPU utilization. Memory utilization. Queue wait times. Idle capacity trends. That's the monthly statement she never had."

"Same balance. Same investment. But now every dollar, every GPU, every watt of power — is working."

---


### Slide 52: Closing Slide

Land the plane. Short, confident, inviting.

"Five layers of Kubernetes-native platform intelligence. Five technologies: vLLM for efficiency, MIG for density, DRA for smart selection, Kueue for governance, llm-d for intelligent routing. WVA ties them together with AI-aware autoscaling."

"Same 500 GPUs. From 5% utilization to 75%+. From $97K monthly waste to governed, visible, shared capacity. From 3-to-5-day ServiceNow tickets to a dropdown."

"The technology is production-ready. The reference architecture is deployable in 12 weeks. And every component we discussed today is either GA or on a published roadmap."

--- pause ---

"I'd love to take your questions. What resonated? Where are you in this journey?"

---

## Narrative Flow Validation

### Does the SCQA structure hold?

| Phase | Slides | Content | Validates? |
|-------|--------|---------|-----------|
| Situation | 3 | $20M fleet, 5% utilization, 3–5 day wait | Shared context everyone agrees on ✓ |
| Complication | 4 | Dashboard hiding 5 problems | Tension that demands action ✓ |
| Answer | 5 | Journey map (governing thought) | Top of the pyramid ✓ |

### Does each concept build on the previous?

| Slide | Concept | Builds On | Why This Order |
|-------|---------|-----------|---------------|
| 1-2 | Title + Agenda | Nothing | Set expectations — audience knows the roadmap |
| 3-5 | SCQA Opening | Agenda | Situation → Complication → Answer |
| 6-11 | GPU Reality | Complication | Physical → fungibility → topology → packing → conflict → paradigm shift |
| 12-13 | Analogy | Problems | 401(k) quote → fund-by-fund mapping |
| 14 | Five tech preview | Analogy | Previews five technologies — cognitive reset |
| 15 | vLLM | The problem | Every org starts here — deploy a model |
| 16-17 | MIG | vLLM | "vLLM is efficient, but small models need GPU splitting" |
| 18 | DRA | MIG | "GPUs can be sliced — now request the right slice" |
| 19-21 | Kueue | MIG + DRA | "We can slice and select — who gets capacity?" |
| 22 | Fair-share | Kueue | DRS algorithm in action — visual evidence |
| 23 | LLM signals | Kueue | "Governance set — here are the 9 signals llm-d uses for routing" |
| 24-26 | llm-d | vLLM + Kueue + signals | "Now optimize across vLLM instances using those signals" |
| 27 | Rosetta Stone | All five | Connects five technologies back to 401(k) analogy |
| 28 | Five-layer stack | All five | "How they compose — five-layer architecture map" |
| 29-30 | Deployment patterns | Five layers | "Concrete first: dedicated/shared, prod/elastic" |
| 31 | Kueue pool | Deployment patterns | "The elastic pool needs a gatekeeper — WANT vs HAVE" |
| 32 | WVA explained | Kueue pool | "WHO gets GPUs (Kueue) vs HOW MANY replicas (WVA)" |
| 33-35 | Interactions | WVA + Kueue | "Control loops → fairness → request flow" |
| 36-37 | Reference | All | "Component table → multi-tenant isolation" |
| 38-45 | FinOps + Ops | Architecture | "Metering → pricing → showback → charge model → WVA → training → multi-cluster" |
| 46-52 | Solution | Everything | "Team callback → concrete steps → roadmap → analogy callback → close" |

### Is there any concept used before it's introduced?

- vLLM: first on slide 15 ✓
- MIG: first on slide 16, after vLLM ✓
- DRA: first on slide 18, after MIG ✓
- Kueue: first on slide 19, after MIG + DRA ✓
- LLM signals: slide 23, after Kueue — provides context for llm-d routing ✓
- llm-d: first on slide 24, after vLLM + Kueue + signals ✓
- WVA: first on slide 32 (WVA Explained), after deployment patterns + Kueue pool ✓
- Three control loops: slide 33, after WVA is introduced ✓
- Five-layer stack: slide 28, first slide of Platform Architecture section ✓

**Result: No concept is used before it's introduced.** ✓

### Does the analogy appear ONLY where it should?

| Location | Analogy Content | Correct? |
|----------|----------------|----------|
| Slides 12-13 | Full analogy — 401(k), funds, fractional shares | ✓ |
| Slide 27 | Rosetta Stone — maps technologies to investing fixes | ✓ |
| Slides 14-26, 28-50 | ZERO analogy language | ✓ |
| Slide 51 | 401(k) callback — "every dollar is working" | ✓ |

**Result: Analogy is cleanly separated.** ✓

---

## Timing Guide (60-minute session)

| Segment | Slides | Count | Minutes |
|---------|--------|-------|---------|
| Title + Agenda | 1–2 | 2 | 2 |
| SCQA Opening | 3–5 | 3 | 5 |
| GPU Reality | 6–11 | 6 | 8 |
| The Analogy | 12–13 | 2 | 3 |
| Architecture Deep Dive | 14–27 | 14 | 17 |
| Platform Architecture | 28–37 | 10 | 10 |
| FinOps and Operations | 38–45 | 8 | 8 |
| Reference Solution + Closing | 46–52 | 7 | 7 |
| **Total** | **1–52** | **52** | **60 min** |

**If running short (55 min):** Spend 15 seconds each on slides 8 (topology), 17 (MIG slicing zoom), and 22 (fair-share) — show the visual, deliver one sentence, move on. Skip the "IF SOMEONE ASKS" sections entirely.

**If running long:** Spend less time on slides 36 (component table) and 40 (monthly bill) — scan, don't read.
