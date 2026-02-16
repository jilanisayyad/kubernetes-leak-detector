PYTHON ?= python3
VENV_DIR ?= .venv
PIP = $(VENV_DIR)/bin/pip
CLI = $(VENV_DIR)/bin/kube-leak-detector
PY = $(VENV_DIR)/bin/python
TWINE = $(VENV_DIR)/bin/twine
COLOR ?= --color

.PHONY: venv install run run-ci tools build publish clean

venv:
	$(PYTHON) -m venv $(VENV_DIR)

install: venv
	$(PIP) install -e .

run: install
	$(CLI) $(COLOR) || true

run-ci: install
	$(CLI) $(COLOR)

tools: venv
	$(PIP) install -U build twine

build: tools
	$(PY) -m build

publish: build
	$(TWINE) upload dist/*

clean:
	rm -rf dist build *.egg-info
