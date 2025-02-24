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

# -------------------- Định nghĩa màu sắc --------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (220, 220, 220)
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
            label = self.font.render("Step-by-step", True, BLACK)
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
            color = (int(r * 255), int(g * 255), int(b * 255))
            pygame.draw.line(surface, color, (self.rect.x, self.rect.y + i), (self.rect.x + self.rect.width, self.rect.y + i))
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
        self.WIDTH = 600
        self.HEIGHT = 700
        self.BOARD_SIZE = 540
        self.OPTION_HEIGHT = self.HEIGHT - self.BOARD_SIZE
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Sudoku Pygame")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)
        self.large_font = pygame.font.SysFont("Arial", 30)
        self.running = True
        self.state = "menu"
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
        self.setup_menu_ui()

    def setup_menu_ui(self):
        self.buttons.clear()
        difficulties = ["Basic", "Easy", "Intermediate", "Advance", "Extreme", "Evil"]
        for i, diff in enumerate(difficulties):
            btn = Button(rect=(20 + i * 95, self.BOARD_SIZE + 20, 90, 30), text=diff, callback=lambda idx=i: self.select_difficulty(idx + 1), font=self.font)
            self.buttons.append(btn)
        self.input_buttons.clear()
        preset_btn = Button(rect=(50, self.BOARD_SIZE + 60, 120, 30), text="Preset", callback=lambda: self.select_input_mode(1), font=self.font)
        random_btn = Button(rect=(200, self.BOARD_SIZE + 60, 120, 30), text="Random", callback=lambda: self.select_input_mode(2), font=self.font)
        self.input_buttons.extend([preset_btn, random_btn])
        self.algo_buttons.clear()
        dfs_btn = Button(rect=(50, self.BOARD_SIZE + 100, 100, 30), text="DFS", callback=lambda: self.select_algorithm(1), font=self.font)
        mrv_btn = Button(rect=(200, self.BOARD_SIZE + 100, 100, 30), text="MRV", callback=lambda: self.select_algorithm(2), font=self.font)
        self.algo_buttons.extend([dfs_btn, mrv_btn])
        self.toggle = Toggle(rect=(350, self.BOARD_SIZE + 100, 60, 30), initial=False, font=self.font)
        self.end_buttons.clear()
        play_again = Button(rect=(150, self.BOARD_SIZE + 50, 120, 40), text="Play Again", callback=self.restart_game, font=self.font)
        exit_btn = Button(rect=(330, self.BOARD_SIZE + 50, 120, 40), text="Exit", callback=self.exit_game, font=self.font)
        self.end_buttons.extend([play_again, exit_btn])

    def select_difficulty(self, level):
        self.difficulty = level
        print("Chọn cấp độ:", level)
        self.state = "input"

    def select_input_mode(self, mode):
        self.input_mode = mode
        print("Chọn input:", "Preset" if mode == 1 else "Random")
        if mode == 1:
            level_files = ("basic.txt", "easy.txt", "intermediate.txt", "advance.txt", "extreme.txt", "evil.txt")
            file_input = os.path.join("input", level_files[self.difficulty - 1])
            try:
                puzzle = []
                with open(file_input, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            row = list(map(int, line.split()))
                            puzzle.append(row)
                self.board_obj = Board(puzzle)
            except Exception as e:
                print("Lỗi đọc file:", e)
                return
        else:
            puzzle, _ = gen_input.generate_input(self.difficulty)
            self.board_obj = Board(puzzle)
        self.state = "algorithm"

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
            if self.input_mode == 1:
                level_files = ("basic.txt", "easy.txt", "intermediate.txt", "advance.txt", "extreme.txt", "evil.txt")
                file_input = os.path.join("input", level_files[self.difficulty - 1])
                try:
                    puzzle = []
                    with open(file_input, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                row = list(map(int, line.split()))
                                puzzle.append(row)
                    self.board_obj = Board(puzzle)
                except Exception as e:
                    print("Lỗi đọc file:", e)
                    return
            else:
                puzzle, _ = gen_input.generate_input(self.difficulty)
                self.board_obj = Board(puzzle)
            if algo == 1:
                self.solver = DFSSolver(self.board_obj)
                solve_func = self.solver.solve_dfs
            else:
                self.solver = MRVSolver(self.board_obj)
                solve_func = self.solver.solve_mrv
            self.solve_thread = threading.Thread(target=self.run_solver_animation, args=(solve_func,))
            self.solve_thread.start()
        else:
            self.state = "finished"

    def run_solver_animation(self, solve_func):
        solve_func(drawFlag=True)
        self.state = "finished"

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
        cell_size = self.BOARD_SIZE // 9
        board_surface = pygame.Surface((self.BOARD_SIZE, self.BOARD_SIZE))
        board_surface.fill(WHITE)
        for i in range(10):
            line_width = 3 if i % 3 == 0 else 1
            pygame.draw.line(board_surface, BLACK, (0, i * cell_size), (self.BOARD_SIZE, i * cell_size), line_width)
            pygame.draw.line(board_surface, BLACK, (i * cell_size, 0), (i * cell_size, self.BOARD_SIZE), line_width)
        for row in range(9):
            for col in range(9):
                value = self.board_obj.grid[row][col].get_value()
                if value != 0:
                    color = RED if self.step_by_step and not self.board_obj.grid[row][col].isfixed() else BLACK
                    text_surface = self.large_font.render(str(value), True, color)
                    text_rect = text_surface.get_rect(center=(col * cell_size + cell_size // 2, row * cell_size + cell_size // 2))
                    board_surface.blit(text_surface, text_rect)
        self.screen.blit(board_surface, (board_x, board_y))

    def draw_options(self):
        pygame.draw.rect(self.screen, LIGHT_GRAY, (0, self.BOARD_SIZE, self.WIDTH, self.OPTION_HEIGHT))
        if self.state == "menu":
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
            time_text = self.font.render(f"Time: {self.solve_time:.6f} s", True, BLACK)
            mem_text = self.font.render(f"Memory: {self.solve_memory:.6f} KB", True, BLACK)
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
                self.bg_color = (int(r * 255), int(g * 255), int(b * 255))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if self.state == "menu":
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

    def run(self):
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
