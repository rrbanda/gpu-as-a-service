# Speaker Notes — Running AI Agents Safely at Scale

---

### Slide 1: Title

Welcome everyone. Thank you for making time for this session.

Today we're going to walk through something that took our team considerable effort to learn: running AI agents safely at scale is fundamentally different from running any workload you've operated before. The scheduling model is different. The security model is different. The cost model is different. And if you try to apply traditional infrastructure patterns to agents, you'll leave gaps that real attackers are already exploiting — in 2026, today, not hypothetically.

By the end of this session, you'll have a complete mental model for how to think about agentic workloads, and a concrete architecture you can start building with open-source components.

---

### Slide 2: Agenda

Here's the roadmap for the next sixty minutes.

We'll start by building context — what IS an agent, because most of the confusion in this space comes from people using the word to mean completely different things. Then we'll look at why agents are genuinely hard — five assumptions your infrastructure makes that agents violate. After that, the full open blueprint — an architecture where every component sits behind a neutral interface. Then we'll deep-dive into the five decisions you need to make: isolation, tool governance, inference routing, identity, and where the agentic loop runs. We'll prove the architecture with benchmark results — real attacks against real pods. And we'll close with what's mature today versus what's emerging, and a phased adoption path.

Let's begin with the most important question.

---

### Slide 3: An AI agent pursues a goal autonomously

Let me be very precise about definitions, because this matters.

A chatbot answers one question. You ask "what's the weather?" and it responds. Done. A microservice processes one request. Stateless, short-lived, well-understood.

An agent is different. An agent receives a GOAL — "optimize tomorrow's field-service schedule" or "fix this failing CI pipeline" — and then it PURSUES that goal. Over minutes. Over hours. Sometimes over days. It calls tools. It writes files. It makes decisions about what to do next. It keeps state between steps. It decides when it's done.

Think about the coding assistants many of you are already using — Cursor, Copilot. They read your codebase, plan changes, edit multiple files, run tests, fix errors, and iterate. That's an agent. A field-service optimizer dispatches technicians, checks traffic, re-routes in real-time. That's an agent. A NOC agent monitors alerts, correlates incidents, runs remediation playbooks. That's an agent.

The key insight: at different moments, the same agent looks like completely different Kubernetes workloads. And that's the root of the problem.

---

### Slide 4: Three components — Model, Harness, Sandbox

Let's decompose an agent into its three fundamental components. This decomposition is critical because each has a different lifecycle, different scaling characteristics, and different security requirements.

The Model is the reasoning service — Llama, Nemotron, DeepSeek, Qwen, Mistral. It's stateless. You swap it, version it, scale it independently. It sits behind an OpenAI-compatible API. The model doesn't know it's inside an agent.

The Harness owns the loop. It holds memory, manages the context window, orchestrates tool calls, decides when to stop. OpenClaw, LangGraph, Hermes Agent — these are harnesses. The harness is the "brain" that makes the agent an agent rather than a single API call.

The Sandbox decides what the agent may touch — which files, which binaries, which network endpoints. OpenShell, Kata Containers, the emerging agent-sandbox API. The sandbox doesn't trust the harness OR the model.

Separate lifecycles, separate scaling, separate security. And that separation is exactly why Red Hat AI is a natural host — we already operate platforms where these concerns are independently managed.

---

### Slide 5: Shape-shifting workload

This is the slide that should make your infrastructure team uncomfortable.

Minute one: the agent receives a goal and plans its approach. It looks like a request/response service. You'd put it behind a Deployment.

Minute five: it dispatches a physics simulation to a GPU cluster. Now it's a batch job scheduler. You'd use a Job or a Kueue workload.

Minute ten: it calls an LLM to summarize intermediate results. Now it's an inference client hitting a serving endpoint. That's a KnativeService or a vLLM deployment.

Minute sixty: it's still running. Holding state. Waiting for a human to approve a high-risk action. It's a long-running stateful workload. That's a StatefulSet pattern.

No single Kubernetes primitive maps cleanly to this lifecycle. A Deployment assumes stateless replicas. A Job assumes termination. A KnativeService assumes scale-to-zero. An agent is ALL of these at different moments. And that's why we need a new architecture, not just new labels on existing resources.

---

### Slide 6: Agent-as-a-Workload vs Agent-as-a-Service

This diagram from the Red Hat Developers article shows the two fundamental deployment patterns for agents.

On the left: Agent-as-a-Workload. The agentic loop ships inside the pod alongside the harness. The agent has its own identity — a SPIFFE SVID scoped to its namespace and service account. It has its own blast radius — the sandbox constrains what it can do. This is for long-running, autonomous workloads. Think field-service optimizers, research agents, CI/CD agents.

