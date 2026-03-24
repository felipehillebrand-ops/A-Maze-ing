import time
import random
from typing import Any, Dict, List, Optional, Tuple

from mlx import mlx

WIN_WIDTH = 900
WIN_HEIGHT = 800
OFFSET = 24
HUD_HEIGHT = 38
PATH_STEP_INTERVAL = 0.035
PATH_TARGET_STEPS = 200


class MazeVisualizer:
    def __init__(
        self,
        maze_instance: Any,
        solution_path: Optional[List[Tuple[int, int]]] = None,
    ) -> None:
        self.maze = maze_instance
        self.solution_path: List[Tuple[int, int]] = solution_path or []
        self.pattern_cells = set(getattr(self.maze, "res_cells", []))
        self.show_solution = True
        self.palette = self._generate_random_palette()
        self.needs_render = True
        self.path_visible_segments = 0
        self.path_animating = False
        self.last_path_step_at = 0.0

        self.cell_w = 1
        self.cell_h = 1
        self.wall_thickness = 1

        self.m = mlx.Mlx()
        self.mlx_ptr = self.m.mlx_init()
        self.win_ptr = self.m.mlx_new_window(
            self.mlx_ptr,
            WIN_WIDTH,
            WIN_HEIGHT,
            "A-Maze-ing 42",
        )

        self.img_ptr = self.m.mlx_new_image(
            self.mlx_ptr,
            WIN_WIDTH,
            WIN_HEIGHT,
        )
        raw_addr = self.m.mlx_get_data_addr(self.img_ptr)
        self.img_data = raw_addr[0]
        self.bits_per_pixel = int(raw_addr[1])
        self.stride = int(raw_addr[2])
        self.bytes_per_pixel = max(3, self.bits_per_pixel // 8)

        self.m.mlx_key_hook(self.win_ptr, self.handle_keys, self)
        self.m.mlx_hook(self.win_ptr, 17, 0, self.handle_close, self)
        self.m.mlx_loop_hook(self.mlx_ptr, self._loop_handler, self)

        self._calc_geometry()

    def _update_solution(self) -> None:
        self.solution_path = self.maze.solve()
        self.pattern_cells = set(getattr(self.maze, "res_cells", []))
        self._calc_geometry()
        self._restart_path_animation()

    def _max_path_segments(self) -> int:
        return max(0, len(self.solution_path) - 1)

    def _path_step_size(self) -> int:
        max_segments = self._max_path_segments()
        if max_segments == 0:
            return 1
        return max(1, max_segments // PATH_TARGET_STEPS)

    def _restart_path_animation(self) -> None:
        max_segments = self._max_path_segments()
        if self.show_solution and max_segments > 0:
            self.path_visible_segments = 0
            self.path_animating = True
            self.last_path_step_at = 0.0
        else:
            self.path_visible_segments = max_segments
            self.path_animating = False

    def _palette(self) -> Dict[str, int]:
        return self.palette

    def _rgb_to_int(self, rgb: Tuple[int, int, int]) -> int:
        red, green, blue = rgb
        return (red << 16) | (green << 8) | blue

    def _brightness(self, rgb: Tuple[int, int, int]) -> float:
        red, green, blue = rgb
        return (0.299 * red) + (0.587 * green) + (0.114 * blue)

    def _random_bright_color(
        self,
        min_channel: int = 90,
    ) -> Tuple[int, int, int]:
        return (
            random.randint(min_channel, 255),
            random.randint(min_channel, 255),
            random.randint(min_channel, 255),
        )

    def _generate_random_palette(self) -> Dict[str, int]:
        bg_rgb = (
            random.randint(0, 28),
            random.randint(0, 28),
            random.randint(0, 28),
        )

        wall_rgb = self._random_bright_color(70)
        path_rgb = self._random_bright_color(110)
        entry_rgb = self._random_bright_color(120)
        exit_rgb = self._random_bright_color(120)
        pattern_rgb = self._random_bright_color(80)

        ui_rgb = (245, 245, 245)
        if self._brightness(bg_rgb) > 110:
            ui_rgb = (20, 20, 20)

        return {
            "bg": self._rgb_to_int(bg_rgb),
            "wall": self._rgb_to_int(wall_rgb),
            "path": self._rgb_to_int(path_rgb),
            "entry": self._rgb_to_int(entry_rgb),
            "exit": self._rgb_to_int(exit_rgb),
            "pattern": self._rgb_to_int(pattern_rgb),
            "ui": self._rgb_to_int(ui_rgb),
        }

    def _calc_geometry(self) -> None:
        available_w = WIN_WIDTH - (OFFSET * 2)
        available_h = WIN_HEIGHT - (OFFSET * 2) - HUD_HEIGHT
        self.cell_w = max(4, available_w // self.maze.width)
        self.cell_h = max(4, available_h // self.maze.height)
        self.wall_thickness = max(1, min(self.cell_w, self.cell_h) // 7)

    def _put_pixel(self, x: int, y: int, color: int) -> None:
        if x < 0 or y < 0 or x >= WIN_WIDTH or y >= WIN_HEIGHT:
            return
        idx = (y * self.stride) + (x * self.bytes_per_pixel)
        self.img_data[idx] = color & 0xFF
        self.img_data[idx + 1] = (color >> 8) & 0xFF
        self.img_data[idx + 2] = (color >> 16) & 0xFF
        if self.bytes_per_pixel > 3:
            self.img_data[idx + 3] = 0xFF

    def _draw_rect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: int,
    ) -> None:
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(WIN_WIDTH, x + width)
        y1 = min(WIN_HEIGHT, y + height)
        if x1 <= x0 or y1 <= y0:
            return

        color_bytes = bytearray(self.bytes_per_pixel)
        color_bytes[0] = color & 0xFF
        color_bytes[1] = (color >> 8) & 0xFF
        color_bytes[2] = (color >> 16) & 0xFF
        if self.bytes_per_pixel > 3:
            color_bytes[3] = 0xFF

        row_fill = bytes(color_bytes) * (x1 - x0)
        for py in range(y0, y1):
            row_start = (py * self.stride) + (x0 * self.bytes_per_pixel)
            row_end = row_start + ((x1 - x0) * self.bytes_per_pixel)
            self.img_data[row_start:row_end] = row_fill

    def _draw_hline(
        self,
        x0: int,
        x1: int,
        y: int,
        color: int,
        thickness: Optional[int] = None,
    ) -> None:
        line_thickness = thickness or self.wall_thickness
        start = min(x0, x1)
        width = abs(x1 - x0) + 1
        self._draw_rect(
            start,
            y - (line_thickness // 2),
            width,
            line_thickness,
            color,
        )

    def _draw_vline(
        self,
        x: int,
        y0: int,
        y1: int,
        color: int,
        thickness: Optional[int] = None,
    ) -> None:
        line_thickness = thickness or self.wall_thickness
        start = min(y0, y1)
        height = abs(y1 - y0) + 1
        self._draw_rect(
            x - (line_thickness // 2),
            start,
            line_thickness,
            height,
            color,
        )

    def _clear_background(self, color: int) -> None:
        color_bytes = bytearray(self.bytes_per_pixel)
        color_bytes[0] = color & 0xFF
        color_bytes[1] = (color >> 8) & 0xFF
        color_bytes[2] = (color >> 16) & 0xFF
        if self.bytes_per_pixel > 3:
            color_bytes[3] = 0xFF

        row_fill = bytes(color_bytes) * WIN_WIDTH
        row_len = WIN_WIDTH * self.bytes_per_pixel
        for py in range(WIN_HEIGHT):
            row_start = py * self.stride
            row_end = row_start + row_len
            self.img_data[row_start:row_end] = row_fill

    def _draw_cell(
        self,
        x: int,
        y: int,
        wall_color: int,
        pattern_color: int,
    ) -> None:
        px = OFFSET + (x * self.cell_w)
        py = OFFSET + (y * self.cell_h)
        cell = self.maze.maze[y][x]

        if (x, y) in self.pattern_cells:
            pad = max(1, min(self.cell_w, self.cell_h) // 4)
            self._draw_rect(
                px + pad,
                py + pad,
                max(1, self.cell_w - (pad * 2)),
                max(1, self.cell_h - (pad * 2)),
                pattern_color,
            )

        if cell & 1:
            self._draw_hline(px, px + self.cell_w, py, wall_color)
        if cell & 2:
            self._draw_vline(
                px + self.cell_w,
                py,
                py + self.cell_h,
                wall_color,
            )
        if cell & 4:
            self._draw_hline(
                px,
                px + self.cell_w,
                py + self.cell_h,
                wall_color,
            )
        if cell & 8:
            self._draw_vline(px, py, py + self.cell_h, wall_color)

    def _draw_all_walls(self, wall_color: int, pattern_color: int) -> None:
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                self._draw_cell(x, y, wall_color, pattern_color)

    def _cell_center(self, cx: int, cy: int) -> Tuple[int, int]:
        return (
            OFFSET + (cx * self.cell_w) + (self.cell_w // 2),
            OFFSET + (cy * self.cell_h) + (self.cell_h // 2),
        )

    def _draw_solution_path(self, path_color: int, segments: int) -> None:
        if len(self.solution_path) < 2 or segments <= 0:
            return
        path_thickness = max(2, self.wall_thickness + 1)
        max_segments = min(segments, len(self.solution_path) - 1)
        for index in range(max_segments):
            x0, y0 = self.solution_path[index]
            x1, y1 = self.solution_path[index + 1]
            start_x, start_y = self._cell_center(x0, y0)
            end_x, end_y = self._cell_center(x1, y1)
            if start_x == end_x:
                self._draw_vline(
                    start_x,
                    start_y,
                    end_y,
                    path_color,
                    path_thickness,
                )
            else:
                self._draw_hline(
                    start_x,
                    end_x,
                    start_y,
                    path_color,
                    path_thickness,
                )

    def _draw_endpoints(self, entry_color: int, exit_color: int) -> None:
        pad = max(1, min(self.cell_w, self.cell_h) // 4)
        width = max(1, self.cell_w - (pad * 2))
        height = max(1, self.cell_h - (pad * 2))

        entry_x, entry_y = self.maze.entry
        self._draw_rect(
            OFFSET + (entry_x * self.cell_w) + pad,
            OFFSET + (entry_y * self.cell_h) + pad,
            width,
            height,
            entry_color,
        )

        exit_x, exit_y = self.maze.exit
        self._draw_rect(
            OFFSET + (exit_x * self.cell_w) + pad,
            OFFSET + (exit_y * self.cell_h) + pad,
            width,
            height,
            exit_color,
        )

    def _draw_ui(self, color: int) -> None:
        text = "1: regen | 2: path | 3: color | ESC: quit"
        self.m.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            14,
            WIN_HEIGHT - 18,
            color,
            text,
        )

    def render(self) -> None:
        palette = self._palette()

        self._clear_background(palette["bg"])
        self._draw_all_walls(palette["wall"], palette["pattern"])
        self._draw_endpoints(palette["entry"], palette["exit"])

        if self.show_solution:
            self._draw_solution_path(
                palette["path"],
                self.path_visible_segments,
            )

        self.m.mlx_put_image_to_window(
            self.mlx_ptr,
            self.win_ptr,
            self.img_ptr,
            0,
            0,
        )
        self._draw_ui(palette["ui"])

    def _loop_handler(self, param: Any) -> None:
        if self.path_animating and self.show_solution:
            now = time.monotonic()
            if (now - self.last_path_step_at) >= PATH_STEP_INTERVAL:
                max_segments = self._max_path_segments()
                step = self._path_step_size()
                self.path_visible_segments = min(
                    max_segments,
                    self.path_visible_segments + step,
                )
                self.last_path_step_at = now
                self.needs_render = True
                if self.path_visible_segments >= max_segments:
                    self.path_animating = False

        if self.needs_render:
            self.render()
            self.needs_render = False

    def handle_keys(self, keycode: int, param: Any) -> None:
        if keycode in [53, 65307]:
            self.close()
        elif keycode in [49, 18]:
            self.maze.generate()
            self._update_solution()
            self.needs_render = True
        elif keycode in [50, 19]:
            self.show_solution = not self.show_solution
            if self.show_solution:
                self._restart_path_animation()
            else:
                self.path_animating = False
            self.needs_render = True
        elif keycode in [51, 20]:
            self.palette = self._generate_random_palette()
            self.needs_render = True

    def handle_close(self, param: Any) -> None:
        self.close()

    def close(self) -> None:
        self.m.mlx_loop_exit(self.mlx_ptr)

    def run(self) -> None:
        self._update_solution()
        self.needs_render = True
        self.m.mlx_loop(self.mlx_ptr)
