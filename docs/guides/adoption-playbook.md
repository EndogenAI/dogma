---
governs: [adoption, client-values, adopt-wizard, onboarding]
---

# Adoption Playbook

> Guides external organisations through adopting the dogma framework — installing `AGENTS.md`, connecting `client-values.yml`, and running the adopt wizard.

## Why Adoption Matters

The dogma framework is designed to be endogenous: values flow inward from the organisation, not outward from a vendor. Adoption is the moment that flow is formalised — the point at which an organisation's mission, priorities, and constraints become first-class inputs to the agent fleet's behaviour.

Every adoption generates two durable artefacts:

1. **`AGENTS.md`** — operational constraints tailored to the adopter's context
2. **`client-values.yml`** — a Deployment Layer external-values file that specialises (but never overrides) the Core Layer constraints in `MANIFESTO.md`

---

## AccessiTech LLC — First External Adoption

**AccessiTech LLC** is the first external organisation to adopt the dogma framework. They are an accessibility-focused technology company whose agent fleet work centres on inclusive UI tooling, accessible documentation pipelines, and assistive-technology integrations.

### Why AccessiTech Matters for the Framework

AccessiTech's adoption is the **primary empirical grounding** for the adopt wizard's defaults, prompts, and validation logic. The following facts were surfaced during their onboarding and directly inform `adopt_wizard.py`'s design:

| Observation | Wizard implication |
|---|---|
| AccessiTech's mission statement is short and precise (≤25 words) | Wizard prompts for a concise mission field; warn if >50 words |
| Their top priorities map cleanly to the three framework axioms | Wizard offers axiom-aligned priority checkboxes as defaults |
| They needed a custom `AGENTS.md` scope for their `docs/a11y/` directory | Wizard must support subdirectory `AGENTS.md` scaffolding |
| `client-values.yml` required a `constraints:` block for WCAG 2.2 AA compliance | Wizard must include a `constraints:` section in the generated template |
| They ran `validate_agent_files.py` before committing — caught a missing section heading | Wizard must call validation scripts automatically before reporting success |

### Branch Reference

The AccessiTech onboarding was prototyped on the `AccessiT3ch/issue22` integration branch. The commit `5b5f2dd fix(ci): also ignore bare conventionalcommits.org domain in lychee` is the first cross-repo CI fix traceable to that adoption context, confirming the setup was exercised end-to-end.

---

## Adoption Steps

These steps apply to any organisation adopting the dogma framework. The adopt wizard (`scripts/adopt_wizard.py`) automates steps 2–5.

### Step 1 — Understand the Deployment Layer

