import pygame
from constants import *

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

def update_hand_positions(hand_cards, hand_position_y, original_hand_positions):
    original_hand_positions.clear()
    if hand_cards:
        total_width = len(hand_cards) * (DECK_CARD_WIDTH - OVERLAP_OFFSET) + (len(hand_cards) - 1) * 10
        start_x = (SCREEN_WIDTH - total_width) // 2
        for i, card in enumerate(hand_cards):
            pos = (start_x + i * (DECK_CARD_WIDTH - OVERLAP_OFFSET + 10), hand_position_y)
            card['rect'].topleft = pos
            card['angle'] = -CARD_TILT_ANGLE * (i - (len(hand_cards) - 1) / 2)
            original_hand_positions.append(pos)

def place_card_pawns(card, base_row, base_col, player, board_values, green_pawn_image, red_pawn_image):
    for placement in card.pawn_placement:
        row_offset, col_offset = placement
        if not player:
            col_offset = -col_offset  # Reverse the column offset for AI player
        new_row = base_row + row_offset
        new_col = base_col + col_offset
        if 0 <= new_row < BOARD_ROWS and 1 <= new_col <= 5:  # Ensure placement is within columns 1 to 5
            index = new_row * BOARD_COLS + new_col
            # Only update pawn counts if there is no card occupying the spot
            if board_values[index]['card'] is None:
                if player:
                    board_values[index]['player'] += 1
                    board_values[index]['ai'] = 0  # Zero out AI's pawn count
                    board_values[index]['image'] = green_pawn_image
                else:
                    board_values[index]['ai'] += 1
                    board_values[index]['player'] = 0  # Zero out player's pawn count
                    board_values[index]['image'] = red_pawn_image
                print(f"Pawn placed at ({new_row}, {new_col}). Player: {board_values[index]['player']}, AI: {board_values[index]['ai']}")


def ai_place_card(ai_hand_cards, board_values, ai_deck, green_pawn_image, red_pawn_image, draw_card_from_ai_deck, place_card_on_board, original_ai_hand_positions):
    if ai_hand_cards:
        for card in ai_hand_cards:
            for row in range(BOARD_ROWS):
                for col in range(BOARD_COLS):
                    index = row * BOARD_COLS + col
                    if 1 <= col <= 5 and board_values[index]['ai'] > 0:  # Ensure placement is within columns 1 to 5 and there's at least one AI pawn
                        if board_values[index]['ai'] >= card['card'].placement_cost:
                            place_card_on_board(card['card'], row, col, player=False)
                            ai_hand_cards.remove(card)
                            update_hand_positions(ai_hand_cards, AI_HAND_POSITION_Y, original_ai_hand_positions)
                            draw_card_from_ai_deck(ai_deck)
                            print(f"AI placed {card['card'].name} at ({row}, {col})")
                            return