On the right: Agent-as-a-Service. The loop runs in a shared runtime — OGX behind a Responses API. The client sends a goal, the server manages the loop. Centralized audit trail. Credential isolation — clients never hold tool credentials. This is for request-scoped assistants and copilots. Think customer support bots, internal help desks.

Duration and ownership pick the pattern. If the agent runs for hours and makes autonomous decisions, it's a workload. If it handles one user request and returns, it's a service. Most organizations will run both.

---

### Slide 7: Same governance across both patterns

Here's the key insight that bridges these two patterns: the governance layer is identical.

Whether the agentic loop runs inside the pod or in a shared runtime, the same two mechanisms apply. SPIFFE establishes WHO the agent is — cryptographic identity at the pod or request level. The MCP Gateway decides WHAT that identity can do — which tools, which endpoints, which data.

Neither mechanism consults the model. And that is the point. Authorization is not the model's decision to make. A prompt injection can redirect the model's goals, but it cannot change the identity claims or the tool entitlements.

This also means the two patterns compose. A sandboxed agent pod can delegate tool execution to a shared OGX loop while keeping its own identity. The MCP Gateway preserves per-agent policy throughout the chain.

Now that you understand what agents are and how they deploy, let me show you why they're hard.

---

### Slide 8: What keeps you up at night?

When agents go from demo to production, these are the eight things that keep infrastructure and security teams up at night.

Prompt injection — adversarial inputs can redirect agent goals and exfiltrate secrets. Static API keys — one leaked key exposes everything the agent can reach. No cost control — agents call the most expensive model for every task because nobody told them not to. Container escapes — kernel bugs give agents cross-tenant access. No tool governance — any agent can call any tool with no infrastructure check. Long-running state — schedulers assume workloads are short-lived. No end-to-end trace — tool calls, LLM hops, decisions are invisible. And vendor lock-in — CUDA libraries, NIM containers, proprietary APIs.

Each of these is solvable. But they're solvable only if you acknowledge that agents are a new workload class, not a clever use of existing primitives. Let me show you the five specific assumptions they break.

---

### Slide 9: Five broken assumptions

Your infrastructure was built for request/response workloads. Agents break five fundamental assumptions.

First: requests are short-lived. Agents run for minutes, hours, sometimes days. Your scheduler, your load balancer, your autoscaler — all assume the workload will be done soon.

Second: the workload does what you coded. With agents, the MODEL decides the next step. You didn't code the behavior — you gave it a goal and tools. The execution path is non-deterministic.

Third: network policy equals security boundary. Agents choose their own tools at runtime. A static NetworkPolicy can't anticipate which endpoints the agent will decide to call.

Fourth: credentials are static secrets. An agent workspace is attackable via prompt injection. If the agent can read its own environment variables, a successful injection means credential exfiltration.

Fifth: one model, one endpoint. Agents need three routing decisions per inference call — WHERE may it go (security), WHICH model (cost), WHICH replica (efficiency). Your current ingress can't make those three decisions.

These aren't theoretical. Let me show you two real attacks from 2026.

---

### Slide 10: Two real attacks from 2026

These are not hypothetical scenarios. These are documented attacks from this year.

On the left: the Microsoft PR injection attack from June 2026. Researchers demonstrated that prompt injections embedded in GitHub pull requests can hijack CI/CD coding agents. The malicious instructions are disguised as a routine review checklist. The agent reads /proc/self/environ, extracts API keys, and POSTs them to an attacker-controlled endpoint. This is assumption four — credentials as static secrets — being exploited in the wild.

On the right: CVE-2026-31431, the Copy Fail vulnerability from May 2026. This is a logic flaw in the Linux kernel's algif_aead subsystem, part of the AF_ALG crypto interface. A 732-byte Python script gives any unprivileged process a page-cache write primitive — the ability to write 4 bytes at a time to any file's page cache, even if the file is only open for reading. It uses splice() to create a pipe between the page cache and an AF_ALG socket. Under runc with overlayfs, the page cache is shared with the host kernel — corrupting a file's cached content inside one container makes that corruption visible to every other container sharing the same image layer. CISA added it to the KEV catalog because it's 100% reliable.

---

### Slide 11: The gap

Let me be very clear about why these two attack classes matter together.

Prompt injection redirects the agent's goals. The agent reads secrets and sends them to an attacker. This is an application-layer attack. You can defend against it with egress filtering, output scanning, guardrails.

Container escapes give the agent kernel-level access. The agent can read files from other containers, other tenants. Application-layer controls can't help here because the attack is BELOW the application.

These are two completely different threat classes requiring two completely different defenses. Application-layer isolation (OpenShell) catches the first. Hardware-level isolation (Kata) contains the second. You need both.

The architecture we're about to walk through addresses both simultaneously. And we'll prove it works with benchmark data.

---

### Slide 12: The complete open blueprint

Take a moment to absorb this diagram. This is Figure 1 from the Red Hat Developers article, and it's the full open agentic AI blueprint.

