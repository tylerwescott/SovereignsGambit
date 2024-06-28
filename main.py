import pygame
import sys
from constants import *
from deck import Deck
from images import load_images
from utils import draw_rotated_card, get_arc_position_and_angle, update_hand_positions, ai_place_card, place_card_pawns
from card import Card

pygame.init()

# Load images
green_pawn_image, red_pawn_image, foot_soldier_image, apprentice_image, rogue_image, spearman_image, archer_image = load_images()  # Update to load archer_image

# Create card instances
foot_soldier_card = Card("Foot Soldier", 1, foot_soldier_image, [(0, 1)], 2)
apprentice_card = Card("Apprentice", 1, apprentice_image, [(0, 2)], 1)
rogue_card = Card("Rogue", 1, rogue_image, [(0, 3)], 1)
spearman_card = Card("Spearman", 2, spearman_image, [(0, 1), (0, 2)], 2)
archer_card = Card("Archer", 2, archer_image, [(0, 2), (0, 3)], 2)  # Add archer card

# Initialize player and AI decks with 30 cards each
player_deck = Deck([foot_soldier_card, apprentice_card, rogue_card, spearman_card, archer_card] * 6)
ai_deck = Deck([foot_soldier_card, apprentice_card, rogue_card, spearman_card, archer_card] * 6)

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
board_values = [{'player': 0, 'ai': 0, 'image': None, 'card': None} for _ in range(BOARD_ROWS * BOARD_COLS)]
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
            moving_card = {'rect': pygame.Rect(PLAYER_DECK_POSITION_X, PLAYER_DECK_POSITION_Y, DECK_CARD_WIDTH, DECK_CARD_HEIGHT), 'angle': 0, 'card': drawn_card}
            new_card = {'rect': pygame.Rect(0, 0, DECK_CARD_WIDTH, DECK_CARD_HEIGHT), 'angle': 0, 'card': drawn_card}
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
            ai_moving_card = {'rect': pygame.Rect(AI_DECK_POSITION_X, AI_DECK_POSITION_Y, DECK_CARD_WIDTH, DECK_CARD_HEIGHT), 'angle': 0, 'card': drawn_card}
            new_card = {'rect': pygame.Rect(0, 0, DECK_CARD_WIDTH, DECK_CARD_HEIGHT), 'angle': 0, 'card': drawn_card}
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
    else:
        board_values[index]['ai'] -= card.placement_cost
        board_values[index]['player'] = 0
    board_values[index]['image'] = card.image
    board_values[index]['card'] = card  # Store the card itself
    place_card_pawns(card, row, col, player, board_values, green_pawn_image, red_pawn_image)
    print(f"Card {card.name} placed at ({row}, {col}). Player: {board_values[index]['player']}, AI: {board_values[index]['ai']}")

# Initiate drawing the first card for player and AI
draw_card_from_player_deck(player_deck)
draw_card_from_ai_deck(ai_deck)

running = True
while running:
    if turn_end:
        if is_player_turn:
            is_player_turn = False
            ai_place_card(screen, ai_hand_cards, board_values, ai_deck, green_pawn_image, red_pawn_image, draw_card_from_ai_deck, place_card_on_board, original_ai_hand_positions, centered_margin_x, centered_margin_y, small_font, player_hand_cards, original_player_hand_positions, player_deck.cards_left(), len(player_hand_cards), font)
            turn_end = True  # Ensure the player's turn starts in the next iteration
        else:
            is_player_turn = True
            turn_end = False  # Reset turn_end for the next turn

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and is_player_turn:
            mouse_x, mouse_y = event.pos
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

            # Draw pawn counts for player and AI
            if 1 <= col <= 5:
                player_pawn_count = board_values[index]['player']
                ai_pawn_count = board_values[index]['ai']
                player_pawn_text = small_font.render(f'P: {player_pawn_count}', True, BLACK)
                ai_pawn_text = small_font.render(f'A: {ai_pawn_count}', True, BLACK)
                screen.blit(player_pawn_text, (space_x + 5, space_y + 5))
                screen.blit(ai_pawn_text, (space_x + 5, space_y + 25))

    for i in range(5):
        card_x = PLAYER_DECK_POSITION_X + i * 2
        card_y = PLAYER_DECK_POSITION_Y - i * 2
        card = pygame.Rect(card_x, card_y, DECK_CARD_WIDTH, DECK_CARD_HEIGHT)
        pygame.draw.rect(screen, BLACK, card, 1)

        ai_card_x = AI_DECK_POSITION_X + i * 2
        ai_card_y = AI_DECK_POSITION_Y - i * 2
        ai_card = pygame.Rect(ai_card_x, ai_card_y, DECK_CARD_WIDTH, DECK_CARD_HEIGHT)
        pygame.draw.rect(screen, BLACK, ai_card, 1)

    # Display the number of cards in the player's hand
    player_hand_count_text = font.render(f'Hand: {len(player_hand_cards)}', True, BLACK)
    screen.blit(player_hand_count_text, (10, 10))

    # Display the number of cards left in the player's deck
    player_deck_count_text = font.render(f'Deck: {player_deck.cards_left()}', True, BLACK)
    screen.blit(player_deck_count_text, (10, 70))

    # Display the number of cards in the AI's hand
    ai_hand_count_text = font.render(f'AI Hand: {len(ai_hand_cards)}', True, BLACK)
    screen.blit(ai_hand_count_text, (10, 130))

    # Display the number of cards left in the AI's deck
    ai_deck_count_text = font.render(f'AI Deck: {ai_deck.cards_left()}', True, BLACK)
    screen.blit(ai_deck_count_text, (10, 190))

    if moving_card is not None:
        arc_progress += ANIMATION_SPEED
        if arc_progress >= 1:
            moving_card['rect'].center = moving_target_pos
            moving_card['angle'] = target_angle
            player_hand_cards.append(moving_card)
            update_hand_positions(player_hand_cards, PLAYER_HAND_POSITION_Y, original_player_hand_positions)
            print(
                f"Card {moving_card['card'].name} reached final position: {moving_card['rect'].center}, Angle: {moving_card['angle']}")
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
                (PLAYER_DECK_POSITION_X, PLAYER_DECK_POSITION_Y), moving_target_pos, 0, target_angle, arc_progress,
                ARC_HEIGHT
            )
            print(
                f"Moving card: {moving_card['card'].name}, Position: {moving_card['rect'].center}, Angle: {moving_card['angle']}")
            current_top_left = draw_rotated_card(screen, moving_card)
            print(f"Top left position while moving: {current_top_left}")

    for card in player_hand_cards:
        final_top_left = draw_rotated_card(screen, card)

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
                (AI_DECK_POSITION_X, AI_DECK_POSITION_Y), ai_moving_target_pos, 0, ai_target_angle, ai_arc_progress,
                ARC_HEIGHT
            )

        if ai_moving_card:
            draw_rotated_card(screen, ai_moving_card)

    for card in ai_hand_cards:
        draw_rotated_card(screen, card)

    if dragging_card:
        draw_rotated_card(screen, dragging_card)

    pygame.display.flip()

pygame.quit()
sys.exit()