import random
from typing import List, Tuple, Any


class MazeGenerator:
    def __init__(self, config: dict):
        """
        Initializes the maze generator with the given configuration.
        """
        self.width: int = config["WIDTH"]
        self.height: int = config["HEIGHT"]
        self.entry: Tuple[int, int] = config["ENTRY"]
        self.exit: Tuple[int, int] = config["EXIT"]
        self.perfect: bool = config["PERFECT"]

        seed_value: Any = config.get("SEED")
        if seed_value is not None:
            random.seed(seed_value)

        self.maze: List[List[int]] = [
            [15 for _ in range(self.width)]
            for _ in range(self.height)
        ]
        self.res_cells: List[Tuple[int, int]] = []

    def _get_reserved_42_coords(self) -> List[Tuple[int, int]]:
        """
        Calculates and returns the coordinates reserved for the '42' pattern.
        """
        pattern_42 = [
            [1, 0, 1, 0, 1, 1, 1],
            [1, 0, 1, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1]
        ]

        p_height = len(pattern_42)
        p_width = len(pattern_42[0])

        reserved = []
        if self.width < p_width + 2 or self.height < p_height + 2:
            print("Error: Maze too small to draw the '42' pattern.")
            return reserved

        start_x = (self.width - p_width) // 2
        start_y = (self.height - p_height) // 2

        for y in range(p_height):
            for x in range(p_width):
                if pattern_42[y][x] == 1:
                    reserved.append((start_x + x, start_y + y))
        return reserved

    def _sculpt_42(self) -> None:
        """
        Ensures the '42' pattern cells remain as full walls (15).
        """
        for x, y in self.res_cells:
            self.maze[y][x] = 15

    def _open_external_wall(self, coords: Tuple[int, int]) -> None:
        """Opens the wall that faces the outside of the maze."""
        x, y = coords
        if y == 0:
            self.maze[y][x] &= ~1
        elif y == self.height - 1:
            self.maze[y][x] &= ~4

        if x == 0:
            self.maze[y][x] &= ~8
        elif x == self.width - 1:
            self.maze[y][x] &= ~2

    def _get_neighbors(self, x: int,
                       y: int) -> List[Tuple[int, int, int, int]]:
        """
        Returns a list of valid neighbors that have not been visited yet.
        """
        neighbors: List[Tuple[int, int, int, int]] = []
        directions = [
            (0, -1, 1, 4),
            (0, 1, 4, 1),
            (1, 0, 2, 8),
            (-1, 0, 8, 2)
        ]

        for dx, dy, wall_me, wall_them in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if self.maze[ny][nx] == 15 and (nx, ny) not in self.res_cells:
                    neighbors.append((nx, ny, wall_me, wall_them))
        return neighbors

    def generate(self) -> None:
        """
        Generates the maze using the Recursive Backtracking algorithm.
        """
        self.res_cells = self._get_reserved_42_coords()
        self._sculpt_42()

        stack: List[Tuple[int, int]] = [self.entry]

        while stack:
            cx, cy = stack[-1]
            neighbors = self._get_neighbors(cx, cy)

            if neighbors:
                nx, ny, wall_me, wall_them = random.choice(neighbors)
                self.maze[cy][cx] -= wall_me
                self.maze[ny][nx] -= wall_them
                stack.append((nx, ny))
            else:
                stack.pop()

        self._open_external_wall(self.entry)
        self._open_external_wall(self.exit)

        print(f"\nGrid {self.width}x{self.height} successfully initialized!")
        print(f"\nEntry: {self.entry}")
        print(f"Exit: {self.exit}")
        print(f"Perfect: {self.perfect}")
        print("\nMaze generated successfully!")

    def display(self) -> None:
        """
        Displays the current state of the maze grid in Uppercase Hexadecimal.
        """
        print("\n--- Current Maze Grid (Hexadecimal) ---")
        for row in self.maze:
            print(" ".join(f"{cell:X}" for cell in row))