Three horizontal bands. The top band is the control plane — where governance decisions are made. Agent blueprints, GitOps, policy. The middle band is where the magic happens — where agents actually run. Sandboxed pods, shared runtimes, the MCP Gateway checkpoint between them. The bottom band is the platform — OpenShift, SPIFFE, observability, the inference pool.

The MCP Gateway sits between the execution layer and the tool backends. Every tool call passes through it. Every authorization decision is logged.

The critical design principle: every component is a ROLE that several implementations can fill. The model role can be filled by Llama, Nemotron, DeepSeek. The sandbox role can be filled by OpenShell, Kata, the agent-sandbox API. The inference routing role can be filled by llm-d, Praxis, or a custom EPP.

We're about to zoom into five specific decisions within this blueprint.

---

### Slide 13: Five decisions

These are the five decisions every organization running agents at scale needs to make. Each one sits behind a neutral interface, which means your choice is reversible.

Decision 1: Isolation — how do you contain the blast radius of a misbehaving agent? Decision 2: Tool Governance — who decides which tools an agent can call? Decision 3: Inference Routing — how do you balance security, cost, and efficiency for every inference call? Decision 4: Identity — how does the infrastructure know WHO is making a request? Decision 5: Loop Placement — does the agentic loop run inside the pod or in a shared runtime?

We'll spend the next section going three slides deep on each decision: the concept, the implementation, and the honest limitations. Let's start with isolation.

---

### Slide 14: Solution components table

Before we dive into each decision, here's the reference table. Every component in the blueprint, its role, and the implementation options available today.

I want you to notice the pattern: every row has multiple implementation options. Agent Blueprint can be Helm and GitOps, NemoClaw, or OpenShell. The sandbox can be OpenShell, Kata, or the agent-sandbox SIG spec. The model can be any OpenAI-compatible inference service. The identity layer is SPIFFE.

This is not a product pitch. This is an architecture where vendors compete on price and performance per component, and your procurement decisions stay reversible because every component sits behind a neutral interface.

We'll come back to this table when we discuss maturity — which of these are production-grade today versus emerging.

---

### Slide 15: Agent pod anatomy

Let's zoom into Decision 1: Isolation. This is the internal anatomy of an agent pod.

The supervisor process runs as PID 1. It enforces per-binary, per-path, per-endpoint policy using kernel primitives — seccomp profiles, Landlock LSM, network namespaces. The agent process runs as a child of the supervisor, inside the sandbox.

Three nested defense rings. Ring 1 is the process level — seccomp, Landlock, namespaces. This is the innermost ring, the tightest constraint. Ring 2 is the pod level — Kubernetes Pod Security Standards, SELinux, NetworkPolicy, and optionally RuntimeClass pointing to Kata for hardware isolation. Ring 3 is the hardware level — when you need confidential computing, memory encryption at the VM boundary.

The design principle: each ring assumes the ring inside it has ALREADY FAILED. Pod-level controls assume process-level controls were bypassed. Hardware-level controls assume pod-level controls were bypassed. Defense in depth means each layer is independently sufficient to contain one class of attack.

---

### Slide 16: Supervisor ingress/egress proxy

This slide directly addresses the supervisor's role as the security gateway for every agent pod. This is a component Ramesh's team specifically asked about, so let me go deep.

The supervisor runs as PID 1 — it starts before the agent does. Its startup sequence is: fetch policy from the sandbox control plane, install kernel filters (seccomp profiles, Landlock rules), inject credentials (the SPIFFE SVID from the Auth Bridge), and THEN launch the harness as its child process. The agent never runs unsupervised.

The egress proxy is the critical piece. Every outbound connection — HTTP, HTTPS, or raw TCP — routes through this proxy. The default posture is deny-all. You write a policy that allowlists exactly the endpoints your agent needs. For an AI coding agent backed by a local inference server, that might be a single entry: the model API endpoint on port 8000. Everything else returns policy_denied.

Here's the key for your internal vs external flow question: Tier 1 routing lives inside the supervisor. Confidential context never leaves the cluster — the supervisor enforces this. Anything routed to an external endpoint gets PII masking first — detection-and-redaction at the proxy. Even in-cluster inference enters through the AI Gateway, not directly to model endpoints. This means there is no "back door" to the inference pool.

The failure mode you need to monitor: PII masking is detection-and-redaction, so residual false-negative leakage is possible. You should have downstream monitoring for this.

---

### Slide 17: Defense in depth — three rings

This diagram from the article shows the three concentric defense rings and the four cross-cutting controls that apply to all of them.

Ring 1, the innermost: process-level isolation. Seccomp restricts system calls. Landlock restricts file and network access. Namespaces provide resource isolation. This is what OpenShell provides.

Ring 2: pod-level isolation. Pod Security Standards enforce a restricted profile. SELinux provides mandatory access control. NetworkPolicy restricts network access. Kata provides a dedicated micro-VM with its own kernel.

