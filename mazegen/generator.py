import random
from collections import deque
from typing import List, Tuple, Any, Dict, Optional


class MazeGenerator:
    def __init__(self, config: Dict[str, Any]):
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

        reserved: List[Tuple[int, int]] = []
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
        self.maze = [
            [15 for _ in range(self.width)]
            for _ in range(self.height)
        ]
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

        print(f"\nGrid {self.width}x{self.height} successfully initialized!")
        print(f"\nEntry: {self.entry}")
        print(f"Exit: {self.exit}")
        print(f"Perfect: {self.perfect}")
        print("\nMaze generated successfully!")

    def solve(self) -> List[Tuple[int, int]]:
        """
        Solves the maze using the Breadth-First Search (BFS) algorithm.
        Returns the shortest path as a list of coordinates.
        """
        start = self.entry
        goal = self.exit
        queue = deque([start])
        parent: Dict[Tuple[int, int],
                     Optional[Tuple[int, int]]] = {start: None}

        while queue:
            curr_x, curr_y = queue.popleft()
            if (curr_x, curr_y) == goal:
                return self._reconstruct_path(parent, goal)

            directions = [
                (0, -1, 1),
                (1, 0, 2),
                (0, 1, 4),
                (-1, 0, 8)
            ]

            for dx, dy, wall_bit in directions:
                nx, ny = curr_x + dx, curr_y + dy

                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if not (self.maze[curr_y][curr_x] & wall_bit):
                        if (nx, ny) not in parent:
                            parent[(nx, ny)] = (curr_x, curr_y)
                            queue.append((nx, ny))
        return []

    def _reconstruct_path(
        self,
        parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]],
        goal: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """
        Helper method to backtrack from the goal to the start using
        the parent dictionary.
        """
        path: List[Tuple[int, int]] = []
        curr: Optional[Tuple[int, int]] = goal
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        return path[::-1]

    def get_solution_path(self, path: List[Tuple[int, int]]) -> str:
        """
        Converts the BFS path coordinates into a sequence
        of N, E, S, W letters.
        """
        if not path or len(path) < 2:
            return ""

        directions = []
        for i in range(len(path) - 1):
            curr = path[i]
            nxt = path[i + 1]

            dx = nxt[0] - curr[0]
            dy = nxt[1] - curr[1]

            if dx == 1:
                directions.append("E")
            elif dx == -1:
                directions.append("W")
            elif dy == 1:
                directions.append("S")
            elif dy == -1:
                directions.append("N")
        return "".join(directions)

    def display(self) -> None:
        """
        Displays the current state of the maze grid in Uppercase Hexadecimal.
        """
        print("\n--- Current Maze Grid (Hexadecimal) ---")
        for row in self.maze:
            print(" ".join(f"{cell:X}" for cell in row))
