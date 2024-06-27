import pygame
import sys
import random
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
FOOT_SOLDIER_IMAGE_PATH = 'images/footSoldier.jpg'
APPRENTICE_IMAGE_PATH = 'images/apprentice.jpg'

# Load images
green_pawn_image = pygame.image.load(GREEN_PAWN_IMAGE_PATH)
green_pawn_image = pygame.transform.scale(green_pawn_image, (RECT_WIDTH - 2, RECT_HEIGHT - 2))
red_pawn_image = pygame.image.load(RED_PAWN_IMAGE_PATH)
red_pawn_image = pygame.transform.scale(red_pawn_image, (RECT_WIDTH - 2, RECT_HEIGHT - 2))
foot_soldier_image = pygame.image.load(FOOT_SOLDIER_IMAGE_PATH)
foot_soldier_image = pygame.transform.scale(foot_soldier_image, (RECT_WIDTH - 2, RECT_HEIGHT - 2))
apprentice_image = pygame.image.load(APPRENTICE_IMAGE_PATH)
apprentice_image = pygame.transform.scale(apprentice_image, (RECT_WIDTH - 2, RECT_HEIGHT - 2))

# Font
font = pygame.font.SysFont(None, 55)

# Player and AI values
player_value = 0
ai_value = 0

# Card data structure
class Card:
    def __init__(self, name, placement_cost, image, pawn_placement):
        self.name = name
        self.placement_cost = placement_cost
        self.image = image
        self.pawn_placement = pawn_placement

# Create card instances
foot_soldier_card = Card("Foot Soldier", 1, foot_soldier_image, [(0, 1)])
apprentice_card = Card("Apprentice", 1, apprentice_image, [(0, 2)])

# Deck class
class Deck:
    def __init__(self, cards):
        self.cards = cards
        random.shuffle(self.cards)

    def draw_card(self):
        if self.cards:
            return self.cards.pop()
        return None

# Initialize player and AI decks
player_deck = Deck([foot_soldier_card, apprentice_card] * 5)
ai_deck = Deck([foot_soldier_card, apprentice_card] * 5)

# Hand cards and other variables
hand_cards = []
moving_card = None
moving_target_pos = None
arc_progress = 0
target_angle = 0
initial_draw_count = 5
auto_drawing = True  # Flag to control automatic drawing at start
dragging_card = None
dragging_offset_x = 0
dragging_offset_y = 0
original_hand_positions = []

# Set up the screen
centered_margin_x = (SCREEN_WIDTH - BOARD_WIDTH) // 2
centered_margin_y = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2 - 50

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sovereign's Gambit - Board and Deck")

# Initialize the board with values
board_values = [{'player': 0, 'ai': 0, 'image': None} for _ in range(BOARD_ROWS * BOARD_COLS)]
for row in range(BOARD_ROWS):
    for col in range(1, 6):
        if col == 1:
            board_values[row * BOARD_COLS + col]['player'] = 1
        if col == 5:
            board_values[row * BOARD_COLS + col]['ai'] = 1

def update_hand_positions():
    global original_hand_positions
    original_hand_positions = []
    if hand_cards:
        total_width = len(hand_cards) * (DECK_CARD_WIDTH - OVERLAP_OFFSET) + (len(hand_cards) - 1) * 10
        start_x = (SCREEN_WIDTH - total_width) // 2
        for i, card in enumerate(hand_cards):
            pos = (start_x + i * (DECK_CARD_WIDTH - OVERLAP_OFFSET + 10), HAND_POSITION_Y)
            card['rect'].topleft = pos
            card['angle'] = -CARD_TILT_ANGLE * (i - (len(hand_cards) - 1) / 2)
            original_hand_positions.append(pos)

def draw_rotated_card(screen, card):
    rect = card['rect']
    angle = card['angle']
    image = card['card'].image
    card_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    card_surface.fill((0, 0, 0, 0))  # Transparent fill
    card_surface.blit(image, (1, 1))
    pygame.draw.rect(card_surface, BLACK, card_surface.get_rect(), 1)
    rotated_card = pygame.transform.rotate(card_surface, angle)
    rotated_rect = rotated_card.get_rect(center=rect.center)
    screen.blit(rotated_card, rotated_rect.topleft)

def get_arc_position_and_angle(start_pos, end_pos, start_angle, end_angle, progress, arc_height):
    x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
    mid_x = (start_pos[0] + end_pos[0]) / 2
    a = -4 * arc_height / ((start_pos[0] - end_pos[0]) ** 2)
    y = a * (x - mid_x) ** 2 + min(start_pos[1], end_pos[1]) - arc_height
    angle = start_angle + (end_angle - start_angle) * progress
    return (x, y), angle

