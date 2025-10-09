env:
	python -m venv .venv && . .venv/bin/activate && pip install -e .[dev]
dev: lint test
lint:
	ruff check . && black --check .
test:
	pytest -q
eval:
	python -m trustbench_core.orchestrator --profile profiles/default.yaml
report:
	python -m trustbench_core.reports.writer --open-last
