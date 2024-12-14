import os
import pygame
import numpy as np


# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
sidebar_width = 200
screen = pygame.display.set_mode((width, height))

# Grid dimensions
n_cells_x, n_cells_y = 40, 30
cell_width = width // n_cells_x
cell_height = height // n_cells_y

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
gray = (128, 128, 128)
green = (0, 255, 0)

#singleton
class GameState:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameState, cls).__new__(cls)
            cls._instance.state = None
        return cls._instance

    def initialize(self, n_cells_x, n_cells_y):
        self.state = np.random.choice([0, 1], size=(n_cells_x, n_cells_y), p=[0.8, 0.2])

def draw_grid():
    for y in range(0, height, cell_height):
        for x in range(0, width, cell_width):
            cell = pygame.Rect(x, y, cell_width, cell_height)
            pygame.draw.rect(screen, gray, cell, 1)


def draw_sidebar():
    sidebar_rect = pygame.Rect(width - sidebar_width, 0, sidebar_width, height)
    pygame.draw.rect(screen, gray, sidebar_rect)

    font = pygame.font.Font(None, 24)
    text_lines = [
        "Controls:",
        "Space: Pause/Resume",
        "S: Save Game",
        "L: Load Game",
        "R: Reset Grid",
    ]

    for i, line in enumerate(text_lines):
        text_surface = font.render(line, True, white)
        screen.blit(text_surface, (width - sidebar_width + 10, 10 + i * 30))


def next_generation():
    game_state = GameState()
    new_state = np.copy(game_state.state)

    for y in range(n_cells_y):
        for x in range(n_cells_x):
            n_neighbors = game_state.state[(x - 1) % n_cells_x, (y - 1) % n_cells_y] + \
                          game_state.state[(x)     % n_cells_x, (y - 1) % n_cells_y] + \
                          game_state.state[(x + 1) % n_cells_x, (y - 1) % n_cells_y] + \
                          game_state.state[(x - 1) % n_cells_x, (y)     % n_cells_y] + \
                          game_state.state[(x + 1) % n_cells_x, (y)     % n_cells_y] + \
                          game_state.state[(x - 1) % n_cells_x, (y + 1) % n_cells_y] + \
                          game_state.state[(x)     % n_cells_x, (y + 1) % n_cells_y] + \
                          game_state.state[(x + 1) % n_cells_x, (y + 1) % n_cells_y]

            if game_state.state[x, y] == 1 and (n_neighbors < 2 or n_neighbors > 3):
                new_state[x, y] = 0
            elif game_state.state[x, y] == 0 and n_neighbors == 3:
                new_state[x, y] = 1

    game_state.state = new_state

def draw_cells():
    game_state = GameState()
    for y in range(n_cells_y):
        for x in range(n_cells_x):
            cell = pygame.Rect(x * cell_width, y * cell_height, cell_width, cell_height)
            if game_state.state[x, y] == 1:
                pygame.draw.rect(screen, black, cell)

def save_game():
    game_state = GameState()
    np.save('game_state.npy', game_state.state)

def load_game():
    game_state = GameState()
    if os.path.exists('game_state.npy'):
        game_state.state = np.load('game_state.npy')


class SimulationState():
    game_state = GameState()
    def handle_input(self, simulation, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                save_game()
            if event.key == pygame.K_l:
                load_game()
            if event.key == pygame.K_r:
                game_state.initialize(n_cells_x, n_cells_y)

class PlayingState(SimulationState):
    def handle_input(self, simulation, event):
        super().handle_input(simulation, event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                simulation.change_state(PausedState())


class PausedState(SimulationState):
    def handle_input(self, simulation, event):
        super().handle_input(simulation, event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                simulation.change_state(PlayingState())


class Simulation():
    def __init__(self):
        self.state = PlayingState()

    def change_state(self, state):
        self.state = state

    def handle_input(self, event):
        self.state.handle_input(self, event)


clock = pygame.time.Clock()
i = 0
running = True
playing = True
game_state = GameState()
game_state.initialize(n_cells_x, n_cells_y)
simulation = Simulation()

while running:
    clock.tick(60)
    screen.fill(white)
    draw_grid()
    draw_cells()
    draw_sidebar()
    pygame.display.flip()
    i += 1

    if isinstance(simulation.state, PlayingState) and (i%20 == 0):
        next_generation()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            simulation.handle_input(event)


pygame.quit()