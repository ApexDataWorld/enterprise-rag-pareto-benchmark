# Troubleshooting

## `ModuleNotFoundError: No module named 'rag_pareto'`

Install the package or set `PYTHONPATH`:

```bash
python3 -m pip install -e .
```

or:

```bash
PYTHONPATH=src python -m rag_pareto.cli run --config configs/default.yaml
```

## Neural dependencies are missing

If `make reproduce-neural` fails with a Sentence Transformers import error:

```bash
python3 -m pip install -e '.[neural]'
make reproduce-neural
```

## Sentence Transformer model download fails

The optional neural validation may need internet access or a populated local
cache. Use the deterministic default benchmark if model download is unavailable:

```bash
make reproduce-main
```

## Empty or missing results

Check:

- `corpus_path` in the config;
- `questions_path` in the config;
- `output_dir` permissions;
- that the command completed without traceback.

## Chunk IDs do not match relevance labels

`relevant_chunk_ids` depend on chunk size and overlap. If you change chunking,
review chunk-level labels or use document-level labels.

## LaTeX/PDF generation is missing

This repository currently provides paper-facing tables and figures, but it does
not require a manuscript LaTeX build for benchmark reproduction. A local TeX
distribution is needed if a separate manuscript source is added and compiled.

## Different results across runs

Check:

- `seed`;
- config file;
- Python version;
- dependency versions for optional runs;
- whether the same `output_dir` was overwritten;
- whether optional neural model/cache changed.
