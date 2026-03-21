import sys
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
            sys.stderr.write("Error: Maze size does not allow the "
                             "'42' pattern. Omitting it.\n")
            return []

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

    def is_reserved(self, x: int, y: int) -> bool:
        """
        Checks if a given coordinate is part of the reserved '42' pattern.
        """
        if not self.res_cells:
            self.res_cells = self._get_reserved_42_coords()
        return (x, y) in self.res_cells

    def _get_neighbors(self, x: int, y: int,
                       visited: set) -> List[Tuple[int, int, int, int]]:
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
                if (nx, ny) not in visited:
                    neighbors.append((nx, ny, wall_me, wall_them))
        return neighbors

    def generate(self) -> None:
        """
        Generates the maze using the Recursive Backtracking algorithm.
        """
        self.res_cells = self._get_reserved_42_coords()
        self._sculpt_42()

        stack: List[Tuple[int, int]] = [self.entry]

        visited = set()
        visited.add(self.entry)

        for cell in self.res_cells:
            visited.add(cell)

        while stack:
            cx, cy = stack[-1]
            neighbors = self._get_neighbors(cx, cy, visited)

            if neighbors:
                nx, ny, wall_me, wall_them = random.choice(neighbors)
                self.maze[cy][cx] &= ~wall_me
                self.maze[ny][nx] &= ~wall_them
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

        if not self.perfect:
            self._make_imperfect()

        print(f"\nGrid {self.width}x{self.height} successfully initialized!")
        print(f"\nEntry: {self.entry}")
        print(f"Exit: {self.exit}")
        print(f"Perfect: {self.perfect}")
        print("\nMaze generated successfully!")

    def _creates_3x3_open_zone(self, x: int, y: int, nx: int, ny: int) -> bool:
        """
        Checks if removing the wall between (x, y) and (nx, ny) would create
        an open zone of 3x3 or larger.
        """
        min_x = min(x, nx)
        min_y = min(y, ny)

        for r in range(min_y - 1, min_y + 1):
            for c in range(min_x - 1, min_x + 1):
                if 0 <= r < self.height - 1 and 0 <= c < self.width - 1:
                    h1 = not (self.maze[r][c] & 2)
                    h2 = not (self.maze[r+1][c] & 2)
                    v1 = not (self.maze[r][c] & 4)
                    v2 = not (self.maze[r][c+1] & 4)

                    if h1 and h2 and v1 and v2:
                        return True
        return False

    def _make_imperfect(self) -> None:
        """
        Creates loops and multiple paths by randomly removing internal walls.
        It strictly prevents the creation of 3x3 open zones and protects
        the '42' pattern and external boundaries.
        """
        extra_paths = (self.width * self.height) // 10
        attempts = 0
        removed = 0

        while removed < extra_paths and attempts < extra_paths * 5:
            attempts += 1
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)

            if (x, y) in self.res_cells:
                continue

            direction = random.choice([1, 2, 4, 8])
            if not (self.maze[y][x] & direction):
                continue

            nx, ny = x, y
            opp_direction = 0
            if direction == 1:
                ny, opp_direction = y - 1, 4
            elif direction == 2:
                nx, opp_direction = x + 1, 8
            elif direction == 4:
                ny, opp_direction = y + 1, 1
            elif direction == 8:
                nx, opp_direction = x - 1, 2
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if (nx, ny) not in self.res_cells:
                    if not self._creates_3x3_open_zone(x, y, nx, ny):
                        self.maze[y][x] &= ~direction
                        self.maze[ny][nx] &= ~opp_direction
                        removed += 1

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
