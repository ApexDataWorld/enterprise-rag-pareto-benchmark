# Contributing

## Scope

This repository is a research benchmark and reproducibility package for
enterprise RAG configuration evaluation. Contributions should preserve the
default dependency-free benchmark path unless a change explicitly targets an
optional validation experiment.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e '.[dev]'
```

Optional neural validation requires:

```bash
python3 -m pip install -e '.[neural]'
```

## Running tests

```bash
make test
```

The default tests should not require external API keys, hosted vector databases,
or neural model downloads.

## Running benchmark experiments

```bash
make reproduce-main
make reproduce-chunk-sensitivity
make reproduce-query-type
make reproduce-sensitivity
make artifact-manifest
```

Use `make reproduce-neural` only after installing the neural extra.

## Code style

- Python 3.10+.
- Use type hints where practical.
- Keep deterministic behavior for the default benchmark.
- Keep tests deterministic.
- Do not require external APIs for the default path.
- Keep configs versioned.
- Do not add result claims without regenerated artifacts under `results/`.

Optional tools are configured in `pyproject.toml`:

```bash
ruff check .
black .
```

## Adding a new configuration

1. Add or copy a YAML config in `configs/`.
2. Use a unique `output_dir`.
3. Give every variant a unique `name`.
4. Run the config:

   ```bash
   PYTHONPATH=src python -m rag_pareto.cli run --config configs/your_config.yaml
   ```

5. Review `summary_metrics.csv`, `pareto_frontier_data.csv`, traces, and
   metadata before documenting any result.

## Adding a new metric

1. Add query-level metric logic in `src/rag_pareto/metrics.py`.
2. Add aggregation support if needed.
3. Add tests with small deterministic inputs.
4. Update `docs/RESULTS_INTERPRETATION.md`.
5. Regenerate affected artifacts.

Do not change existing metric formulas without documenting the reason and
regenerating all dependent results.

## Adding a new corpus

1. Create JSONL documents and queries using the formats in
   `docs/CUSTOM_CORPUS.md`.
2. Add a new config that points to the custom files.
3. Use a unique output directory.
4. Remember that `relevant_chunk_ids` depend on chunking.

Do not commit secrets, private customer data, PHI, or proprietary content.

## Pull request checklist

- [ ] Tests pass.
- [ ] README/docs updated if behavior changed.
- [ ] New configs have unique output directories.
- [ ] Generated artifacts are either committed intentionally or excluded intentionally.
- [ ] No unsupported claims added to paper-facing docs.
- [ ] Default benchmark remains dependency-free.
- [ ] No fake DOI, venue acceptance, or artifact badge is added.

## Reporting issues

Use the GitHub issue templates. Include:

- command used;
- config file;
- Python version;
- operating system;
- relevant logs or traceback;
- expected output file, if applicable.
