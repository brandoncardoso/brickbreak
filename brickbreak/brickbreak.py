﻿import pygame
import sys
from src.entities import Ball, Paddle, Brick, BrickGrid
from src.spatial import SpatialHash
from src.misc import Colors, ScreenText
from src.state import GameState, GameStateRelation, GameStateManager

pygame.init()

pygame.display.set_caption("Brick Break")
pygame.mouse.set_visible(False)

windowSize = width, height = 800, 600
screen = pygame.display.set_mode(windowSize, pygame.DOUBLEBUF)
dirty_rects = []

clock = pygame.time.Clock()

### title screen objects
title_text = ScreenText("BRICK BREAK", "Consolas", 48, (width/2, height/2), True, Colors.RED)
exit_title_text = ScreenText("Press any key to start", "Consolas", 12, (width/2, height/2 + 100), True, Colors.WHITE, Colors.NONE, False)

### game objects
fps_counter = ScreenText(0, "Consolas", 12, (5, 5), False, Colors.WHITE, Colors.NONE, False)
ball_radius = 5
ball = Ball([screen.get_width()/2 - ball_radius/2, screen.get_height()/2 - ball_radius/2], [0, 2], Colors.WHITE, ball_radius)
paddle = Paddle([0, 550], [60, 8], Colors.WHITE)
brick_grid = BrickGrid([40, 40], 10, 30, screen.get_width() - 80, 200)
brick_hash = SpatialHash(width, height, 10, 10, brick_grid.get_bricks())
lives = 3
lives_text = ScreenText("Lives: " + str(lives), "Consolas", 12, (5, height - 12 - 5), False, Colors.WHITE, Colors.NONE, False)

### pause screen objects
paused_text = ScreenText("PAUSED", "Consolas", 32, (width/2, height/2), True, Colors.BLACK, Colors.WHITE)


def clear_screen():
    global dirty_rects
    screen.fill((0,0,0))
    dirty_rects.append(pygame.Rect(0, 0, width, height))

def run_title_screen():
    global dirty_rects
    title_text.draw(screen)
    exit_title_text.draw(screen)
    dirty_rects.extend([title_text.get_rect(),
                        exit_title_text.get_rect()])

def run_game():
    global dirty_rects

    lives_text.draw(screen)
    dirty_rects.append(lives_text.get_rect())

    dirty_rects.extend([paddle.get_rect(), ball.get_rect()])
    paddle.update(screen)

    brick_grid.update(screen)

    bricks_near_ball = brick_hash.get_nearby(ball.get_rect())
    ball.update(screen, paddle, bricks_near_ball)

    dirty_rects.extend([paddle.get_rect(), ball.get_rect()])
    dirty_rects.extend(brick_grid.get_dirty())

    if ball.get_rect().top > paddle.get_rect().bottom:
        global lives
        lives -= 1
        lives_text.set_text("Lives: " + str(lives))
        ball.reset()

def run_pause_screen():
    global dirty_rects
    paused_text.draw(screen)
    dirty_rects.append(paused_text.get_rect())

def redraw_bricks():
    brick_grid.update(screen, True)

### state
game_state_manager = GameStateManager(GameState.TITLE)
game_state_manager.add_relation(GameStateRelation("Exit Title Screen", GameState.TITLE, GameState.INGAME))
game_state_manager.add_relation(GameStateRelation("Pause Game", GameState.INGAME, GameState.PAUSED, pygame.K_p))
game_state_manager.add_relation(GameStateRelation("Pause Game", GameState.INGAME, GameState.PAUSED, pygame.K_SPACE))
game_state_manager.add_relation(GameStateRelation("Unpause Game", GameState.PAUSED, GameState.INGAME, pygame.K_p))
game_state_manager.add_relation(GameStateRelation("Unpause Game", GameState.PAUSED, GameState.INGAME, pygame.K_SPACE))

game_state_manager.add_enter_callback(GameState.INGAME, redraw_bricks)

game_state_manager.add_exit_callback(GameState.TITLE, clear_screen)
game_state_manager.add_exit_callback(GameState.PAUSED, clear_screen)

### event handlers
def handle_event(event):
    if event.type == pygame.QUIT:
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        game_state_manager.handle_key(event.key, event.mod)
    elif event.type == pygame.MOUSEBUTTONDOWN:
        if game_state_manager.get_state() == GameState.INGAME:
            ball.launch()

while True:
    screen.fill(Colors.BLACK)
    clock.tick(144) # caps fps at 144

    dirty_rects = [] # clear dirty rectangles

    fps_counter.set_text(str(int(clock.get_fps())))
    fps_counter.draw(screen)
    dirty_rects.append(fps_counter.get_rect())

    for event in pygame.event.get():
        handle_event(event)

    game_state = game_state_manager.get_state()

    if game_state == GameState.TITLE:
        run_title_screen()
    elif game_state == GameState.INGAME:
        run_game()
    elif game_state == GameState.PAUSED:
        run_pause_screen()

    if len(dirty_rects) > 0:
        pygame.display.update(dirty_rects)

pygame.quit()
