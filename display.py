import sys
from mlx import mlx

WIN_SIZE = 800
MARGIN = 40
COLOR_WALL = 0x2C3E50
COLOR_PATH = 0xECF0F1
COLOR_BG = 0x17202A


class MazeVisualizer:
    def __init__(self, maze_instance):
        self.maze = maze_instance

        self.m = mlx.Mlx()
        self.mlx_ptr = self.m.mlx_init()
        self.win_ptr = self.m.mlx_new_window(
            self.mlx_ptr,
            WIN_SIZE,
            WIN_SIZE,
            "A-Maze-ing 42"
        )

        self.img_ptr = self.m.mlx_new_image(self.mlx_ptr, WIN_SIZE, WIN_SIZE)

        res = self.m.mlx_get_data_addr(self.img_ptr)
        self.img_data = res[0]
        self.bpp = res[1]
        self.size_line = res[2]

        self.tile_w = (WIN_SIZE - (2 * MARGIN)) // self.maze.width
        self.tile_h = (WIN_SIZE - (2 * MARGIN)) // self.maze.height

        self.m.mlx_key_hook(self.win_ptr, self.handle_keys, self)

    def put_pixel_to_buffer(self, x, y, color):
        if 0 <= x < WIN_SIZE and 0 <= y < WIN_SIZE:
            index = (y * self.size_line) + (x * 4)

            self.img_data[index] = color & 0xFF
            self.img_data[index + 1] = (color >> 8) & 0xFF
            self.img_data[index + 2] = (color >> 16) & 0xFF

    def draw_block(self, x_start, y_start, w, h, color):
        for i in range(h):
            for j in range(w):
                self.put_pixel_to_buffer(x_start + j, y_start + i, color)

    def render(self):
        self.draw_block(0, 0, WIN_SIZE, WIN_SIZE, COLOR_BG)
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                px = MARGIN + (x * self.tile_w)
                py = MARGIN + (y * self.tile_h)

                color = COLOR_WALL if self.maze.grid[y][x] == 1 else COLOR_PATH

                self.draw_block(px, py, self.tile_w - 1, self.tile_h - 1,
                                color)

        self.m.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr,
                                       self.img_ptr, 0, 0)

        self.m.mlx_string_put(self.mlx_ptr, self.win_ptr, 20, WIN_SIZE - 15,
                              0xFFFFFF)

    def handle_keys(self, keycode, param):
        # 53 = ESC no Mac | 65307 = ESC no Linux
        if keycode == 53 or keycode == 65307:
            print("A sair...")
            sys.exit(0)
        return 0

    def run(self):
        self.render()
        self.m.mlx_loop(self.mlx_ptr)
