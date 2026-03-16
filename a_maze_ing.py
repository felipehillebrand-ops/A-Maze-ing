from typing import Dict, Any, Tuple, List, Union
from maze_generator import MazeGenerator


ConfigDict = Dict[str, Union[int, bool, Tuple[int, int]]]


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
        key = key.strip()
        value_str = raw_value.strip()
        value: Any
        try:
            if key in ["WIDTH", "HEIGHT"]:
                value = int(value_str)
            elif key in ["ENTRY", "EXIT"]:
                x, y = value_str.split(",")
                value = (int(x), int(y))
            elif key == "PERFECT":
                value = value_str.lower() == "true"
            else:
                value = value_str
        except Exception:
            raise ValueError(f"Invalid value for '{key}': '{value_str}'")
        config[key] = value

    width = config.get("WIDTH")
    height = config.get("HEIGHT")
    entry = config.get("ENTRY")
    exit_point = config.get("EXIT")

    if not isinstance(width, int) or not isinstance(height, int):
        raise ValueError("WIDTH and HEIGHT must be integers")
    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be greater than zero")

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
    config: ConfigDict = parse_config("config.txt")
    maze = MazeGenerator(config)
    maze.generate()
    maze.display()


if __name__ == "__main__":
    main()
