from mlx import mlx

WIN_WIDTH = 1100
WIN_HEIGHT = 900
PANEL_TOP = 30
PANEL_BOTTOM = 220
SIDE_MARGIN = 120


THEMES = [
    {
        "bg": 0x050608,
        "cell": 0x70D9F2,
        "wall": 0x163541,
        "path": 0xF39C12,
        "entry": 0x2ECC71,
        "exit": 0xF1C40F,
        "text": 0xF5F7FA,
        "muted": 0xAAB4BE,
        "logo": 0x000000,
        "divider": 0x4A5A67
    },
    {
        "bg": 0x0A0D11,
        "cell": 0xB8C0FF,
        "wall": 0x2C335E,
        "path": 0xFF7A59,
        "entry": 0x4ADE80,
        "exit": 0xFACC15,
        "text": 0xF8FAFC,
        "muted": 0x94A3B8,
        "logo": 0x111827,
        "divider": 0x475569
    },
    {
        "bg": 0x0C0F0C,
        "cell": 0xB0F2B6,
        "wall": 0x2A4B2F,
        "path": 0xFF9F1C,
        "entry": 0x06D6A0,
        "exit": 0xFFD166,
        "text": 0xF1F5F1,
        "muted": 0xA3B7A5,
        "logo": 0x101712,
        "divider": 0x4D6651
    }
]


