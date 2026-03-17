PYTHON = python3
PIP = pip3
NAME = a_maze_ing.py
CONFIG = config.txt
VENV = venv
BIN = $(VENV)/bin

all: run

install:
		$(PYTHON) -m venv $(VENV)
		$(BIN)/pip install --upgrade pip
		$(BIN)/pip install flake8 mypy build

run:
		$(BIN)/python $(NAME) $(CONFIG)

debug:
		$(BIN)/python -m pdb $(NAME) $(CONFIG)
	
clean:
		rm -rf __pycache__ .mypy_cache .pytest_cache $(VENV)
		rm -rf dist build *.egg-info
		find . -type d -name "__pycache__" -exec rm -rf {} +

lint:
		$(BIN)/flake8 . --exclude=$(VENV)
		$(BIN)/mypy . --exclude $(VENV) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
		$(BIN)/flake8 . --exclude=$(VENV)
		$(BIN)/mypy . --strict --exclude $(VENV)

.PHONY: all install run debug clean lint lint-strict