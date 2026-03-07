# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project does not yet use semantic versioning — entries are date-grouped until a v1.0 tag is established.

---

## [Unreleased]

### Added

- Research sprint deliverables: testing tools & frameworks, dev workflow automations, OSS documentation best practices, PM & team structures (issues #16–#19)
- Research seed deliverables: product research & design methodologies, comms/marketing/bizdev (issues #20–#21)
- `validate_synthesis.py` — D4 validation gate for research synthesis documents
- `migrate_agent_xml.py` — batch XML-format migration for agent instruction files
- `scaffold_agent.py` — scaffold new agent files from template
- `scaffold_workplan.py` — scaffold structured workplan docs
- `pr_review_reply.py` — generalized PR review reply and resolve script
- Scratchpad isolation pattern: branch-slug subdirectories under `.tmp/`
- Comprehensive pytest suite with CI/CD gating (`tests/`)
- Heredoc guardrail encoded in all `AGENTS.md` files
- This `CHANGELOG.md`

### Changed

- All executive agent files updated with research-derived recommendations
- `docs/guides/testing.md` updated with testing research R1–R6
- `docs/guides/workflows.md` PM workflow section updated
- `CONTRIBUTING.md` expanded with dev-env setup and idempotency checklist

---

## [Earlier work — 2026-03-06]

### Added

- Initial agent fleet: 14 agents across executive, research, and utility tiers
- `docs/guides/` — workflows, agents, session management, programmatic-first, local compute, testing, mental models guides
- `docs/research/` — agent fleet design patterns, agentic research flows, XML agent instruction format
- `scripts/` — prune_scratchpad, watch_scratchpad, fetch_source, fetch_all_sources, generate_agent_manifest, link_source_stubs
- `MANIFESTO.md`, `AGENTS.md`, `CONTRIBUTING.md`, `README.md`
- `docs/plans/` — workplan files for agent fleet design, formalize workflows, implement research findings, XML agent instruction format, research expansion sprint
- GitHub issue templates and PR template
