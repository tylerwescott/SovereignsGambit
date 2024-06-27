# Constants
ORIGINAL_RECT_WIDTH = 100
ORIGINAL_RECT_HEIGHT = int(ORIGINAL_RECT_WIDTH * 1.5)
RECT_WIDTH = ORIGINAL_RECT_WIDTH * 2
RECT_HEIGHT = RECT_WIDTH * 1.5
BOARD_COLS = 7  # Number of columns
BOARD_ROWS = 3  # Number of rows
BOARD_WIDTH = RECT_WIDTH * BOARD_COLS
BOARD_HEIGHT = RECT_HEIGHT * 3
MARGIN = 300
SCREEN_WIDTH = BOARD_WIDTH + 2 * MARGIN + 200
SCREEN_HEIGHT = BOARD_HEIGHT + 2 * MARGIN + 200  # Increased height for AI hand space
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DECK_CARD_WIDTH = RECT_WIDTH
DECK_CARD_HEIGHT = RECT_HEIGHT
PLAYER_DECK_POSITION_X = 50
PLAYER_DECK_POSITION_Y = SCREEN_HEIGHT - DECK_CARD_HEIGHT - 50
PLAYER_HAND_POSITION_Y = SCREEN_HEIGHT - DECK_CARD_HEIGHT - 50
AI_HAND_POSITION_Y = 50
AI_DECK_POSITION_X = SCREEN_WIDTH - DECK_CARD_WIDTH - 50
AI_DECK_POSITION_Y = 50
ANIMATION_SPEED = 0.005  # Significantly slower animation speed
CARD_TILT_ANGLE = 5  # Slight tilt angle for the cards in hand
OVERLAP_OFFSET = 60  # Increased amount of overlap between cards
ARC_HEIGHT = -100  # Height of the arc during the card movement (negative for upward arc)
MAX_HAND_CARDS = 10  # Maximum number of cards in the hand