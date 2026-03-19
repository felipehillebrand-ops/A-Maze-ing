PYTHON = python3
NAME = a_maze_ing.py
CONFIG = config.txt
VENV = venv
BIN = $(VENV)/bin

# 1. ESSENCIAL: Sem isto o Python não encontra a libmlx.so na pasta mlx
export LD_LIBRARY_PATH := $(shell pwd)/mlx:$(LD_LIBRARY_PATH)

all: run

# Regra para criar o ambiente virtual
$(VENV):
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install flake8 mypy build

# 2. ADICIONADO: 'run' agora depende de '$(VENV)'
run: $(VENV)
	@# Verificação extra para a pasta mlx
	@if [ ! -d "mlx" ]; then echo "Erro: Pasta 'mlx' não encontrada!"; exit 1; fi
	$(BIN)/python3 $(NAME) $(CONFIG)

install: $(VENV)

debug: $(VENV)
	$(BIN)/python3 -m pdb $(NAME) $(CONFIG)
    
clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache $(VENV)
	rm -rf dist build *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf mlx/__pycache__

lint: $(VENV)
	$(BIN)/flake8 . --exclude=$(VENV)
	$(BIN)/mypy . --exclude $(VENV) --ignore-missing-imports

re: clean all

.PHONY: all install run debug clean lint re