Read [`AGENTS.md` § Deployment Layer integration](../../AGENTS.md#deployment-layer-integration). The key constraint: `client-values.yml` can specialise Core Layer constraints but cannot override them. Before running the wizard, confirm you understand which axioms in `MANIFESTO.md` are non-negotiable.

### Step 2 — Run the Adopt Wizard

```bash
uv run python scripts/adopt_wizard.py --org <your-org> --repo <your-repo>
```

The wizard prompts for:
- Organisation name and mission (used in `client-values.yml` header)
- Top priorities (mapped to framework axioms)
- Any domain-specific constraints (e.g., WCAG 2.2 AA, HIPAA, SOC 2)
- Whether subdirectory `AGENTS.md` files are needed

### Step 3 — Review Generated Files

The wizard generates:

| File | Purpose |
|---|---|
| `client-values.yml` | Deployment Layer values for the adopter |
| `AGENTS.md` | Root constraint file, seeded with client-values integration note |
| `docs/AGENTS.md` *(optional)* | Subdirectory constraints, if requested |

Review each file before committing. The wizard outputs a diff preview; press `y` to confirm.

### Step 4 — Run Validation

The wizard automatically runs:

```bash
uv run python scripts/validate_agent_files.py --all
```

If validation fails, the wizard prints the failing file and the first unmet check. Fix the issue before committing.

### Step 5 — Commit and Verify

```bash
git add client-values.yml AGENTS.md
git commit -m "chore(adoption): initialise dogma framework for <org>"
```

Verify the files are committed and CI passes before proceeding to agent fleet setup.

### Step 6 — Extend the Fleet

With the framework installed, add `.agent.md` role files under `.github/agents/` following the [agent file authoring guide](agents.md). Each agent file will inherit the constraints from `AGENTS.md` and the Deployment Layer values from `client-values.yml`.

---

## Acceptance Criteria for the Adopt Wizard (#56, #125)

These criteria are derived directly from the AccessiTech LLC onboarding experience and govern the `adopt_wizard.py` implementation.

### AC1 — CLI Flags

The wizard accepts `--org` and `--repo` flags as positional identifiers. Both flags are required; the wizard exits with a non-zero code and a descriptive error if either is missing.

```bash
uv run python scripts/adopt_wizard.py --org AccessiTech --repo platform
```

### AC2 — Client Values Prompting

The wizard interactively prompts for:
- `mission` — one sentence describing the organisation's purpose (warned if >50 words)
- `priorities` — up to three items, each optionally mapped to a framework axiom (Endogenous-First / Algorithms Before Tokens / Local Compute-First)
- `constraints` — zero or more domain-specific compliance constraints (free text)

On completion, the wizard writes a valid `client-values.yml` to the repository root. The file must conform to the schema referenced in [`AGENTS.md` § Deployment Layer integration](../../AGENTS.md#deployment-layer-integration).

### AC3 — AGENTS.md Scaffolding

The wizard copies the canonical `AGENTS.md` template and inserts a Deployment Layer integration note referencing the generated `client-values.yml`. The note must appear in the `## Deployment Layer integration` section and include the path `client-values.yml` as the local external-values file.

Subdirectory `AGENTS.md` files are scaffolded if the user opts in during prompting.

### AC4 — Automatic Validation

Before reporting success, the wizard runs:

```bash
uv run python scripts/validate_agent_files.py --all
```

If validation fails, the wizard:
1. Prints the failing file and first unmet check
2. Exits with a non-zero code
3. Does **not** print the success summary

The wizard does not suppress or wrap the validator's output — raw validator output is surfaced to the user.

### AC5 — Summary Output

On success, the wizard prints a structured summary:

```
Adoption complete for <org>/<repo>.

Files created:
  client-values.yml         ✓ valid
  AGENTS.md                 ✓ valid
  docs/AGENTS.md            ✓ valid  (if requested)

Validation: PASSED

Next steps:
  1. git add client-values.yml AGENTS.md && git commit -m "chore(adoption): ..."
  2. Add .agent.md role files to .github/agents/  (see docs/guides/agents.md)
  3. Install pre-commit hooks: uv run pre-commit install
```

The summary is machine-parseable (one key: value per line under each section header) to facilitate future automation.

---

## client-values.yml Schema Reference

A minimal `client-values.yml` for the Deployment Layer:

```yaml
# client-values.yml — Deployment Layer external-values file
# Specialises (does not override) Core Layer constraints in MANIFESTO.md.

org: AccessiTech LLC
repo: platform
mission: Build accessible technology that removes barriers for people with disabilities.

priorities:
  - Endogenous-First       # scaffold from our existing accessibility knowledge
  - Local Compute-First    # minimize external API dependency for sensitive user data

constraints:
  - WCAG 2.2 AA compliance on all agent-generated UI documentation
```

The `constraints:` block is passed through by the framework as an informational signal
to agents — it does not programmatically restrict tool calls. Agents must read and honour
it as a Deployment Layer directive.

---

## Related Guides and References

- [agents.md](agents.md) — authoring `.agent.md` role files
- [workflows.md](workflows.md) — session and delegation workflows
- [session-management.md](session-management.md) — scratchpad and session lifecycle
- [`AGENTS.md` § Deployment Layer integration](../../AGENTS.md#deployment-layer-integration)
- [`MANIFESTO.md`](../../MANIFESTO.md) — core dogma; non-negotiable axioms
- Issue [#56](https://github.com/EndogenAI/Workflows/issues/56) — adopt wizard implementation
- Issue [#125](https://github.com/EndogenAI/Workflows/issues/125) — client-values.yml integration
- Issue [#205](https://github.com/EndogenAI/Workflows/issues/205) — AccessiTech use case (this document closes #205)
