.PHONY: test coverage lint security install clean

test:
	python -m pytest tests/ -v

coverage:
	python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-fail-under=75

lint:
	ruff check src/ tests/
	mypy src/ || true

security:
	bandit -r src/ -f json -o bandit-report.json || true
	pip-audit --desc || true

install:
	pip install -e ".[dev]"

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage bandit-report.json
