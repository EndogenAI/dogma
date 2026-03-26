# Readiness Contracts

**Purpose**: Define intent-bound acceptance tests for any initiative's "readiness" claim, preventing false-positive readiness signals from phase completion without intent satisfaction.

**Source**: `docs/research/readiness-false-positive-analysis.md` § Recommendations 1–3

---

## Intent-Bound Template

A readiness contract specifies **what the system must do for a real user** — not what tasks were completed. Store at `docs/plans/<initiative>/intent-contract.md` or reference from the initiative workplan.

```yaml
# Intent Contract — <Initiative Name>
intent: |
  <Human intent statement: job-to-be-done, 1–2 sentences>
  Example: "System can generate grounded answers to questions about dogma with citations."

scope:
  in: [list what is in scope]
  out: [list what is explicitly out of scope — prevents scope creep readiness claims]

acceptance_tests:
  - name: <test name>
    command: <how to run it>
    expected: <what success looks like>

demo_artifact:
  question: <a real user question>
  answer_file: docs/plans/<initiative>/demo-answer.md
  citations_required: true

capability_matrix:
  retrieval: "yes | partial | no"  # Can the system retrieve relevant context?
  augmentation: "yes | partial | no"  # Can it augment with retrieved context?
  generation: "yes | partial | no"  # Can it generate grounded answers?
  end_to_end: "yes | partial | no"  # Full pipeline passing?
```

## Capability Matrix

**Readiness claims require a passing capability matrix.** No dimension may be unknown or "partial" if a readiness claim is being made.

| Dimension | Description | Readiness required |
|-----------|-------------|-------------------|
| Retrieval | System retrieves relevant chunks for a query | yes |
| Augmentation | Chunks are injected into the generation context | yes |
| Generation | System generates a grounded answer with citations | yes |
| End-to-End | Full pipeline passes with a real user question | yes |

**Anti-pattern**: Claiming "ready" when retrieval passes but generation is untested.

**Required wording for partial states**: "Retrieval-ready; generation in progress — not ready for end-to-end use."

## Demo Artifact Requirement

Before any readiness claim is accepted:
1. Run a real user question through the full system
2. Record: question + generated answer + source citations
3. Store at `docs/plans/<initiative>/demo-answer.md`
4. Reference demo artifact in the issue or PR that closes readiness

**Prohibited**: Readiness claims without a linked demo artifact.

## Workplan Extension

Every workplan that gates on a readiness claim must include:

```markdown
### Readiness Gate

- [ ] Intent contract exists at `docs/plans/<initiative>/intent-contract.md`
- [ ] Capability matrix: all dimensions passing
- [ ] Demo artifact: question + answer + citations recorded
- [ ] `scripts/check_plan_to_intent_drift.py` passes (workplan delivers on intent)
```

## Cross-References

- `scripts/check_readiness_matrix.py` — validates capability matrix presence in claims
- `scripts/check_plan_to_intent_drift.py` — checks workplan completion maps to intent
- [AGENTS.md § Readiness Language Guard](../../AGENTS.md#readiness-language-guard) — language constraints