class MazeVisualizer:
    def __init__(self, maze_instance, solution_path=None):
        self.maze = maze_instance
        self.solution_path = solution_path or []
        self.show_solution = True
        self.theme_index = 0

        self.m = mlx.Mlx()
        self.mlx_ptr = self.m.mlx_init()
        self.win_ptr = self.m.mlx_new_window(
            self.mlx_ptr,
            WIN_WIDTH,
            WIN_HEIGHT,
            "A-Maze-ing 42"
        )

        self.img_ptr = self.m.mlx_new_image(
            self.mlx_ptr,
            WIN_WIDTH,
            WIN_HEIGHT
        )
        img_data, bpp, size_line, endian = self.m.mlx_get_data_addr(
            self.img_ptr
        )
        self.img_data = img_data
        self.bits_per_pixel = bpp
        self.size_line = size_line
        self.endian = endian
        self.pixel_bytes = max(1, self.bits_per_pixel // 8)

        self._recalculate_layout()

        # Configurar Hooks
        self.m.mlx_key_hook(self.win_ptr, self.handle_keys, self)
        self.m.mlx_hook(self.win_ptr, 17, 0, self.handle_close, self)

    def _recalculate_layout(self):
        board_max_w = WIN_WIDTH - (2 * SIDE_MARGIN)
        board_max_h = WIN_HEIGHT - PANEL_TOP - PANEL_BOTTOM

        fit_w = board_max_w // max(1, self.maze.width)
        fit_h = board_max_h // max(1, self.maze.height)
        self.tile_size = max(1, min(fit_w, fit_h))
        self.board_w = self.tile_size * self.maze.width
        self.board_h = self.tile_size * self.maze.height

        self.board_x = (WIN_WIDTH - self.board_w) // 2
        self.board_y = PANEL_TOP + ((board_max_h - self.board_h) // 2)

        self.wall_thickness = max(1, self.tile_size // 8)
        self.path_inset = (
            0 if self.tile_size <= 3 else max(1, self.tile_size // 4)
        )
        self.marker_inset = (
            0 if self.tile_size <= 4 else max(1, self.tile_size // 6)
        )

    def _update_solution(self):
        self.solution_path = self.maze.solve()
        self.solution_cells = set(self.solution_path)

    def _theme(self):
        return THEMES[self.theme_index]

    def put_pixel(self, x, y, color):
        if 0 <= x < WIN_WIDTH and 0 <= y < WIN_HEIGHT:
            index = (y * self.size_line) + (x * self.pixel_bytes)
            if index < 0 or index + self.pixel_bytes > len(self.img_data):
                return

            red = (color >> 16) & 0xFF
            green = (color >> 8) & 0xFF
            blue = color & 0xFF

            if self.endian == 0:
                self.img_data[index] = blue
                if self.pixel_bytes > 1:
                    self.img_data[index + 1] = green
                if self.pixel_bytes > 2:
                    self.img_data[index + 2] = red
                if self.pixel_bytes > 3:
                    self.img_data[index + 3] = 0xFF
            else:
                if self.pixel_bytes > 3:
                    self.img_data[index] = 0x00
                    self.img_data[index + 1] = red
                    self.img_data[index + 2] = green
                    self.img_data[index + 3] = blue
                else:
                    self.img_data[index] = red
                    if self.pixel_bytes > 1:
                        self.img_data[index + 1] = green
                    if self.pixel_bytes > 2:
                        self.img_data[index + 2] = blue

    def draw_block(self, x_start, y_start, width, height, color):
        if width <= 0 or height <= 0:
            return
        for row in range(height):
            for col in range(width):
                self.put_pixel(x_start + col, y_start + row, color)

    def _draw_maze(self):
        theme = self._theme()

        self.draw_block(self.board_x, self.board_y,
                        self.board_w, self.board_h, theme["cell"])

        if self.show_solution:
            for x, y in self.solution_cells:
                px = self.board_x + (x * self.tile_size) + self.path_inset
                py = self.board_y + (y * self.tile_size) + self.path_inset
                size = self.tile_size - (2 * self.path_inset)
                self.draw_block(px, py, size, size, theme["path"])

        for y in range(self.maze.height):
            for x in range(self.maze.width):
                cell = self.maze.maze[y][x]
                px = self.board_x + (x * self.tile_size)
                py = self.board_y + (y * self.tile_size)

                if (x, y) == self.maze.entry:
                    self.draw_block(
                        px + self.marker_inset,
                        py + self.marker_inset,
                        self.tile_size - (2 * self.marker_inset),
                        self.tile_size - (2 * self.marker_inset),
                        theme["entry"]
                    )
                elif (x, y) == self.maze.exit:
                    self.draw_block(
                        px + self.marker_inset,
                        py + self.marker_inset,
                        self.tile_size - (2 * self.marker_inset),
                        self.tile_size - (2 * self.marker_inset),
                        theme["exit"]
                    )
                elif cell == 15:
                    self.draw_block(
                        px,
                        py,
                        self.tile_size,
                        self.tile_size,
                        theme["logo"]
                    )

                if cell & 1:
                    self.draw_block(px, py,
                                    self.tile_size, self.wall_thickness,
                                    theme["wall"])
                if cell & 2:
                    self.draw_block(px + self.tile_size - self.wall_thickness,
                                    py,
                                    self.wall_thickness, self.tile_size,
                                    theme["wall"])
                if cell & 4:
                    self.draw_block(px,
                                    py + self.tile_size - self.wall_thickness,
                                    self.tile_size, self.wall_thickness,
                                    theme["wall"])
                if cell & 8:
                    self.draw_block(px, py,
                                    self.wall_thickness, self.tile_size,
                                    theme["wall"])

        self.draw_block(self.board_x - self.wall_thickness,
                        self.board_y - self.wall_thickness,
                        self.board_w + (2 * self.wall_thickness),
                        self.wall_thickness,
                        theme["wall"])
        self.draw_block(self.board_x - self.wall_thickness,
                        self.board_y + self.board_h,
                        self.board_w + (2 * self.wall_thickness),
                        self.wall_thickness,
                        theme["wall"])
        self.draw_block(self.board_x - self.wall_thickness,
                        self.board_y,
                        self.wall_thickness,
                        self.board_h,
                        theme["wall"])
        self.draw_block(self.board_x + self.board_w,
                        self.board_y,
                        self.wall_thickness,
                        self.board_h,
                        theme["wall"])

    def _draw_hud(self):
        theme = self._theme()
        divider_y = self.board_y + self.board_h + 28
        self.draw_block(130, divider_y, WIN_WIDTH - 260, 2, theme["divider"])

        info_color = theme["text"]
        muted_color = theme["muted"]
        steps = max(0, len(self.solution_path) - 1)
        path_state = "ON" if self.show_solution else "OFF"
        info_line = (
            f"Maze {self.maze.width}x{self.maze.height}  |  "
            f"Steps: {steps}  |  Path: {path_state}"
        )

        self.m.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            150,
            divider_y + 26,
            info_color,
            info_line
        )
        self.m.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            150,
            divider_y + 54,
            muted_color,
            f"Theme {self.theme_index + 1}/{len(THEMES)}"
        )
        self.m.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            150,
            divider_y + 94,
            info_color,
            "1: Regenerate maze"
        )
        self.m.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            150,
            divider_y + 120,
            info_color,
            "2: Show/hide path from entry to exit"
        )
        self.m.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            150,
            divider_y + 146,
            info_color,
            "3: Change maze colors"
        )
        self.m.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            150,
            divider_y + 172,
            info_color,
            "ESC: Quit the program"
        )

    def render(self):
        self.draw_block(0, 0, WIN_WIDTH, WIN_HEIGHT, self._theme()["bg"])
        self._draw_maze()
        self.m.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr,
                                       self.img_ptr, 0, 0)
        self._draw_hud()

    def render_hook(self, param):
        self.render()
        return 0

    def handle_keys(self, keycode, param):
        if keycode in [53, 65307]:
            self.close()
        elif keycode in [49, 18]:
            self.maze.generate()
            self._update_solution()
            self.render()
        elif keycode in [50, 19]:
            self.show_solution = not self.show_solution
            self.render()
        elif keycode in [51, 20]:
            self.theme_index = (self.theme_index + 1) % len(THEMES)
            self.render()
        return 0

    def handle_close(self, param):
        self.close()
        return 0

    def close(self):
        self.m.mlx_loop_exit(self.mlx_ptr)

    def run(self):
        self._update_solution()
        self.render()
        self.m.mlx_loop(self.mlx_ptr)
