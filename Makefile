.PHONY: install lint test sample check

install:
	python -m pip install --upgrade pip
	pip install -e .[dev]

lint:
	ruff check .

test:
	pytest -q

sample:
	stock-brushup sample --output reports

check: install lint test sample
