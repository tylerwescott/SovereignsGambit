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

def ai_place_card(screen, ai_hand_cards, board_values, ai_deck, green_pawn_image, red_pawn_image, draw_card_from_ai_deck, place_card_on_board, original_ai_hand_positions, centered_margin_x, centered_margin_y, small_font, player_hand_cards, original_player_hand_positions, player_deck_count, font):
    for card in ai_hand_cards:
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                index = row * BOARD_COLS + col
                if 1 <= col <= 5 and board_values[index]['ai'] >= card['card'].placement_cost:
                    ai_hand_cards.remove(card)
                    update_hand_positions(ai_hand_cards, AI_HAND_POSITION_Y, original_ai_hand_positions)

                    start_pos = card['rect'].center
                    end_pos = ((centered_margin_x + col * RECT_WIDTH) + RECT_WIDTH // 2, (centered_margin_y + row * RECT_HEIGHT) + RECT_HEIGHT // 2)
                    angle = card['angle']

                    # Pass additional parameters to animate_card_to_board
                    animate_card_to_board(screen, card, start_pos, end_pos, angle, 1000, centered_margin_x, centered_margin_y, board_values, green_pawn_image, red_pawn_image, small_font, ai_hand_cards, ai_deck.cards_left(), original_ai_hand_positions, len(ai_hand_cards), player_hand_cards, player_deck_count, original_player_hand_positions, len(player_hand_cards), font)

                    place_card_on_board(card['card'], row, col, player=False)
                    return

    draw_card_from_ai_deck(ai_deck)

def animate_card_to_board(screen, card, start_pos, end_pos, angle, duration, centered_margin_x, centered_margin_y,
                          board_values, green_pawn_image, red_pawn_image, small_font, ai_hand_cards, ai_deck_count,
                          original_ai_hand_positions, ai_hand_count, player_hand_cards, player_deck_count,
                          original_player_hand_positions, player_hand_count, font):
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < duration:
        elapsed = pygame.time.get_ticks() - start_time
        progress = elapsed / duration

        current_x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
        current_y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress

        screen.fill(WHITE)

        # Draw the board and pawns
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                space_x = centered_margin_x + col * RECT_WIDTH
                space_y = centered_margin_y + row * RECT_HEIGHT
                space = pygame.Rect(space_x, space_y, RECT_WIDTH, RECT_HEIGHT)
                pygame.draw.rect(screen, BLACK, space, 1)

                index = row * BOARD_COLS + col
                if board_values[index]['image'] is not None:
                    screen.blit(board_values[index]['image'], (space_x + 1, space_y + 1))
                else:
                    if col == 1:
                        screen.blit(green_pawn_image, (space_x + 1, space_y + 1))
                    elif col == 5:
                        screen.blit(red_pawn_image, (space_x + 1, space_y + 1))

                if 1 <= col <= 5:
                    player_pawn_count = board_values[index]['player']
                    ai_pawn_count = board_values[index]['ai']
                    player_pawn_text = small_font.render(f'P: {player_pawn_count}', True, BLACK)
                    ai_pawn_text = small_font.render(f'A: {ai_pawn_count}', True, BLACK)
                    screen.blit(player_pawn_text, (space_x + 5, space_y + 5))
                    screen.blit(ai_pawn_text, (space_x + 5, space_y + 25))

        # Draw the player's hand
        for player_card in player_hand_cards:
            draw_rotated_card(screen, player_card)

        # Draw the AI's hand
        for ai_card in ai_hand_cards:
            draw_rotated_card(screen, ai_card)

        # Draw the player's deck and count
        for i in range(5):
            card_x = PLAYER_DECK_POSITION_X + i * 2
            card_y = PLAYER_DECK_POSITION_Y - i * 2
            card_rect = pygame.Rect(card_x, card_y, DECK_CARD_WIDTH, DECK_CARD_HEIGHT)
            pygame.draw.rect(screen, BLACK, card_rect, 1)

        player_hand_count_text = font.render(f'Hand: {player_hand_count}', True, BLACK)
        screen.blit(player_hand_count_text, (10, 10))
        player_deck_count_text = font.render(f'Deck: {player_deck_count}', True, BLACK)
        screen.blit(player_deck_count_text, (10, 70))

        # Draw the AI's deck and count
        for i in range(5):
            card_x = AI_DECK_POSITION_X + i * 2
            card_y = AI_DECK_POSITION_Y - i * 2
            card_rect = pygame.Rect(card_x, card_y, DECK_CARD_WIDTH, DECK_CARD_HEIGHT)
            pygame.draw.rect(screen, BLACK, card_rect, 1)

        ai_hand_count_text = font.render(f'AI Hand: {ai_hand_count}', True, BLACK)
        screen.blit(ai_hand_count_text, (10, 130))
        ai_deck_count_text = font.render(f'AI Deck: {ai_deck_count}', True, BLACK)
        screen.blit(ai_deck_count_text, (10, 190))

        # Draw the moving card
        draw_rotated_card(screen, {
            'rect': pygame.Rect(current_x, current_y, DECK_CARD_WIDTH, DECK_CARD_HEIGHT),
            'angle': angle,
            'card': card['card']
        })

        pygame.display.flip()

    card['rect'].center = end_pos