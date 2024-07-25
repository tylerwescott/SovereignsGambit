import pygame
import sys
from constants import *
from deck import Deck
from images import load_images
from utils import draw_rotated_card, get_arc_position_and_angle, update_hand_positions, ai_place_card, place_card_pawns, draw_board_and_elements, apply_power_up, draw_tooltip
from card import Card

pygame.init()

# Load images
green_pawn_image, red_pawn_image, foot_soldier_image, apprentice_image, rogue_image, spearman_image, archer_image, shieldbearer_image, knight_image, vanguard_image, guardian_image = load_images()

# Create card instances
foot_soldier_card = Card("Foot Soldier", 1, foot_soldier_image, [(0, 1)], 2)
apprentice_card = Card("Apprentice", 1, apprentice_image, [(0, 2)], 1)
rogue_card = Card("Rogue", 1, rogue_image, [(0, 3)], 1)
spearman_card = Card("Spearman", 2, spearman_image, [(0, 1), (0, 2)], 2)
archer_card = Card("Archer", 2, archer_image, [(0, 2), (0, 3)], 2)
shieldbearer_card = Card("Shieldbearer", 1, shieldbearer_image, [(-1, 0), (1, 0)], 1)
knight_card = Card("Knight", 2, knight_image, [(0, 0)], 3, power_up_positions=[(-1, 0), (1, 0)], power_up_value=1)  # Knight card with power-up
vanguard_card = Card("Vanguard", 1, vanguard_image, [(-1, 0), (1, 0), (0, -1), (0, 1)], 1)  # Vanguard card
guardian_card = Card("Guardian", 1, guardian_image, [(0, 1)], 1, power_up_positions=[(-1, 0)], power_up_value=1)

# Initialize player and AI decks with the Guardian card included
player_deck = Deck([foot_soldier_card, apprentice_card, rogue_card, spearman_card, archer_card, shieldbearer_card, knight_card, vanguard_card, guardian_card] * 3)
ai_deck = Deck([foot_soldier_card, apprentice_card, rogue_card, spearman_card, archer_card, shieldbearer_card, knight_card, vanguard_card, guardian_card] * 3)

# Player hand cards and other variables
player_hand_cards = []
moving_card = None
moving_target_pos = None
arc_progress = 0
target_angle = 0
initial_draw_count = 5
auto_drawing = True  # Flag to control automatic drawing at start
dragging_card = None
dragging_offset_x = 0
dragging_offset_y = 0
original_player_hand_positions = []

# AI hand cards and other variables
ai_hand_cards = []
ai_moving_card = None
ai_moving_target_pos = None
ai_arc_progress = 0
ai_target_angle = 0
ai_initial_draw_count = 5
ai_auto_drawing = True  # Flag to control automatic drawing at start
original_ai_hand_positions = []

# Turn variables
is_player_turn = True
turn_end = False

# Set up the screen
centered_margin_x = (SCREEN_WIDTH - BOARD_WIDTH) // 2
centered_margin_y = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sovereign's Gambit - Board and Deck")

# Fonts
font = pygame.font.SysFont(None, 55)
small_font = pygame.font.SysFont(None, 25)

# Initialize the board with values
board_values = [{'player': 0, 'ai': 0, 'image': None, 'card': None, 'owner': None, 'strength': 0} for _ in range(BOARD_ROWS * BOARD_COLS)]
for row in range(BOARD_ROWS):
    for col in range(1, 6):
        if col == 1:
            board_values[row * BOARD_COLS + col]['player'] = 1
        if col == 5:
            board_values[row * BOARD_COLS + col]['ai'] = 1

def draw_card_from_player_deck(deck):
    global moving_card, moving_target_pos, target_angle, arc_progress
    if len(player_hand_cards) < MAX_HAND_CARDS:
        drawn_card = deck.draw_card()
        if drawn_card:
            moving_card = {
                'rect': pygame.Rect(0, 0, DECK_CARD_WIDTH, DECK_CARD_HEIGHT),
                'angle': 0,
                'card': drawn_card
            }
            moving_card['rect'].topleft = (PLAYER_DECK_POSITION_X, PLAYER_DECK_POSITION_Y)
            new_card = {
                'rect': pygame.Rect(0, 0, DECK_CARD_WIDTH, DECK_CARD_HEIGHT),
                'angle': 0,
                'card': drawn_card
            }
            player_hand_cards.append(new_card)
            update_hand_positions(player_hand_cards, PLAYER_HAND_POSITION_Y, original_player_hand_positions)
            moving_target_pos = new_card['rect'].center
            target_angle = new_card['angle']
            player_hand_cards.pop()
            arc_progress = 0
            print(f"Drawing card: {drawn_card.name} to hand. Target position: {moving_target_pos}, Target angle: {target_angle}")

