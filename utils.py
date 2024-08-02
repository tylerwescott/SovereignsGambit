import pygame
import random
from images import load_images
from particlePrinciple import ParticlePrinciple
from constants import *
green_pawn_image, red_pawn_image, foot_soldier_image, apprentice_image, rogue_image, spearman_image, archer_image, shieldbearer_image, knight_image, vanguard_image, guardian_image, sorcerer_image, fire_summoner_image, fire_monster_image = load_images()

def draw_rotated_card(screen, card):
    rect = card['rect']
    angle = card['angle']
    image = card['card'].image
    strength = card['card'].strength
    placement_cost = card['card'].placement_cost
    pawn_placement = card['card'].pawn_placement
    power_up_positions = card['card'].power_up_positions
    power_down_positions = card['card'].power_down_positions  # Add this attribute to the Card class

    card_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    card_surface.fill((0, 0, 0, 0))  # Transparent fill
    card_surface.blit(image, (1, 1))
    pygame.draw.rect(card_surface, BLACK, card_surface.get_rect(), 1)

    # Render the strength text in the bottom left corner
    font = pygame.font.SysFont(None, 25)
    strength_text = font.render(str(strength), True, BLACK)
    strength_text = pygame.transform.rotate(strength_text, angle)
    strength_rect = strength_text.get_rect()
    strength_rect.bottomleft = (5, rect.height - 5)
    card_surface.blit(strength_text, strength_rect.topleft)

    # Render the placement cost text in the top left corner
    placement_cost_text = font.render(str(placement_cost), True, BLACK)
    placement_cost_text = pygame.transform.rotate(placement_cost_text, angle)
    placement_cost_rect = placement_cost_text.get_rect()
    placement_cost_rect.topleft = (5, 5)
    card_surface.blit(placement_cost_text, placement_cost_rect.topleft)

    # Draw the 7x7 grid to show pawn placement, power-up, and power-down positions
    grid_size = 7
    original_cell_size = min(rect.width, rect.height) // grid_size
    cell_size = int(original_cell_size * (1 / 3))  # Resize to one-third
    grid_surface = pygame.Surface((cell_size * grid_size, cell_size * grid_size), pygame.SRCALPHA)
    grid_surface.fill((0, 0, 0, 0))  # Transparent fill

    for row in range(grid_size):
        for col in range(grid_size):
            cell_x = col * cell_size
            cell_y = row * cell_size
            # Draw red for power-down positions
            if (row - grid_size // 2, col - grid_size // 2) in power_down_positions:
                pygame.draw.rect(grid_surface, RED, (cell_x, cell_y, cell_size, cell_size))
            elif (row - grid_size // 2, col - grid_size // 2) in pawn_placement:
                pygame.draw.rect(grid_surface, YELLOW, (cell_x, cell_y, cell_size, cell_size))
            elif (row - grid_size // 2, col - grid_size // 2) in power_up_positions:
                pygame.draw.rect(grid_surface, BLUE, (cell_x, cell_y, cell_size, cell_size))
            pygame.draw.rect(grid_surface, BLACK, (cell_x, cell_y, cell_size, cell_size), 1)

    # Draw the center cell in white
    center_x = (grid_size // 2) * cell_size
    center_y = (grid_size // 2) * cell_size
    pygame.draw.rect(grid_surface, WHITE, (center_x, center_y, cell_size, cell_size))

    rotated_grid = pygame.transform.rotate(grid_surface, angle)
    grid_rect = rotated_grid.get_rect(center=(rect.width // 2, rect.height - cell_size * grid_size // 2))

    card_surface.blit(rotated_grid, grid_rect.topleft)

    rotated_card = pygame.transform.rotate(card_surface, angle)
    rotated_rect = rotated_card.get_rect(center=rect.center)
    screen.blit(rotated_card, rotated_rect.topleft)

    # Calculate the position of the top left corner of the rotated image
    top_left_offset = pygame.math.Vector2(-rect.width // 2, -rect.height // 2).rotate(-angle)
    top_left_pos = pygame.math.Vector2(rect.center) + top_left_offset

    pygame.draw.circle(screen, (255, 0, 0), top_left_pos, 5)  # Red dot at top left
    return top_left_pos
def place_card_on_board(card, row, col, board_values, player=True, particle_system=None, centered_margin_x=None, centered_margin_y=None):
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
    board_values[index]['card'] = card
    board_values[index]['strength'] = card.strength
    place_card_pawns(card, row, col, player, board_values, green_pawn_image, red_pawn_image)
    apply_power_up(card, row, col, board_values, player)
    apply_power_down(card, row, col, board_values, player)
    if particle_system and centered_margin_x is not None and centered_margin_y is not None:
        trigger_particle_effect(row, col, centered_margin_x, centered_margin_y, particle_system)

def trigger_particle_effect(row, col, centered_margin_x, centered_margin_y, particle_system):
    card_x = centered_margin_x + col * RECT_WIDTH
    card_y = centered_margin_y + row * RECT_HEIGHT
    card_width = RECT_WIDTH
    card_height = RECT_HEIGHT

    # Emit particles from the sides of the card's rectangle
    for offset in range(0, int(card_width), 5):
        particle_system.add_particles((card_x + offset, card_y))
        particle_system.add_particles((card_x + offset, card_y + card_height))

    for offset in range(0, int(card_height), 5):
        particle_system.add_particles((card_x, card_y + offset))
        particle_system.add_particles((card_x + card_width, card_y + offset))

def get_arc_position_and_angle(start_pos, end_pos, start_angle, end_angle, progress, arc_height):
    x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
    mid_x = (start_pos[0] + end_pos[0]) / 2
    a = -4 * arc_height / ((start_pos[0] - end_pos[0]) ** 2)
    y = a * (x - mid_x) ** 2 + min(start_pos[1], end_pos[1]) - arc_height
    y = y + (end_pos[1] - y) * progress  # Smooth out the y position to reach the end smoothly
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

def ai_place_card(screen, ai_hand_cards, board_values, ai_deck, green_pawn_image, red_pawn_image, draw_card_from_ai_deck,
                  place_card_on_board, original_ai_hand_positions, centered_margin_x, centered_margin_y, small_font,
                  player_hand_cards, original_player_hand_positions, player_deck_count, player_hand_count, font, particle_system):
    for card in ai_hand_cards:
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                index = row * BOARD_COLS + col
                if 1 <= col <= 5 and board_values[index]['ai'] >= card['card'].placement_cost:
                    ai_hand_cards.remove(card)
                    update_hand_positions(ai_hand_cards, AI_HAND_POSITION_Y, original_ai_hand_positions)

                    start_pos = card['rect'].center
                    end_pos = ((centered_margin_x + col * RECT_WIDTH) + RECT_WIDTH // 2, (centered_margin_y + row * RECT_HEIGHT) + RECT_HEIGHT // 2)
                    start_angle = card['angle']
                    end_angle = 0  # Set the angle to 0 when placing on the board

                    # Animate the card to the board
                    animate_card_to_board(screen, card, start_pos, end_pos, start_angle, end_angle, 1000, centered_margin_x, centered_margin_y, board_values, green_pawn_image, red_pawn_image, small_font, ai_hand_cards, ai_deck.cards_left(), original_ai_hand_positions, len(ai_hand_cards), player_hand_cards, player_deck_count, original_player_hand_positions, player_hand_count, font)

                    # After animation, place the card and trigger effects
                    place_card_on_board(card['card'], row, col, board_values, player=False, particle_system=particle_system, centered_margin_x=centered_margin_x, centered_margin_y=centered_margin_y)
                    return

    draw_card_from_ai_deck(ai_deck)

def draw_board_and_elements(screen, board_values, centered_margin_x, centered_margin_y, small_font, player_hand_cards,
                            ai_hand_cards, player_deck_count, player_hand_count, ai_deck_count, ai_hand_count, font,
                            green_pawn_image, red_pawn_image, dragging_card=None):
    screen.fill(WHITE)

    player_row_strengths = [0] * BOARD_ROWS
    ai_row_strengths = [0] * BOARD_ROWS

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

                # Draw the strength text if the card is present
                if board_values[index]['card'] is not None:
                    strength = board_values[index]['strength']
                    strength_text = small_font.render(str(strength), True, BLACK)
                    strength_rect = strength_text.get_rect()
                    strength_rect.bottomleft = (space_x + 5, space_y + RECT_HEIGHT - 5)
                    screen.blit(strength_text, strength_rect.topleft)

                    # Draw border based on card owner
                    if board_values[index]['owner'] == 'player':
                        pygame.draw.rect(screen, BLUE, space, 3)  # Blue border for player
                        player_row_strengths[row] += strength
                    elif board_values[index]['owner'] == 'ai':
                        pygame.draw.rect(screen, RED, space, 3)  # Red border for AI
                        ai_row_strengths[row] += strength

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
                screen.blit(player_pawn_text,
                            (space_x + 5, space_y + RECT_HEIGHT // 2 - player_pawn_text.get_height() // 2))
                screen.blit(ai_pawn_text, (space_x + 5, space_y + RECT_HEIGHT // 2 + ai_pawn_text.get_height() // 2))

    # Preview strength changes while dragging a card
    if dragging_card:
        valid_placement = False
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                index = row * BOARD_COLS + col
                if board_values[index]['card'] is None and pygame.Rect(centered_margin_x + col * RECT_WIDTH,
                                                                       centered_margin_y + row * RECT_HEIGHT,
                                                                       RECT_WIDTH, RECT_HEIGHT).collidepoint(
                    dragging_card['rect'].center):
                    # Check if the card can be placed here based on pawn placement requirements
                    can_place = True
                    required_pawns = 0
                    for placement in dragging_card['card'].pawn_placement:
                        new_row = row + placement[0]
                        new_col = col + placement[1]
                        if new_row < 0 or new_row >= BOARD_ROWS or new_col < 1 or new_col > 5:
                            can_place = False
                            break
                        new_index = new_row * BOARD_COLS + new_col
                        if board_values[new_index]['card'] is not None:
                            can_place = False
                            break
                        required_pawns += 1

                    if can_place and board_values[index]['player'] >= required_pawns:
                        valid_placement = True
                        # Highlight the valid space and handle strength preview...
                        # Your existing code for highlighting and strength preview

                        # Calculate potential strength changes
                        preview_player_row_strengths = player_row_strengths[:]
                        preview_ai_row_strengths = ai_row_strengths[:]

                        preview_player_row_strengths[row] += dragging_card['card'].strength if dragging_card['card'].strength else 0

                        for pos in dragging_card['card'].power_up_positions:
                            new_row = row + pos[0]
                            new_col = col + pos[1]
                            if 0 <= new_row < BOARD_ROWS and 0 <= new_col < BOARD_COLS:
                                new_index = new_row * BOARD_COLS + new_col
                                if board_values[new_index]['card'] and board_values[new_index]['owner'] == 'player':
                                    preview_player_row_strengths[new_row] += dragging_card['card'].power_up_value

                        for pos in dragging_card['card'].power_down_positions:
                            new_row = row + pos[0]
                            new_col = col + pos[1]
                            if 0 <= new_row < BOARD_ROWS and 0 <= new_col < BOARD_COLS:
                                new_index = new_row * BOARD_COLS + new_col
                                if board_values[new_index]['card'] and board_values[new_index]['owner'] == 'ai':
                                    current_strength = board_values[new_index]['strength']
                                    reduction = min(current_strength, dragging_card['card'].power_down_value)
                                    preview_ai_row_strengths[new_row] -= reduction

                        # Display the strength previews if the card can be placed
                        if valid_placement:
                            for r in range(BOARD_ROWS):
                                player_strength_text = f'Strength ttl: {player_row_strengths[r]}'
                                ai_strength_text = f'Strength ttl: {ai_row_strengths[r]}'

                                if player_row_strengths[r] != preview_player_row_strengths[r]:
                                    player_change = preview_player_row_strengths[r] - player_row_strengths[r]
                                    player_strength_text += f' ({"+" if player_change > 0 else ""}{player_change})'
                                if ai_row_strengths[r] != preview_ai_row_strengths[r]:
                                    ai_change = preview_ai_row_strengths[r] - ai_row_strengths[r]
                                    ai_strength_text += f' ({"+" if ai_change > 0 else ""}{ai_change})'

                                player_strength_text_surface = small_font.render(player_strength_text, True, BLUE)
                                ai_strength_text_surface = small_font.render(ai_strength_text, True, RED)

                                player_strength_rect = player_strength_text_surface.get_rect(
                                    center=(centered_margin_x - RECT_WIDTH // 2, centered_margin_y + r * RECT_HEIGHT + RECT_HEIGHT // 2))
                                ai_strength_rect = ai_strength_text_surface.get_rect(center=(
                                    centered_margin_x + BOARD_COLS * RECT_WIDTH + RECT_WIDTH // 2,
                                    centered_margin_y + r * RECT_HEIGHT + RECT_HEIGHT // 2))

                                screen.blit(player_strength_text_surface, player_strength_rect)
                                screen.blit(ai_strength_text_surface, ai_strength_rect)

    # Highlight the valid board space and show faded green pawns
    if dragging_card and valid_placement:
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                space_x = centered_margin_x + col * RECT_WIDTH
                space_y = centered_margin_y + row * RECT_HEIGHT
                space = pygame.Rect(space_x, space_y, RECT_WIDTH, RECT_HEIGHT)
                index = row * BOARD_COLS + col
                if space.collidepoint(dragging_card['rect'].center):
                    if board_values[index]['card'] is None and board_values[index]['player'] >= dragging_card[
                        'card'].placement_cost:
                        pygame.draw.rect(screen, (0, 255, 0), space, 5)

                        # Show faded green pawns where they will be placed
                        for placement in dragging_card['card'].pawn_placement:
                            row_offset, col_offset = placement
                            new_row = row + row_offset
                            new_col = col + col_offset
                            if 0 <= new_row < BOARD_ROWS and 1 <= new_col <= 5:
                                pawn_index = new_row * BOARD_COLS + new_col
                                if board_values[pawn_index]['card'] is None:
                                    pawn_x = centered_margin_x + new_col * RECT_WIDTH
                                    pawn_y = centered_margin_y + new_row * RECT_HEIGHT
                                    faded_green_pawn = green_pawn_image.copy()
                                    faded_green_pawn.set_alpha(128)  # Set transparency to 50%
                                    screen.blit(faded_green_pawn, (pawn_x + 1, pawn_y + 1))

                        # Show power-up indicator
                        for row_offset, col_offset in dragging_card['card'].power_up_positions:
                            new_row = row + row_offset
                            new_col = col + col_offset
                            if 0 <= new_row < BOARD_ROWS and 0 <= new_col < BOARD_COLS:
                                power_up_index = new_row * BOARD_COLS + new_col
                                if board_values[power_up_index]['card'] is not None:
                                    power_up_x = centered_margin_x + new_col * RECT_WIDTH
                                    power_up_y = centered_margin_y + new_row * RECT_HEIGHT
                                    power_up_image = pygame.image.load('images/powerUp.jpg')
                                    power_up_size = int(RECT_WIDTH / 4)
                                    power_up_image = pygame.transform.scale(power_up_image,
                                                                            (power_up_size, power_up_size))
                                    screen.blit(power_up_image, (
                                        power_up_x + RECT_WIDTH // 2 - power_up_image.get_width() // 2,
                                        power_up_y + RECT_HEIGHT - power_up_image.get_height() - 5))

                                    # Show the potential new strength value in green next to the current strength value
                                    current_strength = board_values[power_up_index]['strength']
                                    new_strength = current_strength + dragging_card['card'].power_up_value
                                    power_up_value_text = small_font.render(f"+{dragging_card['card'].power_up_value}",
                                                                            True, (0, 255, 0))
                                    power_up_value_rect = power_up_value_text.get_rect()
                                    power_up_value_rect.bottomleft = (
                                        power_up_x + 5 + strength_text.get_width(), power_up_y + RECT_HEIGHT - 5)
                                    screen.blit(power_up_value_text, power_up_value_rect.topleft)

                        # Show power-down indicator
                        for row_offset, col_offset in dragging_card['card'].power_down_positions:
                            new_row = row + row_offset
                            new_col = col + col_offset
                            if 0 <= new_row < BOARD_ROWS and 0 <= new_col < BOARD_COLS:
                                power_down_index = new_row * BOARD_COLS + new_col
                                if board_values[power_down_index]['card'] is not None:
                                    power_down_x = centered_margin_x + new_col * RECT_WIDTH
                                    power_down_y = centered_margin_y + new_row * RECT_HEIGHT
                                    power_down_image = pygame.image.load('images/powerDown.jpg')
                                    power_down_size = int(RECT_WIDTH / 4)
                                    power_down_image = pygame.transform.scale(power_down_image,
                                                                              (power_down_size, power_down_size))
                                    screen.blit(power_down_image, (
                                        power_down_x + RECT_WIDTH // 2 - power_down_image.get_width() // 2,
                                        power_down_y + RECT_HEIGHT - power_down_image.get_height() - 5))

                                    # Show the potential strength decrease value in red next to the current strength value
                                    current_strength = board_values[power_down_index]['strength']
                                    power_down_value = min(current_strength, dragging_card['card'].power_down_value)
                                    power_down_value_text = small_font.render(
                                        f"-{power_down_value}",
                                        True, (255, 0, 0))
                                    power_down_value_rect = power_down_value_text.get_rect()
                                    power_down_value_rect.bottomleft = (
                                        power_down_x + 5 + strength_text.get_width(), power_down_y + RECT_HEIGHT - 5)
                                    screen.blit(power_down_value_text, power_down_value_rect.topleft)

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

    player_hand_count_text = small_font.render(f'Hand: {player_hand_count}', True, BLACK)
    screen.blit(player_hand_count_text, (10, 10))
    player_deck_count_text = small_font.render(f'Deck: {player_deck_count}', True, BLACK)
    screen.blit(player_deck_count_text, (10, 70))

    # Draw the AI's deck and count
    for i in range(5):
        card_x = AI_DECK_POSITION_X + i * 2
        card_y = AI_DECK_POSITION_Y - i * 2
        card_rect = pygame.Rect(card_x, card_y, DECK_CARD_WIDTH, DECK_CARD_HEIGHT)
        pygame.draw.rect(screen, BLACK, card_rect, 1)

    ai_hand_count_text = small_font.render(f'AI Hand: {ai_hand_count}', True, BLACK)
    screen.blit(ai_hand_count_text, (10, 130))
    ai_deck_count_text = small_font.render(f'AI Deck: {ai_deck_count}', True, BLACK)
    screen.blit(ai_deck_count_text, (10, 190))

def animate_card_to_board(screen, card, start_pos, end_pos, start_angle, end_angle, duration, centered_margin_x,
                          centered_margin_y, board_values, green_pawn_image, red_pawn_image, small_font, ai_hand_cards,
                          ai_deck_count, original_ai_hand_positions, ai_hand_count, player_hand_cards, player_deck_count,
                          original_player_hand_positions, player_hand_count, font):
    start_time = pygame.time.get_ticks()
    card_width, card_height = DECK_CARD_WIDTH, DECK_CARD_HEIGHT
    card_center_offset = (card_width // 2, card_height // 2)

    while pygame.time.get_ticks() - start_time < duration:
        elapsed = pygame.time.get_ticks() - start_time
        progress = elapsed / duration

        current_x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
        current_y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress
        current_angle = start_angle + (end_angle - start_angle) * progress

        draw_board_and_elements(screen, board_values, centered_margin_x, centered_margin_y, small_font, player_hand_cards, ai_hand_cards, player_deck_count, player_hand_count, ai_deck_count, ai_hand_count, font, green_pawn_image, red_pawn_image)

        moving_card_rect = pygame.Rect(current_x - card_center_offset[0], current_y - card_center_offset[1], card_width, card_height)
        draw_rotated_card(screen, {
            'rect': moving_card_rect,
            'angle': current_angle,
            'card': card['card']
        })

        pygame.display.flip()

    card['rect'].center = end_pos
    card['angle'] = end_angle

    # Debug: Draw final position marker
    pygame.draw.circle(screen, (255, 0, 0), end_pos, 5)
    pygame.display.flip()

def apply_power_up(card, base_row, base_col, board_values, player):
    for row_offset, col_offset in card.power_up_positions:
        new_row = base_row + row_offset
        new_col = base_col + col_offset
        if 0 <= new_row < BOARD_ROWS and 0 <= new_col < BOARD_COLS:
            index = new_row * BOARD_COLS + new_col
            target_card = board_values[index]['card']
            target_owner = board_values[index]['owner']
            # Ensure only the player's own cards are affected
            if target_card and ((player and target_owner == 'player') or (not player and target_owner == 'ai')):
                board_values[index]['strength'] += card.power_up_value
                print(f"Power-up applied at ({new_row}, {new_col}). New strength: {board_values[index]['strength']}")


def apply_power_down(card, base_row, base_col, board_values, player):
    for row_offset, col_offset in card.power_down_positions:
        # Invert the column offset if the AI placed the card
        if not player:
            col_offset = -col_offset

        new_row = base_row + row_offset
        new_col = base_col + col_offset
        if 0 <= new_row < BOARD_ROWS and 0 <= new_col < BOARD_COLS:
            index = new_row * BOARD_COLS + new_col
            target_card = board_values[index]['card']
            target_owner = board_values[index]['owner']
            # Ensure only the opponent's cards are affected
            if target_card and ((player and target_owner == 'ai') or (not player and target_owner == 'player')):
                board_values[index]['strength'] -= card.power_down_value
                print(f"Power-down applied at ({new_row}, {new_col}). New strength: {board_values[index]['strength']}")

                # Check if the card's strength is 0 or less
                if board_values[index]['strength'] <= 0:
                    # Remove the card and replace it with a pawn
                    board_values[index]['card'] = None
                    board_values[index]['strength'] = 0
                    board_values[index]['owner'] = None
                    # Place a pawn for the player who played the power-down card
                    if player:
                        board_values[index]['player'] = 1
                        board_values[index]['ai'] = 0
                        board_values[index]['image'] = green_pawn_image
                    else:
                        board_values[index]['player'] = 0
                        board_values[index]['ai'] = 1
                        board_values[index]['image'] = red_pawn_image

def draw_tooltip(screen, card, position):
    # Create a surface for the tooltip
    font = pygame.font.SysFont(None, 24)
    text_lines = [
        f"Name: {card.name}",
        f"Strength: {card.strength}",
        f"Cost: {card.placement_cost}",
        f"Pawns: {card.pawn_placement}",
        f"Power Up: {card.power_up_positions} ({card.power_up_value})"
    ]
    text_surfaces = [font.render(line, True, (255, 255, 255)) for line in text_lines]
    tooltip_width = max(surface.get_width() for surface in text_surfaces) + 10
    tooltip_height = sum(surface.get_height() for surface in text_surfaces) + 10

    tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
    tooltip_surface.fill((0, 0, 0, 180))  # Semi-transparent black background

    # Render the text on the tooltip surface
    y_offset = 5
    for text_surface in text_surfaces:
        tooltip_surface.blit(text_surface, (5, y_offset))
        y_offset += text_surface.get_height()

    # Position the tooltip near the cursor but within screen bounds
    screen_width, screen_height = screen.get_size()
    x, y = position
    x = min(x, screen_width - tooltip_width)
    y = min(y, screen_height - tooltip_height)

    # Blit the tooltip surface onto the main screen
    screen.blit(tooltip_surface, (x, y))