Ring 3: hardware-level isolation. Confidential Containers protect memory at the VM boundary. This is for the most sensitive workloads.

The four cross-cutting controls: workload identity (SPIFFE), tool authorization (MCP Gateway), inference guardrails (TrustyAI), and pre-production testing. These apply regardless of which rings you've enabled.

The reading rule: start from the outside and work in. Every ring you enable reduces the attack surface for the next ring.

---

### Slide 18: OpenShell + Kata — neither alone is sufficient

This is the honest-limitations slide, and it's one of the most important in the deck.

On the left: OpenShell provides application-layer isolation. It catches data exfiltration through its egress proxy — if the agent tries to POST secrets to an external endpoint, the proxy blocks it. It enforces per-binary, per-path, per-endpoint policy. But it CANNOT stop kernel exploits. OpenShell shares the kernel with the agent. If the agent exploits CVE-2026-31431, OpenShell is bypassed entirely. Worse — because OpenShell's own proxy and supervisor share the same kernel and page cache as the workload, a kernel-level exploit could potentially corrupt the enforcement mechanism itself.

On the right: Kata Containers provide VM-layer isolation. Each pod gets a dedicated micro-VM with its own kernel. virtiofs blocks page-cache attacks because it doesn't expose the host's page cache to the guest. The splice-based exploit has no valid target. Kata CONTAINS kernel exploits. But Kata CANNOT filter network traffic at the application level. curl is a normal userspace operation. Kata has no mechanism to inspect or block outbound data.

---

### Slide 19: Run both — dual protection

The answer is run both. OpenShell inside a Kata micro-VM. Application-layer policy AND kernel-level isolation.

OpenShell catches prompt injection exfiltration — the egress proxy blocks unauthorized network calls before they leave the pod. Kata contains kernel exploits — the dedicated VM with its own kernel means a page-cache attack affects only the agent's own VM, not the host or other tenants.

Neither alone is sufficient. We've proven this empirically — and I'll show you the benchmark results in a few slides.

The dual-protected pod is the only configuration we've tested that stops both attack classes. This is not a theoretical argument. It's an empirical result. The pod gets dual protection by specifying the Kata RuntimeClass and running inside an OpenShell sandbox. Same container image, same agent configuration, same model endpoint. The security layers are infrastructure concerns, not application changes.

---

### Slide 20: MCP Gateway — claims-based tool authorization

Decision 2: Tool Governance. The MCP Gateway fronts every MCP tool server behind a single MCP_URL.

Here's how it works. The agent presents its JWT — the one it got from the Auth Bridge, the one with its identity claims and tool entitlements. The MCP Gateway — which is Envoy with Kuadrant/Authorino as the authorization engine — checks the token's "tools" claim against the requested tool. If the tool is in the allowed set, the request passes through to the tool server. If not, it's denied.

The critical design decision: authorization is based on token claims, not on the prompt. The model's opinion about which tools it should call is irrelevant. The infrastructure decides.

The same claims-based check covers every tool backend equally: a CUDA service, an OR-Tools container, or a SaaS endpoint. MCP itself was donated to the Agentic AI Foundation under the Linux Foundation in late 2025. It's under neutral governance. The authorization model makes each tool server an OAuth 2.1 resource server — which is precisely the claims-checking this gateway enforces.

---

### Slide 21: Prompt injection fails at the infrastructure layer

Let me walk through a specific attack scenario.

The attack: an injected prompt forces the model to call /exfil, disguised as a compliance dashboard endpoint. The model dutifully makes the tool call because it can't distinguish legitimate instructions from injected ones.

The defense: the MCP Gateway receives the tool call request. It checks the JWT's tools claim. /exfil is not in the allowed set for this agent's identity. Request denied. HTTP 403. The model can try again — it will get 403 again. The authorization decision was made at the infrastructure layer.

This is the same principle as RBAC for Kubernetes API calls. kubectl can try to delete a namespace, but if the service account doesn't have that permission, it fails. The user's intent is irrelevant — the policy is the policy. We're applying the same principle to agent tool calls.

---

### Slide 22: What the gateway cannot stop

I want to be honest about limitations, because trust requires honesty.

The MCP Gateway cannot stop misuse of tools the agent IS entitled to call. If the agent is authorized to call a database query tool, and an injected prompt instructs it to query sensitive tables — the gateway will allow it, because the tool is in the allowed set.

That risk belongs to a different control. Inference guardrails — TrustyAI, NeMo Guardrails — can scan prompts and responses for sensitive data patterns. Egress policy can restrict which database schemas the agent's queries can touch. Output filtering can redact PII before it leaves the system.

The MCP Gateway is one control among several. It prevents unauthorized tool calls. It does not prevent misuse of authorized tools. The combination of all controls — gateway, guardrails, egress policy, identity — provides defense in depth.

