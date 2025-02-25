import pygame
import sys
import time
import threading
import os
import tracemalloc
import colorsys
from board import Board
from solve import Solver as DFSSolver
from solve_mrv import MRVSolver
import gen_input

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLOR_OPTION = (0, 0, 0, 100)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)

class Button:
    def __init__(self, rect, text, callback, font, bg_color=BLUE, text_color=WHITE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=5)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Toggle:
    def __init__(self, rect, initial=False, callback=None, font=None):
        self.rect = pygame.Rect(rect)
        self.state = initial
        self.callback = callback
        self.font = font

    def draw(self, surface):
        bg_color = GREEN if self.state else RED
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=15)
        circle_radius = self.rect.height // 2 - 4
        if self.state:
            circle_x = self.rect.right - circle_radius - 4
        else:
            circle_x = self.rect.left + circle_radius + 4
        circle_y = self.rect.centery
        pygame.draw.circle(surface, WHITE, (circle_x, circle_y), circle_radius)
        if self.font:
            label = self.font.render("Step-by-step", True, WHITE)
            surface.blit(label, (self.rect.right + 10, self.rect.top))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.state = not self.state
            if self.callback:
                self.callback(self.state)

class ColorSlider:
    def __init__(self, x, y, width, height, initial=0.0, min_value=0.0, max_value=1.0):
        self.rect = pygame.Rect(x, y, width, height)
        self.value = initial
        self.min_value = min_value
        self.max_value = max_value
        self.knob_radius = 8
        self.dragging = False

    def draw(self, surface):
        for i in range(self.rect.height):
            ratio = i / self.rect.height
            hue = ratio
            r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
            color = (int(r*255), int(g*255), int(b*255))
            pygame.draw.line(surface, color, (self.rect.x, self.rect.y + i),
                             (self.rect.x + self.rect.width, self.rect.y + i))
        knob_y = self.rect.y + self.value * self.rect.height
        knob_x = self.rect.centerx
        pygame.draw.circle(surface, BLACK, (int(knob_x), int(knob_y)), self.knob_radius)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_value(event.pos[1])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_value(event.pos[1])

    def update_value(self, mouse_y):
        rel_y = mouse_y - self.rect.y
        if rel_y < 0:
            rel_y = 0
        elif rel_y > self.rect.height:
            rel_y = self.rect.height
        self.value = rel_y / self.rect.height

