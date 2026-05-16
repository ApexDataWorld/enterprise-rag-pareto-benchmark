# Makefile Targets

The Makefile uses `.venv/bin/python` when a local virtual environment exists;
otherwise it uses `python3`.

## install

Installs the dependency-free package.

```bash
make install
```

Output: editable local install.

Runtime category: short.

## test

Runs the unit tests.

```bash
make test
```

Wrapped command:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

Runtime category: short.

## reproduce-main

Runs the dependency-free default benchmark.

```bash
make reproduce-main
```

Expected outputs:

- `results/default/tables/summary_metrics.csv`
- `results/default/tables/pareto_frontier_data.csv`
- `results/default/figures/*.pdf`
- `results/default/run_metadata.json`

Runtime category: short.

## reproduce-neural

Runs optional Sentence Transformers validation.

```bash
python3 -m pip install -e '.[neural]'
make reproduce-neural
```

Expected output: `results/neural_embedding_validation/`.

Runtime category: medium. Requires optional neural dependencies.

## reproduce-chunk-sensitivity

Runs chunk-size sensitivity experiments.

```bash
make reproduce-chunk-sensitivity
```

Expected output: `results/chunk_size_sensitivity/`.

Runtime category: medium.

## reproduce-query-type

Generates query-type analysis.

```bash
make reproduce-query-type
```

Expected output: `results/query_type_analysis.csv`.

Runtime category: short.

## reproduce-risk-sensitivity

Runs hallucination-risk weighting sensitivity.

```bash
make reproduce-risk-sensitivity
```

Expected output: `results/sensitivity/hallucination_weighting.csv`.

Runtime category: short.

## reproduce-cost-sensitivity

Runs latency/cost sensitivity.

```bash
make reproduce-cost-sensitivity
```

Expected output: `results/sensitivity/latency_cost_sensitivity.csv`.

Runtime category: short.

## reproduce-latency-cost-sensitivity

Alias for `reproduce-cost-sensitivity`.

```bash
make reproduce-latency-cost-sensitivity
```

Runtime category: short.

## reproduce-hybrid-ablation

Runs hybrid-weight ablation.

```bash
make reproduce-hybrid-ablation
```

Expected output: `results/sensitivity/hybrid_weight_ablation.csv`.

Runtime category: short.

## reproduce-hybrid-weight-ablation

Alias for `reproduce-hybrid-ablation`.

```bash
make reproduce-hybrid-weight-ablation
```

Runtime category: short.

## reproduce-sensitivity

Runs dependency-free sensitivity studies:

```bash
make reproduce-sensitivity
```

This includes risk weighting, latency/cost, and hybrid-weight sensitivity.

Runtime category: medium.

## reproduce-all

Runs dependency-free reproduction targets and paper artifact generation.

```bash
make reproduce-all
```

This target intentionally does not run neural validation because neural
validation requires optional dependencies.

Runtime category: medium.

## paper-tables

Generates paper-facing table artifacts from checked-in result files.

```bash
make paper-tables
```

Expected output: `paper/tables/`, if paper table generation is enabled.

Runtime category: short.

## paper-figures

Regenerates default figures through the main benchmark.

```bash
make paper-figures
```

Runtime category: short.

## paper-pdf

Currently prints a message because no manuscript LaTeX source is required for
the repository artifact.

```bash
make paper-pdf
```

Runtime category: short.

## paper-artifacts

Runs table generation and artifact manifest generation.

```bash
make paper-artifacts
```

Runtime category: short.

## artifact-manifest

Generates repository-level artifact hashes.

```bash
make artifact-manifest
```

Expected output: `results/run_metadata/final_artifact_manifest.json`.

Runtime category: short.

## summarize-results

Prints a README-safe summary from checked-in result CSV files.

```bash
make summarize-results
```

Runtime category: short.

## clean and clean-results

Deletes generated result directories and `.cache`.

```bash
make clean
make clean-results
```

Use with care.