---

### Slide 23: Three routing tiers

Decision 3: Inference Routing. This diagram from the article shows the three-tier routing architecture.

Tier 1 is the security tier — the sandbox egress router, which lives inside the supervisor in every agent pod. It answers: WHERE may this request go? Can it leave the cluster? Does it contain PII that needs masking? Is this a request that policy requires to stay on in-cluster models? The security team owns this tier. It changes slowly — policy updates, not code deploys.

Tier 2 is the cost tier — semantic routing. It answers: WHICH model should serve this request? A simple summarization task doesn't need a 405B parameter model. A complex reasoning task does. vLLM Semantic Router or the AI gateway makes this decision based on intent classification, complexity scoring, and cost constraints. FinOps owns this tier.

Tier 3 is the efficiency tier — llm-d Router with the Endpoint Picker. It answers: WHICH replica should serve this request? The one with warm KV cache hits, low queue depth, available GPU memory. Infrastructure SRE owns this tier. It changes constantly — millisecond decisions based on real-time telemetry.

---

### Slide 24: Three tiers, three owners

This table maps each tier to its component, its question, its decision inputs, and its owner.

The security tier uses the sandbox egress router built into the supervisor. Decision inputs: policy, PII detection, local-vs-cloud routing rules. Owner: security team.

The cost tier uses semantic routing — either vLLM's built-in Semantic Router or the AI gateway's routing rules. Decision inputs: intent classification, complexity scoring, cost constraints, reasoning requirements. Owner: FinOps or platform team.

The efficiency tier uses the llm-d Router with EPP extensions via Gateway API. Decision inputs: KV cache state, queue depth, prefill/decode ratio, GPU utilization. Owner: infrastructure SRE.

Collapsing these into one router puts one component in charge of three concerns with three different change cadences. The separation means each team can iterate independently.

---

### Slide 25: AI Gateway — the governed front door

This is a component Ramesh's team specifically asked about, so let me be precise.

The AI Gateway is the governed front door for ALL inference traffic. Its role is authentication, quota enforcement, and presenting a single OpenAI-compatible or OpenResponses API for all models behind it. Implementation options today are OGX, LiteLLM, or the Red Hat AI gateway.

The critical design decision: even in-cluster inference enters through the AI Gateway, not directly to vLLM workers. This means there is no way for an agent to bypass quota enforcement or authentication by going directly to a model endpoint. Every inference request — whether it originated from an in-cluster agent or was routed from an external source — goes through the same governed front door.

The gateway enforces per-agent quotas and rate limits from the same JWT claims used for tool governance. It also emits OpenTelemetry spans for every request — latency, token count, cost, model selection. This is how your FinOps team gets cost attribution per agent.

Semantic routing — Tier 2 — runs behind the AI Gateway. The classifier that picks the cheapest adequate model operates after authentication and quota checks have already passed.

---

### Slide 26: Internal vs External flows

This is the slide that matters most for financial services. The question your security team needs answered: does this data leave my cluster?

Internal flow: confidential context stays on in-cluster models. Traffic enters through the AI Gateway — the governed front door. Tier 2 picks the model, Tier 3 picks the replica. Full OpenTelemetry trace within the cluster. No PII masking needed because data stays within your trust boundary.

External flow: Tier 1 — the supervisor egress router — makes the decision. If the request contains confidential data, it stays internal, full stop. If it's low-risk and the policy allows external routing, PII detection-and-redaction runs at the proxy BEFORE any data exits the cluster. The masked request is then routed to the external LLM endpoint.

The failure mode you need to plan for: PII masking is detection-and-redaction, which means false negatives are possible. You should monitor for residual leakage downstream. The safest policy for regulated environments is to block external endpoints entirely for agents handling sensitive data.

For your architecture, this means you can run agents that handle customer data with a policy that says "all inference stays in-cluster" — and the supervisor enforces that at the network level, not at the application level.

---

### Slide 27: Three skill execution patterns

This table completes the routing picture by showing how agents actually execute skills — the compute-intensive work that agents dispatch.

Pattern 1: in-pod execution. Light work runs inside the sandbox. DataFrame transformations with cuDF, Polars, or DuckDB. The kernel enforces the policy — seccomp and Landlock constrain what the code can do.

Pattern 2: service call. The agent calls a separate serving pod via REST or MCP. Optimization with cuOpt or OR-Tools, RAG retrieval, embedding generation. The MCP Gateway and egress policy enforce authorization.

Pattern 3: job dispatch. The agent creates a Kubernetes Job or dispatches to Slurm. Physics simulation with JAX, quantum circuit evaluation with Qiskit, large-scale data processing. Scoped RBAC and admission control enforce what the agent can create. This pattern needs the most security attention — an agent that can create Jobs can create arbitrary workloads, so RBAC must be tightly scoped.

