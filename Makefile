.PHONY: install install-api test validate benchmark search api docker clean

PYTHON ?= python3
CORPUS := data/v1/corpus.jsonl
QUERIES := data/v1/queries.jsonl
THRESHOLDS := config/regression.json
ARTIFACT := artifacts/benchmark.json

install:
	$(PYTHON) -m pip install -e .

install-api:
	$(PYTHON) -m pip install -e '.[api]'

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

validate:
	PYTHONPATH=src $(PYTHON) -m rag_eval_workbench.cli validate --corpus $(CORPUS) --queries $(QUERIES)

benchmark:
	PYTHONPATH=src $(PYTHON) -m rag_eval_workbench.cli benchmark --corpus $(CORPUS) --queries $(QUERIES) --thresholds $(THRESHOLDS) --output $(ARTIFACT)

search:
	PYTHONPATH=src $(PYTHON) -m rag_eval_workbench.cli search "prompt injection defense" --corpus $(CORPUS) -k 3

api:
	uvicorn rag_eval_workbench.api:application --factory --host 127.0.0.1 --port 8000

docker:
	docker build -t rag-eval-workbench .
	docker run --rm -p 8000:8000 rag-eval-workbench

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf build dist *.egg-info src/*.egg-info artifacts/*.json