def draw_card_from_deck(deck):
    global moving_card, moving_target_pos, target_angle, arc_progress
    if len(hand_cards) < MAX_HAND_CARDS:
        drawn_card = deck.draw_card()
        if drawn_card:
            moving_card = {'rect': pygame.Rect(DECK_POSITION_X, DECK_POSITION_Y, DECK_CARD_WIDTH, DECK_CARD_HEIGHT), 'angle': 0, 'card': drawn_card}
            new_card = {'rect': pygame.Rect(0, 0, DECK_CARD_WIDTH, DECK_CARD_HEIGHT), 'angle': 0, 'card': drawn_card}
            hand_cards.append(new_card)
            update_hand_positions()
            moving_target_pos = new_card['rect'].center
            target_angle = new_card['angle']
            hand_cards.pop()
            arc_progress = 0

# Initiate drawing the first card
draw_card_from_deck(player_deck)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if moving_card is None:
                for card in hand_cards:
                    if card['rect'].collidepoint(mouse_x, mouse_y):
                        dragging_card = card
                        dragging_offset_x = card['rect'].x - mouse_x
                        dragging_offset_y = card['rect'].y - mouse_y
                        break
            if DECK_POSITION_X <= mouse_x <= DECK_POSITION_X + DECK_CARD_WIDTH and \
               DECK_POSITION_Y <= mouse_y <= DECK_POSITION_Y + DECK_CARD_HEIGHT:
                draw_card_from_deck(player_deck)
        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging_card:
                mouse_x, mouse_y = event.pos
                valid_placement = False
                for row in range(BOARD_ROWS):
                    for col in range(BOARD_COLS):
                        space_x = centered_margin_x + col * RECT_WIDTH
                        space_y = centered_margin_y + row * RECT_HEIGHT
                        space = pygame.Rect(space_x, space_y, RECT_WIDTH, RECT_HEIGHT)
                        index = row * BOARD_COLS + col
                        if space.collidepoint(mouse_x, mouse_y) and 1 <= col <= 5:
                            if board_values[index]['player'] >= dragging_card['card'].placement_cost:
                                board_values[index]['player'] -= dragging_card['card'].placement_cost
                                board_values[index]['image'] = dragging_card['card'].image
                                hand_cards.remove(dragging_card)
                                update_hand_positions()
                                valid_placement = True
                                break
                if not valid_placement:
                    # Snap back to original position
                    idx = hand_cards.index(dragging_card)
                    dragging_card['rect'].topleft = original_hand_positions[idx]
                    dragging_card['angle'] = -CARD_TILT_ANGLE * (idx - (len(hand_cards) - 1) / 2)
                dragging_card = None
        elif event.type == pygame.MOUSEMOTION:
            if dragging_card:
                mouse_x, mouse_y = event.pos
                dragging_card['rect'].x = mouse_x + dragging_offset_x
                dragging_card['rect'].y = mouse_y + dragging_offset_y

    screen.fill(WHITE)

    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            space_x = centered_margin_x + col * RECT_WIDTH
            space_y = centered_margin_y + row * RECT_HEIGHT
            space = pygame.Rect(space_x, space_y, RECT_WIDTH, RECT_HEIGHT)
            pygame.draw.rect(screen, BLACK, space, 1)

            # Draw images on board spaces based on current board values
            index = row * BOARD_COLS + col
            if board_values[index]['image'] is not None:
                screen.blit(board_values[index]['image'], (space_x + 1, space_y + 1))
            else:
                # Draw pawns in columns 1 and 5 if no card image is present
                if col == 1:
                    screen.blit(green_pawn_image, (space_x + 1, space_y + 1))
                elif col == 5:
                    screen.blit(red_pawn_image, (space_x + 1, space_y + 1))

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
                draw_card_from_deck(player_deck)
            elif auto_drawing and initial_draw_count == 1:
                auto_drawing = False
        else:
            moving_card['rect'].center, moving_card['angle'] = get_arc_position_and_angle(
                (DECK_POSITION_X, DECK_POSITION_Y), moving_target_pos, 0, target_angle, arc_progress, ARC_HEIGHT
            )
        if moving_card:
            draw_rotated_card(screen, moving_card)

    for card in hand_cards:
        draw_rotated_card(screen, card)

    if dragging_card:
        draw_rotated_card(screen, dragging_card)

    pygame.display.flip()

pygame.quit()
sys.exit()