The design principle: skills are definitions and thin clients, not workloads. The agent pod stays resource-efficient — CPU-only, dense, long-lived. Expensive accelerators live in pooled backends. This means you can run hundreds of agent pods per node while the GPU pools serve all of them.

---

### Slide 28: SPIFFE identity — no more static keys

Decision 4: Identity. This is arguably the most important decision because every other control depends on it.

SPIFFE — Secure Production Identity Framework for Everyone — gives each agent an automatically rotated cryptographic identity. The identity is scoped to namespace and service account — it's a SPIFFE Verification Identity Document, a JWT-SVID.

Here's the flow. At pod startup, the SPIRE agent validates the pod's attestation — Kubernetes service account token, namespace, labels. It issues a JWT-SVID. The Auth Bridge sidecar exchanges this SVID for a short-lived access token — five minutes — via RFC 8693 token exchange or RFC 7523 client assertion. The token carries claims: subject, tools entitlement, models entitlement, expiration.

The agent never sees a static API key. There IS no static API key. If an attacker compromises the workspace via prompt injection, there's nothing durable to steal. The current token expires in minutes.

---

### Slide 29: Before vs After — static keys to cryptographic identity

Let me make this concrete with a before-and-after comparison.

Before: API keys live in environment variables. They're rotated quarterly — maybe. One key gives full access to all tools. A leaked prompt means a leaked key means game over. There's no per-agent granularity. And revoking a compromised key means redeploying everything that uses it.

After: cryptographic identity at the pod level. Auto-rotated, short-lived — five minutes. Per-agent tool entitlements encoded in token claims. A leaked workspace has nothing durable to steal. Per-agent, per-namespace granularity. And revoking a compromised agent is a single targeted operation — revoke one identity, affect nothing else.

The containment economics are dramatic. Revoking, throttling, or terminating a misbehaving agent goes from an incident-wide hunt to a single API call.

---

### Slide 30: Auth Bridge

This is the Auth Bridge — the component Ramesh's team asked about specifically. Let me walk through exactly what it does.

The Auth Bridge is an authentication sidecar that runs alongside the agent in every pod. Its job is to trade the SPIFFE identity for short-lived access tokens that the MCP Gateway and AI Gateway accept.

The flow: at pod startup, the SPIRE agent validates the pod's attestation — Kubernetes service account token, namespace, labels — and issues a JWT-SVID. The Auth Bridge takes this SVID and exchanges it with your identity provider — Keycloak, for example — using one of two standards-based mechanisms: RFC 8693 token exchange or RFC 7523 JWT bearer grant. The choice depends on your IdP's support for externally issued tokens.

The identity provider returns a short-lived access token with a five-minute TTL. This token carries claims: subject (who is this agent), tools (what MCP tools may it call), models (what inference endpoints may it use), expiration. This is the token that the MCP Gateway and AI Gateway check for every request.

The SVID itself never leaves the pod. The access token is what crosses the wire. And because it expires in five minutes, a stolen token has a very short window of usefulness.

Lifecycle tooling — Kagenti, planned for Red Hat AI — will inject the Auth Bridge sidecar at deploy time, with no agent code changes required. Today it's manual configuration.

---

### Slide 31: Honest gaps in identity

Let me be honest about what's not solved yet.

Identity chaining for Agent-as-a-Service is an open problem. When the agentic loop runs in a shared runtime like OGX, the per-agent identity survives only if the runtime propagates the caller's identity downstream through every tool call. SPIFFE doesn't address this natively. The IETF WIMSE working group — Workload Identity in Multi-System Environments — is defining the standards. It's active work, not production-ready.

Agent-specific injection is the other gap. Today, setting up SPIFFE, the Auth Bridge sidecar, and the policy bindings requires manual configuration per agent type. Kagenti is lifecycle tooling that will inject the sidecar and identity plumbing at deploy time — no code changes. It's in early development. Plan for it architecturally, but don't depend on it for your current deployment.

These are real gaps. We're including them because trust requires honesty about what works today versus what's coming.

---

### Slide 32: Loop placement trade-off matrix

Decision 5: Where does the agentic loop run? This is a deployment pattern decision, not a technology decision.

Agent-as-a-Workload: the loop ships inside the pod with the harness. The agent has its own SPIFFE identity, its own blast radius, its own sandbox. This is for long-running, autonomous workloads — field-service optimizers, research agents, CI/CD agents. Harness options: OpenClaw, LangGraph, custom implementations.

Agent-as-a-Service: the loop runs in a shared runtime — OGX, behind a Responses API. Centralized audit trail across all tenants. Credential isolation — clients never hold tool credentials, the runtime does. This is for request-scoped assistants and copilots. RHOAI 3.5 Early Access.

Duration and ownership pick the pattern. The same way you choose between a Deployment and a Knative service for traditional workloads.

---