class SudokuGame:
    def __init__(self):
        pygame.init()
        self.WIDTH = 1000
        self.HEIGHT = 700
        self.OPTION_HEIGHT = 200
        self.BOARD_SIZE = self.HEIGHT - self.OPTION_HEIGHT
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Sudoku Pygame")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)
        self.large_font = pygame.font.SysFont("Arial", 30)
        self.running = True

        self.state = "choose_size"
        self.dimension = None
        self.block_rows = None
        self.block_cols = None
        self.difficulty = None
        self.input_mode = None
        self.algorithm = None
        self.step_by_step = False

        self.board_obj = None
        self.solver = None
        self.solve_thread = None
        self.solve_time = None
        self.solve_memory = None

        if os.path.exists("background.png"):
            self.background_image = pygame.image.load("background.png")
            self.background_image = pygame.transform.scale(self.background_image, (self.WIDTH, self.HEIGHT))
        else:
            self.background_image = None

        self.bg_slider = ColorSlider(10, self.BOARD_SIZE + 20, 20, self.OPTION_HEIGHT - 40, initial=0.0)
        self.buttons = []
        self.input_buttons = []
        self.algo_buttons = []
        self.end_buttons = []
        self.toggle = None
        self.setup_ui()

    def setup_ui(self):
        if self.state == "choose_size":
            self.buttons.clear()
            sizes = ["9x9", "12x12", "16x16"]
            button_width = 100
            button_height = 40
            spacing = 20
            total_width = len(sizes)*button_width + (len(sizes)-1)*spacing
            start_x = (self.WIDTH - total_width) // 2
            y = (self.HEIGHT - button_height) // 2
            for i, size in enumerate(sizes):
                btn = Button(
                    rect=(start_x + i*(button_width+spacing), y, button_width, button_height),
                    text=size,
                    callback=lambda idx=i: self.select_size(sizes[idx]),
                    font=self.font
                )
                self.buttons.append(btn)
        elif self.state == "menu":
            self.buttons.clear()
            difficulties = ["Basic", "Easy", "Intermediate", "Advance", "Extreme", "Evil"]
            button_width = 90
            button_height = 30
            spacing = 10
            total_width = len(difficulties)*button_width + (len(difficulties)-1)*spacing
            start_x = (self.WIDTH - total_width) // 2
            y = self.BOARD_SIZE + 20
            for i, diff in enumerate(difficulties):
                btn = Button(
                    rect=(start_x + i*(button_width+spacing), y, button_width, button_height),
                    text=diff,
                    callback=lambda idx=i: self.select_difficulty(idx+1),
                    font=self.font
                )
                self.buttons.append(btn)
        elif self.state == "input":
            self.input_buttons.clear()
            button_width = 120
            button_height = 30
            spacing = 20
            total_width = 2 * button_width + spacing
            start_x = (self.WIDTH - total_width) // 2
            y = self.BOARD_SIZE + 60
            preset_btn = Button(
                rect=(start_x, y, button_width, button_height),
                text="Preset",
                callback=lambda: self.select_input_mode(1),
                font=self.font
            )
            random_btn = Button(
                rect=(start_x + button_width + spacing, y, button_width, button_height),
                text="Random",
                callback=lambda: self.select_input_mode(2),
                font=self.font
            )
            self.input_buttons.extend([preset_btn, random_btn])
        elif self.state == "algorithm":
            self.algo_buttons.clear()
            button_width = 100
            button_height = 30
            spacing = 20
            toggle_width = 60
            total_width = 2 * button_width + 2*spacing + toggle_width
            start_x = (self.WIDTH - total_width) // 2
            y = self.BOARD_SIZE + 100
            dfs_btn = Button(
                rect=(start_x, y, button_width, button_height),
                text="DFS",
                callback=lambda: self.select_algorithm(1),
                font=self.font
            )
            mrv_btn = Button(
                rect=(start_x + button_width + spacing, y, button_width, button_height),
                text="MRV",
                callback=lambda: self.select_algorithm(2),
                font=self.font
            )
            self.algo_buttons.extend([dfs_btn, mrv_btn])
            self.toggle = Toggle(
                rect=(start_x + 2*button_width + 2*spacing, y, toggle_width, button_height),
                initial=False,
                font=self.font
            )
        elif self.state == "finished":
            self.end_buttons.clear()
            button_width = 120
            button_height = 40
            spacing = 20
            total_width = 2 * button_width + spacing
            start_x = (self.WIDTH - total_width) // 2
            y = self.BOARD_SIZE + 50
            play_again = Button(
                rect=(start_x, y, button_width, button_height),
                text="Play Again",
                callback=self.restart_game,
                font=self.font
            )
            exit_btn = Button(
                rect=(start_x + button_width + spacing, y, button_width, button_height),
                text="Exit",
                callback=self.exit_game,
                font=self.font
            )
            self.end_buttons.extend([play_again, exit_btn])

    def select_size(self, size_str):
        if size_str == "9x9":
            self.dimension = 9
            self.block_rows = 3
            self.block_cols = 3
        elif size_str == "12x12":
            self.dimension = 12
            self.block_rows = 3
            self.block_cols = 4
        elif size_str == "16x16":
            self.dimension = 16
            self.block_rows = 4
            self.block_cols = 4
        print("Chọn kích thước:", size_str)
        self.state = "menu"
        self.buttons.clear()
        self.setup_ui()

    def save_result(self):
        level_names = {1:"basic", 2:"easy", 3:"intermediate", 4:"advance", 5:"extreme", 6:"evil"}
        level_str = level_names.get(self.difficulty, "basic")
        output_folder = "output"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        filename = f"{level_str}_{self.dimension}x{self.dimension}.txt"
        output_filename = os.path.join(output_folder, filename)
        with open(output_filename, "w") as f:
            for row in self.board_obj.grid:
                line = " ".join(str(cell.get_value()) for cell in row)
                f.write(line + "\n")

    def select_difficulty(self, level):
        self.difficulty = level
        print("Chọn cấp độ:", level)
        self.state = "input"
        self.setup_ui()

    def select_input_mode(self, mode):
        self.input_mode = mode
        print("Chọn input:", "Preset" if mode == 1 else "Random")
        level_names = {1:"basic",2:"easy",3:"intermediate",4:"advance",5:"extreme",6:"evil"}
        level_str = level_names.get(self.difficulty, "basic")
        if mode == 1:
            file_input = os.path.join("input", f"{level_str}_{self.dimension}x{self.dimension}.txt")
        else:
            file_input = os.path.join("input", f"{level_str}_{self.dimension}x{self.dimension}_random.txt")
        if not os.path.exists(file_input):
            puzzle, _ = gen_input.generate_input(self.difficulty, self.dimension, self.block_rows, self.block_cols)
        try:
            puzzle = []
            with open(file_input, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        row = list(map(int, line.split()))
                        puzzle.append(row)
            self.board_obj = Board(puzzle, self.dimension, self.block_rows, self.block_cols)
        except Exception as e:
            print("Lỗi đọc file:", e)
            return
        self.state = "algorithm"
        self.setup_ui()

    def select_algorithm(self, algo):
        self.algorithm = algo
        print("Chọn thuật toán:", "DFS" if algo == 1 else "MRV")
        self.step_by_step = self.toggle.state
        self.state = "solving"
        tracemalloc.start()
        self.solve_start_time = time.time()
        if algo == 1:
            measure_solver = DFSSolver(self.board_obj)
            measure_func = measure_solver.solve_dfs
        else:
            measure_solver = MRVSolver(self.board_obj)
            measure_func = measure_solver.solve_mrv
        measure_func(drawFlag=False)
        measured_time = time.time() - self.solve_start_time
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        measured_memory = top_stats[0].size / 1024 if top_stats else 0
        self.solve_time = measured_time
        self.solve_memory = measured_memory
        if self.step_by_step:
            level_names = {1:"basic",2:"easy",3:"intermediate",4:"advance",5:"extreme",6:"evil"}
            level_str = level_names.get(self.difficulty, "basic")
            if self.input_mode == 1:
                file_input = os.path.join("input", f"{level_str}_{self.dimension}x{self.dimension}.txt")
            else:
                file_input = os.path.join("input", f"{level_str}_{self.dimension}x{self.dimension}_random.txt")
            try:
                puzzle = []
                with open(file_input, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            row = list(map(int, line.split()))
                            puzzle.append(row)
                self.board_obj = Board(puzzle, self.dimension, self.block_rows, self.block_cols)
            except Exception as e:
                print("Lỗi đọc file:", e)
                return
            if algo == 1:
                self.solver = DFSSolver(self.board_obj)
                solve_func = self.solver.solve_dfs
            else:
                self.solver = MRVSolver(self.board_obj)
                solve_func = self.solver.solve_mrv
            self.solve_thread = threading.Thread(target=self.run_solver_animation, args=(solve_func,))
            self.solve_thread.start()
        else:
            self.save_result()
            self.state = "finished"
        self.setup_ui()

    def run_solver_animation(self, solve_func):
        solve_func(drawFlag=True)
        self.save_result()
        self.state = "finished"
        self.setup_ui()

    def run_solver(self, solve_func):
        solved = solve_func(drawFlag=self.step_by_step)
        self.solve_time = time.time() - self.solve_start_time
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        self.solve_memory = top_stats[0].size / 1024 if top_stats else 0
        self.state = "finished"
        print("Giải xong:", solved)

    def restart_game(self):
        self.__init__()

    def exit_game(self):
        self.running = False

    def draw_board(self):
        if self.board_obj is None:
            return
        board_x = (self.WIDTH - self.BOARD_SIZE) // 2
        board_y = 0
        cell_size = self.BOARD_SIZE // self.dimension
        board_surface = pygame.Surface((self.BOARD_SIZE, self.BOARD_SIZE))
        board_surface.fill(WHITE)
        for i in range(1, self.dimension):
            line_width = 3 if i % self.block_rows == 0 else 1
            pygame.draw.line(board_surface, BLACK, (0, i * cell_size), (self.BOARD_SIZE, i * cell_size), line_width)
        for j in range(1, self.dimension):
            line_width = 3 if j % self.block_cols == 0 else 1
            pygame.draw.line(board_surface, BLACK, (j * cell_size, 0), (j * cell_size, self.BOARD_SIZE), line_width)
        pygame.draw.rect(board_surface, BLACK, board_surface.get_rect(), 3)

        for row in range(self.dimension):
            for col in range(self.dimension):
                value = self.board_obj.grid[row][col].get_value()
                if value != 0:
                    if self.board_obj.grid[row][col].isfixed():
                        color = GREEN
                    else:
                        color = RED if self.step_by_step else BLACK
                    text = str(value) if value < 10 else chr(ord('A') + value - 10)
                    text_surface = self.large_font.render(text, True, color)
                    text_rect = text_surface.get_rect(
                        center=(col * cell_size + cell_size // 2, row * cell_size + cell_size // 2))
                    board_surface.blit(text_surface, text_rect)
        self.screen.blit(board_surface, (board_x, board_y))

    def draw_options(self):
        option_surface = pygame.Surface((self.WIDTH, self.OPTION_HEIGHT), pygame.SRCALPHA)
        option_surface.fill(COLOR_OPTION)
        self.screen.blit(option_surface, (0, self.BOARD_SIZE))
        if self.state == "choose_size":
            for btn in self.buttons:
                btn.draw(self.screen)
        elif self.state == "menu":
            for btn in self.buttons:
                btn.draw(self.screen)
        elif self.state == "input":
            for btn in self.input_buttons:
                btn.draw(self.screen)
        elif self.state == "algorithm":
            for btn in self.algo_buttons:
                btn.draw(self.screen)
            self.toggle.draw(self.screen)
        elif self.state == "finished":
            time_text = self.font.render(f"Time: {self.solve_time:.6f} s", True, WHITE)
            mem_text = self.font.render(f"Memory: {self.solve_memory:.6f} KB", True, WHITE)
            self.screen.blit(time_text, (50, self.BOARD_SIZE + 10))
            self.screen.blit(mem_text, (250, self.BOARD_SIZE + 10))
            for btn in self.end_buttons:
                btn.draw(self.screen)
        if self.background_image is None:
            self.bg_slider.draw(self.screen)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.bg_slider.handle_event(event)
                hue = self.bg_slider.value
                r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
                self.bg_color = (int(r*255), int(g*255), int(b*255))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if self.state in ["choose_size", "menu"]:
                        for btn in self.buttons:
                            if btn.is_clicked(pos):
                                btn.callback()
                    elif self.state == "input":
                        for btn in self.input_buttons:
                            if btn.is_clicked(pos):
                                btn.callback()
                    elif self.state == "algorithm":
                        for btn in self.algo_buttons:
                            if btn.is_clicked(pos):
                                btn.callback()
                        self.toggle.handle_event(event)
                    elif self.state == "finished":
                        for btn in self.end_buttons:
                            if btn.is_clicked(pos):
                                btn.callback()

    def show_intro(self):
        if os.path.exists("intro_bg.png"):
            intro_bg = pygame.image.load("intro_bg.png")
            intro_bg = pygame.transform.scale(intro_bg, (self.WIDTH, self.HEIGHT))
        else:
            intro_bg = None
        intro = True
        intro_font = pygame.font.SysFont("Arial", 40)
        skip_font = pygame.font.SysFont("Arial", 24)
        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    intro = False
            if intro_bg:
                self.screen.blit(intro_bg, (0, 0))
            else:
                self.screen.fill(BLACK)
            line1 = intro_font.render("Welcome to the sudoku of the BTL_TTNT_HK242", True, BLACK)
            line2 = intro_font.render("Instructor: Mr. Vuong Ba Thinh!", True, BLACK)
            skip_text = skip_font.render("Press any key or click to skip ...", True, BLACK)
            line1_rect = line1.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 20))
            line2_rect = line2.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 + 20))
            skip_rect = skip_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT - 100))
            self.screen.blit(line1, line1_rect)
            self.screen.blit(line2, line2_rect)
            self.screen.blit(skip_text, skip_rect)
            pygame.display.flip()
            self.clock.tick(30)

    def run(self):
        self.show_intro()
        while self.running:
            self.handle_events()
            if self.background_image:
                bg = pygame.transform.scale(self.background_image, (self.WIDTH, self.HEIGHT))
                self.screen.blit(bg, (0, 0))
            else:
                self.screen.fill(self.bg_color)
            self.draw_board()
            self.draw_options()
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SudokuGame()
    game.run()