def draw_card_from_ai_deck(deck):
    global ai_moving_card, ai_moving_target_pos, ai_target_angle, ai_arc_progress
    if len(ai_hand_cards) < MAX_HAND_CARDS:
        drawn_card = deck.draw_card()
        if drawn_card:
            ai_moving_card = {
                'rect': pygame.Rect(0, 0, DECK_CARD_WIDTH, DECK_CARD_HEIGHT),
                'angle': 0,
                'card': drawn_card
            }
            ai_moving_card['rect'].topleft = (AI_DECK_POSITION_X, AI_DECK_POSITION_Y)
            new_card = {
                'rect': pygame.Rect(0, 0, DECK_CARD_WIDTH, DECK_CARD_HEIGHT),
                'angle': 0,
                'card': drawn_card
            }
            ai_hand_cards.append(new_card)
            update_hand_positions(ai_hand_cards, AI_HAND_POSITION_Y, original_ai_hand_positions)
            ai_moving_target_pos = new_card['rect'].center
            ai_target_angle = new_card['angle']
            ai_hand_cards.pop()
            ai_arc_progress = 0

def place_card_on_board(card, row, col, player=True):
    index = row * BOARD_COLS + col
    if player:
        board_values[index]['player'] -= card.placement_cost
        board_values[index]['ai'] = 0
        board_values[index]['owner'] = 'player'
    else:
        board_values[index]['ai'] -= card.placement_cost
        board_values[index]['player'] = 0
        board_values[index]['owner'] = 'ai'
    board_values[index]['image'] = card.image
    board_values[index]['card'] = card  # Store the card itself
    board_values[index]['strength'] = card.strength  # Initialize the strength attribute
    place_card_pawns(card, row, col, player, board_values, green_pawn_image, red_pawn_image)
    apply_power_up(card, row, col, board_values, player)
    print(f"Card {card.name} placed at ({row}, {col}). Player: {board_values[index]['player']}, AI: {board_values[index]['ai']}")

def end_turn():
    global is_player_turn, turn_end
    if is_player_turn:
        is_player_turn = False
        turn_end = True

# Print deck positions and draw red dots
print(f"Player Deck Position: ({PLAYER_DECK_POSITION_X}, {PLAYER_DECK_POSITION_Y})")
print(f"AI Deck Position: ({AI_DECK_POSITION_X}, {AI_DECK_POSITION_Y})")

# Initiate drawing the first card for player and AI
draw_card_from_player_deck(player_deck)
draw_card_from_ai_deck(ai_deck)

