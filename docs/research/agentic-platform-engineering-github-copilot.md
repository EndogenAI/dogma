---
title: "Agentic Platform Engineering with GitHub Copilot"
status: Final
closes_issue: 433
x-governs:
  - endogenous-first
  - algorithms-before-tokens
created: 2026-03-24
sources:
  - url: "https://devblogs.microsoft.com/all-things-azure/agentic-platform-engineering-with-github-copilot/"
    title: "Agentic Platform Engineering with GitHub Copilot"
    type: blog_post
recommendations:
  - id: rec-agentic-platform-engineering-github-copilot-001
    title: "ADOPT Crawl-Walk-Run agent rollout as canonical external validation of dogma's L0–L3 framework"
    status: deferred
    effort: Low
    linked_issue: null
    decision_ref: null
  - id: rec-agentic-platform-engineering-github-copilot-002
    title: "DOCUMENT Cluster Doctor pattern as external reference for dogma's agent-file-authoring conventions"
    status: deferred
    effort: Low
    linked_issue: null
    decision_ref: null
  - id: rec-agentic-platform-engineering-github-copilot-003
    title: "EXTEND MCP integration guidance in AGENTS.md to reference AKS MCP server as external implementation model"
    status: deferred
    effort: Medium
    linked_issue: null
    decision_ref: null
---

# Agentic Platform Engineering with GitHub Copilot

## 1. Executive Summary

Microsoft Azure Global Black Belts Diego Casati and Ray Kao present a three-act framework for evolving platform engineering through AI agents — naming it "agentic platform engineering." The research question is: *How does this external three-act framework align with or validate dogma's agent fleet architecture, MCP server design, and L0–L3 maturity model?*

**Key findings**:
1. **Convergent L0–L3 mapping** — The article's crawl-walk-run / three-act progression maps directly to dogma's L0–L3 framework: Act 1 (knowledge encoding) = L1–L2; Act 2 (CI enforcement) = L2–L3; Act 3 (autonomous agents) = L3. This convergence from an independent Microsoft team strengthens confidence in the maturity model.
2. **Agent-file pattern validation** — The Cluster Doctor is defined in a single `cluster-doctor.agent.md` file with persona, workflow, and safety constraints — identical to dogma's `.agent.md` authoring conventions. An independent production team reached the same structural solution.
3. **MCP as integration layer** — The article validates MCP servers as the preferred wiring between GitHub Copilot agents and external systems (AKS clusters, Microsoft Foundry models), confirming dogma's existing `mcp_server/` investment.
4. **Human-in-the-loop enforcement** — All three acts maintain human approval authority; agents propose and diagnose, humans decide. This mirrors dogma's [MANIFESTO.md § Foundational Principle: Augmentive Partnership](../../MANIFESTO.md#foundational-principle-augmentive-partnership).

