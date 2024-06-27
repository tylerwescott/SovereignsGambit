import pygame
import sys

pygame.init()

ORIGINAL_RECT_WIDTH = 100
ORIGINAL_RECT_HEIGHT = int(ORIGINAL_RECT_WIDTH * 1.5)
RECT_WIDTH = ORIGINAL_RECT_WIDTH * 2
RECT_HEIGHT = ORIGINAL_RECT_HEIGHT * 2
BOARD_COLS = 5
BOARD_ROWS = 3
BOARD_WIDTH = RECT_WIDTH * BOARD_COLS
BOARD_HEIGHT = RECT_HEIGHT * BOARD_ROWS
MARGIN = 300
SCREEN_WIDTH = BOARD_WIDTH + 2 * MARGIN + 200
SCREEN_HEIGHT = BOARD_HEIGHT + 2 * MARGIN + 100
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DECK_RECT_WIDTH = RECT_WIDTH
DECK_RECT_HEIGHT = RECT_HEIGHT
DECK_POSITION_X = 50
DECK_POSITION_Y = SCREEN_HEIGHT - DECK_RECT_HEIGHT - 50
HAND_POSITION_Y = SCREEN_HEIGHT - DECK_RECT_HEIGHT - 50
ANIMATION_SPEED = 10

centered_margin_x = (SCREEN_WIDTH - BOARD_WIDTH) // 2
centered_margin_y = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2 - 50

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sovereign's Gambit - Board and Deck")

hand_rects = []
moving_rect = None
moving_target_pos = None

def update_hand_positions():
    if hand_rects:
        total_width = len(hand_rects) * DECK_RECT_WIDTH + (len(hand_rects) - 1) * 10
        start_x = (SCREEN_WIDTH - total_width) // 2
        for i, rect in enumerate(hand_rects):
            rect.topleft = (start_x + i * (DECK_RECT_WIDTH + 10), HAND_POSITION_Y)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and moving_rect is None:
            mouse_x, mouse_y = event.pos
            if DECK_POSITION_X <= mouse_x <= DECK_POSITION_X + DECK_RECT_WIDTH and \
               DECK_POSITION_Y <= mouse_y <= DECK_POSITION_Y + DECK_RECT_HEIGHT:
                moving_rect = pygame.Rect(DECK_POSITION_X, DECK_POSITION_Y, DECK_RECT_WIDTH, DECK_RECT_HEIGHT)
                new_card_rect = pygame.Rect(0, 0, DECK_RECT_WIDTH, DECK_RECT_HEIGHT)
                hand_rects.append(new_card_rect)
                update_hand_positions()
                moving_target_pos = new_card_rect.topleft
                hand_rects.pop()

    screen.fill(WHITE)

    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            rect_x = centered_margin_x + col * RECT_WIDTH
            rect_y = centered_margin_y + row * RECT_HEIGHT
            rect = pygame.Rect(rect_x, rect_y, RECT_WIDTH, RECT_HEIGHT)
            pygame.draw.rect(screen, BLACK, rect, 1)

    for i in range(5):
        rect_x = DECK_POSITION_X + i * 2
        rect_y = DECK_POSITION_Y - i * 2
        rect = pygame.Rect(rect_x, rect_y, DECK_RECT_WIDTH, DECK_RECT_HEIGHT)
        pygame.draw.rect(screen, BLACK, rect, 1)

    if moving_rect is not None:
        dx = moving_target_pos[0] - moving_rect.x
        dy = moving_target_pos[1] - moving_rect.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < ANIMATION_SPEED:
            moving_rect.topleft = moving_target_pos
            hand_rects.append(pygame.Rect(moving_target_pos, (DECK_RECT_WIDTH, DECK_RECT_HEIGHT)))
            moving_rect = None
        else:
            move_x = ANIMATION_SPEED * dx / distance
            move_y = ANIMATION_SPEED * dy / distance
            moving_rect.x += move_x
            moving_rect.y += move_y
        if moving_rect:
            pygame.draw.rect(screen, BLACK, moving_rect, 1)

    for rect in hand_rects:
        pygame.draw.rect(screen, BLACK, rect, 1)

    pygame.display.flip()

pygame.quit()
sys.exit()
