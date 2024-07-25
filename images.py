import pygame
from constants import RECT_WIDTH, RECT_HEIGHT

def load_images():
    GREEN_PAWN_IMAGE_PATH = 'images/greenPawn.jpg'
    RED_PAWN_IMAGE_PATH = 'images/redPawn.jpg'
    FOOT_SOLDIER_IMAGE_PATH = 'images/footSoldier.jpg'
    APPRENTICE_IMAGE_PATH = 'images/apprentice.jpg'
    ROGUE_IMAGE_PATH = 'images/rogue.jpg'
    SPEARMAN_IMAGE_PATH = 'images/spearman.jpg'
    ARCHER_IMAGE_PATH = 'images/archer.jpg'
    SHIELDBEARER_IMAGE_PATH = 'images/shieldbearer.jpg'
    KNIGHT_IMAGE_PATH = 'images/knight.jpg'  # Path to the knight image
    VANGUARD_IMAGE_PATH = 'images/vanguard.jpg'
    GUARDIAN_IMAGE_PATH = 'images/guardian.jpg'

    green_pawn_image = pygame.image.load(GREEN_PAWN_IMAGE_PATH)
    green_pawn_image = pygame.transform.scale(green_pawn_image, (RECT_WIDTH - 2, RECT_HEIGHT - 2))
    red_pawn_image = pygame.image.load(RED_PAWN_IMAGE_PATH)
    red_pawn_image = pygame.transform.scale(red_pawn_image, (RECT_WIDTH - 2, RECT_HEIGHT - 2))
    foot_soldier_image = pygame.image.load(FOOT_SOLDIER_IMAGE_PATH)
    foot_soldier_image = pygame.transform.scale(foot_soldier_image, (RECT_WIDTH - 2, RECT_HEIGHT - 2))
    apprentice_image = pygame.image.load(APPRENTICE_IMAGE_PATH)
    apprentice_image = pygame.transform.scale(apprentice_image, (RECT_WIDTH - 2, RECT_HEIGHT - 2))
    rogue_image = pygame.image.load(ROGUE_IMAGE_PATH)
    rogue_image = pygame.transform.scale(rogue_image, (RECT_WIDTH - 2, RECT_HEIGHT - 2))
    spearman_image = pygame.image.load(SPEARMAN_IMAGE_PATH)
    spearman_image = pygame.transform.scale(spearman_image, (RECT_WIDTH - 2, RECT_HEIGHT - 2))
    archer_image = pygame.image.load(ARCHER_IMAGE_PATH)
    archer_image = pygame.transform.scale(archer_image, (RECT_WIDTH - 2, RECT_HEIGHT - 2))
    shieldbearer_image = pygame.image.load(SHIELDBEARER_IMAGE_PATH)
    shieldbearer_image = pygame.transform.scale(shieldbearer_image, (RECT_WIDTH - 2, RECT_HEIGHT - 2))
    knight_image = pygame.image.load(KNIGHT_IMAGE_PATH)  # Load knight image
    knight_image = pygame.transform.scale(knight_image, (RECT_WIDTH - 2, RECT_HEIGHT - 2))
    vanguard_image = pygame.image.load(VANGUARD_IMAGE_PATH)
    vanguard_image = pygame.transform.scale(vanguard_image, (RECT_WIDTH - 2, RECT_HEIGHT - 2))
    guardian_image = pygame.image.load(GUARDIAN_IMAGE_PATH)
    guardian_image = pygame.transform.scale(guardian_image, (RECT_WIDTH - 2, RECT_HEIGHT - 2))

    return green_pawn_image, red_pawn_image, foot_soldier_image, apprentice_image, rogue_image, spearman_image, archer_image, shieldbearer_image, knight_image, vanguard_image, guardian_image
