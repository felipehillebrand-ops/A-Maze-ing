*This project has been created as part of the 42 curriculum by fjose-hi, kde-arru.*

## Description

`A-Maze-ing` is a Python maze generator and visualizer project.
It reads a configuration file, builds a valid maze using a wall-bit encoding
(N/E/S/W), solves the shortest path from entry to exit, writes the output file,
and displays the maze with MLX.

Core features:
- Config parsing with validation and clear error messages.
- Maze generation with reproducibility via `SEED`.
- `42` pattern reservation when maze dimensions allow it.
- Shortest path solving (BFS).
- Graphical rendering with controls:
	- `1`: regenerate
	- `2`: show/hide shortest path
	- `3`: change palette
	- `ESC`: quit

## Instructions

### Setup

```bash
make install
```

### Run

```bash
make run
```

Equivalent direct command:

```bash
python3 a_maze_ing.py config.txt
```

### Debug

```bash
make debug
```

### Lint

```bash
make lint
```

Optional strict mode:

```bash
make lint-strict
```

### Clean

```bash
make clean
```

## Configuration File Format

One `KEY=VALUE` pair per line.
Comment lines start with `#`.

Mandatory keys:

- `WIDTH` (int): maze width in cells
- `HEIGHT` (int): maze height in cells
- `ENTRY` (`x,y`): entry coordinates
- `EXIT` (`x,y`): exit coordinates
- `OUTPUT_FILE` (str): output file path
- `PERFECT` (`True`/`False`): perfect maze mode

Optional keys:

- `SEED` (int): deterministic generation

Example:

```txt
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=12345
```

## Maze Generation Algorithm

Current algorithm: **Recursive Backtracking (Depth-First Search carving)**.

Why this algorithm:
- Simple and reliable for grid mazes.
- Naturally creates connected mazes.
- Easy to keep deterministic with seeded randomness.
- Good fit for wall-bit representation and path-solving workflows.

## Output Format

The output file writes:
1. Maze rows in hexadecimal wall-bit format.
2. A blank line.
3. Entry coordinates (`x,y`).
4. Exit coordinates (`x,y`).
5. Shortest path as `N/E/S/W` string.

## Resources

- 42 project subject (`A-Maze-ing`).
- BFS and DFS maze generation references.
- MiniLibX documentation (`mlx/docs/*`).

AI usage note:
- Used for code review, lint/type cleanup, and iterative rendering fixes.
- All generated suggestions were manually reviewed and tested before adoption.
