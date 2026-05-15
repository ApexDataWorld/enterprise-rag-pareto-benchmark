PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

.PHONY: install test run reproduce-main reproduce-neural reproduce-chunk-sensitivity reproduce-query-type reproduce-risk-sensitivity reproduce-cost-sensitivity reproduce-hybrid-ablation reproduce-sensitivity reproduce-all paper-tables paper-figures paper-pdf paper-artifacts artifact-manifest clean

install:
	$(PYTHON) -m pip install -e .

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests

run: reproduce-main

reproduce-main:
	PYTHONPATH=src $(PYTHON) scripts/run_main_benchmark.py

reproduce-neural:
	PYTHONPATH=src $(PYTHON) scripts/run_neural_embedding_validation.py

reproduce-chunk-sensitivity:
	PYTHONPATH=src $(PYTHON) scripts/run_chunk_size_sensitivity.py

reproduce-query-type:
	PYTHONPATH=src $(PYTHON) scripts/generate_query_type_analysis.py

reproduce-risk-sensitivity:
	PYTHONPATH=src $(PYTHON) scripts/run_risk_weight_sensitivity.py

reproduce-cost-sensitivity:
	PYTHONPATH=src $(PYTHON) scripts/run_latency_cost_sensitivity.py

reproduce-hybrid-ablation:
	PYTHONPATH=src $(PYTHON) scripts/run_hybrid_weight_ablation.py

reproduce-sensitivity: reproduce-risk-sensitivity reproduce-cost-sensitivity reproduce-hybrid-ablation

reproduce-all: reproduce-main reproduce-query-type reproduce-chunk-sensitivity reproduce-sensitivity paper-artifacts

paper-tables:
	PYTHONPATH=src $(PYTHON) scripts/generate_paper_tables.py

paper-figures: reproduce-main

paper-pdf:
	@echo "No manuscript LaTeX source is present in this repository yet."

paper-artifacts: paper-tables artifact-manifest

artifact-manifest:
	PYTHONPATH=src $(PYTHON) scripts/generate_artifact_manifest.py

clean:
	rm -rf results/default results/chunk_size_sensitivity results/sensitivity results/run_metadata .cache
