.PHONY: install test smoke lint format clean report help auth groups transactions profile balance settings api multigroup headed debug

PYTHON := python
PYTEST := pytest
SRC := src

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run all tests"
	@echo "  make smoke      - Run smoke tests only"
	@echo "  make auth       - Run auth tests"
	@echo "  make headed     - Run tests with visible browser"
	@echo "  make lint       - Run linter"
	@echo "  make format     - Format code"
	@echo "  make report     - Open Allure report"
	@echo "  make transactions - Run transaction tests"
	@echo "  make profile    - Run profile tests"
	@echo "  make balance    - Run balance tests"
	@echo "  make settings   - Run settings tests"
	@echo "  make api        - Run API-only tests"
	@echo "  make multigroup - Run multi-person group tests"
	@echo "  make clean      - Clean cache files"

install:
	pip install -e ".[dev]"
	playwright install chromium

test:
	cd $(SRC) && $(PYTEST)

smoke:
	cd $(SRC) && $(PYTEST) -m smoke

auth:
	cd $(SRC) && $(PYTEST) -m auth

groups:
	cd $(SRC) && $(PYTEST) -m groups

transactions:
	cd $(SRC) && $(PYTEST) -m transactions

profile:
	cd $(SRC) && $(PYTEST) -m profile

balance:
	cd $(SRC) && $(PYTEST) -m balance

settings:
	cd $(SRC) && $(PYTEST) -m settings

api:
	cd $(SRC) && $(PYTEST) -m api

multigroup:
	cd $(SRC) && $(PYTEST) -m multigroup

headed:
	cd $(SRC) && HEADLESS=false SLOW_MO=300 $(PYTEST)

debug:
	cd $(SRC) && HEADLESS=false SLOW_MO=500 $(PYTEST) -x -s

lint:
	ruff check $(SRC)

format:
	ruff format $(SRC)
	ruff check $(SRC) --fix

report:
	allure serve $(SRC)/allure-results

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "allure-results" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
