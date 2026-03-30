---
title: "Vector Databases Explained — Indexing Algorithms, Distance Metrics, and DB Selection for RAG"
status: Final
closes_issue: 503
x-governs:
  - local-compute-first
  - endogenous-first
created: 2026-03-30
sources:
  - url: "https://machinelearningmastery.com/vector-databases-explained-in-3-levels-of-difficulty/"
    title: "Vector Databases Explained in 3 Levels of Difficulty"
    type: blog_post
    author: "Bala Priya C"
    date: "2026-03-27"
  - url: "https://www.pinecone.io/learn/vector-database/"
    title: "What is a Vector Database?"
    type: documentation
    author: "Pinecone"
    date: null
  - url: "https://www.deeplearning.ai/short-courses/building-applications-vector-databases/"
    title: "Building Applications with Vector Databases (Short Course)"
    type: course
    author: "DeepLearning.AI"
    date: null
  - url: "https://machinelearningmastery.com/top-5-vector-databases/"
    title: "Top 5 Vector Databases"
    type: blog_post
    author: "MLMastery"
    date: "2025-12"
  - url: "https://machinelearningmastery.com/build-a-rag-system-part-vii/"
    title: "Build a RAG System Part VII"
    type: blog_post
    author: "MLMastery"
    date: "2025-03"
recommendations:
  - id: rec-vector-databases-explained-001
    title: "ADOPT pgvector as the default starting point for new RAG features within dogma if already on Postgres; defer to LanceDB for embedded/local-first workflows"
    status: deferred
    effort: Low
    linked_issue: null
    decision_ref: null
  - id: rec-vector-databases-explained-002
    title: "ENFORCE metric-embedding alignment: every vector index declaration must document the embedding model AND the distance metric used; add as a required field in any RAG configuration schema"
    status: deferred
    effort: Low
    linked_issue: null
    decision_ref: null
  - id: rec-vector-databases-explained-003
    title: "ADOPT hybrid search (ANN + BM25 / RRF) as the default retrieval strategy in the dogma RAG stack rather than dense-only ANN; update intelligence-architecture-synthesis.md accordingly"
    status: deferred
    effort: Medium
    linked_issue: null
    decision_ref: null
  - id: rec-vector-databases-explained-004
    title: "DOCUMENT LanceDB's absence from mainstream VDB surveys as a known gap; add a note to local-rag-adoption-patterns.md explaining why it was chosen over the surveyed options"
    status: deferred
    effort: Low
    linked_issue: null
    decision_ref: null
  - id: rec-vector-databases-explained-005
    title: "RESEARCH re-ranking (cross-encoder) as a follow-on issue — identified gap in primary source; high-precision RAG requires a re-ranking step not covered by ANN alone"
    status: deferred
    effort: Medium
    linked_issue: null
    decision_ref: null
---

# Vector Databases Explained — Indexing Algorithms, Distance Metrics, and DB Selection for RAG

## Executive Summary

Vector databases (VDBs) are the storage and retrieval layer that makes semantic search
practical at scale. Unlike traditional databases that rely on exact-match or B-tree indices,
VDBs store high-dimensional float arrays ("embeddings") produced by machine-learning models
and answer approximate-nearest-neighbour (ANN) queries — returning vectors whose geometric
distance to a query vector is minimised.

For dogma's RAG stack (documented in [local-rag-adoption-patterns.md](local-rag-adoption-patterns.md)
and [intelligence-architecture-synthesis.md](intelligence-architecture-synthesis.md)), the
choice of VDB is a foundational infrastructure decision with direct consequences for latency,
memory footprint, and operational complexity. The primary source (Bala Priya C, MLMastery,
March 2026) delivers a pedagogically rigorous three-level treatment — from embedding basics
through ANN index internals — that maps well onto dogma's **Local Compute First** and
**Endogenous-First** axioms: start with the simplest viable option in existing infrastructure,
and only adopt managed SaaS after local alternatives are exhausted.

Key finding: dogma's chosen stack (LanceDB + BGE-Small) is absent from mainstream VDB surveys.
This is not a deficiency — LanceDB's embedded columnar-vector architecture predates or falls
outside the "traditional VDB" category surveyed by most articles. This synthesis documents
why the absence is expected and why LanceDB remains the correct local-first choice.

## Hypothesis Validation

**Hypothesis**: Vector databases are necessary infrastructure for effective RAG.

**Verdict**: Partially validated — VDB capabilities are necessary; a dedicated VDB server is not.

### Supporting evidence

