| Agent | Description | Posture | Capabilities | Handoffs |
|-------|-------------|---------|--------------|----------|
| A5 Context Architect | Evaluate context governance options — AFS context layers, semantic memory isolation, and scratchpad vs repo-memory tradeoffs — and design context layering conventions. | readonly | evaluate-context, afs-context, semantic-memory, scratchpad-repo-memory, design-context | Research Reviewer, Executive Orchestrator, Executive Docs |
| B5 Dependency Auditor | Audit uv.lock and pyproject.toml for known CVEs, outdated packages, and version conflicts; output a structured compatibility report. | readonly | audit, lock-pyproject, toml-known, outdated-packages, version-conflicts | Executive Scripter, Security Researcher, Executive Orchestrator |
| CI Monitor | Watch CI run history for recurring failure patterns, triage flaky tests, identify slow steps, and surface actionable fix suggestions for the GitHub Actions pipeline. | full | watch-run, triage-flaky, identify-slow, surface-actionable | Executive Scripter, Executive Automator, Executive Orchestrator |
| Community Pulse | Aggregate GitHub community health signals — Stars, issue response time, PR velocity, contributor retention — and produce periodic health reports for project maintainers. | full | aggregate-github, stars, issue-response, velocity, contributor-retention | Executive PM, DevRel Strategist, Executive Orchestrator |
| D4 Methodology Enforcer | Validate proposed changes against MANIFESTO.md axioms — flag over-interactivity, unnecessary token burn, and Programmatic-First violations. | readonly | validate-proposed, axioms, flag-over-interactivity, unnecessary-token, programmatic-first-violations | Executive Scripter, Executive Docs, Executive Orchestrator |
| D5 Knowledge Base | Manage docs/research/OPEN_RESEARCH.md as a living queue — track status, retire completed items, and propose new seed questions from synthesis gaps. | creator | manage-docs, living-queue, track-status, retire-completed, propose-new | Executive Researcher, Executive PM, Executive Orchestrator |
| Deep Research | > | full |  | Deep Research, Research Scout, Research Synthesizer, Research Reviewer, Research Archivist |
| DevRel Strategist | Plan developer relations content — blog cadence, tutorial pipeline, Discussions announcements, and DevEx narrative for an agent-first open-source project. | creator | plan-developer, blog-cadence, tutorial-pipeline, discussions-announcements, devex-narrative | Executive Docs, Executive PM, Executive Orchestrator |
| Docs Linter | Audit docs/research/ for D4 heading gaps, dead source stubs, missing frontmatter, and validate_synthesis compliance. Advisory-only; never edits docs directly. | readonly | audit-docs, dead-source, missing-frontmatter, validate-synthesis, advisory-only | Executive Docs, Review |
| Env Validator | Audit Python environment consistency across .python-version, uv.lock, pyproject.toml, and CI matrix — flag compatibility drift and suggest remediation. | readonly | audit-python, python-version, lock, pyproject, toml | Executive Scripter, Executive Orchestrator |
| Executive Automator | Design and implement non-agent automation — file watchers, pre-commit hooks, CI tasks, and VS Code task definitions. First escalation point for anything that should run without an agent. | full | design-implement, file-watchers, pre-commit-hooks, tasks, code-task | Review, GitHub, Executive Scripter |
| Executive Docs | Maintain and evolve all project documentation — encoding dogmatic values, guiding axioms, and methodology across every documentation layer. | creator | maintain-evolve, encoding-dogmatic, guiding-axioms, methodology-across | Review, GitHub, Executive Researcher |
| Executive Fleet | Manage the agent fleet — create, audit, update, and deprecate .agent.md files and fleet documentation to maintain standards compliance. | full | manage-agent, create, audit, update, deprecate | Executive Fleet, Review, GitHub, Executive Docs |
| Executive Orchestrator | Coordinate multi-workflow sessions spanning research, docs, scripting, and fleet changes — sequence executive agents and maintain session coherence. | full | coordinate-multi-workflow, docs, scripting, fleet-changes, sequence-executive |  |
| Executive Planner | Decompose complex multi-step requests into structured plans with phases, gates, agent assignments, and dependency ordering before any execution begins. | readonly | decompose-complex, gates, agent-assignments, dependency-ordering | Executive Orchestrator |
| Executive PM | Maintain the health of the repository as an open-source resource — issues, labels, milestones, changelog, contributing docs, and community standards. | full | maintain-health, issues, labels, milestones, changelog | Executive PM, Review, GitHub, Executive Docs, Executive Orchestrator |
| Executive Researcher | Orchestrate research sessions end-to-end — delegate to the research fleet, synthesize outputs, and spawn new area-specific research agents as needed. | full | orchestrate-research, delegate-research, synthesize-outputs, spawn-new | Executive Researcher, Research Scout, Research Synthesizer, Research Reviewer, Research Archivist, Executive Scripter, Executive Docs, Review |
| Executive Scripter | Identify repeated interactive tasks and encode them as committed scripts. Audit scripts/ for gaps, propose new scripts, and extend existing ones — enforcing the programmatic-first principle. | full | identify-repeated, audit-scripts, propose-new, extend-existing, enforcing-programmatic-first | Review, GitHub, Executive Automator |
| GitHub | Commit approved changes to the current branch following Conventional Commits. The final step in every agent workflow before human review. | full | commit-approved, final-step | Review |
| Issue Triage | First-pass triage on new issues — suggest labels, priority, effort; flag duplicates; draft clarifying comments. Does not close or merge without human confirmation. | full | first-pass-triage, suggest-labels, priority, effort, flag-duplicates | Executive PM, Executive Orchestrator |
| LLM Cost Optimizer | Build and maintain a model selection decision table (capability × cost × latency) and recommend model tiers per task type to minimize token spend. | creator | build-maintain, build | Executive Docs, Executive Orchestrator |
| Local Compute Scout | Survey local inference stacks (Ollama, LM Studio, llama.cpp), benchmark models, document hardware prereqs, and maintain a local model registry for this project. | creator | survey-local, studio, llama, cpp, benchmark-models | Research Synthesizer, Executive Researcher, Executive Scripter, Review |
| MCP Architect | Design locally-distributed MCP framework topologies, evaluate server composition patterns, and define MCP deployment conventions for this project. | creator | design-locally-distributed, evaluate-server, define-mcp | Research Synthesizer, Executive Scripter, Local Compute Scout, Review, Executive Researcher |
| Release Manager | Orchestrate versioning, CHANGELOG entries, and GitHub Releases — manage SemVer decisions, tag commits, and ensure every release has a correlated milestone. | full | orchestrate-versioning, changelog-entries, github-releases, manage-semver, tag-commits | Review, GitHub, Executive PM, Executive Orchestrator |
| Research Archivist | Finalise reviewed research drafts — update status, commit to docs/research/, and close the corresponding GitHub issue. | full | finalise-reviewed, update-status, commit-docs, close-corresponding | Review, Executive Researcher |
| Research Reviewer | Validate research synthesis drafts against endogenic methodology standards — flag gaps, unsupported claims, and contradictions before archiving. | readonly | validate-research, flag-gaps, unsupported-claims, contradictions-archiving | Executive Researcher |
| Research Scout | Survey the web and local sources for a given research topic. Catalogue raw findings in the session scratchpad — do not synthesize. | readonly | survey-web, catalogue-raw, synthesize | Executive Researcher |
| Research Synthesizer | Transform raw Scout findings into structured, opinionated synthesis documents in docs/research/ following the expansion→contraction pattern. | creator | transform-raw, opinionated-synthesis | Executive Researcher |
| Review | Review changed files against AGENTS.md constraints and project standards before any commit. Read-only — flags issues and returns control to the originating agent. | readonly | review-changed, constraints-project, read-only, flags-issues | GitHub, Executive Researcher |
| Security Researcher | Threat-model agentic workflows and identify attack surfaces — survey OWASP, evaluate CIA-triad exposure in agent designs, and produce security synthesis docs. | creator | threat-model-agentic, survey-owasp, evaluate-cia-triad, produce-security | Research Synthesizer, Research Reviewer, Executive Researcher, Executive Docs, Review |
| Test Coordinator | Map pytest markers to CI phases, identify untested scripts, and recommend which tests gate which PR merge stage to keep the test suite fast and meaningful. | readonly | map-pytest, identify-untested, recommend-which | Executive Scripter, Executive Orchestrator |
| User Researcher | Synthesize closed GitHub issues, PRs, and Discussions into JTBD summaries and friction reports for quarterly OSS user research. | full | synthesize-closed, prs, discussions-jtbd | Review, GitHub, Executive PM |
| Values Researcher | Investigate verbally encoding values in agent instructions — survey philosophy-of-language, alignment literature, and prior art to ground endogenic axiom authoring. | creator | investigate-verbally, survey-philosophy-of-language, alignment-literature, prior-art | Research Synthesizer, Executive Docs, Review, Executive Researcher |

## Cross-Reference Density

| Agent | cross_ref_density |
|-------|-------------------|
| A5 Context Architect | 12 |
| B5 Dependency Auditor | 3 |
| CI Monitor | 1 |
| Community Pulse | 1 |
| D4 Methodology Enforcer | 22 |
| D5 Knowledge Base | 4 |
| Deep Research | 5 |
| DevRel Strategist | 5 |
| Docs Linter | 3 |
| Env Validator | 1 |
| Executive Automator | 3 |
| Executive Docs | 16 |
| Executive Fleet | 7 |
| Executive Orchestrator | 9 |
| Executive Planner | 7 |
| Executive PM | 11 |
| Executive Researcher | 7 |
| Executive Scripter | 3 |
| GitHub | 2 |
| Issue Triage | 2 |
| LLM Cost Optimizer | 5 |
| Local Compute Scout | 3 |
| MCP Architect | 3 |
| Release Manager | 2 |
| Research Archivist | 2 |
| Research Reviewer | 5 |
| Research Scout | 1 |
| Research Synthesizer | 2 |
| Review | 9 |
| Security Researcher | 5 |
| Test Coordinator | 2 |
| User Researcher | 1 |
| Values Researcher | 13 |
| **Fleet average** | **5.36** |
