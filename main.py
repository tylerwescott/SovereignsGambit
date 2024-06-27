import pygame
import sys
import math

pygame.init()

# Constants
ORIGINAL_RECT_WIDTH = 100
ORIGINAL_RECT_HEIGHT = int(ORIGINAL_RECT_WIDTH * 1.5)
RECT_WIDTH = ORIGINAL_RECT_WIDTH * 2
RECT_HEIGHT = RECT_WIDTH * 1.5
BOARD_COLS = 7  # Number of columns
BOARD_ROWS = 3  # Number of rows
BOARD_WIDTH = RECT_WIDTH * BOARD_COLS
BOARD_HEIGHT = RECT_HEIGHT * BOARD_ROWS
MARGIN = 300
SCREEN_WIDTH = BOARD_WIDTH + 2 * MARGIN + 200
SCREEN_HEIGHT = BOARD_HEIGHT + 2 * MARGIN + 100
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DECK_CARD_WIDTH = RECT_WIDTH
DECK_CARD_HEIGHT = RECT_HEIGHT
DECK_POSITION_X = 50
DECK_POSITION_Y = SCREEN_HEIGHT - DECK_CARD_HEIGHT - 50
HAND_POSITION_Y = SCREEN_HEIGHT - DECK_CARD_HEIGHT - 50
ANIMATION_SPEED = 0.005  # Significantly slower animation speed
CARD_TILT_ANGLE = 5  # Slight tilt angle for the cards in hand
OVERLAP_OFFSET = 60  # Increased amount of overlap between cards
ARC_HEIGHT = -100  # Height of the arc during the card movement (negative for upward arc)
MAX_HAND_CARDS = 10  # Maximum number of cards in the hand

# File paths
GREEN_PAWN_IMAGE_PATH = 'images/greenPawn.jpg'
RED_PAWN_IMAGE_PATH = 'images/redPawn.jpg'

centered_margin_x = (SCREEN_WIDTH - BOARD_WIDTH) // 2
centered_margin_y = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2 - 50

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.setCaption("Sovereign's Gambit - Board and Deck")

# Load images
green_pawn_image = pygame.image.load(GREEN_PAWN_IMAGE_PATH)
green_pawn_image = pygame.transform.scale(green_pawn_image, (RECT_WIDTH, RECT_HEIGHT))
red_pawn_image = pygame.image.load(RED_PAWN_IMAGE_PATH)
red_pawn_image = pygame.transform.scale(red_pawn_image, (RECT_WIDTH, RECT_HEIGHT))

font = pygame.font.SysFont(None, 55)

player_value = 0
ai_value = 0

hand_cards = []
moving_card = None
moving_target_pos = None
arc_progress = 0
target_angle = 0
initial_draw_count = 5
auto_drawing = True  # Flag to control automatic drawing at start

def update_hand_positions():
    if hand_cards:
        total_width = len(hand_cards) * (DECK_CARD_WIDTH - OVERLAP_OFFSET) + (len(hand_cards) - 1) * 10
        start_x = (SCREEN_WIDTH - total_width) // 2
        for i, card in enumerate(hand_cards):
            card['rect'].topleft = (start_x + i * (DECK_CARD_WIDTH - OVERLAP_OFFSET + 10), HAND_POSITION_Y)
            card['angle'] = -CARD_TILT_ANGLE * (i - (len(hand_cards) - 1) / 2)

def draw_rotated_rect(screen, card, color):
    rect = card['rect']
    angle = card['angle']
    image = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    image.fill((0, 0, 0, 0))  # Transparent fill
    pygame.draw.rect(image, color, image.get_rect(), 1)  # Draw only the outline
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_rect = rotated_image.get_rect(center=rect.center)
    screen.blit(rotated_image, rotated_rect.topleft)

def get_arc_position_and_angle(start_pos, end_pos, start_angle, end_angle, progress, arc_height):
    x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
    mid_x = (start_pos[0] + end_pos[0]) / 2
    a = -4 * arc_height / ((start_pos[0] - end_pos[0]) ** 2)
    y = a * (x - mid_x) ** 2 + min(start_pos[1], end_pos[1]) - arc_height
    angle = start_angle + (end_angle - start_angle) * progress
    return (x, y), angle

def draw_card_from_deck():
    global moving_card, moving_target_pos, target_angle, arc_progress
    if len(hand_cards) < MAX_HAND_CARDS:
        moving_card = {'rect': pygame.Rect(DECK_POSITION_X, DECK_POSITION_Y, DECK_CARD_WIDTH, DECK_CARD_HEIGHT), 'angle': 0}
        new_card = {'rect': pygame.Rect(0, 0, DECK_CARD_WIDTH, DECK_CARD_HEIGHT), 'angle': 0}
        hand_cards.append(new_card)
        update_hand_positions()
        moving_target_pos = new_card['rect'].center
        target_angle = new_card['angle']
        hand_cards.pop()
        arc_progress = 0

# Initiate drawing the first card
draw_card_from_deck()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and moving_card is None:
            mouse_x, mouse_y = event.pos
            if DECK_POSITION_X <= mouse_x <= DECK_POSITION_X + DECK_CARD_WIDTH and \
               DECK_POSITION_Y <= mouse_y <= DECK_POSITION_Y + DECK_CARD_HEIGHT:
                draw_card_from_deck()

    screen.fill(WHITE)

    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            space_x = centered_margin_x + col * RECT_WIDTH
            space_y = centered_margin_y + row * RECT_HEIGHT
            space = pygame.Rect(space_x, space_y, RECT_WIDTH, RECT_HEIGHT)
            pygame.draw.rect(screen, BLACK, space, 1)

            # Draw pawns in columns 1 and 5
            if col == 1:
                screen.blit(green_pawn_image, (space_x, space_y))
            elif col == 5:
                screen.blit(red_pawn_image, (space_x, space_y))

            # Draw player and AI values in columns 0 and 6
            if col == 0:
                value = player_value
                text = font.render(str(value), True, BLACK)
                text_rect = text.get_rect(center=space.center)
                screen.blit(text, text_rect)
            elif col == 6:
                value = ai_value
                text = font.render(str(value), True, BLACK)
                text_rect = text.get_rect(center=space.center)
                screen.blit(text, text_rect)

    for i in range(5):
        card_x = DECK_POSITION_X + i * 2
        card_y = DECK_POSITION_Y - i * 2
        card = pygame.Rect(card_x, card_y, DECK_CARD_WIDTH, DECK_CARD_HEIGHT)
        pygame.draw.rect(screen, BLACK, card, 1)

    if moving_card is not None:
        arc_progress += ANIMATION_SPEED
        if arc_progress >= 1:
            moving_card['rect'].center = moving_target_pos
            moving_card['angle'] = target_angle
            hand_cards.append(moving_card)
            update_hand_positions()
            moving_card = None
            if auto_drawing and initial_draw_count > 1:
                initial_draw_count -= 1
                draw_card_from_deck()
            elif auto_drawing and initial_draw_count == 1:
                auto_drawing = False
        else:
            moving_card['rect'].center, moving_card['angle'] = get_arc_position_and_angle(
                (DECK_POSITION_X, DECK_POSITION_Y), moving_target_pos, 0, target_angle, arc_progress, ARC_HEIGHT
            )
        if moving_card:
            draw_rotated_rect(screen, moving_card, BLACK)

    for card in hand_cards:
        draw_rotated_rect(screen, card, BLACK)

    pygame.display.flip()

pygame.quit()
sys.exit()
