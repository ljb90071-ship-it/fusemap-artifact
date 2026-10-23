# FuseMap supplemental material

Companion to **FuseMap: Reoptimizing Entity Assignments to Resolve Schema
Ambiguity**. FuseMap profiles each schema mapping by solving its induced partial
entity assignment. Start with the two-row example, inspect the bounds and
component search, then browse the result tables.

## Navigate

- [Implementation](src/fusemap.py): partial assignment, optimal dual prices, transferred/reset/zero bounds, connected components, alternating optimization, diversified restarts and profiled schema search.
- [Two-row example](examples/reassignment.json) and [two-component example](examples/two_components.json).
- [Input contract and algorithm notes](docs/reference.md).
- [Evaluation parameters](configs/paper_protocol.json).
- [Result schema and coverage](results/README.md).
- [Paper-to-file map](paper-map.md).

## Run

Use Python 3.10 or later and its standard library. Run from the repository root:

```sh
python scripts/run_example.py
python scripts/run_example.py examples/two_components.json
python scripts/check_reference.py
python scripts/analyze_results.py
```

The first example starts at schema `[0]` with profile 13 and finishes at `[1]`
with profile 18. The old assignment scores 10 under the new schema. Alternating
optimization stays at 13; diversified restarts recover 18. This input has three
distinct starts, so the eight-start request completes three. The search modes
produce freshly decoded terminal row pairs. The check script compares bounds,
matchings and search paths with independent exhaustive calculations.

## Inputs and results

The implementation accepts cached integer edge contributions on a fixed
bipartite graph. Its exact dynamic-programming assignment backend supports up to
20 columns per component and breaks matching ties lexicographically. Objective
values determine profile comparisons and schema acceptance exactly. The
[algorithm guide](docs/reference.md) explains this backend and the paper's
ordered min-cost-flow decoder.

`analyze_results.py` reads the aggregate result tables and computes the paper's
comparisons. The [result dictionary](results/README.md) defines quality, coverage,
runtime units and aggregation. [Evaluation parameters](configs/paper_protocol.json)
record the retrieval, scoring and comparison settings associated with those tables.
