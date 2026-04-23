import pygame
import characterSprite1

pygame.init()

SCREEN_WIDTH = 950
SCREEN_HEIGTH = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGTH))
pygame.display.set_caption("Pixel Path")
clock = pygame.time.Clock()

# Size
C_WIDTH = 32
C_HEIGTH = 32

# Gravity
GRAVITY = 0.6
JUMP_HEIGTH = -12

# Colors
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BROWN = (101, 67, 33)
BLACK = (0, 0, 0)

# animation
animation_list = []
animation_steps = [10, 10, 6]
action = 0
last_update = pygame.time.get_ticks()
anim_cooldown = 300 # millisecond
frame = 0
step_count = 0

# idle
character_image = pygame.image.load('image/male_hero.png').convert_alpha()

def get_image(sheet, width, heigth, scale, color):
    image = pygame.Surface((width, heigth)).convert_alpha()
    image.blit(sheet, (0, 0), (128, 128, width, heigth))
    image = pygame.transform.scale(image, (width * scale, heigth * scale))
    image.set_colorkey(color)

    return image
    

frame_1 = get_image(character_image, 128, 128, 3, BLACK)
frame_2 = get_image(character_image, 128, 128, 3, BLACK)
frame_3 = get_image(character_image, 128, 128, 3, BLACK)
frame_4 = get_image(character_image, 128, 128, 3, BLACK)

# for animation in animation_steps:
#     temp_image_list = []
#     for _ in range(animation):
#         temp_image_list.append(character_sheet.get_image(step_count, 128, 128, 1.5, WHITE))
#         step_count += 1
#     animation_list.append(temp_image_list)

run = True

while run:
    clock.tick(60)
    screen.fill(BROWN)

    screen.blit(frame_1, (0, 0))
    screen.blit(frame_2, (100, 0))
    screen.blit(frame_3, (200, 0))
    screen.blit(frame_4, (300, 0))
    # screen.blit(character_image, (100, 0))
    # update animation
    # current_time = pygame.time.get_ticks()
    # if current_time - last_update >= anim_cooldown:
    #     frame += 1
    #     last_update = current_time
    #     if frame >= len(animation_list):
    #         frame = 0

    # # show frame idle
    # screen.blit(animation_list[action][frame], (0, 0))
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # if event.type == pygame.KEYDOWN:
        #     if event.type == pygame.K_LEFT:


    pygame.display.update()
pygame.quit()