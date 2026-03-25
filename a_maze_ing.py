import sys
from typing import Dict, Tuple, List, Union
from mazegen.generator import MazeGenerator
from display import MazeVisualizer

ConfigDict = Dict[str, Union[int, Tuple[int, int], str, bool]]


def save_maze_to_file(maze: 'MazeGenerator', output_filename: str) -> None:
    """
    Saves the maze and its solution to a file in hexadecimal format.
    """
    path = maze.solve()
    with open(output_filename, "w") as f:
        for row in maze.maze:
            hex_row = "".join(f"{cell:X}" for cell in row)
            f.write(hex_row + "\n")

        f.write("\n")
        f.write(f"{maze.entry[0]},{maze.entry[1]}\n")
        f.write(f"{maze.exit[0]},{maze.exit[1]}\n")

        trajectory = maze.get_solution_path(path)
        f.write(trajectory + "\n")
    print(f"\nMaze and path saved to {output_filename}")
    if path:
        print(f"Path found! It takes {len(path)} steps.")
    else:
        print("No path found.")


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
                if value < 0:
                    raise ValueError(f"{key} cannot be negative")
                elif value < 3:
                    raise ValueError(f"{key} must be at least 3 to "
                                     f"generate a valid maze.")
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
                if value_str != "maze.txt":
                    raise ValueError("Invalid output file, try 'maze.txt'")
            elif key == "SEED":
                value = int(value_str)
            else:
                continue

            config[key] = value

        except (ValueError, IndexError, TypeError) as e:
            is_val_err = isinstance(e, ValueError)
            custom_msgs = ["cannot be negative", "at least 3",
                           "Duplicate", "PERFECT"]
            if is_val_err and any(msg in str(e) for msg in custom_msgs):
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
        sys.stderr.write("Usage: python3 a_maze_ing.py <config_file>\n")
        sys.exit(1)

    try:

        config: ConfigDict = parse_config(sys.argv[1])
        output_filename = str(config["OUTPUT_FILE"])
        maze = MazeGenerator(config)
        entry = config["ENTRY"]
        exit_pt = config["EXIT"]

        if isinstance(entry, tuple) and isinstance(exit_pt, tuple):
            if maze.is_reserved(entry[0], entry[1]):
                raise ValueError(f"Entry {entry} collides with the '42 '"
                                 f"pattern. Please move it.")
            if maze.is_reserved(exit_pt[0], exit_pt[1]):
                raise ValueError(f"Exit {exit_pt} collides with the '42' "
                                 f"pattern. Please move it.")

        maze.generate()
        maze.display()

        print("\nSolving the maze...")
        save_maze_to_file(maze, output_filename)
        visualizer = MazeVisualizer(maze, config, save_maze_to_file)
        visualizer.run()

    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