1. **Unstructured data requires semantic indexing.** Exact-match search cannot retrieve
   relevant passages from a 10 000-document corpus by meaning. Embedding models produce
   float arrays whose geometric proximity encodes semantic similarity; a storage layer
   that can index and query those arrays efficiently is required for any non-trivial RAG
   workload. (Source: Bala Priya C, Level 1 section.)

2. **Brute-force k-NN is O(n) — impractical at scale.** Exhaustive distance calculation
   over millions of vectors exceeds acceptable latency budgets. ANN indices (HNSW, IVF)
   reduce query time to sub-linear at the cost of approximate (not exact) results.
   (Source: Bala Priya C, Level 2, ANN discussion.)

3. **Hybrid search is now table stakes for production RAG.** Dense ANN retrieval alone
   misses keyword-critical queries; sparse BM25 alone misses semantic matches. Combining
   both via Reciprocal Rank Fusion (RRF) consistently outperforms either alone.
   (Source: Bala Priya C, Level 2, Hybrid Search section; corroborated by Weaviate and
   Pinecone documentation.)

### Nuance: embedded libraries satisfy the requirement

A dedicated VDB server (Pinecone, Qdrant, Weaviate) is not the only way to satisfy the
requirement. Embedded libraries (Faiss, LanceDB, Chroma) provide equivalent indexing
capabilities with no network hop and no separate process. For dogma's local-first mandate,
embedded options satisfy the hypothesis without the operational overhead of a managed service.
LanceDB specifically is a columnar-vector store that ships as a Python package — it provides
HNSW indexing and hybrid search while writing to disk files, fully compatible with dogma's
preference for inspectable, file-resident state.

**Conclusion**: The *capabilities* of a VDB are necessary. A *dedicated VDB server* is not,
particularly for sub-100M-vector workloads where an embedded library suffices.

## Pattern Catalog

### Pattern 1 — Three Cognitive Levels of VDB Understanding

Understanding VDB technology across three levels prevents both under-engineering (treating
the VDB as a magic black box) and over-engineering (tuning HNSW parameters before measuring
baseline latency).

#### Level 1 — Core Concept (Anyone building RAG should know this)

- Unstructured data (text, images, audio) cannot be searched with SQL `WHERE` clauses.
- Embedding models convert unstructured data to fixed-length float arrays — e.g. a 768-float
  vector for a text passage from BGE-Small-EN-v1.5.
- VDBs store those arrays and answer **k-nearest-neighbour (k-NN)** queries: "return the 5
  vectors geometrically closest to this query vector."
- Geometric closeness encodes semantic similarity: passages about the same topic cluster in
  the high-dimensional space.

#### Level 2 — Operational Detail (Anyone tuning a RAG system should know this)

**Distance metrics — must match embedding model training:**

| Metric | Formula | When to use |
|--------|---------|-------------|
| Cosine similarity | $\cos(\theta) = \frac{A \cdot B}{\|A\|\|B\|}$ | Text embeddings trained with cosine loss (most common) |
| Dot product | $A \cdot B$ | Models trained with dot-product loss; normalised embeddings where dot = cosine |
| Euclidean (L2) | $\sqrt{\sum (a_i - b_i)^2}$ | When magnitude carries meaning; image embeddings |

**Critical rule**: using the wrong metric for a given embedding model degrades result quality.
BGE-Small-EN is trained with cosine loss; always configure cosine similarity when using it.

**Approximate Nearest Neighbour (ANN) — why it is necessary:**

Brute-force k-NN is O(n) per query. At 1M vectors with 768 dimensions a single query requires
~6 GB of distance calculations. ANN indices trade a small recall penalty (typically < 2–5%
on standard benchmarks) for query times in the millisecond range.

**Metadata filtering tradeoffs:**

- **Pre-filter**: apply metadata constraints before ANN search → smaller candidate set,
  faster ANN, but risk of filtering out nearest neighbours.
- **Post-filter**: run ANN first, then filter results → guaranteed k results if corpus is
  large; may surface semantically far matches if filter is restrictive.
