PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

.PHONY: install test run reproduce-main reproduce-neural reproduce-chunk-sensitivity reproduce-query-type reproduce-risk-sensitivity reproduce-cost-sensitivity reproduce-latency-cost-sensitivity reproduce-hybrid-ablation reproduce-hybrid-weight-ablation reproduce-sensitivity reproduce-all paper-tables paper-figures paper-pdf paper-artifacts artifact-manifest summarize-results clean clean-results

# Install the dependency-free default package.
install:
	$(PYTHON) -m pip install -e .

# Run the unit test suite.
test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests

run: reproduce-main

# Run the dependency-free default benchmark.
reproduce-main:
	PYTHONPATH=src $(PYTHON) scripts/run_main_benchmark.py

# Run optional Sentence Transformers validation. Requires `pip install -e '.[neural]'`.
reproduce-neural:
	PYTHONPATH=src $(PYTHON) scripts/run_neural_embedding_validation.py

# Run chunk-size sensitivity experiments.
reproduce-chunk-sensitivity:
	PYTHONPATH=src $(PYTHON) scripts/run_chunk_size_sensitivity.py

# Regenerate query-type analysis from default query metrics.
reproduce-query-type:
	PYTHONPATH=src $(PYTHON) scripts/generate_query_type_analysis.py

# Run hallucination-risk weighting sensitivity.
reproduce-risk-sensitivity:
	PYTHONPATH=src $(PYTHON) scripts/run_risk_weight_sensitivity.py

# Run latency/cost sensitivity.
reproduce-cost-sensitivity:
	PYTHONPATH=src $(PYTHON) scripts/run_latency_cost_sensitivity.py

reproduce-latency-cost-sensitivity: reproduce-cost-sensitivity

# Run hybrid retrieval weight ablation.
reproduce-hybrid-ablation:
	PYTHONPATH=src $(PYTHON) scripts/run_hybrid_weight_ablation.py

reproduce-hybrid-weight-ablation: reproduce-hybrid-ablation

# Run all dependency-free sensitivity studies.
reproduce-sensitivity: reproduce-risk-sensitivity reproduce-cost-sensitivity reproduce-hybrid-ablation

# Run dependency-free reproduction targets. Neural validation is separate.
reproduce-all: reproduce-main reproduce-query-type reproduce-chunk-sensitivity reproduce-sensitivity paper-artifacts

# Generate paper-facing tables from checked-in result artifacts.
paper-tables:
	PYTHONPATH=src $(PYTHON) scripts/generate_paper_tables.py

# Regenerate default figures through the main benchmark.
paper-figures: reproduce-main

# No manuscript source is currently included.
paper-pdf:
	@echo "No manuscript LaTeX source is present in this repository yet."

paper-artifacts: paper-tables artifact-manifest

# Generate repository-level artifact manifest with hashes.
artifact-manifest:
	PYTHONPATH=src $(PYTHON) scripts/generate_artifact_manifest.py

summarize-results:
	PYTHONPATH=src $(PYTHON) scripts/summarize_checked_in_results.py

clean:
	rm -rf results/default results/chunk_size_sensitivity results/sensitivity results/run_metadata .cache

clean-results: clean
