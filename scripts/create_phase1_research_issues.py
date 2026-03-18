#!/usr/bin/env python
"""
Create Phase 1 Research Recommendation issues from structured data.

Usage:
    uv run python scripts/create_phase1_research_issues.py

Returns:
    Prints the range of created issues (first and last issue numbers).
"""

import re
import subprocess
import sys

issues = [
    # High priority
    {
        "title": "feat(decision-logic): encode decision tables for strategic recommendations",
        "labels": ["type:follow-up", "source:research", "area:agents", "priority:high"],
        "source": "319",
        "body": "Encode decision tables for strategic agent tasks",
    },
    {
        "title": "feat(governance): enforce approval gates for file/branch operations",
        "labels": ["type:follow-up", "source:research", "area:agents", "priority:high"],
        "source": "318",
        "body": "Enforce approval gates for irreversible agent actions",
    },
    {
        "title": "feat(agents): implement multi-provider inference abstraction",
        "labels": ["type:follow-up", "source:research", "area:agents", "priority:high"],
        "source": "317",
        "body": "Implement multi-provider agent abstraction",
    },
    {
        "title": "feat(observability): adopt OpenTelemetry for agent instrumentation",
        "labels": ["type:follow-up", "source:research", "area:ci", "priority:high"],
        "source": "316",
        "body": "Adopt OpenTelemetry for inter-agent calls",
    },
    {
        "title": "feat(agents): enforce return compression ceiling per subagent",
        "labels": ["type:follow-up", "source:research", "area:agents", "priority:high"],
        "source": "315",
        "body": "Enforce subagent return compression ≤300 tokens",
    },
    {
        "title": "refactor(mcp): standardize cross-platform tools via MCP",
        "labels": ["type:follow-up", "source:research", "area:mcp", "priority:high"],
        "source": "314",
        "body": "Use MCP for all cross-platform tooling",
    },
    # Medium priority
    {
        "title": "feat(guardrails): adopt L1 semantic output validation",
        "labels": ["type:follow-up", "source:research", "area:agents", "priority:medium"],
        "source": "313",
        "body": "Adopt NeMo guardrails L1 output validation",
    },
    {
        "title": "feat(guardrails): encode L2 constraints as schema-validated YAML",
        "labels": ["type:follow-up", "source:research", "area:agents", "priority:medium"],
        "source": "313",
        "body": "Encode L2 constraints as machine-readable YAML",
    },
    {
        "title": 'docs(agents): update "when to ask" decision boundary with governance levels',
        "labels": ["type:follow-up", "source:research", "area:docs", "priority:medium"],
        "source": "318",
        "body": 'Update "Ask vs Proceed" decision boundary',
    },
    {
        "title": "docs(guides): add Copilot ecosystem limitations guide",
        "labels": ["type:follow-up", "source:research", "area:docs", "priority:medium"],
        "source": "314",
        "body": "Document Copilot-specific limitations",
    },
    {
        "title": "docs(agents): add CMA report citation to Minimal-Posture principle",
        "labels": ["type:follow-up", "source:research", "area:docs", "priority:medium"],
        "source": "318",
        "body": "Link CMA report in AGENTS.md Minimal-Posture",
    },
    {
        "title": "feat(observability): implement /health endpoints for long-running services",
        "labels": ["type:follow-up", "source:research", "area:ci", "priority:medium"],
        "source": "316",
        "body": "Implement observable /health endpoints",
    },
    {
        "title": "feat(scratchpad): add ## Telemetry section to session schema",
        "labels": ["type:follow-up", "source:research", "area:ci", "priority:medium"],
        "source": "316",
        "body": "Add telemetry to session scratchpad schema",
    },
    {
        "title": "refactor(scripts): encode phase-gating orchestration logic",
        "labels": ["type:follow-up", "source:research", "area:scripts", "priority:medium"],
        "source": "315",
        "body": "Encode multi-phase orchestration as scripts",
    },
    {
        "title": "feat(tracking): measure verification effort per orchestration phase",
        "labels": ["type:follow-up", "source:research", "area:ci", "priority:medium"],
        "source": "315",
        "body": "Measure human effort per phase",
    },
    # Medium-Low priority
    {
        "title": "feat(metrics): detect slow error discovery in token-heavy workflows",
        "labels": ["type:follow-up", "source:research", "area:metrics", "priority:medium"],
        "source": "315",
        "body": "Monitor delay-to-decision metric",
    },
    {
        "title": "docs(agents): document platform binding separation pattern",
        "labels": ["type:follow-up", "source:research", "area:docs", "priority:low"],
        "source": "314",
        "body": "Define platform bindings separately",
    },
    {
        "title": "docs(agents): document Copilot collaboration phase expectations",
        "labels": ["type:follow-up", "source:research", "area:docs", "priority:low"],
        "source": "312",
        "body": "Document collaboration norms in agents",
    },
    {
        "title": "feat(review): standardize review gates with numbered acceptance criteria",
        "labels": ["type:follow-up", "source:research", "area:agents", "priority:medium"],
        "source": "312",
        "body": "Strengthen review gates with numbered criteria",
    },
    {
        "title": "feat(testing): gate human review with automated test validation",
        "labels": ["type:follow-up", "source:research", "area:ci", "priority:low"],
        "source": "312",
        "body": "Use tests as validation layer",
    },
    {
        "title": "feat(metrics): track performance metrics by agent role",
        "labels": ["type:follow-up", "source:research", "area:metrics", "priority:low"],
        "source": "312",
        "body": "Measure role-specific agent velocity",
    },
    # Low priority
    {
        "title": "feat(rag): adopt LanceDB + BGE-Small for greenfield RAG patterns",
        "labels": ["type:follow-up", "source:research", "area:research", "priority:low"],
        "source": "294",
        "body": "Adopt LanceDB + BGE-Small for RAG",
    },
    {
        "title": "feat(rag): implement embedding model version tracking in MCP",
        "labels": ["type:follow-up", "source:research", "area:mcp", "priority:low"],
        "source": "294",
        "body": "Implement embedding model versioning",
    },
    {
        "title": "docs(rag): define standard H2-semantic document chunking strategy",
        "labels": ["type:follow-up", "source:research", "area:docs", "priority:low"],
        "source": "294",
        "body": "Define H2-semantic chunking strategy",
    },
    {
        "title": "feat(rag): measure RAG value via token savings + latency",
        "labels": ["type:follow-up", "source:research", "area:metrics", "priority:low"],
        "source": "294",
        "body": "Measure RAG value metrics",
    },
]

created_issues = []
first_issue = None
last_issue = None

for i, issue in enumerate(issues, 1):
    body = f"Recommended by: #{issue['source']}\n\n{issue['body']}"

    cmd = [
        "gh",
        "issue",
        "create",
        "--title",
        issue["title"],
        "--body",
        body,
    ]

    # Add each label with -l flag
    for label in issue["labels"]:
        cmd.extend(["-l", label])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to create issue #{i}: {issue['title']}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)

    # Extract issue number from output (e.g., "https://github.com/owner/repo/issues/1234")
    match = re.search(r"issues/(\d+)", result.stdout)
    if match:
        issue_num = match.group(1)
        created_issues.append(issue_num)
        if first_issue is None:
            first_issue = issue_num
        last_issue = issue_num
        print(f"[{i:2d}/25] Created #{issue_num}: {issue['title'][:60]}")

if created_issues:
    print(f"\nCreated {len(created_issues)} issues: #{first_issue}–#{last_issue} (all linked to source research docs)")
else:
    print("No issues created.", file=sys.stderr)
    sys.exit(1)
