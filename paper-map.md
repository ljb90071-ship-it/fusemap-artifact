# Paper-to-file map

| Paper claim or object | Material | What can be checked |
|---|---|---|
| Section 2 objective and Table 1 | [example](examples/reassignment.json), [runner](scripts/run_example.py) | Fixed-link score 10 versus profiled score 18; original profile 13 |
| Section 2 role constraints | [neighbors and valid](src/fusemap.py) | Partial injection, replacements, swaps, null |
| Section 3 dual repair and reset | [bounds](src/fusemap.py), [checks](scripts/check_reference.py) | Exact lower/upper bounds versus exhaustive assignment |
| Section 3 component refinement / Algorithm 1 | [Problem.search](src/fusemap.py), [two components](examples/two_components.json) | Full/transferred/zero search paths and solve counters |
| Section 3 exact selection semantics | [reference notes](docs/reference.md) | Stable ties and rational objective comparisons |
| Section 4 experimental design | [protocol](configs/paper_protocol.json) | Candidate, score and aggregation parameters |
| Workload, coverage, quality and runtime tables; Figure 2 | [result index](results/README.md), [analysis](scripts/analyze_results.py) | Archived values and arithmetic |

The supplemental code demonstrates core optimization on small cached graphs. It does not cover the full retrieval/learning pipeline, external baselines, large benchmark execution, or the paper's min-cost-flow implementation. The component and dual checks test mathematical behavior independently of archived quality and timing data.

The column-candidate coverage table maps to [column_coverage.csv](results/column_coverage.csv); the named Alternating/FuseMap joint-row comparison maps to [joint_row.csv](results/joint_row.csv). Section 3 execution semantics maps to `Problem.decode` and the terminal-tie regression in the check script. Its updated scan-cost expression counts cached reads s separately from nonzero weight updates z; the reference still recomputes full component dictionaries rather than implementing sparse delta scans.

The restart initialization equation maps to `Problem.restart_starts`; the eight-start comparator maps to `alternating_restarts`. The matched-time comparison maps to [restart_budget.csv](results/restart_budget.csv) and the protocol configuration. The two-row example demonstrates both the alternating trap and successful recovery by restarting; it does not assert that profiling dominates every restart on every instance.