**Verdict**: Strong external validation. All three dogma axioms ([MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first), [MANIFESTO.md § 2 Algorithms-Before-Tokens](../../MANIFESTO.md#2-algorithms-before-tokens)) are enacted in the Microsoft reference implementation, independently and at production scale.

**Recommendation**: **ADOPT** crawl-walk-run framing as canonical external reference in guides; **DOCUMENT** Cluster Doctor as external model for agent-file authoring; **EXTEND** MCP guidance with AKS MCP as implementation reference.

---

## 2. Hypothesis Validation

| Hypothesis | Result | Evidence |
|------------|--------|----------|
| **H1**: The three-act framework maps to dogma's L0–L3 maturity levels | ✅ **STRONGLY SUPPORTED** | Act 1 (ask Copilot, encode knowledge in repos) = L1–L2 individual standardization; Act 2 (CI enforcement, rule files) = L2–L3 org-wide enforcement; Act 3 (autonomous agent loop) = L3 policy enforcement. The progression is structurally identical. |
| **H2**: The Microsoft agent-file pattern will match dogma's `.agent.md` conventions | ✅ **SUPPORTED** | `cluster-doctor.agent.md` has a persona section ("senior Kubernetes administrator and SRE"), a systematic diagnostic workflow section, and explicit safety constraints — the same three-part structure dogma's BDI (`Beliefs & Context`, `Workflow & Intentions`, `Desired Outcomes`) enforces. |
| **H3**: MCP servers are the external integration pattern adopted by production teams | ✅ **STRONGLY SUPPORTED** | Act 3 wires GitHub Copilot to an AKS MCP server deployed inside the cluster, exposing `kubectl` and eBPF diagnostics without embedding credentials in CI workflows. This is the same pattern dogma's `mcp_server/dogma_server.py` implements for governance tools. |
| **H4**: Human approval is maintained at every act boundary | ✅ **SUPPORTED** | Crawl: Copilot suggests, engineer approves. Walk: label triggers agent, human reviews PR. Run: agent opens PR, human merges. No act removes human approval authority — consistent with dogma's Augmentive Partnership constraint. |

---

## 3. Pattern Catalog

### Pattern 1: Knowledge Encoding via Repository-Grounded Copilot (Act 1)

**Problem**: Tribal platform knowledge lives in people's heads, not scale, and walks out the door when engineers leave. Documentation drifts from reality within months.

**Solution**: Encode knowledge directly into the repository — infrastructure definitions, service catalog, conventions — and expose it via GitHub Copilot conversation. The platform becomes the "experienced colleague who's always available."

**Canonical example**: Brownfield infrastructure reverse-engineering. An AI assistant examines an Azure resource group deployed manually without IaC, catalogs the deployed services, and generates the Terraform/Bicep templates that should have been written first. Knowledge that existed only in the deployed state is promoted into versioned, queryable form.

**Dogma mapping**: This is [MANIFESTO.md § 1 Endogenous-First](../../MANIFESTO.md#1-endogenous-first) applied to platform engineering: scaffold from existing system knowledge before reaching outward. The repository is the endogenous source.

---

### Pattern 2: CI-Driven Adaptive Enforcement (Act 2)

**Problem**: Compliance rules encoded in static linting scripts become stale and require pipeline changes when rules evolve. Manual review processes are brittle — people forget, copy-paste from Stack Overflow, or unknowingly violate policy.

**Solution**: GitHub Actions trigger on every push and run GitHub Copilot with a standardized `.prompt.md` file that specifies exactly what to check. Rules live in Markdown files commited to the repo — updating rules means editing a file, not rewriting a pipeline.

**Canonical example**: Documentation generation workflow. A `.github/workflows/copilot.generate-docs.yml` runs GitHub Copilot CLI on every push; `aks-check-pods.prompt.md` and `aks-remediation.prompt.md` provide the diagnostic and remediation steps. When new compliance requirements arrive, they are added to the prompt file — no pipeline change required.

**Anti-pattern**: Static linting rules (`if`-statement based) that require pipeline modifications whenever organizational standards change. These bottleneck on engineering time and accumulate drift as standards evolve faster than the pipeline can be updated. The article explicitly contrasts this with the adaptive prompt-based approach.

**Dogma mapping**: This is [MANIFESTO.md § 2 Algorithms-Before-Tokens](../../MANIFESTO.md#2-algorithms-before-tokens) — the rule structure is encoded algorithmically in a prompt file, not re-derived interactively each time. It also enacts dogma's Programmatic-First principle: the third time you check something manually, encode it as a script (here: a reusable `.prompt.md`).

---

### Pattern 3: Event-Driven Autonomous Agent Loop (Act 3 — Cluster Doctor)

**Problem**: Platform engineers spend time firefighting Kubernetes failures rather than improving the platform. Diagnostic expertise doesn't scale — runbooks are static and don't map to every failure scenario.

**Solution**: Argo CD detects deployment failures → fires webhook to GitHub Actions → creates a structured GitHub issue with cluster context and labels → Copilot agent picks up the issue → authenticates to Azure via Workload Identity Federation → runs `kubectl` and queries the AKS MCP server → opens a PR with proposed fix. Human reviews and merges.

**Canonical example**: Cluster Doctor workflow sequence:
1. Argo CD Notifications shapes failure into a webhook payload (cluster name, resource group, failure reason, suggested diagnostic commands)
2. `argocd-deployment-failure.yml` creates or updates a GitHub issue with deduplication (if an issue already exists for this app, it adds a comment instead)
3. `copilot.trigger-cluster-doctor.yml` fires on `cluster-doctor` label, invokes the agent
4. Agent authenticates, runs diagnostics (including eBPF via Inspektor Gadget), and opens a remediation PR
5. Human engineer reviews and approves — the agent does the detective work; the human makes the call

**Anti-pattern**: Manually triggered runbooks that require a human to connect to the cluster, run a predefined sequence of `kubectl` commands, and consult static documentation. The runbook cannot adapt to the specific failure in front of it — DNS issues, latency spikes, and config drift each require different investigation paths that a static runbook either covers exhaustively (long) or misses (dangerous).

**Dogma mapping**: The crawl-walk-run progression (crawl: prompt engineering in repo; walk: wire into ops workflow with human trigger; run: remove human trigger, full automation with human approval) is the Cluster Doctor instantiation of the L0–L3 maturity ladder directly encoding dogma's incremental adoption principle.

---

### Pattern 4: MCP Server as Credentials-Safe External API Surface

**Problem**: Giving agents direct API credentials to Kubernetes clusters or cloud APIs is a security anti-pattern. Embedding cluster credentials in GitHub Actions workflows exposes them in CI logs.

**Solution**: Deploy an MCP server inside the cluster (authenticated via Workload Identity Federation, not stored credentials). Configure GitHub Copilot's `.copilot/mcp-config.json` to point to both the GitHub MCP server (for issue/PR operations) and the cluster-internal AKS MCP server (for `kubectl` and diagnostics). The cluster embeds its own identity metadata in an Argo CD config map — the agent discovers where to look without hardcoded configuration.

**Anti-pattern**: Storing `KUBECONFIG` or service account tokens as GitHub Actions secrets and exposing them to every CI workflow. This grants overly broad cluster access to the entire GitHub Actions runner context rather than scoping access through a purpose-built MCP server with controlled tool surface.

---

## 4. Recommendations

1. **ADOPT crawl-walk-run as canonical external L0–L3 reference** (Rec 1): Add a "Canonical external example" callout to `docs/research/ramp-l0l3-framework.md` citing this article's three-act framework as independent external validation. The two frameworks are structurally isomorphic — citing one from the other strengthens the evidence base for both.

2. **DOCUMENT Cluster Doctor as external agent-file reference** (Rec 2): Add a reference to `cluster-doctor.agent.md` from `microsoftgbb/agentic-platform-engineering` in `.github/skills/agent-file-authoring/SKILL.md` as an external production example of the persona + workflow + safety-constraints structure dogma enforces. Helps future contributors see the pattern used in a real production context.

3. **EXTEND MCP guidance with AKS MCP as implementation reference** (Rec 3): The `mcp_server/README.md` currently describes only dogma's internal governance server. Add a "See also: external implementations" section pointing to the AKS MCP server pattern (deployed inside a cluster, exposed via Workload Identity Federation) as an example of the same architectural pattern scaled to production infrastructure tooling.

---

## 5. References

1. **Casati, Diego; Kao, Ray** (2026-03-24). "Agentic Platform Engineering with GitHub Copilot." *Microsoft All Things Azure Blog*. Retrieved 2026-03-24. https://devblogs.microsoft.com/all-things-azure/agentic-platform-engineering-with-github-copilot/

2. **microsoftgbb/agentic-platform-engineering** (GitHub repository). Three-act reference implementation — Act 1 (knowledge encoding), Act 2 (CI enforcement), Act 3 (Cluster Doctor). https://github.com/microsoftgbb/agentic-platform-engineering

3. **dogma MANIFESTO.md § 1 Endogenous-First** — foundational axiom for repository-grounded knowledge encoding. [../../MANIFESTO.md](../../MANIFESTO.md#1-endogenous-first)

4. **dogma AGENTS.md § Agent Fleet Maturity (L0–L3)** — maturity progression framework validated by the three-act model. [../../AGENTS.md](../../AGENTS.md#agent-fleet-maturity)

5. **dogma AGENTS.md § MCP Toolset** — internal MCP server configuration and governance tools. [../../AGENTS.md](../../AGENTS.md#mcp-toolset)
