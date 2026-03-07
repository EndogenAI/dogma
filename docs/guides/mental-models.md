# Endogenic Development: Mental Models

> A guide to understanding endogenic development through nature's metaphors.

---

## Why Metaphors Matter

The endogenic methodology is built on precise principles and practices. But principles alone are abstract. **Metaphors make them tangible.**

This guide explains the three core nature metaphors used throughout the project: DNA (encoding and expression), seedlings (phased growth), and tree rings (recursive accumulation). These metaphors are not decoration — they reveal the structure and patterns that run through every level of the system.

---

## DNA: Encoding and Expression

### The Metaphor

Just as living organisms store their operational blueprint in DNA and express it through biochemical processes, endogenic systems encode operational knowledge in documented practices (scripts, agent files, guides) and express it through agent behavior.

DNA is:
- **Passed forward**: Each generation inherits DNA from all ancestors. Each session inherits scripts, guides, and conventions from all prior sessions.
- **Not static**: DNA can mutate and adapt. Similarly, principles can be refined, scripts improved, and conventions updated without breaking what came before.
- **The source of expression**: DNA does not build the organism directly — it provides instructions that cells read and act on. Agents do not invent behavior; they read encoded principles and conventions, then execute against them.
- **Replicated with fidelity**: DNA is copied accurately across cell divisions. Commits, documented conventions, and version control ensure that encoded knowledge is replicated accurately across sessions.

### What This Means in Practice

When you **encode a solution as a script** (instead of solving it interactively each time), you are updating the system's DNA. Future agents don't have to re-discover how to fetch sources or validate commits — they read the script (the DNA instruction) and execute it.

When you **document a convention in AGENTS.md**, you are writing genetic code. Agents read it and express that convention in their behavior.

When you **synthesize external knowledge** into scripts and guides, you are absorbing that knowledge into your DNA — making it permanent, heritable, and part of your operating system.

---

## Seedlings: Phased, Endogenic Growth

### The Metaphor

A seedling contains *everything it needs to grow* — the germinal tissue, stored nutrients, growth instructions. But it cannot grow without the right *environment*: soil, moisture, light, temperature within certain bounds.

Similarly, an endogenic project starts from a seed — the initial axioms, scripts, and documented conventions. It grows through phases, each of which requires the right conditions.

Seedlings exhibit:
- **Inherent structure**: A seedling knows who it is. It will grow into an oak, not a maple. Agents know what they are because of AGENTS.md and the documented fleet structure.
- **Environmental sensitivity**: Soil quality, water availability, and light angle all affect how the seedling grows. Likewise, the human's oversight, the quality of research inputs, and project-specific constraints all affect how the system evolves.
- **Phased unfolding**: Seedlings do not become full trees overnight. They go through germination, shoot emergence, leaf unfurling, branching. Endogenic projects go through phases: Orient → Frame → Scout → Synthesize → Review → Archive. Each phase has conditions that must be met before advancing.
- **Vulnerability in early stages**: Young seedlings are fragile; harsh conditions can stunt or kill them. Early sessions are similarly fragile — the agent fleet is new, conventions are being established, the substrate is thin. This is why gates exist: to protect early growth.

### What This Means in Practice

When you **define a research workflow with gates**, you are creating the conditions for healthy growth. The Orient phase establishes the right soil; the Frame phase ensures the seed knows which direction to grow; the Scout phase provides nutrient-rich water; the Synthesize phase lets the shoot emerge.

When you **run an agent through a documented workflow**, you are not over-controlling the system. You are providing the environmental conditions it needs to grow correctly.

---

## Tree Rings: Recursive Encoding of Knowledge

### The Metaphor

A tree ring is a complete annual record of growth: wood laid down in spring (rapid growth), wood laid down in summer/fall (slower growth, denser). The thickness and density of the ring tells a story — was it a good year (thick ring) or a harsh year (thin ring)?

