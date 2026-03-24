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
	$(BIN)/flake8 a_maze_ing.py display.py mazegen --exclude=$(VENV),.venv,mlx
	$(BIN)/mypy a_maze_ing.py display.py mazegen --exclude '(^venv/|^\.venv/|^mlx/)' --follow-imports=skip --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: $(VENV)
	$(BIN)/flake8 a_maze_ing.py display.py mazegen --exclude=$(VENV),.venv,mlx
	$(BIN)/mypy a_maze_ing.py display.py mazegen --exclude '(^venv/|^\.venv/|^mlx/)' --follow-imports=skip --strict

re: clean all

.PHONY: all install run debug clean lint lint-strict re
