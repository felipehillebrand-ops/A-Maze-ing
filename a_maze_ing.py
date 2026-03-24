import sys
from typing import Dict, Tuple, List, Union
from mazegen.generator import MazeGenerator
from display import MazeVisualizer


ConfigDict = Dict[str, Union[int, Tuple[int, int], str, bool]]


def parse_config(filename: str) -> ConfigDict:
    """
    Parses the configuration file and returns a dictionary of settings.
    """
    config: ConfigDict = {}
    try:
        with open(filename, "r") as f:
            lines: List[str] = [
                line.strip() for line in f
                if line.strip() and not line.startswith("#")
            ]
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file '{filename}' not found!")

    for line in lines:
        try:
            key, raw_value = line.split("=")
        except ValueError:
            raise ValueError(f"Invalid line in config: '{line}'."
                             f"Expected format KEY=VALUE")
        key = key.strip().upper()
        value_str = raw_value.strip()

        if key in config:
            raise ValueError(f"Duplicate key found: '{key}'. "
                             f"Each setting must be defined only once.")
        value: Union[int, bool, Tuple[int, int], str]

        try:
            if key in ["WIDTH", "HEIGHT"]:
                value = int(value_str)
            elif key in ["ENTRY", "EXIT"]:
                x, y = value_str.split(",")
                value = (int(x), int(y))
            elif key == "PERFECT":
                normalized = value_str.lower()
                if normalized == "true":
                    value = True
                elif normalized == "false":
                    value = False
                else:
                    raise ValueError("PERFECT must be 'true' or 'false'")
            elif key == "OUTPUT_FILE":
                value = value_str
            elif key == "SEED":
                value = int(value_str)
            else:
                continue

            config[key] = value

        except (ValueError, IndexError, TypeError) as e:
            if isinstance(e, ValueError) and ("Duplicate" in str(e)
                                              or "PERFECT" in str(e)):
                raise e
            raise ValueError(f"Invalid value for '{key}':"
                             f"'{value_str}'") from e

    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
    for req in required:
        if req not in config:
            raise ValueError(f"Missing required configuration key: {req}")

    width = config.get("WIDTH")
    height = config.get("HEIGHT")
    entry = config.get("ENTRY")
    exit_point = config.get("EXIT")

    if not isinstance(width, int) or not isinstance(height, int):
        raise ValueError("WIDTH and HEIGHT must be integers")
    if width <= 0 or height <= 0:
        raise ValueError("WIDTH and HEIGHT must be greater than zero")

    if isinstance(entry, tuple) and isinstance(exit_point, tuple):
        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ValueError("Entry coordinates are out of maze bounds")
        if not (0 <= exit_point[0] < width and 0 <= exit_point[1] < height):
            raise ValueError("Exit coordinates are out of maze bounds")
        if entry == exit_point:
            raise ValueError("Entry and exit cannot be the same cell")

    return config


def main() -> None:
    """
    Main function to run the A-Maze-ing program.
    """

    if len(sys.argv) != 2:
        sys.stderr.write("Error: Invalid number of arguments.\n")
        sys.stderr.write("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    try:
        config: ConfigDict = parse_config(sys.argv[1])
        maze = MazeGenerator(config)
        maze.generate()
        maze.display()

        print("\nSolving the maze...")
        path = maze.solve()

        output_filename = str(config["OUTPUT_FILE"])

        with open(output_filename, "w") as f:
            for row in maze.maze:
                hex_row = "".join(f"{cell:X}" for cell in row)
                f.write(hex_row + "\n")

            f.write("\n")
            f.write(f"{maze.entry[0]},{maze.entry[1]}\n")
            f.write(f"{maze.exit[0]},{maze.exit[1]}\n")

            trajectory = maze.get_solution_path(path)
            f.write(trajectory + "\n")

        print(f"\nSuccess! Maze and path saved to {output_filename}")

        if path:
            print(f"Path found! It takes {len(path)} steps.")
        else:
            print("No path found.")

        visualizer = MazeVisualizer(maze, path)
        visualizer.run()

    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
