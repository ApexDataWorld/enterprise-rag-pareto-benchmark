# Results Interpretation

This guide explains the generated outputs and metrics.

## Output files

| File | Meaning |
|---|---|
| `summary_metrics.csv` | Variant-level mean metrics, cost, latency, and Pareto labels. |
| `query_metrics.csv` | Per-query metrics for each variant. |
| `statistical_comparisons.csv` | Paired sign-test comparisons against the configured baseline, with Benjamini-Hochberg correction. |
| `confidence_intervals.csv` | Bootstrap confidence intervals for selected metrics. |
| `pareto_frontier_data.csv` | Pareto labels and reasons. |
| `query_type_summary.csv` | Mean metrics grouped by query type and variant. |
| `retrieval_traces.json` | Retrieved chunk IDs, expected evidence IDs, and generated answers. |
| `run_metadata.json` | Environment, config, artifact paths, and hashes. |

## Metrics

### Recall@k

Fraction of expected evidence recovered in the retrieved top-k set.

### MRR

Mean reciprocal rank of the first relevant retrieved item.

### NDCG@k

Normalized discounted cumulative gain for the retrieved ranking.

### Context precision

Fraction of retrieved chunks that are relevant under the configured labels.

### Faithfulness

Automatic proxy measuring how much of the generated extractive answer is
supported by retrieved context.

### Hallucination risk

Automatic proxy computed from faithfulness and answer-term coverage:

```text
risk = max(0, 1 - (0.65 * faithfulness + 0.35 * answer_term_coverage))
```

This is not a substitute for human factuality assessment.

### Latency and cost

Estimated system metrics derived from transparent constants in the config. They
are useful for controlled comparison, not production capacity planning.

## Pareto-optimality

A Pareto-optimal configuration is not necessarily globally best. It means that,
within the evaluated experiment set, no other configuration improves all
selected objectives simultaneously under the implemented dominance rule.

Multiple Pareto-optimal variants can exist because enterprise workloads impose
different constraints. For example, a low-cost variant and a low-risk variant
can both be rational choices.

## Statistical comparisons

`statistical_comparisons.csv` contains paired exact sign-test outputs over
query-level values. The file includes raw p-values, Benjamini-Hochberg adjusted
p-values, and significance flags.

Statistical significance should be interpreted with operational trade-offs. A
configuration can be statistically different but still too expensive or slow for
a target workload.

## Query-type breakdown

`query_type_summary.csv` helps identify failure modes. Query types such as
multi-hop or ambiguous queries may be harder for single-pass retrieval than
fact-lookup queries. The benchmark does not claim that single-pass RAG solves all
multi-hop enterprise reasoning.
