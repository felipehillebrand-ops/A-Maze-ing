PYTHON = python3
NAME = a_maze_ing.py
CONFIG = config.txt
VENV = venv
BIN = $(VENV)/bin

export LD_LIBRARY_PATH := $(shell pwd)/mlx:$(LD_LIBRARY_PATH)

all: run

$(VENV):
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install flake8 mypy build

install: $(VENV)
	$(BIN)/pip install -e .

run: $(VENV)
	@if [ ! -d "mlx" ]; then echo "Erro: Pasta 'mlx' não encontrada!"; exit 1; fi
	$(BIN)/python3 $(NAME) $(CONFIG)

debug: $(VENV)
	$(BIN)/python3 -m pdb $(NAME) $(CONFIG)
    
clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache $(VENV)
	rm -rf dist build *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +

lint: $(VENV)
	@echo "Running flake8..."
	$(BIN)/flake8 . --exclude=$(VENV),mlx
	@echo "Running mypy..."
	$(BIN)/mypy . --exclude $(VENV) --exclude mlx --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: $(VENV)
	@echo "Running flake8..."
	$(BIN)/flake8 . --exclude=$(VENV),mlx
	@echo "Running mypy..."
	$(BIN)/mypy . --exclude $(VENV) --exclude mlx --strict

re: clean all

.PHONY: all install run debug clean lint lint-strict re
