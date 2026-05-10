.PHONY: run test clean

run:
	PYTHONPATH=src python -m rag_pareto.cli run --config configs/default.yaml

test:
	PYTHONPATH=src python -m unittest discover -s tests

clean:
	rm -rf results/default figures/*.svg tables/*.csv
