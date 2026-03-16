PYTHON = python3
PIP = pip3
NAME = a_maze_ing.py
CONFIG = config.txt

install:
		$(PIP) install flake8 mypy build

run:
		$(PYTHON) $(NAME) $(CONFIG)

debug:
		$(PYTHON) -m pdb $(NAME) $(CONFIG)
	
clean:
		rm -rf __pycache__ .mypy_cache .pytest_cache
		rm -rf dist build *.egg-info
		find . -type d -name "__pycache__" -exec rm -rf {} +

lint:
		flake8 .
		mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
		flake8 .
		mypy . --strict

.PHONY: install run debug clean lint lint-strict