- Most production VDBs now support **filtered ANN** (e.g. Qdrant's payload index) — closer
  to pre-filter accuracy without the recall penalty.

**Hybrid search — ANN + BM25 merged via RRF:**

```
Score_RRF(d) = Σ 1 / (k + rank_i(d))
```

where `rank_i(d)` is document `d`'s rank in retrieval list `i` and `k` is a smoothing
constant (typically 60). RRF is non-parametric: no weight tuning required. Weaviate, Qdrant,
and Elasticsearch all implement RRF natively as of 2025. This is now the recommended default
for production RAG, not an optional enhancement.

#### Level 3 — Internals (System designers and performance engineers)

**HNSW (Hierarchical Navigable Small World):**

- Multi-layer graph where each node connects to its nearest neighbours (`M` bidirectional
  edges per node).
- Upper layers are sparse (long-range navigation); lower layers are dense (fine-grained
  search).
- Query: greedy graph traversal top-down → sub-linear query time, effectively O(log n) in
  practice.
- Key parameters:
  - `ef_construction` (build-time): wider beam search = higher recall, slower build.
    Typical starting value: 128–200.
  - `M` (graph connectivity): more edges = higher recall, higher memory. Typical: 16–32.
  - `ef_search` (query-time): candidates evaluated per query. Increase to trade query speed
    for recall. Typical starting value: 64–128.
- **Memory profile**: stores the full graph in RAM. At 1M 768-dim float32 vectors + HNSW
  index, expect 3–6 GB RAM. Unsuitable for very large corpora on memory-constrained hosts.

**IVF (Inverted File / Inverted Index):**

- Clusters vectors into `nlist` Voronoi cells via k-means during build (requires training
  pass over the corpus).
- Query: candidate cells are identified (`nprobe` cells searched), then brute-force within
  those cells.
- Lower memory than HNSW (no graph stored, just cluster centroids + inverted lists).
- Key parameters:
  - `nlist`: number of clusters. Rule of thumb: $\sqrt{n}$ where $n$ is corpus size.
  - `nprobe`: cells searched per query. Increase to trade speed for recall.
- Requires a training step — unsuitable for dynamic corpora with frequent inserts.

**Product Quantisation (PQ) and IVF-PQ:**

- PQ compresses vectors by splitting them into sub-vectors and quantising each (lossy).
- IVF-PQ combines IVF clustering and PQ compression for billion-scale workloads.
- 4–32× memory reduction at the cost of some recall. Standard in Faiss; supported in
  Milvus and Qdrant.

**DiskANN:**

- SSD-resident index for corpora too large for RAM (hundreds of millions to billions of
  vectors).
- Query latency higher than in-memory HNSW but proportionally cheaper per-vector.
- Supported natively in Azure AI Search; available in Milvus and Weaviate.

**Sharding:**

- At ~50–100M vectors, a single-node HNSW index saturates RAM on a standard server.
- Sharding distributes the corpus across nodes; Milvus uses this as a core design primitive.
- For dogma's local workloads, sharding is not relevant at current scale — flag for review
  if corpus exceeds 10M vectors.

---

### Pattern 2 — DB Selection Matrix

| DB | Type | Memory | Hybrid search | Best for | Dogma relevance |
|----|------|--------|--------------|---------|-----------------|
| **LanceDB** | Embedded columnar | Low (SSD-backed) | Yes (Lance native) | Local-first RAG, embedded Python | **Dogma's chosen stack** — not in primary source |
| **pgvector** | Postgres extension | Moderate | Via `pg_bestmatch` + RRF | New RAG at moderate scale on existing Postgres | Strong Local Compute First fit |
| **Chroma** | Embedded lightweight | Low | Limited | Prototyping, local dev | Acceptable for dogma local spikes |
| **Qdrant** | Open-source Rust server | Moderate | Yes (native) | Performance + control, self-hosted | If LanceDB outgrown |
| **Weaviate** | Open-source server | Moderate | Yes (native, BM25+ANN) | Hybrid search, multimodal | If LanceDB outgrown |
| **Milvus** | Open-source, Kubernetes | High | Yes | Billion-scale, distributed | Beyond dogma's current scope |
| **Pinecone** | Managed SaaS | N/A (cloud) | Yes | Fastest time-to-production, no infra | Violates Local Compute First |
| **Faiss** | Library (Meta) | Low–High (config) | No (ANN only) | Research, custom pipelines | Building block; no metadata or filtering |

**Selection heuristic (Local Compute First order):**

```
Embedded/local first:
  → LanceDB (dogma default)
  → Chroma (prototyping only)
  → pgvector (if Postgres already present)

Self-hosted server (if embedded outgrown):
  → Qdrant (performance, small ops team)
  → Weaviate (multimodal or strong hybrid requirements)
  → Milvus (billion-scale, Kubernetes-native)

Managed SaaS (last resort):
  → Pinecone
```

---

### Pattern 3 — Index Algorithm Selection

| Algorithm | Memory | Build speed | Query speed | Dynamic inserts | When to use |
|-----------|--------|------------|------------|-----------------|-------------|
| **Flat (brute-force)** | High | Instant | O(n) — slow | Yes | < 100K vectors; exact recall required |
| **HNSW** | High | Slow | Very fast | Yes | Default for < 50M vectors with RAM budget |
| **IVF** | Low | Moderate (training) | Fast | Rebuild needed | Large static corpora, memory-constrained |
| **IVF-PQ** | Very low | Slow | Fast | Rebuild needed | Billion-scale, strong memory constraints |
| **DiskANN** | Very low (SSD) | Very slow | Moderate | Partial support | > 100M vectors, RAM cost prohibitive |

**Dogma default recommendation**: HNSW with `M=16`, `ef_construction=128`, `ef_search=64` as
a starting point. Profile recall@10 on a held-out set before increasing parameters.

---

**Canonical example**: "For new RAG applications at moderate scale, pgvector is often a good
starting point if you are already using Postgres because it minimizes operational overhead. As
needs grow, Qdrant or Weaviate become more compelling; Pinecone is ideal if you prefer fully
managed." — paraphrased from Bala Priya C, MLMastery, 2026-03-27. This heuristic aligns
directly with **Local Compute First** ([MANIFESTO.md §3](../../MANIFESTO.md#3-local-compute-first)).
Dogma extends it one step further — before pgvector, prefer LanceDB (embedded Python, no
separate Postgres process, SSD-resident, columnar-vector hybrid). The pgvector path is correct
when Postgres is already present; LanceDB is correct for greenfield Python-native workloads.

---

**Anti-pattern**: Using the wrong distance metric for the embedding model — e.g. Euclidean
distance with a model trained under cosine loss produces subtly wrong rankings. The error is
silent; queries return results but precision is degraded compared to the correct metric. Always
verify the metric in the embedding model's model card and configure the VDB index to match.
BGE-Small-EN-v1.5 recommends cosine.

**Anti-pattern**: "More vectors = better retrieval" assumption — adding every document chunk
without quality filtering increases corpus size and retrieval noise. A 2M-vector corpus of
high-quality chunks outperforms a 10M-vector corpus with 40% irrelevant chunks. Chunk quality
and deduplication matter as much as embedding quality.

**Anti-pattern**: Tuning HNSW parameters without measuring baseline recall first — increasing
`ef_construction` and `M` before profiling wastes build time and memory. Measure recall@10 on
a representative query set at default parameters; only tune if measured recall falls below the
target threshold (typically 0.90–0.95 for production RAG).

**Anti-pattern**: Dense-only retrieval for production RAG — deploying ANN without a sparse
(BM25) component misses keyword-critical queries (product codes, named entities, exact
phrases). Hybrid search with RRF is the recommended default; dense-only is appropriate only
for pure semantic search tasks where keywords are not discriminative.

---

### Known Gap — Re-ranking

The primary source does not cover **cross-encoder re-ranking** — the step after ANN retrieval
where a more expensive model scores candidate passages against the query directly. Re-ranking
is a well-established pattern (Cohere Rerank, BGE-Reranker, Jina Reranker) that consistently
improves precision@5 by 10–30% over ANN-only pipelines. This gap is noted in
[local-rag-adoption-patterns.md](local-rag-adoption-patterns.md) as requiring follow-up.
See recommendation `rec-vector-databases-explained-005` for the proposed follow-on issue.

---

### LanceDB and Dogma's Stack — Why the Absence from Surveys is Expected

LanceDB is absent from the primary source and most mainstream VDB surveys because it occupies
a distinct architectural niche: it is a **columnar-vector store**, not a traditional HNSW/IVF
server. It stores data in Lance format (built on Apache Arrow) with vectors as one column
type among many. It does not run as a network server; it is imported as a Python library
and writes to disk like SQLite. Most "VDB comparison" articles focus on server-oriented
databases (Qdrant, Weaviate, Pinecone) because those are the deployment choices that require
the most infrastructure decision-making.

Dogma's preference for LanceDB (documented in [local-rag-adoption-patterns.md](local-rag-adoption-patterns.md)
and [intelligence-architecture-synthesis.md](intelligence-architecture-synthesis.md)) is not
contradicted by its absence from this survey — it is confirmed by it. The article's own
selection heuristic (start with lowest operational overhead) points toward embedded options
first; LanceDB is simply the best-of-class embedded option for Python-native workloads.

## Recommendations

### R1 — ADOPT LanceDB as the default embedded VDB; use pgvector when Postgres is present

**Priority: High | Effort: Low | Action: Validate + document**

For all dogma-local RAG workflows, LanceDB remains the default (Local Compute First, MANIFESTO §3).
When a Postgres instance is already deployed (e.g. a client `client-values.yml` stack includes
Postgres), pgvector eliminates a dependency while providing adequate ANN performance at
moderate scale (< 5M vectors). Do not introduce a dedicated VDB server before exhausing
embedded and extension options.

**Acceptance criteria**: `intelligence-architecture-synthesis.md` and `local-rag-adoption-patterns.md`
explicitly document the selection ladder: LanceDB → pgvector → Qdrant/Weaviate → Milvus/Pinecone.

### R2 — ENFORCE metric-embedding alignment in all index configurations

**Priority: High | Effort: Low | Action: Schema or pre-commit gate**

Every VDB index declaration — whether in a Python config file, schema YAML, or MCP tool
parameter — must document both the embedding model name and the distance metric. Mismatches
are silent and cause degraded precision. Enforce this as a documentation requirement in any
RAG configuration schema; consider a `validate_rag_config.py` script that checks these two
fields are co-present and validates the metric against a known-good model-metric map.

**Acceptance criteria**: the `rag_query` MCP tool's configuration contract names both
`embedding_model` and `distance_metric` as required fields.

### R3 — ADOPT hybrid search (ANN + BM25, merged via RRF) as the default retrieval strategy

**Priority: Medium | Effort: Medium | Action: Implement + document**

Dense-only ANN retrieval misses keyword-critical queries. RRF is non-parametric (no weight
to tune) and is natively supported by Weaviate, Qdrant, and LanceDB. For dogma's current
stack (LanceDB + BGE-Small), enable LanceDB's full-text search index alongside the vector
index and merge results via RRF at query time. Update `intelligence-architecture-synthesis.md`
to reflect hybrid search as the recommended default.

**Acceptance criteria**: the RAG query path in the dogma MCP server performs ANN + BM25
retrieval and merges results via RRF before returning candidates to the calling agent.

### R4 — DOCUMENT LanceDB's absence from mainstream surveys in local-rag-adoption-patterns.md

**Priority: Low | Effort: Low | Action: Documentation update**

Add a paragraph to [local-rag-adoption-patterns.md](local-rag-adoption-patterns.md) explaining
that LanceDB does not appear in traditional VDB comparisons because it is a columnar-vector
library, not a server. This prevents future agents from treating the absence as a signal that
LanceDB is inferior or unproven, and closes a potential "why didn't we pick Qdrant?" question
that could surface during onboarding or PR review.

### R5 — RESEARCH cross-encoder re-ranking as a follow-on issue

**Priority: Medium | Effort: Medium | Action: New GitHub issue**

The primary source does not cover re-ranking. For high-precision RAG (the intent classification
and evidence retrieval use cases in dogma), a cross-encoder re-ranking step after ANN
retrieval is well-evidenced to improve precision@5 by 10–30%. Candidate models: BGE-Reranker-v2,
Jina Reranker, or Cohere Rerank API. Create a follow-on secondary research issue targeting
`docs/research/reranking-patterns.md` and referencing this document.

## Sources

| # | Title | Author | Date | URL |
|---|-------|--------|------|-----|
| 1 | Vector Databases Explained in 3 Levels of Difficulty | Bala Priya C | 2026-03-27 | https://machinelearningmastery.com/vector-databases-explained-in-3-levels-of-difficulty/ |
| 2 | What is a Vector Database? | Pinecone | — | https://www.pinecone.io/learn/vector-database/ |
| 3 | Building Applications with Vector Databases | DeepLearning.AI | — | https://www.deeplearning.ai/short-courses/building-applications-vector-databases/ |
| 4 | Top 5 Vector Databases | MLMastery | 2025-12 | https://machinelearningmastery.com/top-5-vector-databases/ |
| 5 | Build a RAG System Part VII | MLMastery | 2025-03 | https://machinelearningmastery.com/build-a-rag-system-part-vii/ |

### Internal cross-references

- [local-rag-adoption-patterns.md](local-rag-adoption-patterns.md) — dogma's canonical RAG stack (LanceDB + BGE-Small + MCP server)
- [intelligence-architecture-synthesis.md](intelligence-architecture-synthesis.md) — hybrid chunking and retrieval architecture
- [platform-agnosticism.md](platform-agnosticism.md) — `rag_query` MCP tool as the portability surface hiding VDB implementation details