### Slide 33: The patterns compose

Here's the insight that ties the loop placement decision together: the two patterns compose. They're not mutually exclusive.

A sandboxed agent pod — Agent-as-a-Workload — can delegate tool execution to a shared OGX loop — Agent-as-a-Service. The agent keeps its own identity and its own defense rings. The MCP Gateway preserves per-agent policy inside the shared runtime.

Start with Agent-as-a-Workload for your autonomous, long-running agents. Use Agent-as-a-Service for your request-scoped assistants and copilots. The same governance — identity plus tool authorization — works across both patterns.

This composability means you're not making a one-time architectural choice. You're choosing the right pattern per agent type, and the governance layer stays consistent.

---

### Slide 34: The supervisor pattern

This slide shows a concrete multi-agent deployment pattern that puts all five decisions together.

The supervisor pattern splits orchestration from execution. The brain — which could be Claude, or any orchestration layer — handles task decomposition, agent routing, and result synthesis. It never touches your data or your infrastructure. The workers are pods running on your OpenShift cluster, each inside its own OpenShell sandbox with its own per-agent network policy.

Look at the three sandboxes in this diagram. The metrics agent can reach Prometheus and vLLM — nothing else. The log agent can reach the log aggregator and vLLM — nothing else. The runbook agent gets vLLM and a read-only filesystem — no network access to live systems. Each policy is enforced at the kernel level with Landlock for filesystem, seccomp for syscalls, and L7 network rules scoped per binary.

Why does this matter? Consider the blast radius. If the log agent gets prompt-injected through a malicious log entry, the attacker can search logs — but cannot reach the Prometheus API, the runbook system, or any external endpoint. The blast radius is one agent's sandbox, not your entire monitoring stack.

The sandbox lifecycle is create, install dependencies, apply per-agent network policy, run, collect stdout, delete. When the agent finishes, its sandbox is destroyed. No state leaks between agents. No credentials persist. This is ephemeral isolation at the agent level, not just the pod level.

The key architectural insight: the brain decides WHAT to investigate, the sandboxed agents decide HOW. Reasoning stays on your cluster. Only summarized results cross back to the orchestration layer. Raw data — including customer PII in log entries — never leaves the sandbox.

This pattern makes sense when your workload touches multiple data sources with different sensitivity levels. Incident investigation, KYC onboarding, compliance reviews, CI/CD pipelines — anywhere a single agent would need access to more systems than it should.

---

### Slide 35: Benchmark results

Now let's prove this architecture works. This data comes from Eitan Geiger's published benchmark at Red Hat Developers, July 2026.

Same container image. Same AI coding agent — OpenCode. Same vLLM endpoint — Gemma4-31b. OpenShift 4.21. Three pod configurations: opencode-kata-only, opencode-openshell-only, opencode-dual.

Attack 1: Prompt injection exfiltration. We ran curl to an attacker-listener pod with the contents of /proc/self/environ — bypassing the LLM entirely to test OpenShell's value directly. Kata-only: DATA LEAKED. curl is normal userspace — Kata has no mechanism to filter it. OpenShell-only: BLOCKED. The egress proxy returned policy_denied because the attacker endpoint wasn't in the allowlist. Dual: BLOCKED.

Attack 2: CVE-2026-31431 container escape. The exploit uses AF_ALG sockets and splice() to get a page-cache write primitive. On runc with overlayfs, page cache is shared with the host — corruption escapes to other containers on the same node. Kata-only: CONTAINED. virtiofs doesn't expose the host's page cache to the guest — the exploit's write primitive has no valid target. OpenShell-only: HOST COMPROMISED. The exploit operates entirely within the kernel — seccomp can't block AF_ALG without breaking TLS. The verification pod read PWN!CT. Dual: CONTAINED.

Only the dual-protected pod stopped both attacks.

---

### Slide 36: Vendor gravity

Let me address the elephant in the room: vendor lock-in.

The architecture is interface-portable. Models sit behind OpenAI-compatible APIs — swap providers without changing client code. The sandbox uses stock Linux primitives — seccomp, Landlock, namespaces are not vendor-specific. vLLM runs on CUDA, ROCm, XPU, and CPU — it's not tied to one hardware vendor.

But some things are sticky. CUDA-X libraries — cuDF for DataFrames, cuOpt for optimization, PhysicsNeMo for simulation — these are NVIDIA-only. NIM containers are proprietary. If your agents depend on these skills, you have NVIDIA gravity.

The architecture controls the PRICE of the swap. Skill backends sit behind neutral REST or MCP interfaces. Replacing cuOpt with OR-Tools is an endpoint and policy change, not an architecture redesign. NVIDIA becomes a per-component choice rather than a structural dependency.

---

### Slide 37: The open architecture rule

I want to leave you with one sentence that captures the architectural philosophy.

