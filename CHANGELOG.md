## [0.12.2](https://github.com/EndogenAI/dogma/compare/v0.12.1...v0.12.2) (2026-03-18)


### Bug Fixes

* **scripts:** address Copilot PR [#384](https://github.com/EndogenAI/dogma/issues/384) review — fleet integration robustness and doc accuracy ([899979e](https://github.com/EndogenAI/dogma/commit/899979efdb6280900c8477eb9c3c2717468b7c5f))



## [0.12.1](https://github.com/EndogenAI/dogma/compare/v0.12.0...v0.12.1) (2026-03-18)


### Reverts

* **agents:** revert Review agent MCP tool additions ([2cdd713](https://github.com/EndogenAI/dogma/commit/2cdd713fac2406c69f1353d4836f68cf5be7deb1))



# [0.12.0](https://github.com/EndogenAI/dogma/compare/v0.11.0...v0.12.0) (2026-03-18)


### Features

* **agents:** wire Review agent to MCP tools for read-only verification ([a09746c](https://github.com/EndogenAI/dogma/commit/a09746c90dd4de765ba97fc4d00eeaedd44edbc5))



# [0.11.0](https://github.com/EndogenAI/dogma/compare/v0.10.0...v0.11.0) (2026-03-18)


### Bug Fixes

* **docs,scripts:** address PR [#330](https://github.com/EndogenAI/dogma/issues/330) Copilot review comments ([bdcf671](https://github.com/EndogenAI/dogma/commit/bdcf671081931d2ee71bda4f6339dbf0cbedfd6c))
* **docs:** reconcile contradictory acceptance criteria status ([b0fe6ba](https://github.com/EndogenAI/dogma/commit/b0fe6ba0aae2fee67e551266dd179b46e0b38607))
* **docs:** typo in research doc source reference ([e233799](https://github.com/EndogenAI/dogma/commit/e233799d855e7de5d4d4d04e6682954ebffaafbd))
* **integration:** correct rate-limit threshold & anchor link ([c54a34e](https://github.com/EndogenAI/dogma/commit/c54a34e84078263265b152de3210b5f6a4490f0b))
* **scripts:** circuit-breaker decision alignment ([fb90681](https://github.com/EndogenAI/dogma/commit/fb90681cfd38c764c0bea11739db38eb9a640ba4))
* **scripts:** fallback provider loading ([2d9afd3](https://github.com/EndogenAI/dogma/commit/2d9afd38e5b4781a9aa82ac27612ad48fc38fe33))
* **scripts:** fix detect_rate_limit sleep policy — policy clamp at budget exhaustion ([1b74d17](https://github.com/EndogenAI/dogma/commit/1b74d178328ef4a7b4ee5f635b1658f8dd1c770f))
* **scripts:** remove non-functional --dry-run flag ([5e2f8d5](https://github.com/EndogenAI/dogma/commit/5e2f8d51e890ad19185ffebb5ed49aa9a94df572))
* **scripts:** resolve ruff lint failures for CI — import sort, W293, E501, F401, budget boundary ([ffe2770](https://github.com/EndogenAI/dogma/commit/ffe2770d32753fda46da79b821a13fbea1787a37))
* **tests:** audit log isolation + unused imports + boundary assertions ([94b9d69](https://github.com/EndogenAI/dogma/commit/94b9d69c808b391a9f216423b40c86451f4793af))


### Features

* **scripts:** implement Phase 0 rate-limit resilience foundation ([88b55c0](https://github.com/EndogenAI/dogma/commit/88b55c015e0a51046c20ef8a20489259e2689ef7)), closes [#322](https://github.com/EndogenAI/dogma/issues/322) [#323](https://github.com/EndogenAI/dogma/issues/323) [#325](https://github.com/EndogenAI/dogma/issues/325) [#322](https://github.com/EndogenAI/dogma/issues/322) [#323](https://github.com/EndogenAI/dogma/issues/323) [#324](https://github.com/EndogenAI/dogma/issues/324) [#325](https://github.com/EndogenAI/dogma/issues/325)



# [0.10.0](https://github.com/EndogenAI/dogma/compare/v0.9.0...v0.10.0) (2026-03-18)


### Bug Fixes

* **ci:** ignore flaky XDA HTTP/2 link in lychee checks ([963193e](https://github.com/EndogenAI/dogma/commit/963193e3836d967c0f355253678c16cc0638150d))
* **ci:** ignore monorepo.tools — connection failure in CI runners ([d53f401](https://github.com/EndogenAI/dogma/commit/d53f4019ed8c8a0c4d07042487cb93f0f97b7e34))
* **ci:** resolve PR [#321](https://github.com/EndogenAI/dogma/issues/321) test/link failures; track rate-limit follow-ups ([ae18f3b](https://github.com/EndogenAI/dogma/commit/ae18f3bc73d66d43275b06395bc67a2d7d735d86)), closes [#322](https://github.com/EndogenAI/dogma/issues/322) [-#325](https://github.com/-/issues/325)
* **mcp:** use mocker.patch throughout test_mcp_server; add mcp_server to coverage source ([70971e1](https://github.com/EndogenAI/dogma/commit/70971e1c979b23caa92d3927b6d40d2d6840b559))
* **review:** address Copilot re-review — 11 comments across 8 files ([2b21e8f](https://github.com/EndogenAI/dogma/commit/2b21e8fd5a2bacd180f2eb756e2960affd5f99a7))
* **review:** address PR [#321](https://github.com/EndogenAI/dogma/issues/321) routing/rate-limit/MCP feedback ([d3387f2](https://github.com/EndogenAI/dogma/commit/d3387f22afcccb7770d1ce08d2bb2c29d16fb048))
* **scripts:** stricter rate-limit mitigation — 60s post-delegation, 120s phase-boundary, 15k safety margin ([d71f5ad](https://github.com/EndogenAI/dogma/commit/d71f5adf04cddeb045436e59375eed8870630431))


### Features

* **mcp:** dogma governance MCP server — 8 tools, FastMCP (closes [#303](https://github.com/EndogenAI/dogma/issues/303)) ([22bebea](https://github.com/EndogenAI/dogma/commit/22bebea4bdd7f43983cd87453ff3d9caab7a9695))
* **packages:** dogma-governance standalone pre-commit bundle (closes [#305](https://github.com/EndogenAI/dogma/issues/305)) ([6e67a33](https://github.com/EndogenAI/dogma/commit/6e67a331f15cce453696d228afe006c0f9a2520c))
* **scripts:** add rate-limit detector with budget tracking ([9c84fdf](https://github.com/EndogenAI/dogma/commit/9c84fdfdf601fbbf81943fae98b5031adb65a8e7))
* **scripts:** AFS FTS5 index, fleet coupling, routing (closes [#129](https://github.com/EndogenAI/dogma/issues/129), [#291](https://github.com/EndogenAI/dogma/issues/291), [#292](https://github.com/EndogenAI/dogma/issues/292)) ([5ac954c](https://github.com/EndogenAI/dogma/commit/5ac954c6fbc13c34187ec09769f2f123df734d9d))



# [0.9.0](https://github.com/EndogenAI/dogma/compare/v0.8.0...v0.9.0) (2026-03-17)


### Bug Fixes

* **docs:** address PR review — Copilot review comments [#306](https://github.com/EndogenAI/dogma/issues/306) ([2b2d6f7](https://github.com/EndogenAI/dogma/commit/2b2d6f742eee3c7a93e16f728dbd84effea86967)), closes [#129](https://github.com/EndogenAI/dogma/issues/129)
* **research:** convert MANIFESTO.md plain-text refs to hyperlinks in [#297](https://github.com/EndogenAI/dogma/issues/297) doc ([1fe4bf1](https://github.com/EndogenAI/dogma/commit/1fe4bf118d2fde920491617be80a99d08dc94cd3))


### Features

* **agents:** Sprint 16 — PR merge gate, Claude Code hooks integration, print mode policy ([0be0c2b](https://github.com/EndogenAI/dogma/commit/0be0c2bc50d92a215a3dbcfcc23f9d0574400e68)), closes [#307](https://github.com/EndogenAI/dogma/issues/307) [#309](https://github.com/EndogenAI/dogma/issues/309)
* **scripts:** Candidate C — extend YAML schema in prune_scratchpad --init (closes [#308](https://github.com/EndogenAI/dogma/issues/308)) ([3ab98d8](https://github.com/EndogenAI/dogma/commit/3ab98d8308d719c6a2d5ae51ce0f11b411ec13fb))



# [0.8.0](https://github.com/EndogenAI/dogma/compare/v0.7.0...v0.8.0) (2026-03-16)


### Bug Fixes

* address Copilot PR review — schema validation, delta mode, drift CI gate, HGT acronym ([bf41280](https://github.com/EndogenAI/dogma/commit/bf41280fb7710207aef8c23f4c20fe9d8671dad5))


### Features

* **ci:** validate_adr.py — ADR structure validator + pre-commit hook ([30a684c](https://github.com/EndogenAI/dogma/commit/30a684c1be69bb87c277dc58eec6348c6ec3e49a)), closes [#281](https://github.com/EndogenAI/dogma/issues/281)
* **data:** substrate-atlas.yml — 23-substrate registry + health check integration ([1857897](https://github.com/EndogenAI/dogma/commit/18578979fb9b90b5b5a30be76d6948e1ecd85c6a)), closes [#279](https://github.com/EndogenAI/dogma/issues/279)
* **scripts:** assess_doc_quality.py — composite readability/structure/completeness scorer ([917b969](https://github.com/EndogenAI/dogma/commit/917b969bf14f24f22aaa3454d515d47d687eac41))
* **scripts:** check_divergence.py — cookiecutter template drift detector ([400cc26](https://github.com/EndogenAI/dogma/commit/400cc268e6e015be94c8f94a597603b01b810489)), closes [#293](https://github.com/EndogenAI/dogma/issues/293)
* **scripts:** check_glossary_coverage.py — bold-term glossary scanner ([1a97239](https://github.com/EndogenAI/dogma/commit/1a97239ee0c0e39916e17e0786da4ceb9d32caf9))
* **scripts:** parse_fsm_to_graph.py — FSM-to-NetworkX path analysis + CI invariant check ([539757a](https://github.com/EndogenAI/dogma/commit/539757adb9e5febdc7c53b50e14002a9c8135d54))
* **scripts:** validate_session_state.py — YAML phase-status block parsing ([6a5b74d](https://github.com/EndogenAI/dogma/commit/6a5b74dd31d59a8489b0fc8453b0967d41b7c6b5))



# [0.7.0](https://github.com/EndogenAI/dogma/compare/v0.6.0...v0.7.0) (2026-03-16)


### Bug Fixes

* **docs:** address PR review comments on Sprint 12 research docs ([0d6a3fe](https://github.com/EndogenAI/dogma/commit/0d6a3fea20c4ef6ff2477994b1e07dd752b93c4c))
* **research:** [#276](https://github.com/EndogenAI/dogma/issues/276) add Wave 1 substrate-atlas cross-reference — Wave 4 review gate fix ([de704f2](https://github.com/EndogenAI/dogma/commit/de704f2626e9d3a8881324217e75ad0e77befd9d))


### Features

* **research:** [#269](https://github.com/EndogenAI/dogma/issues/269) local inference & RAG — D4 synthesis [closes [#269](https://github.com/EndogenAI/dogma/issues/269)] ([a02b24d](https://github.com/EndogenAI/dogma/commit/a02b24d2aeb9e209805ca2db2eec50179a2ee139))
* **research:** [#270](https://github.com/EndogenAI/dogma/issues/270) platform agnosticism — D4 synthesis [closes [#270](https://github.com/EndogenAI/dogma/issues/270)] ([f6a6740](https://github.com/EndogenAI/dogma/commit/f6a674077d9e6253b04e106ff6100ab63f461e18))
* **research:** [#271](https://github.com/EndogenAI/dogma/issues/271) greenfield repo candidates — D4 synthesis [closes [#271](https://github.com/EndogenAI/dogma/issues/271)] ([99d634a](https://github.com/EndogenAI/dogma/commit/99d634a7abb49065b36592344e9b64bc008b63aa))
* **research:** [#272](https://github.com/EndogenAI/dogma/issues/272) agent-to-agent communication protocol — D4 synthesis [closes [#272](https://github.com/EndogenAI/dogma/issues/272)] ([b240a9e](https://github.com/EndogenAI/dogma/commit/b240a9e7d85c1a130e3951256833abb4cabc7074))
* **research:** [#273](https://github.com/EndogenAI/dogma/issues/273) biological evolution dogma propagation — D4 synthesis [closes [#273](https://github.com/EndogenAI/dogma/issues/273)] ([01a1c95](https://github.com/EndogenAI/dogma/commit/01a1c95dd8f97c3f0ee12202e0410d10cc1493f6))
* **research:** [#277](https://github.com/EndogenAI/dogma/issues/277) semantic encoding modes and contextual routing — D4 synthesis [closes [#277](https://github.com/EndogenAI/dogma/issues/277)] ([a4401bf](https://github.com/EndogenAI/dogma/commit/a4401bfc8d93c6a4a0bd272b705f14b347bfc74b))
* **research:** intelligence-architecture-synthesis.md — Sprint 12 cross-cutting synthesis ([1720904](https://github.com/EndogenAI/dogma/commit/172090495184ca143fc24dfcd49c6f227331553a)), closes [#264](https://github.com/EndogenAI/dogma/issues/264) [#265](https://github.com/EndogenAI/dogma/issues/265) [#266](https://github.com/EndogenAI/dogma/issues/266) [#267](https://github.com/EndogenAI/dogma/issues/267) [#268](https://github.com/EndogenAI/dogma/issues/268) [#269](https://github.com/EndogenAI/dogma/issues/269) [#270](https://github.com/EndogenAI/dogma/issues/270) [#271](https://github.com/EndogenAI/dogma/issues/271) [#272](https://github.com/EndogenAI/dogma/issues/272) [#273](https://github.com/EndogenAI/dogma/issues/273) [#274](https://github.com/EndogenAI/dogma/issues/274) [#275](https://github.com/EndogenAI/dogma/issues/275) [#276](https://github.com/EndogenAI/dogma/issues/276) [#277](https://github.com/EndogenAI/dogma/issues/277) [#230](https://github.com/EndogenAI/dogma/issues/230) [#232](https://github.com/EndogenAI/dogma/issues/232)



# [0.6.0](https://github.com/EndogenAI/dogma/compare/v0.5.0...v0.6.0) (2026-03-16)


### Bug Fixes

* **research:** [#268](https://github.com/EndogenAI/dogma/issues/268) substrate atlas — add second MANIFESTO axiom citation (Algorithms Before Tokens §2) ([d38d291](https://github.com/EndogenAI/dogma/commit/d38d291f92356b42be894b3e3e3c95d3107d83e6))
* **research:** add MANIFESTO.md axiom citations to Wave 1 docs — pass D4 review criterion 4 ([4da838b](https://github.com/EndogenAI/dogma/commit/4da838bd1c49f420790da4202fbb074afca9ac55))


### Features

* **research:** [#264](https://github.com/EndogenAI/dogma/issues/264) MCP state architecture — D4 synthesis [closes [#264](https://github.com/EndogenAI/dogma/issues/264)] ([9fa06cf](https://github.com/EndogenAI/dogma/commit/9fa06cf6fb585b0756b39b675507148db755714b))
* **research:** [#265](https://github.com/EndogenAI/dogma/issues/265) custom agent service modules — D4 synthesis [closes [#265](https://github.com/EndogenAI/dogma/issues/265)] ([e0a2885](https://github.com/EndogenAI/dogma/commit/e0a28852d254733d4db00b5fa2aef2aa089df9ce))
* **research:** [#268](https://github.com/EndogenAI/dogma/issues/268) substrate atlas — D4 synthesis [closes [#268](https://github.com/EndogenAI/dogma/issues/268)] ([8af8ac0](https://github.com/EndogenAI/dogma/commit/8af8ac099f4424a1b3be2cad02138ab04e2094f9))



# [0.5.0](https://github.com/EndogenAI/dogma/compare/v0.4.0...v0.5.0) (2026-03-16)


### Bug Fixes

* **agents:** agent_registry flow-sequence parsing, scoped tool IDs, relative paths ([#278](https://github.com/EndogenAI/dogma/issues/278)) ([fdc1a9a](https://github.com/EndogenAI/dogma/commit/fdc1a9abd096859c8689c75f42d60c9d8583b4a5))


### Features

* **agents:** capability-aware agent registry design ([#158](https://github.com/EndogenAI/dogma/issues/158)) ([2e46c84](https://github.com/EndogenAI/dogma/commit/2e46c841b9ea1f4fc98f94bb69ee94f97b36bea6))
* **scripts:** PREEXEC subshell audit logging and token-spin detection ([#156](https://github.com/EndogenAI/dogma/issues/156), [#157](https://github.com/EndogenAI/dogma/issues/157)) ([e9dc455](https://github.com/EndogenAI/dogma/commit/e9dc455b8ed7fed11cbf49b9eac3ecc79f360138))
* **skills:** sprint-planning skill and fleet wiring for Executive PM + Planner ([5bf4448](https://github.com/EndogenAI/dogma/commit/5bf44482f7b9b3ef27a4d21c011f6191e759dfee))



# [0.4.0](https://github.com/EndogenAI/dogma/compare/v0.3.1...v0.4.0) (2026-03-15)


### Bug Fixes

* **agents:** replace unverifiable commit-discipline governs: cites with canonical MANIFESTO.md axioms ([f98de6a](https://github.com/EndogenAI/dogma/commit/f98de6a9910605e8421da6b64f063c3db422be79))
* **docs:** remove forthcoming external-value-architecture.md reference from fork guide ([#204](https://github.com/EndogenAI/dogma/issues/204)) ([4e47972](https://github.com/EndogenAI/dogma/commit/4e479724719e489c28fc383ebbdb7af6c227bb2f))
* **sprint:** address PR [#263](https://github.com/EndogenAI/dogma/issues/263) review — traceability + template links + interface docs ([24161d2](https://github.com/EndogenAI/dogma/commit/24161d227849c3a710405ec137e0db515be4893b))


### Features

* **adoption:** Greenfield cookiecutter template — scaffold new dogma forks via uvx cookiecutter ([#57](https://github.com/EndogenAI/dogma/issues/57)) ([4f8559c](https://github.com/EndogenAI/dogma/commit/4f8559c01e795f78be1bcac77ce94da5b484fad4))
* **ci,scripts,agents:** stale-URL pre-commit hook, amplify_context.py, corpus-sweep skill ([#259](https://github.com/EndogenAI/dogma/issues/259), [#105](https://github.com/EndogenAI/dogma/issues/105), [#223](https://github.com/EndogenAI/dogma/issues/223)) ([8e12024](https://github.com/EndogenAI/dogma/commit/8e1202406ef73fab16e6f1ca7bed97d6cc0c83c1))
* **scripts:** bulk_github_operations.py and bulk_github_read.py — batch GitHub ops with rate-limit throttling and structured read ([#260](https://github.com/EndogenAI/dogma/issues/260), [#261](https://github.com/EndogenAI/dogma/issues/261)) ([88ffafd](https://github.com/EndogenAI/dogma/commit/88ffafd172dec16e1cf33e90412a8077bc6008f1))



## [0.3.1](https://github.com/EndogenAI/dogma/compare/v0.3.0...v0.3.1) (2026-03-15)


### Bug Fixes

* **ci:** accept HTTP 502 in lychee link check ([2d5b21d](https://github.com/EndogenAI/dogma/commit/2d5b21dc3275e1b8eff4cba3a0be7066cc23a10f))
* **ci:** skip README.md in validate_synthesis loop ([c9a1d85](https://github.com/EndogenAI/dogma/commit/c9a1d855f958ad63558d749f493837a2a4aa1284))
* **docs:** correct dead neuroscience entry point link in research README ([c24248d](https://github.com/EndogenAI/dogma/commit/c24248d36b218ecea797a6ca552aea7be339775e)), closes [#262](https://github.com/EndogenAI/dogma/issues/262)
* **docs:** rewrite all relative links after research/ restructuring ([68e4a2e](https://github.com/EndogenAI/dogma/commit/68e4a2e8a4c59be494b10f177a6eb487f7a330cd))



# [0.3.0](https://github.com/EndogenAI/dogma/compare/v0.2.0...v0.3.0) (2026-03-15)


### Bug Fixes

* **docs:** correct broken repo URLs, review count errors + provenance annotations ([98f4c5b](https://github.com/EndogenAI/dogma/commit/98f4c5bfd3f65d7de426bda3b5ab2968549e3c8a)), closes [#56](https://github.com/EndogenAI/dogma/issues/56) [#125](https://github.com/EndogenAI/dogma/issues/125) [#205](https://github.com/EndogenAI/dogma/issues/205) [MANIFESTO.md#3](https://github.com/MANIFESTO.md/issues/3)
* **scripts:** validate_synthesis.py — accept multiple files for pre-commit pass_filenames compatibility ([7fed812](https://github.com/EndogenAI/dogma/commit/7fed8122f95e35531449930c58ac05da083fed47))
* **security:** block IPv6 link-local addresses in fetch_source.py validate_url() closes [#106](https://github.com/EndogenAI/dogma/issues/106) ([f8e44c0](https://github.com/EndogenAI/dogma/commit/f8e44c0a3f21954a1c853c5a5541d7a953d80503))


### Features

* **ci:** issue-metrics action — weekly issue/PR health snapshot for agent orientation closes [#214](https://github.com/EndogenAI/dogma/issues/214) ([cdf1376](https://github.com/EndogenAI/dogma/commit/cdf13767d5a2d8b20f5fd7e526dbf61c7c826c7e))
* **scripts,ci:** validate_agent_files.py — specificity metrics + MANIFESTO section-anchored citation check closes [#257](https://github.com/EndogenAI/dogma/issues/257) ([b0d0253](https://github.com/EndogenAI/dogma/commit/b0d0253e79e1cd9de295477c958e4d227d2b008a))
* **scripts,docs:** deprecate prune_scratchpad --force + encode sprint-close requirements ([3c89004](https://github.com/EndogenAI/dogma/commit/3c8900458aa27fc67c5cf952af89aa3fe289a1aa))
* **scripts:** adopt_wizard.py — dogma onboarding wizard closes [#56](https://github.com/EndogenAI/dogma/issues/56) ([1fd7d5c](https://github.com/EndogenAI/dogma/commit/1fd7d5c5377df8b4d2018ef02b72748b263527cc))
* **scripts:** encoding_coverage.py — MANIFESTO F1-F4 coverage baseline closes [#237](https://github.com/EndogenAI/dogma/issues/237) ([77c52d5](https://github.com/EndogenAI/dogma/commit/77c52d56255f7bb08055c803f700f96817a3571e))
* **scripts:** extract_action_items.py — D4 doc action item extraction with BM25 dedup closes [#256](https://github.com/EndogenAI/dogma/issues/256) ([4601593](https://github.com/EndogenAI/dogma/commit/4601593d587474c6ce92a26b8365ba71d8968bad))
* **scripts:** generate_script_docs.py — pydoc-markdown wrapper for scripts/docs/ closes [#255](https://github.com/EndogenAI/dogma/issues/255) ([7c8ada7](https://github.com/EndogenAI/dogma/commit/7c8ada7ed469e3861a721bdc2a49c917d4b25030))
* **scripts:** orientation_snapshot.py — pre-computed session orientation digest closes [#241](https://github.com/EndogenAI/dogma/issues/241) ([11dbf10](https://github.com/EndogenAI/dogma/commit/11dbf10bcdd6f75201833def4cec25bc154481ee))
* **scripts:** prune_scratchpad.py phase 2 — docs/sessions/ archive + session-hash frontmatter closes [#254](https://github.com/EndogenAI/dogma/issues/254) ([5e5285e](https://github.com/EndogenAI/dogma/commit/5e5285e87ae32ef5ba25e284393afc8ca97819bf))
* **scripts:** validate_session.py — constitutional AI value fidelity hook (OQ-4) closes [#238](https://github.com/EndogenAI/dogma/issues/238) ([41f6ee7](https://github.com/EndogenAI/dogma/commit/41f6ee77116b8df29e6e21f13e8bb87c465e8cb5))
* **scripts:** validate_synthesis.py — manual stop gate warning for Final-status doc edits closes [#224](https://github.com/EndogenAI/dogma/issues/224) ([f330a0f](https://github.com/EndogenAI/dogma/commit/f330a0fe5af2feb1ac3ba07986cd3fff413a8a77))



# [0.2.0](https://github.com/EndogenAI/dogma/compare/v0.1.0...v0.2.0) (2026-03-15)


### Bug Fixes

* **ci:** correct broken relative paths in lcf-axiom-positioning + add lycheeignore entries ([dcaaa42](https://github.com/EndogenAI/dogma/commit/dcaaa4265c2eedd057803d5121c3a056a50fbfc0)), closes [MANIFESTO.md#3](https://github.com/MANIFESTO.md/issues/3) [../../MANIFESTO.md#3](https://github.com/../../MANIFESTO.md/issues/3)
* **research:** [#203](https://github.com/EndogenAI/dogma/issues/203) pattern catalog labels — H3→bold inline per D4 convention ([401aa6d](https://github.com/EndogenAI/dogma/commit/401aa6d1b1ec95242cf06d6e2ec3815fcc015bb5))
* **research:** [#242](https://github.com/EndogenAI/dogma/issues/242) add second MANIFESTO §1 citation to scratchpad-architecture-maturation.md ([7e8ebcd](https://github.com/EndogenAI/dogma/commit/7e8ebcd8da614f21b834a218429c2a413bf73a06))
* **research:** [#247](https://github.com/EndogenAI/dogma/issues/247) add rank-bm25 external source to action-item-extraction.md ([6786856](https://github.com/EndogenAI/dogma/commit/6786856b48fe19d57c6285b6b6224e8d531d773f))
* **research:** [#252](https://github.com/EndogenAI/dogma/issues/252) add scipy external source URL to crd-output-quality-study.md ([d9212fb](https://github.com/EndogenAI/dogma/commit/d9212fbb7f080d4f3b3a7c8f00ae3ad04673ac00))


### Features

* **agents:** elevate GitHub Agent to executive tier; docs: sub-issues decision ([863f71d](https://github.com/EndogenAI/dogma/commit/863f71ddae6c8788503a2abe869d3042acb6e178)), closes [#200](https://github.com/EndogenAI/dogma/issues/200) [#48](https://github.com/EndogenAI/dogma/issues/48)
* **ci,scripts:** resolve [#249](https://github.com/EndogenAI/dogma/issues/249) [#248](https://github.com/EndogenAI/dogma/issues/248) [#107](https://github.com/EndogenAI/dogma/issues/107) — axiom §-ref warn, CRD substrate health, drift gate calibration ([5b44d6e](https://github.com/EndogenAI/dogma/commit/5b44d6eca83338d2b79d74136a9cfe10a4d0ea4e))



# [0.1.0](https://github.com/EndogenAI/dogma/compare/12f8382bf74e514be69953642a92a5fb17d2692d...v0.1.0) (2026-03-13)


### Bug Fixes

* add endogenous sources to shifting-constraints-from-tokens.md ([34628d8](https://github.com/EndogenAI/dogma/commit/34628d8fac7d8c97c5ac599fc5c7b185d53dd1d5))
* add required YAML frontmatter to specialist agents (tools, handoffs) ([3b2aee6](https://github.com/EndogenAI/dogma/commit/3b2aee6ee37164a62504501c6792a2000b3b1885))
* address 10 review comments from PR [#153](https://github.com/EndogenAI/dogma/issues/153) ([70b3a4c](https://github.com/EndogenAI/dogma/commit/70b3a4cab64e736df32f20c4a9c474cae5da4d45))
* address Copilot review comments and CI failures on PR [#199](https://github.com/EndogenAI/dogma/issues/199) ([aad53d4](https://github.com/EndogenAI/dogma/commit/aad53d4b76cd5682ac87643f6d32e2ce3ce9ed5a)), closes [#2920271870](https://github.com/EndogenAI/dogma/issues/2920271870) [#2920271912](https://github.com/EndogenAI/dogma/issues/2920271912) [#2920272032](https://github.com/EndogenAI/dogma/issues/2920272032) [#2920272078](https://github.com/EndogenAI/dogma/issues/2920272078) [#2920272059](https://github.com/EndogenAI/dogma/issues/2920272059) [#2920271974](https://github.com/EndogenAI/dogma/issues/2920271974) [#292027](https://github.com/EndogenAI/dogma/issues/292027) [#292027](https://github.com/EndogenAI/dogma/issues/292027)
* address Copilot review comments and CI failures on PR [#58](https://github.com/EndogenAI/dogma/issues/58) ([dfafaaa](https://github.com/EndogenAI/dogma/commit/dfafaaaa6cf71a2a8cb6b5c47bd15a4169708fce))
* address Copilot review feedback on PR [#141](https://github.com/EndogenAI/dogma/issues/141) — consolidate Session History, add metaphor citation, add client-values context, fix BDI heading hierarchy ([7684b5a](https://github.com/EndogenAI/dogma/commit/7684b5ad8a094470b4cdbbf66c37707f0df3f19b))
* address ruff E501 line-too-long in test_remaining_scripts.py ([37d4883](https://github.com/EndogenAI/dogma/commit/37d48830ed50e9c6d849fc09293b58be63888122))
* **agents:** address Copilot review — standardise Review Output heading, fix per-phase sequence, YAML block scalar, gate summary, title casing ([71d0593](https://github.com/EndogenAI/dogma/commit/71d0593fd26fa8e5b8815422d8bbad79fa0131fd))
* **agents:** address PR [#46](https://github.com/EndogenAI/dogma/issues/46) review comments ([c86c259](https://github.com/EndogenAI/dogma/commit/c86c2592dd1dacb5dce259e9f5aa64020b6dc1e0))
* **agents:** address review 3911940826 — 5 guardrail/label corrections ([4444ecf](https://github.com/EndogenAI/dogma/commit/4444ecf21a67656bf04c4d4b27c49e4bd065b571))
* **agents:** fleet audit fixes — orchestrator tools normalised, review.agent.md path corrected ([0258d5e](https://github.com/EndogenAI/dogma/commit/0258d5e73d619b86782ac29791894c016de0ec7b)), closes [#64](https://github.com/EndogenAI/dogma/issues/64)
* **ci:** add theatlantic.com As-We-May-Think to lycheeignore (503 from CI runners) ([3fed803](https://github.com/EndogenAI/dogma/commit/3fed80360409cedc1fb0339df639e27f42b403c6))
* **ci:** address PR [#110](https://github.com/EndogenAI/dogma/issues/110) Copilot review — lint, broken links, axiom refs, drift advisory ([26a3764](https://github.com/EndogenAI/dogma/commit/26a3764728a38387c66cd774a6556dedcf73959c))
* **ci:** enforce pre-commit checks before commit; fix CI failures ([82e6812](https://github.com/EndogenAI/dogma/commit/82e6812cdc7939266eb49a6b1740cf859b6059db))
* **ci:** PR [#244](https://github.com/EndogenAI/dogma/issues/244) review remediation — lychee, gitignore, weave_links parser, stale messages, label-sync format, release-drafter, export --fields, fleet governs: annotations ([d51b131](https://github.com/EndogenAI/dogma/commit/d51b13132a376b2e8a375e0cafe1ec971576678a)), closes [#245](https://github.com/EndogenAI/dogma/issues/245) [#245](https://github.com/EndogenAI/dogma/issues/245) [#245](https://github.com/EndogenAI/dogma/issues/245)
* **ci:** resolve ruff W291/I001/F401 linting errors in capability_gate + pr_review_reply ([b01133a](https://github.com/EndogenAI/dogma/commit/b01133ab98ca54c5ccc9dde0f8f46ac357c57f22))
* **ci:** ruff format test_capability_gate.py ([a257c83](https://github.com/EndogenAI/dogma/commit/a257c83c93b524ab0f46e95c2fdf642ed9eb4448))
* clean up unused imports in test_wait_for_github_run.py ([7ae2b46](https://github.com/EndogenAI/dogma/commit/7ae2b46364026cd181a252052bc33574e3cd27da))
* correct rationale_summary regex pattern in handoff permeability script ([d1ff419](https://github.com/EndogenAI/dogma/commit/d1ff419502814b5a1508434673559e2b1afee213))
* correct relative links in research frontmatter references ([66fbe83](https://github.com/EndogenAI/dogma/commit/66fbe835b36f2d69969aa79bedfc5fef880d765b))
* correct relative links in session-checkpoint-and-safeguard-patterns.md ([2397f3a](https://github.com/EndogenAI/dogma/commit/2397f3a96450558719ea112c10e33db70cfc319f))
* correct signal detection patterns and test fixtures for Phase 3b ([591a695](https://github.com/EndogenAI/dogma/commit/591a69566e4b2a4d23ee6a1bc5e0e3194c832f5b))
* correct type hint from callable to Callable in validate_handoff_permeability.py ([ab2068e](https://github.com/EndogenAI/dogma/commit/ab2068ee5d145dec3a24902711e22fabb515899e))
* **docs:** correct broken relative paths for .github/ refs in new docs ([cc06f9a](https://github.com/EndogenAI/dogma/commit/cc06f9a13ed109a382019a0fba3cede2e55c6993)), closes [#63](https://github.com/EndogenAI/dogma/issues/63)
* **docs:** correct Endogenous-First F4 gate status in [4,1] audit ([7f9f089](https://github.com/EndogenAI/dogma/commit/7f9f08961b8cdb06389b6a8836266b0f12c4522c)), closes [#53](https://github.com/EndogenAI/dogma/issues/53)
* **docs:** correct grep alternation syntax for UTF-8 validation ([68c73fb](https://github.com/EndogenAI/dogma/commit/68c73fba5f4b0e0fc822ef03661113265109b769))
* **generate_sweep_table:** time-relative recency; fix workflows.md CLI example ([0a914d6](https://github.com/EndogenAI/dogma/commit/0a914d68d83f0181e0fb0f2d818b9230877fee20)), closes [#208](https://github.com/EndogenAI/dogma/issues/208)
* **manifesto,plans:** address PR [#89](https://github.com/EndogenAI/dogma/issues/89) review comments ([ba96148](https://github.com/EndogenAI/dogma/commit/ba96148961a72f9602e64cb28dd091a21f474b6b))
* **plans:** restore missing Phase 6 heading in value-encoding-fidelity workplan ([7563765](https://github.com/EndogenAI/dogma/commit/756376510d6f93602ccd23db31205814c4c7c6d6))
* **pr-review:** address Copilot review [#3911133661](https://github.com/EndogenAI/dogma/issues/3911133661) on PR [#63](https://github.com/EndogenAI/dogma/issues/63) ([fc85411](https://github.com/EndogenAI/dogma/commit/fc854111694aeff18e73ad7fc338dccfd00ce174))
* **research:** [#190](https://github.com/EndogenAI/dogma/issues/190) — correct section numbering (gaps & duplicates) ([7c873ac](https://github.com/EndogenAI/dogma/commit/7c873ace138b84a0f352fb1f3bf2a99ead0edb42))
* **research:** [#190](https://github.com/EndogenAI/dogma/issues/190) — correct section numbering D4 compliance ([c1cb560](https://github.com/EndogenAI/dogma/commit/c1cb560d46e13dd271331c7a85b95f9175f7bb40))
* **research:** [#191](https://github.com/EndogenAI/dogma/issues/191) — add MANIFESTO axiom citations + expand substrate inventory ([568700f](https://github.com/EndogenAI/dogma/commit/568700ff9917b28dbcf6a35f42ea7799b57535e7))
* **research:** [#191](https://github.com/EndogenAI/dogma/issues/191) — correct section numbering (duplicate § 3) ([127c4ca](https://github.com/EndogenAI/dogma/commit/127c4cab32eced2dbe4cf32f95a51d836a1f6b29))
* **research:** add canonical example + anti-pattern to dogma-neuroplasticity Pattern Catalog [[#82](https://github.com/EndogenAI/dogma/issues/82)] ([e598582](https://github.com/EndogenAI/dogma/commit/e5985826534985422d38f863cc4f5555dd53f946))
* **research:** address PR [#111](https://github.com/EndogenAI/dogma/issues/111) review comments — manifest metric operationalize, validate_session CI target, shell injection guard, workplan session note ([0eedb4d](https://github.com/EndogenAI/dogma/commit/0eedb4ddc76f067074bf2041ac13e56acf0ef5e8))
* **research:** address PR [#87](https://github.com/EndogenAI/dogma/issues/87) review comments ([226361a](https://github.com/EndogenAI/dogma/commit/226361a154796751edec68789669c50dc8e1b1ca))
* resolve broken links in six-layer-topological-extension.md ([a2b3eed](https://github.com/EndogenAI/dogma/commit/a2b3eed953bfd9b6e179000e4a69d0b2f211daaa))
* resolve linting errors in seed_action_items.py ([e16e257](https://github.com/EndogenAI/dogma/commit/e16e257533efcbb988cb59fa8388e3420e0edc2f))
* resolve regex error in validate_handoff_permeability verdict pattern ([3899da9](https://github.com/EndogenAI/dogma/commit/3899da9696346bdc5aeab8355e43a0cc2d63f3db))
* **review:** address Copilot PR [#109](https://github.com/EndogenAI/dogma/issues/109) comments — remove unused import, add output error handling, gate env-specific test, align doc/README to actual behavior [[#82](https://github.com/EndogenAI/dogma/issues/82)] ([bcc96c8](https://github.com/EndogenAI/dogma/commit/bcc96c8339b527c83b9c818b2b4902a8b0b39ea4))
* **review:** address Copilot review comments on PR [#92](https://github.com/EndogenAI/dogma/issues/92) — threshold, grep scope, FSM guards, AGENTS.md column label, workplan headings ([898c2f1](https://github.com/EndogenAI/dogma/commit/898c2f1fadaa21040b39dccf2ce844393f452fdf))
* **review:** address PR [#61](https://github.com/EndogenAI/dogma/issues/61) Copilot review comments ([d0ef94e](https://github.com/EndogenAI/dogma/commit/d0ef94e62210666a7fd34f4362e48f1089584b58))
* **review:** address PR [#63](https://github.com/EndogenAI/dogma/issues/63) review findings — CI skills gate, 5-layer chain, D4 headings, metric alignment, CLI test [#60](https://github.com/EndogenAI/dogma/issues/60) ([19a2a2c](https://github.com/EndogenAI/dogma/commit/19a2a2c11f842ef3d0eb35e519d41dc1c7636967))
* ruff format pass and correct GitHub MCP server URL ([8c94dcc](https://github.com/EndogenAI/dogma/commit/8c94dcce62d28cf4d8cffb42bc17499f84614866))
* ruff lint violations in scripts/ and tests/ — 108 errors resolved ([0e929d4](https://github.com/EndogenAI/dogma/commit/0e929d4638a7e64f70ffd2989655b30d0a2e3267))
* **scripts,agents:** address Copilot PR [#77](https://github.com/EndogenAI/dogma/issues/77) review comments ([357f85a](https://github.com/EndogenAI/dogma/commit/357f85a8f60c133f47057d9dd0279dad9efffe6a))
* **scripts:** add MANIFESTO.md citations and [@pytest](https://github.com/pytest).mark.io to capability_gate ([ce38f4e](https://github.com/EndogenAI/dogma/commit/ce38f4eddabdc1326c5f972ac4c76f013fdfdb12))
* **scripts:** address Copilot review comments on PR [#91](https://github.com/EndogenAI/dogma/issues/91) ([ab4e31c](https://github.com/EndogenAI/dogma/commit/ab4e31c788964a0ceb0a4c75c4dd81c39e249f0a))
* **scripts:** address PR [#90](https://github.com/EndogenAI/dogma/issues/90) Copilot review — 8 issues across 4 files ([84cb9c0](https://github.com/EndogenAI/dogma/commit/84cb9c033e84bd2030a64911c282081f534d38bb))
* **scripts:** address Review security blockers in weave_links.py ([b11e26c](https://github.com/EndogenAI/dogma/commit/b11e26c5720ad2444ad8a0a46ed6a5448823ecf9))
* **scripts:** correct _resolve_safe docstring; mark Phase 1A complete in workplan ([20b9270](https://github.com/EndogenAI/dogma/commit/20b9270bc75fa8b38ea040f837ff7051d1374174))
* **scripts:** skip links inside inline code spans in check_doc_links.py ([9546088](https://github.com/EndogenAI/dogma/commit/9546088cfe2ef7c17783b0c5f88bbf7ed9d36155))
* sort imports in pr_review_reply.py for ruff compliance ([f6d207a](https://github.com/EndogenAI/dogma/commit/f6d207a5cc7ac9b46ec7c29f60ae382df73c1429))
* **test:** remove unused pytest import in test_scan_research_links ([#59](https://github.com/EndogenAI/dogma/issues/59)) ([551a240](https://github.com/EndogenAI/dogma/commit/551a24000c004c8e19de98c179b3a8a6615d9771))
* **tests:** add missing [@pytest](https://github.com/pytest).mark.io to fixture-based file I/O tests ([50d4656](https://github.com/EndogenAI/dogma/commit/50d46566f67b6767876231639ae22c269920d124))
* **tests:** add missing [@pytest](https://github.com/pytest).mark.io/[@pytest](https://github.com/pytest).mark.integration markers; align T2 requires_adr in spec [[#82](https://github.com/EndogenAI/dogma/issues/82)] ([d52e1f6](https://github.com/EndogenAI/dogma/commit/d52e1f61a7aa1cb39156e3475338c48fb3b61a4d))


### Features

* **#119:** extend query_docs.py with toolchain and skills scopes + tests ([c183198](https://github.com/EndogenAI/dogma/commit/c183198e89591c9f06e974f17f45a185fd3a3db9)), closes [#119](https://github.com/EndogenAI/dogma/issues/119)
* **#120:** complete weave_links.py with --dry-run, idempotency guard, and --scope-filter ([3daf045](https://github.com/EndogenAI/dogma/commit/3daf045acab10699750bf53851e876517bf94cd4)), closes [#120](https://github.com/EndogenAI/dogma/issues/120)
* **#127:** add Core Layer Impermeability citation-order check to validate_agent_files.py ([2d5f2d5](https://github.com/EndogenAI/dogma/commit/2d5f2d559fd7fcfa098b50103d4aaa1648648e1d)), closes [#127](https://github.com/EndogenAI/dogma/issues/127)
* add phase-3 deliverables — strategic roadmap, 90-day workplan, specialist agents ([3110e0e](https://github.com/EndogenAI/dogma/commit/3110e0e2af1d852e0cba8f6844e125a47d5f459c))
* add wait_for_github_run.py polling script with async test suite ([cd688f6](https://github.com/EndogenAI/dogma/commit/cd688f647d9ca0c5ac153344f74e5d9f11c7c65f)), closes [#150](https://github.com/EndogenAI/dogma/issues/150)
* **agents:** add B5, D5, A5, D4 agent files — implements [#67](https://github.com/EndogenAI/dogma/issues/67), [#68](https://github.com/EndogenAI/dogma/issues/68), unblocked A5+D4 ([d416bf9](https://github.com/EndogenAI/dogma/commit/d416bf9ed893b19ca0835a0732ccd98c338301e7))
* **agents:** add context window alert protocol to executive orchestrator ([27d220d](https://github.com/EndogenAI/dogma/commit/27d220d3900bf8d673434b8aa0d9065f5aea30c5))
* **agents:** add delegation-routing and phase-gate-sequence skills; research docs for Phase 6 [[#79](https://github.com/EndogenAI/dogma/issues/79) [#81](https://github.com/EndogenAI/dogma/issues/81) [#72](https://github.com/EndogenAI/dogma/issues/72)] ([c533869](https://github.com/EndogenAI/dogma/commit/c53386904658a21bffca31646b330e15d3e58393))
* **agents:** add Executive Orchestrator, Planner, Fleet, and PM agents ([69c921c](https://github.com/EndogenAI/dogma/commit/69c921ca27773445f53ccf380972427c89dea7c1))
* **agents:** add inter-phase Review gate to orchestration workflow ([e5d92b5](https://github.com/EndogenAI/dogma/commit/e5d92b5ece1ecd45b07be8a9aa07ee3234749276))
* **agents:** add Phase A adopt-now fleet agents (A1, A2, B1, D1) ([5d601c5](https://github.com/EndogenAI/dogma/commit/5d601c53b10970d2b7ca9a3177ac07ea53ee2c69)), closes [#33](https://github.com/EndogenAI/dogma/issues/33) [#41](https://github.com/EndogenAI/dogma/issues/41) [#42](https://github.com/EndogenAI/dogma/issues/42) [#44](https://github.com/EndogenAI/dogma/issues/44)
* **agents:** add Phase B investigate-tier fleet agents (A3, A4, B2-B4, C1-C2, D2-D3) ([56a8658](https://github.com/EndogenAI/dogma/commit/56a86583420355a5755909ba87d29973a79a9b5a)), closes [#41](https://github.com/EndogenAI/dogma/issues/41) [#42](https://github.com/EndogenAI/dogma/issues/42) [#43](https://github.com/EndogenAI/dogma/issues/43) [#44](https://github.com/EndogenAI/dogma/issues/44)
* **agents:** add pre-review grep sweep step to executive-orchestrator per-phase sequence ([7337d9a](https://github.com/EndogenAI/dogma/commit/7337d9ae4f3c86ffe9299486b49c7c529f494d79))
* **agents:** add research fleet, docs executive, review, github, and scaffold script ([c19931f](https://github.com/EndogenAI/dogma/commit/c19931fd0adffcafd7aebc6660b6b9f2e38f7dff))
* **agents:** add runtime capability gates and audit logging ([9e3af73](https://github.com/EndogenAI/dogma/commit/9e3af73c2c16ec535e7994144e6e3cc25c8a9b8f)), closes [#155](https://github.com/EndogenAI/dogma/issues/155)
* **agents:** implement Tier 2 skills backlog — 5 SKILL.md files closes [#62](https://github.com/EndogenAI/dogma/issues/62) ([204403c](https://github.com/EndogenAI/dogma/commit/204403cced881bbd6635730650901b135b02f63b))
* **agents:** Phase 2 taxonomy codification — .github/agents/AGENTS.md, skill-authoring skill, fleet README, scaffold_agent, issue discipline guide ([9c6445f](https://github.com/EndogenAI/dogma/commit/9c6445ffa1b14400e838c9c6337d41dbd5e40ac4)), closes [#64](https://github.com/EndogenAI/dogma/issues/64)
* **agents:** scaffold 3 SKILL.md files and extend validate_agent_files --skills — Phase 3 [#60](https://github.com/EndogenAI/dogma/issues/60) ([be4d7c0](https://github.com/EndogenAI/dogma/commit/be4d7c0132ac75fb7978567f1d249d09db13a44d))
* **agents:** strengthen orchestrator delegation-first and compaction discipline ([5017000](https://github.com/EndogenAI/dogma/commit/5017000be59a7a3138b334f3b8bc25dd3df854d5))
* **ci:** add check_doc_links pre-commit hook to catch broken relative paths ([bd26610](https://github.com/EndogenAI/dogma/commit/bd266102bc79e41a66b1d738e0ad75163deffe05))
* **ci:** add Governor B runtime heredoc governor — .envrc + setup guide (closes [#159](https://github.com/EndogenAI/dogma/issues/159)) ([21a3c52](https://github.com/EndogenAI/dogma/commit/21a3c52dc1815202f69c7be5e969412b82e33489))
* **ci:** add no-heredoc-writes pre-commit governor hook ([b0dc37c](https://github.com/EndogenAI/dogma/commit/b0dc37c93793186cca7fb3a741b2369492965b70))
* **ci:** add unblock-issues workflow; add wave1 workplan ([a2f95b3](https://github.com/EndogenAI/dogma/commit/a2f95b3f36fc27c4f709d7d070b9b90d33b18896)), closes [#60](https://github.com/EndogenAI/dogma/issues/60) [#60](https://github.com/EndogenAI/dogma/issues/60)
* **ci:** enable audit-provenance workflow on pull requests ([00fa6f6](https://github.com/EndogenAI/dogma/commit/00fa6f604e7c1e30543a8fd54982d21673b57528))
* **ci:** implement GitHub automation workflows — label-sync, changelog, release-drafter, stale fix ([#215](https://github.com/EndogenAI/dogma/issues/215) [#216](https://github.com/EndogenAI/dogma/issues/216) [#217](https://github.com/EndogenAI/dogma/issues/217) [#219](https://github.com/EndogenAI/dogma/issues/219) [#220](https://github.com/EndogenAI/dogma/issues/220)) ([b557e61](https://github.com/EndogenAI/dogma/commit/b557e61c6fdc4a21781f84e6736bbefc1cf12150))
* **ci:** implement GitHub PM setup (issue [#22](https://github.com/EndogenAI/dogma/issues/22) R1-R6) ([#28](https://github.com/EndogenAI/dogma/issues/28)) ([ced0d18](https://github.com/EndogenAI/dogma/commit/ced0d18ca7e20c8b285144fb6652d1d91c7bb05e)), closes [#1](https://github.com/EndogenAI/dogma/issues/1) [#4](https://github.com/EndogenAI/dogma/issues/4) [#1](https://github.com/EndogenAI/dogma/issues/1) [-#3](https://github.com/-/issues/3) [#29](https://github.com/EndogenAI/dogma/issues/29) [#30](https://github.com/EndogenAI/dogma/issues/30) [#29](https://github.com/EndogenAI/dogma/issues/29) [#30](https://github.com/EndogenAI/dogma/issues/30)
* **docs:** expand toolchain substrate to uv, ruff, git, pytest ([#35](https://github.com/EndogenAI/dogma/issues/35)) ([8e271c2](https://github.com/EndogenAI/dogma/commit/8e271c2b1a612cd425c53963ec28d64127fe947f))
* **docs:** toolchain API docs substrate — gh CLI reference + automation ([9cbd92e](https://github.com/EndogenAI/dogma/commit/9cbd92eaa21687cbf83093be597d5d2fb19aa55e)), closes [#34](https://github.com/EndogenAI/dogma/issues/34)
* **fleet:** finalize executive privilege model and interconnections ([641b6c6](https://github.com/EndogenAI/dogma/commit/641b6c69a1db44c39c9a0450c22478d7142390e1))
* implement research findings sprint — closes [#23](https://github.com/EndogenAI/dogma/issues/23), [#27](https://github.com/EndogenAI/dogma/issues/27), [#25](https://github.com/EndogenAI/dogma/issues/25) R1-R6 ([88425fc](https://github.com/EndogenAI/dogma/commit/88425fca2267250d25b7c87c227c2a3dae400c41))
* initial repo structure with manifesto, agents, scripts, and docs ([12f8382](https://github.com/EndogenAI/dogma/commit/12f8382bf74e514be69953642a92a5fb17d2692d))
* **plans:** Add issue [#192](https://github.com/EndogenAI/dogma/issues/192) to Phase 4 — Workflow Formula Encoding DSL (Phase 4→5 bridge) ([e470e4e](https://github.com/EndogenAI/dogma/commit/e470e4e1bad86e04405f79e8f1bbabacb0d94694))
* **plans:** Phase 4 research planning — foundational theory topics ([#189](https://github.com/EndogenAI/dogma/issues/189) [#190](https://github.com/EndogenAI/dogma/issues/190) [#191](https://github.com/EndogenAI/dogma/issues/191)) ([d16e260](https://github.com/EndogenAI/dogma/commit/d16e26061758af48203b20456049ec24a26bfa0b))
* **research:** Phase 0 infrastructure — manifest scripts, bibliography, deep-research workflow ([#59](https://github.com/EndogenAI/dogma/issues/59)) ([db6be8a](https://github.com/EndogenAI/dogma/commit/db6be8a59905adc1045287595e9ac364df02d28a))
* **research:** Phase 2a values encoding empirics ([#179](https://github.com/EndogenAI/dogma/issues/179) [#169](https://github.com/EndogenAI/dogma/issues/169) [#178](https://github.com/EndogenAI/dogma/issues/178)) ([2fda3cc](https://github.com/EndogenAI/dogma/commit/2fda3cc2f6db5431140951639890319b800a7c70))
* **research:** Phase 2b conflict resolution framework + hermeneutics guide ([#177](https://github.com/EndogenAI/dogma/issues/177) [#176](https://github.com/EndogenAI/dogma/issues/176)) ([d079a83](https://github.com/EndogenAI/dogma/commit/d079a839110717e74f208b48f514d0f93dfa712d))
* **research:** Phase 3a foundational theory — HBT, topology, pressure ([#188](https://github.com/EndogenAI/dogma/issues/188) [#170](https://github.com/EndogenAI/dogma/issues/170) [#183](https://github.com/EndogenAI/dogma/issues/183)) ([5a61f5a](https://github.com/EndogenAI/dogma/commit/5a61f5aa340a26659243481956c25e7bb3412bca))
* **research:** Phase 3c — six-layer topological extension ([#185](https://github.com/EndogenAI/dogma/issues/185)) ([1b19c87](https://github.com/EndogenAI/dogma/commit/1b19c874aaef775ef4cf37015b74082a3347c8cf)), closes [#56](https://github.com/EndogenAI/dogma/issues/56) [#177](https://github.com/EndogenAI/dogma/issues/177) [#179](https://github.com/EndogenAI/dogma/issues/179) [#184](https://github.com/EndogenAI/dogma/issues/184)
* **scripts,ci:** add export_project_state.py and GitHub automation workflows ([#221](https://github.com/EndogenAI/dogma/issues/221)) ([47b8caf](https://github.com/EndogenAI/dogma/commit/47b8caf61304efb8e8e4fb5f3e1bc3315ba3f1a0)), closes [#216](https://github.com/EndogenAI/dogma/issues/216) [#217](https://github.com/EndogenAI/dogma/issues/217)
* **scripts:** [#112](https://github.com/EndogenAI/dogma/issues/112) — validate_session.py post-commit scratchpad audit ([54cdb47](https://github.com/EndogenAI/dogma/commit/54cdb471003c2ec684057a4879c7cd13f4a29181))
* **scripts:** [#118](https://github.com/EndogenAI/dogma/issues/118) — generate_agent_manifest documentation + CI validation pattern ([432f198](https://github.com/EndogenAI/dogma/commit/432f19823209b7eb92a57026ba9a163beee96e40))
* **scripts:** [#121](https://github.com/EndogenAI/dogma/issues/121) — propose_dogma_edit tier enforcement + ADR output ([1a4ecc3](https://github.com/EndogenAI/dogma/commit/1a4ecc31dd5eb304830ebc7fa7adb38394083869))
* **scripts:** [#122](https://github.com/EndogenAI/dogma/issues/122) — validate_skill_files.py 5-check gate ([8234a1e](https://github.com/EndogenAI/dogma/commit/8234a1e461280b83f4e8805e4459d320323e9a29))
* **scripts:** [#138](https://github.com/EndogenAI/dogma/issues/138) — delegation routing + session state FSM validators ([9216fdf](https://github.com/EndogenAI/dogma/commit/9216fdf50a08abc5f94727dd1887783b7cca10fa))
* **scripts:** add --ci and --issues flags to scaffold_workplan ([ab112fb](https://github.com/EndogenAI/dogma/commit/ab112fbc7ad61d5e7b4974b28088e59c27915525))
* **scripts:** add audit_provenance.py — value signal provenance tracing ([#78](https://github.com/EndogenAI/dogma/issues/78)) ([2e8bb70](https://github.com/EndogenAI/dogma/commit/2e8bb70587fd8a54c6574fc542217bc824882ed2))
* **scripts:** add detect_drift.py — watermark-phrase drift detection ([#71](https://github.com/EndogenAI/dogma/issues/71)) ([cf0d0d0](https://github.com/EndogenAI/dogma/commit/cf0d0d0cc1f7e95b4872695c1fadb58607760aa3))
* **scripts:** add Fetch-before-check and Phase-N-Review-Output checks to validate_agent_files ([ba977f4](https://github.com/EndogenAI/dogma/commit/ba977f4cf4f42b4639986bed0eec9333166524c0))
* **scripts:** add ruff rule for terminal file I/O output redirection ([d089063](https://github.com/EndogenAI/dogma/commit/d089063b46e2f69b985893fcb271b99ce7b91dbe)), closes [#154](https://github.com/EndogenAI/dogma/issues/154) [#151](https://github.com/EndogenAI/dogma/issues/151) [#154](https://github.com/EndogenAI/dogma/issues/154)
* **scripts:** add scaffold_workplan, --append-summary, and corruption detection ([4938f50](https://github.com/EndogenAI/dogma/commit/4938f502cfe32ffe8db87de4df0e7f939a6457fb))
* **scripts:** add wait_for_unblock.py — poll GitHub issue until status:blocked removed ([64ddfe4](https://github.com/EndogenAI/dogma/commit/64ddfe4ea8a53fb52985a80ce083d3276c4fca55))
* **scripts:** BM25 query_docs CLI + tests — retrieve-on-demand corpus querying ([#80](https://github.com/EndogenAI/dogma/issues/80)) ([b5716a1](https://github.com/EndogenAI/dogma/commit/b5716a1775d0d06bc1ab8dccc168dce457bdb5d3))
* **scripts:** extend generate_agent_manifest with cross-reference density score ([#54](https://github.com/EndogenAI/dogma/issues/54)) ([b0b3ebd](https://github.com/EndogenAI/dogma/commit/b0b3ebd6dc2ba64b217804fb5450ac91618a8513))
* **scripts:** extend generate_agent_manifest.py with posture, capabilities, and handoffs fields ([a624dc5](https://github.com/EndogenAI/dogma/commit/a624dc5acff235767d660d921322a7753b53c9d4))
* **scripts:** generate_sweep_table.py — programmatic corpus sweep table with Doc Type + Synthesises + Status columns ([#165](https://github.com/EndogenAI/dogma/issues/165) [#212](https://github.com/EndogenAI/dogma/issues/212)) ([b00f705](https://github.com/EndogenAI/dogma/commit/b00f7053ef03ea697eea9ba003de5f9dd0a64d4a))
* **scripts:** governs: annotation script + link_registry audit ([#243](https://github.com/EndogenAI/dogma/issues/243)) ([a9afdc6](https://github.com/EndogenAI/dogma/commit/a9afdc60fd4aa4d385d0ca70e48765a3f910bcb9))
* **scripts:** non-interactive default for scaffold_workplan.py; add --interactive flag ([ddd7b97](https://github.com/EndogenAI/dogma/commit/ddd7b9779ea70b47402efb0fc313aad10013993c)), closes [#212](https://github.com/EndogenAI/dogma/issues/212) [#221](https://github.com/EndogenAI/dogma/issues/221) [#239](https://github.com/EndogenAI/dogma/issues/239) [#240](https://github.com/EndogenAI/dogma/issues/240)
* **scripts:** Phase 3b operationalization — handoff validation + CI provenance audit ([#181](https://github.com/EndogenAI/dogma/issues/181) [#182](https://github.com/EndogenAI/dogma/issues/182)) ([0303c5a](https://github.com/EndogenAI/dogma/commit/0303c5aa892291205e3b391d5a5ed75e576e633d)), closes [#1](https://github.com/EndogenAI/dogma/issues/1) [#184](https://github.com/EndogenAI/dogma/issues/184) [#184](https://github.com/EndogenAI/dogma/issues/184) [#184](https://github.com/EndogenAI/dogma/issues/184) [#184](https://github.com/EndogenAI/dogma/issues/184) [#170](https://github.com/EndogenAI/dogma/issues/170) [#184](https://github.com/EndogenAI/dogma/issues/184)
* **scripts:** propose_dogma_edit.py + tests ≥80% [[#82](https://github.com/EndogenAI/dogma/issues/82)] ([e8e9ced](https://github.com/EndogenAI/dogma/commit/e8e9ced1a17f54c9ba79d25d8f34af47432c2664))
* **scripts:** validate_agent_files.py — encoding fidelity gate ([#52](https://github.com/EndogenAI/dogma/issues/52)) ([9b5f7dd](https://github.com/EndogenAI/dogma/commit/9b5f7ddf7616c4b15ec483ccdf3fbfdb9bcb97af))
* **scripts:** weave_links.py + link_registry — citation interweb weaving ([#84](https://github.com/EndogenAI/dogma/issues/84)) ([fd21441](https://github.com/EndogenAI/dogma/commit/fd21441bfcb7d788b9d2c3067536484833ce898d))
* **skills:** add research-epic-planning skill ([40470dd](https://github.com/EndogenAI/dogma/commit/40470dd54dde12b0474539316c10f53453a6d584)), closes [#7](https://github.com/EndogenAI/dogma/issues/7)
* **skills:** add session-retrospective skill — insight discovery and substrate encoding ([ba71ac8](https://github.com/EndogenAI/dogma/commit/ba71ac844a26fe5e07f930960b0dba3e46d3c8cb)), closes [#82](https://github.com/EndogenAI/dogma/issues/82)
* **terminology:** rename 'custom agents' → 'Roles' as endogenous project term ([84432c9](https://github.com/EndogenAI/dogma/commit/84432c90afaf19bc34fe014af46435dba5089624)), closes [#63](https://github.com/EndogenAI/dogma/issues/63) [#2901498118](https://github.com/EndogenAI/dogma/issues/2901498118) [#2901499889](https://github.com/EndogenAI/dogma/issues/2901499889) [#2901498926](https://github.com/EndogenAI/dogma/issues/2901498926)



