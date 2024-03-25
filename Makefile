.PHONY: check test build

check:
	ruff format --check
	ruff check
	mypy .
	pytest

test:
	pytest

build:
	# Requires setuptools, wheel, and build deps
	python -m build

