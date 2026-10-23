# Archived aggregate results

These files transcribe the paper's domain-level summaries. They support inspection and arithmetic analysis, not reconstruction of per-task observations or new timing runs. No task-level samples, repetitions, confidence intervals, or hardware logs are supplied.

| File | Rows and units | Paper location |
|---|---|---|
| [task_sizes.csv](task_sizes.csv) | Five domains; median row/edge counts across 12 tasks in thousands; recall in percent | Table 2 |
| [quality.csv](quality.csv) | Method/domain combinations; schema and entity F1 in percent | Common-score quality table |
| [external_quality.csv](external_quality.csv) | Six pipelines; F1 and joint-row accuracy in percent | Complete-system quality table |
| [runtime.csv](runtime.csv) | Five domains; elapsed seconds and unitless ratios | Runtime table |
| [search_cost.json](search_cost.json) | Candidate percentages; component avoidance percentage; Products search seconds | Figure 2 |

An empty CSV field means not applicable, not zero. `joint_row_percent` uses smaller-source rows as the denominator. A shared row must have the correct entity link and every target attribute with a nonmissing gold counterpart must use the correct source column; omission fails. A source-only row passes when correctly abstained. Macro F1 is the unweighted mean of five domain F1 scores. Search speedup is Profile-Warm/FuseMap. Complete speedup adds preprocessing to both numerators and denominators. Published ratios are rounded to two decimals. Candidate outcomes and changed-component avoidance have different denominators and must not be combined.

The [protocol configuration](../configs/paper_protocol.json) records the paper's main candidate/score settings. It is descriptive metadata, not a launcher for absent datasets or external systems. The [analysis script](../scripts/analyze_results.py) checks ratio arithmetic, candidate-percentage totals, and equal Profile-Full/FuseMap entity scores, then computes macro summaries.

[Column coverage](column_coverage.csv) records non-null gold column pairs retained after the cap: each domain has four tasks per level and the same gold count across low, medium and high variants. The aggregate is 968/996 = 97.2%; high ambiguity retains 311/332 = 93.7%. These are column pairs, not row links or F1. The gold-schema reference adds missing gold column compatibility vectors on the original E and uses the same frozen scorer; it does not expand row candidates.

[Joint-row quality](joint_row.csv) identifies the common-score baseline behind the 61.8-to-68.5 comparison: Alternating versus FuseMap, using the same final decoding rule.

[Restart budget comparison](restart_budget.csv) records five domain summaries: seconds for preparation, single-run search, eight-start search and complete time, plus task-budget medians (`fuse_budget_s`), median completed runs and F1 percentages. The latter columns use `_f1` for percentage-valued F1. Each actual task budget is its own median FuseMap search time, not the displayed domain median. Timed F1 averages five timed trials per task, then tasks per domain; completed runs use nested medians. Complete Alt8 time is prep plus search summary. These summaries contain no individual timing traces. All ordinary methods use a common final decoder; timed restarts pay for every improved decoded checkpoint and discarded work at their deadline.