"Every vendor component sits behind a neutral interface. OpenAI-compatible for models, MCP for tools, agent-sandbox API for isolation, SPIFFE for identity. Vendors compete on price/performance per component — procurement decisions stay reversible."

This is from the Red Hat Developers article published in July 2026. It's the design principle that makes this architecture open. Not open-source as a licensing term — open as an architectural property. You can swap any component without redesigning the system.

---

### Slide 38: Maturity map

Let's be precise about what's mature today versus what's emerging. Build your base decisions on the mature column. Adopt from the preview column behind pinned versions and feature gates.

Workload Identity: SPIFFE/SPIRE and JWT-SVID are production-grade. Agent-specific injection via Kagenti and identity chaining via IETF WIMSE are emerging.

Tool Governance: gateway patterns using Envoy and Kuadrant are production-grade. The MCP Gateway with claims-filtered tool catalogs is emerging.

Agent Sandbox: Kata and kernel primitives are production-grade. The agent-sandbox CRD from the SIG Apps working group is v1beta1. OpenShell is alpha.

Inference: vLLM, OpenAI-compatible APIs, and the llm-d Router are all GA and production-grade. Semantic routing is emerging.

Agentic Loop: client-side loops in harnesses are production-grade. OGX server-side loops are RHOAI 3.5 Early Access.

---

### Slide 39: Open items

I want to be transparent about what the blueprint does NOT solve yet.

Human approval patterns: when an agent wants to take a high-risk action, you need product-level human-in-the-loop patterns. The blueprint provides identity and audit trail, but the approval UX is application-specific.

Multi-agent coordination: A2A reached 1.0, but interoperability in practice is not settled.

Memory poisoning: corrupted tool results can corrupt the agent's memory across sessions.

Fleet-scale policy: writing sandbox policies for hundreds of agent types is complex.

Cost modeling: no established benchmarks for long-running agent workloads.

Confidential compute: protects memory at runtime but does nothing about prompt-layer compromise.

---

### Slide 40: Phased adoption

Here's a practical adoption path in four phases.

Phase 1, Foundations, weeks one through four: Deploy vLLM and llm-d for inference routing. Install SPIFFE/SPIRE for workload identity. These are the two highest-value, lowest-risk components.

Phase 2, Isolation, weeks three through six: Enable OpenShift Sandboxed Containers — that's Kata. Deploy OpenShell in alpha. Start with your most sensitive agent use case.

Phase 3, Governance, weeks five through eight: Stand up the MCP Gateway with claims-based authorization. Wire OpenTelemetry and MLflow for end-to-end observability.

Phase 4, Optimization, weeks eight through twelve: Add semantic routing for cost optimization. Evaluate OGX for request-scoped assistants.

---

### Slide 41: End-to-end walkthrough

Let me trace one request through the entire blueprint so you can see all the components working together.

A field-service agent receives a dispatch-optimization goal inside its sandboxed pod. The harness decomposes the goal into steps.

Step one: the agent calls the optimization skill. The MCP Gateway checks the token's tools claim — optimization is in the allowed set. The request passes through to the cuOpt backend.

Step two: the planning prompt carries customer data. Tier 1 — the supervisor egress router — detects PII and routes the request to in-cluster models. The data never leaves the cluster.

Step three: a follow-up summarization is low-risk. Tier 2 routes to a smaller, cheaper model through the AI Gateway. Tier 3 picks the replica with the warmest KV cache.

Every tool call, every authorization decision, every latency measurement, every cost metric lands in the OpenTelemetry and MLflow observability trail.

At no point does the architecture depend on the model performing predictably. Every control is infrastructure-level.

---

### Slide 42: Resources

Here are the resources to get started.

agent-school on GitHub — a 101-level NOC Assistant that runs offline on a laptop in two commands.

Red Hat AI — the enterprise platform for any model and any agent across the hybrid cloud.

Red Hat OpenShift AI — the MLOps platform with OGX, vLLM, and llm-d integration.

The blog series — Layered Sandboxing for AI agents by Eitan Geiger, Defense in Depth, Guardrails for OpenClaw Agents, and the benchmark data article.

The Red Hat Developers article — "Architect an Open Blueprint for Cloud-Native AI Agents" by Fatih Nar, Sally O'Malley, and Adel Zaalouk, July 2026.

---

### Slide 43: Closing

I want to leave you with this framing.

The agentic stack IS the microservices stack — one abstraction up.

Blueprints instead of Helm charts. Sandboxes instead of containers. Inference routing instead of service mesh. Skills instead of client libraries. Shared loop runtimes instead of application servers.

The same disciplines apply: least privilege, declarative policy, separate control and data planes, pooled expensive resources behind schedulers, and keeping the interfaces under your own control.

The difference: this workload makes its own decisions for days at a time. That's why identity, tool governance, and isolation are not optional — they're foundational.

Thank you. I'm happy to take questions.
