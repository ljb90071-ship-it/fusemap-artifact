# FuseMap supplemental material

FuseMap profiles each schema mapping by solving its induced partial entity assignment. This repository accompanies **FuseMap: Reoptimizing Entity Assignments to Resolve Schema Ambiguity**. Start with the two-row example, then inspect the bounds and component search, and finally the archived result tables.

## Navigation

- [Reference implementation](src/fusemap.py): partial assignment, optimal dual prices, transferred/reset/zero bounds, connected components, exact alternating optimization, deterministic diversified restarts, and best-improvement profiled schema search.
- [Two-row example](examples/reassignment.json) and [two-component example](examples/two_components.json).
- [Input contract and algorithm notes](docs/reference.md).
- [Experiment parameters](configs/paper_protocol.json).
- [Result schema and coverage](results/README.md).
- [Paper-to-file map](paper-map.md).

## Run locally

Python 3.10 or newer; standard library only. From this directory:

```sh
python scripts/run_example.py
python scripts/run_example.py examples/two_components.json
python scripts/check_reference.py
python scripts/analyze_results.py
```

The first example starts at schema `[0]` with profile 13 and finishes at `[1]` with profile 18. Its fixed old assignment would score only 10 under the new schema. The exact alternating baseline stays at profile 13. Completing diversified restarts recovers 18 on this example; only three distinct starts exist, so the eight-start request stops at three. All three search modes should return the same path and freshly decoded terminal row pairs. The check script computes independent exhaustive matchings and compares search paths on small generated inputs. The last command analyzes archived aggregate results; it does not rerun the paper experiments.

## Implementation scope

The reference consumes cached integer edge contributions on a fixed bipartite graph. It implements the search and certificate logic with an exact exponential dynamic-programming assignment backend, bounded to 20 columns per component. It does not implement candidate retrieval, representation training, large-scale warm assignment optimization, or the external comparison pipelines. Final matching ties use lexicographic row tuples in this backend; the paper's production decoding uses ordered min-cost flow. Profile values and schema acceptance depend on exact objectives, not a floating-point tolerance. No external datasets, model downloads, credentials, or optional packages are needed.