Tree rings are:
- **Cumulative, not replacing**: A tree doesn't discard last year's ring to make room for next year's. New growth builds on the old ring. The tree gets stronger, wider, and taller with each year.
- **Visible history**: Cut a tree and you can see its biography in cross-section. Running `git log` on your project should tell a similar story: which sessions were productive, which focused on docs, which shipped features.
- **Progressive surface area**: With each ring, the tree's circumference (surface area) expands. With each session, the agent fleet expands its capability surface.
- **Load-bearing**: The tree is strong not because of this year's ring alone, but because of all its rings. The organism is stronger because all that prior growth is still there, supporting new growth on top.
- **Datable and archivable**: Dendrochronology (tree-ring dating) is an entire field. Git commit history serves the same function: you can date decisions, trace their consequences, and understand the evolution of the system.

### What This Means in Practice

When you **commit incrementally** (not one giant commit at the end of the session), you are creating readable tree rings. Each commit is a dated, complete unit of work. Future sessions can see what changed, why, and when.

When you **archive session scratchpads** into the `.tmp/_index.md`, you are creating a chronological record. This is your tree-ring archive.

When you **add a new script, new agent, or new guide**, you are adding a visible ring of growth. The project gets wider (more capability) and stronger (more encoded knowledge).

When you **run a research session and commit the results**, that session is a tree ring. Thick rings are productive sessions with many commits. Thin rings are focused sessions. The pattern of rings over time tells the story of the project's evolution.

---

## How the Three Metaphors Interlock

| DNA | Seedlings | Tree Rings |
|-----|-----------|-----------|
| **Encoding** the knowledge system works with | **Growing phased**ly according to documented workflow | **Accumulating** that knowledge into durable layers |
| Instructions read and executed | Conditions that enable right execution | Historical record of what accumulated |
| Replicated with fidelity | Sensitive to environment | Visible in version control |
| What agents *know* | What agents *do* | What agents have *achieved* |

### Example: A Research Session as All Three Metaphors

1. **DNA aspect**: The session reads the research workflow DNA (Outline → Frame → Scout → Synthesize → Review → Archive) encoded in `docs/guides/workflows.md`. This is genetic instruction.

2. **Seedling aspect**: The session unfolds through phases. Each phase has conditions (gates) that must be met. Scout phase requires 3-5 sources; Synthesize phase requires isolated invocations. These conditions are the soil, water, and light that let the seedling unfold correctly.

3. **Tree ring aspect**: Each session leaves a dated layer of artifacts (commits, scratchpad entries, archived research). When you run `git log` or read `.tmp/_index.md`, you see the rings. The system is stronger because all those prior sessions are still there.

---

## Why Nature Metaphors?

Endogenous development is young. Naming its core concepts with metaphors from nature serves several purposes:

1. **Universality**: Everyone understands growth, DNA, and tree rings. They're not dependent on any particular technology or framework.

2. **Intuition**: When a new contributor reads "tree rings," they immediately understand the image without needing lengthy explanation. DNA carries meaning about heredity and instruction.

3. **Humility**: Treating the endogenic system as analogous to living systems (not superior to them) grounds the work in billions of years of proven principles. We're not inventing new patterns — we're recognizing patterns that evolution has already validated.

4. **Coherence**: DNA, seedlings, and tree rings come from the same domain (biology). Using a coherent set of metaphors — rather than ad-hoc comparisons — creates deeper understanding.

---

## Next Steps

As you work with endogenic projects, use these metaphors as diagnostic tools:

- **"Is this encoding (DNA)?"** — Am I documenting this decision so future sessions can read and execute it? Or will the next agent have to re-discover it?
- **"Are the growth conditions (seedling environment) right?"** — Does this session have the gates, research frame, and documented workflow it needs?
- **"Is this a visible ring (tree growth)?"** — Will this work be datable and readable in git history? Or will it disappear into ephemeral chat?

When you see violations, ask: *Which metaphor is being ignored?*

---

*This guide is itself a growing artifact. Metaphors deepen as the system evolves. If you discover a better way to explain a concept, or a new metaphor that illuminates endogenic practice, add it.*