running = True
while running:
    if turn_end:
        if not is_player_turn:
            ai_place_card(screen, ai_hand_cards, board_values, ai_deck, green_pawn_image, red_pawn_image, draw_card_from_ai_deck, place_card_on_board, original_ai_hand_positions, centered_margin_x, centered_margin_y, small_font, player_hand_cards, original_player_hand_positions, player_deck.cards_left(), len(player_hand_cards), font)
            turn_end = False  # Ensure the player's turn starts in the next iteration
            is_player_turn = True

    mouse_x, mouse_y = pygame.mouse.get_pos()  # Track the mouse position for tooltip display

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if end_turn_button.collidepoint(mouse_x, mouse_y):
                end_turn()
            elif is_player_turn:
                if moving_card is None:
                    for card in player_hand_cards:
                        if card['rect'].collidepoint(mouse_x, mouse_y):
                            dragging_card = card
                            dragging_offset_x = card['rect'].x - mouse_x
                            dragging_offset_y = card['rect'].y - mouse_y
                            break
                if PLAYER_DECK_POSITION_X <= mouse_x <= PLAYER_DECK_POSITION_X + DECK_CARD_WIDTH and \
                   PLAYER_DECK_POSITION_Y <= mouse_y <= DECK_CARD_HEIGHT + PLAYER_DECK_POSITION_Y:
                    draw_card_from_player_deck(player_deck)
        elif event.type == pygame.MOUSEBUTTONUP and is_player_turn:
            if dragging_card:
                valid_placement = False
                for row in range(BOARD_ROWS):
                    for col in range(BOARD_COLS):
                        space_x = centered_margin_x + col * RECT_WIDTH
                        space_y = centered_margin_y + row * RECT_HEIGHT
                        space = pygame.Rect(space_x, space_y, RECT_WIDTH, RECT_HEIGHT)
                        index = row * BOARD_COLS + col
                        if space.collidepoint(mouse_x, mouse_y) and 1 <= col <= 5:
                            if board_values[index]['player'] >= dragging_card['card'].placement_cost:
                                place_card_on_board(dragging_card['card'], row, col, player=True)
                                player_hand_cards.remove(dragging_card)
                                update_hand_positions(player_hand_cards, PLAYER_HAND_POSITION_Y, original_player_hand_positions)
                                valid_placement = True
                                turn_end = True
                                break
                if not valid_placement:
                    # Snap back to original position
                    idx = player_hand_cards.index(dragging_card)
                    dragging_card['rect'].topleft = original_player_hand_positions[idx]
                    dragging_card['angle'] = -CARD_TILT_ANGLE * (idx - (len(player_hand_cards) - 1) / 2)
                dragging_card = None
        elif event.type == pygame.MOUSEMOTION:
            if dragging_card:
                dragging_card['rect'].x = mouse_x + dragging_offset_x
                dragging_card['rect'].y = mouse_y + dragging_offset_y

    # Draw board and elements
    draw_board_and_elements(screen, board_values, centered_margin_x, centered_margin_y, small_font, player_hand_cards,
                            ai_hand_cards, player_deck.cards_left(), len(player_hand_cards), ai_deck.cards_left(),
                            len(ai_hand_cards), font, green_pawn_image, red_pawn_image, dragging_card)

    # Draw red dots at deck positions
    pygame.draw.circle(screen, (255, 0, 0), (PLAYER_DECK_POSITION_X, PLAYER_DECK_POSITION_Y), 5)
    pygame.draw.circle(screen, (255, 0, 0), (AI_DECK_POSITION_X, AI_DECK_POSITION_Y), 5)

    if moving_card is not None:
        arc_progress += ANIMATION_SPEED
        if arc_progress >= 1:
            moving_card['rect'].center = moving_target_pos
            print(f"Card {moving_card['card'].name} center set to target position: {moving_card['rect'].center}")
            moving_card['angle'] = target_angle
            player_hand_cards.append(moving_card)
            update_hand_positions(player_hand_cards, PLAYER_HAND_POSITION_Y, original_player_hand_positions)
            print(f"Card {moving_card['card'].name} reached final position: {moving_card['rect'].center}, Angle: {moving_card['angle']}")
            final_top_left = draw_rotated_card(screen, moving_card)
            print(f"Top left position: {final_top_left}")
            moving_card = None
            if auto_drawing and initial_draw_count > 1:
                initial_draw_count -= 1
                draw_card_from_player_deck(player_deck)
            elif auto_drawing and initial_draw_count == 1:
                auto_drawing = False
        else:
            moving_card['rect'].center, moving_card['angle'] = get_arc_position_and_angle(
                (PLAYER_DECK_TOP_LEFT_X, PLAYER_DECK_TOP_LEFT_Y), moving_target_pos, 0, target_angle, arc_progress, ARC_HEIGHT
            )
            print(f"Player Deck Position X: {PLAYER_DECK_POSITION_X}, Player Deck Position Y: {PLAYER_DECK_POSITION_Y}")

            print(f"Player Deck Center X: {PLAYER_DECK_CENTER_X}, Player Deck Center Y: {PLAYER_DECK_CENTER_Y}")
            print(f"Moving card: {moving_card['card'].name}, Position: {moving_card['rect'].center}, Angle: {moving_card['angle']}")
            current_top_left = draw_rotated_card(screen, moving_card)
            print(f"Top left position while moving: {current_top_left}")

    # Draw the AI's hand
    for card in ai_hand_cards:
        draw_rotated_card(screen, card)

    # Draw the AI's moving card after drawing the AI hand cards
    if ai_moving_card is not None:
        ai_arc_progress += ANIMATION_SPEED
        if ai_arc_progress >= 1:
            ai_moving_card['rect'].center = ai_moving_target_pos
            ai_moving_card['angle'] = ai_target_angle
            ai_hand_cards.append(ai_moving_card)
            update_hand_positions(ai_hand_cards, AI_HAND_POSITION_Y, original_ai_hand_positions)
            ai_moving_card = None
            if ai_auto_drawing and ai_initial_draw_count > 1:
                ai_initial_draw_count -= 1
                draw_card_from_ai_deck(ai_deck)
            elif ai_auto_drawing and ai_initial_draw_count == 1:
                ai_auto_drawing = False
        else:
            ai_moving_card['rect'].center, ai_moving_card['angle'] = get_arc_position_and_angle(
                (AI_DECK_TOP_LEFT_X, AI_DECK_TOP_LEFT_Y), ai_moving_target_pos, 0, ai_target_angle, ai_arc_progress, ARC_HEIGHT
            )

        if ai_moving_card:
            draw_rotated_card(screen, ai_moving_card)

    if dragging_card:
        draw_rotated_card(screen, dragging_card)

    # Draw the "End Turn" button
    end_turn_button = pygame.Rect(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100, 190, 60)
    pygame.draw.rect(screen, BLACK, end_turn_button)
    end_turn_text = small_font.render('End Turn', True, WHITE)
    screen.blit(end_turn_text, (end_turn_button.x + 10, end_turn_button.y + 15))

    # Tooltip feature: Draw tooltip if hovering over a card in hand or on board
    if not dragging_card:  # Show tooltip only if not dragging a card
        for card in player_hand_cards:  # Only show tooltip for cards in player's hand
            if card['rect'].collidepoint(mouse_x, mouse_y):
                draw_tooltip(screen, card['card'], (mouse_x, mouse_y))
                break  # Show tooltip for only one card at a time

        # Check for cards on the board (player and AI)
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                index = row * BOARD_COLS + col
                board_card = board_values[index]['card']
                if board_card and pygame.Rect(centered_margin_x + col * RECT_WIDTH, centered_margin_y + row * RECT_HEIGHT, RECT_WIDTH, RECT_HEIGHT).collidepoint(mouse_x, mouse_y):
                    draw_tooltip(screen, board_card, (mouse_x, mouse_y))
                    break  # Show tooltip for only one card at a time

    pygame.display.flip()

pygame.quit()
sys.exit()
