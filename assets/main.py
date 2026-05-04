import pygame
from pygame import mixer

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pathfinder")

# dont
font = pygame.font.SysFont("Bauhaus 93", 70)
font_score = pygame.font.SysFont("Bauhaus 93", 30)

# Colors
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BROWN = (101, 67, 33)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Custom color
CUSTOM_1 = ("#663300")
CUSTOM_2 = ("#C6C6C6")
CUSTOM_3 = ("#00550A")

FPS = 60

GRAVITY = 0.5
JUMP = -10.5
GROUND = SCREEN_HEIGHT + 10

tile_size = 50
game_over = 0
main_menu = True
level = 1
score = 0
current_lvl = 0

# ==================== IMAGES ====================
character_sprite = pygame.image.load("assets/MainCharacter/male_hero.png").convert_alpha()

# button image
restart_img = pygame.image.load("assets/img/restart_btn.png")
restart_img = pygame.transform.scale(restart_img, (300, 100))
start_img = pygame.image.load("assets/img/start_btn.png")
exit_img = pygame.image.load("assets/img/exit_btn.png")

star_icon = pygame.image.load("assets/img/s1.png")
star_icon = pygame.transform.scale(star_icon, (30, 30))

# background images
menu_bg = pygame.image.load("assets/Background/background4.jpg")
menu_bg = pygame.transform.scale(menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

lvl_1 = pygame.image.load("assets/Background/background1.jpg")
lvl_1 = pygame.transform.scale(lvl_1, (SCREEN_WIDTH, SCREEN_HEIGHT))
lvl_2 = pygame.image.load("assets/Background/background2.jpg")
lvl_2 = pygame.transform.scale(lvl_2, (SCREEN_WIDTH, SCREEN_HEIGHT))
lvl_3 = pygame.image.load("assets/Background/background3.jpg")
lvl_3 = pygame.transform.scale(lvl_3, (SCREEN_WIDTH, SCREEN_HEIGHT))

bg = [menu_bg, lvl_1, lvl_2, lvl_3]

# ==================== SOUND ====================
pygame.mixer.music.load("assets/img/music.wav")
pygame.mixer.music.play(-1, 0.0, 5000)
star_sound = pygame.mixer.Sound("assets/audio/notice.wav")
star_sound.set_volume(0.5)
jump_sound = pygame.mixer.Sound("assets/audio/jump.wav")
jump_sound.set_volume(0.5)
game_over_sound = pygame.mixer.Sound("assets/img/game_over.wav")
game_over_sound.set_volume(0.5)

# ==================== TEXT ====================
def text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

# ==================== ANIMATIONS ====================
def get_image(sheet, frame, width, height, scale, offsetY):
    image = pygame.Surface((width, height)).convert_alpha()
    image.blit(sheet, (0, 0), ((frame * width), offsetY, width, height))
    image = pygame.transform.scale(image, (width * scale, height * scale))
    image.set_colorkey(BLACK)
    return image

ANIMATIONS = {
    "idle": (10, 128),
    "run": (10, 768),
    "jump": (6, 1280),
    "fall": (4, 1408),
    "death": (23, 3072)
}

# ==================== MAP ====================
MAP = [
    [
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,7],
        [0,0,0,0,2,0,0,0,0,2,6,0,0,1,0,0,2,2],
        [2,0,0,0,1,0,0,2,0,1,2,2,0,1,2,0,0,0],
        [0,0,0,0,1,0,2,1,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [2,0,0,0,0,0,0,6,0,0,0,0,2,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,2,2,1,2,0,0,0,0],
        [0,0,2,0,0,0,2,2,0,0,0,0,0,0,0,0,0,2],
        [0,2,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,6,0,0,0,0,0,2,2,0,0,0,2,0],
        [0,0,0,0,0,0,0,0,2,0,2,1,0,0,0,2,1,0],
        [0,0,0,2,0,2,0,0,0,0,0,0,0,0,0,0,0,0],
        [2,2,2,1,2,1,2,0,0,0,0,0,0,0,0,0,0,0]
    ],
    [
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,2,2,2,0,0,0,0,0,0,0,0,0,0,6],
        [6,3,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,2],
        [2,2,2,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,1,2,2,0,0,0,4,0,0,2,0],
        [0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,2,2,1,0,0,0,0,0,0,5,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7],
        [0,5,0,0,0,0,0,0,2,2,0,0,0,0,2,2,2,2],
        [0,0,0,2,2,2,0,0,0,1,2,0,0,2,1,1,1,1],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,3,6],
        [2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,2,2,2]
    ],
    [
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [6,3,0,0,0,0,3,0,0,0,0,0,0,3,0,0,0,6],
        [2,2,0,0,2,2,2,2,0,0,0,0,0,2,2,0,0,2],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,5,3,0,0,0,0,0,0,0,0,5,0,0,0,5,0],
        [0,0,0,2,2,0,0,0,0,0,2,2,0,0,0,0,0,0],
        [3,0,0,0,0,0,0,4,0,0,0,0,0,0,2,2,2,2],
        [2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,3,5,0,0,0,0,0,3,0,0,0,0,0,7],
        [0,0,0,2,2,0,0,0,4,0,0,2,2,0,0,2,2,2],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,5,0,0,0,5,0,0,0,0,0,0,0,0,0,6,3],
        [0,0,0,0,0,0,0,0,4,0,0,0,3,0,0,0,2,2],
        [2,2,0,0,0,0,0,0,0,0,0,2,2,2,0,0,0,0]
    ]
]

# ==================== BUTTON ====================
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        # mouse pos
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
                # print("brrrrt brrrt")

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)

        return action

# ==================== WORLD ====================
class World(pygame.sprite.Sprite):
    def __init__(self, tiles):
        self.tile_list = []

        dirt = pygame.image.load("assets/img/dirt.png")
        grass = pygame.image.load("assets/img/grass.png")

        y = 0
        for row in tiles:
            x = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = x * tile_size
                    img_rect.y = y * tile_size
                    tile = (img, img_rect, 1)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = x * tile_size
                    img_rect.y = y * tile_size
                    tile = (img, img_rect, 2)
                    self.tile_list.append(tile)
                if tile == 3:
                    spike = Spike(x *tile_size, y * tile_size + (tile_size // 2))
                    spike_group.add(spike)
                if tile == 4:
                    platform = Platform(x *tile_size, y * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(x *tile_size, y * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 6:
                    star = Star(x *tile_size + (tile_size // 2), y * tile_size + (tile_size // 2))
                    star_group.add(star)
                if tile == 7:
                    door = Door(x *tile_size, y * tile_size - (tile_size // 2) + 10)
                    door_group.add(door)

                x += 1
            y += 1
    
    def collision(self, rect):
        hit_list = []
        for tile in self.tile_list:
            if rect.colliderect(tile[1]):
                hit_list.append(tile)
        return hit_list

    def move(self, rect, movement):
        collision_types = {"top": False, "bottom": False, "left": False, "right": False}

        # x || left n right col
        rect.x += movement[0]
        hit_list = self.collision(rect)
        for tile in hit_list:
            if movement[0] > 0:
                rect.right = tile[1].left
                collision_types["right"] = True
            elif movement[0] < 0:
                rect.left = tile[1].right
                collision_types["left"] = True

        # y || top n bottom col
        rect.y += movement[1]
        hit_list = self.collision(rect)
        for tile in hit_list:
            if movement[1] > 0:
                rect.bottom = tile[1].top
                collision_types["bottom"] = True
            elif movement[1] < 0:
                rect.top = tile[1].bottom
                collision_types["top"] = True

        return rect, collision_types

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            screen.blit(tile[0], tile[1])
            # block rid
            # pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

# ==================== SPIKE ====================
class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("assets/Trap/Idle.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect(topleft=(x, y))

# ==================== SPIKE ====================
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("assets/img/platform.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.move_count = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y
    
    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_count += 1
        if abs(self.move_count) > 50:
            self.move_direction *= -1
            self.move_count *= -1

# ==================== DOOR ====================
class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("assets/img/exit.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size * 1.3))
        self.rect = self.image.get_rect(topleft=(x, y))

# ==================== STAR ====================
class Star(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("assets/img/s1.png")
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# ==================== PLAYER ====================
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite):
        self.reset(x, y, sprite)

    def update_anim(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.anim_cooldown:
            self.frame += 1
            self.last_update = current_time
            if self.current_action == "death":
                if self.frame < len(self.anim_lists["death"]) - 1:
                    self.frame += 1
                return

            if self.frame >= len(self.anim_lists[self.current_action]):
                self.frame = 0

    def action(self, action, direction=None):
        if action != self.current_action:
            self.current_action = action
            self.frame = 0
        if direction:
            self.direction = direction

    def jump(self):
        if self.on_ground:
            jump_sound.play()
            self.velY = JUMP
            self.on_ground = False
            self.action("jump")

    def update(self, world, game_over):
        if self.dead:
            self.action("death")
            self.update_anim()

            if self.frame >= len(self.anim_lists["death"]) - 1:
                self.frame = len(self.anim_lists["death"]) - 1

            self.image = self.anim_lists["death"][self.frame]
            return -1
        if self.won:          # ← add this block
            self.update_anim()
            return 1

        self.update_anim()

        if game_over == 0:
            keys = pygame.key.get_pressed()
            self.velX = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.velX = -self.speed
                self.direction = "left"
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.velX = self.speed
                self.direction = "right"
            if keys[pygame.K_SPACE]:
                self.jump()

            self.velY += GRAVITY

            # player  hitnox
            self.outline.center = self.rect.center
            movement = [self.velX, self.velY]
            self.outline, collisions = world.move(self.outline, movement)

            # border
            if self.outline.left < 0: # left
                self.outline.left = 0
            if self.outline.right > SCREEN_WIDTH: # right
                self.outline.right = SCREEN_WIDTH
            if self.outline.top < 0: # top
                self.outline.top = 0
            if self.outline.bottom > GROUND: # void
                self.dead = True
                self.velX = 0
                self.velY = 0
                self.frame = 0
                game_over_sound.play()
                self.action("death")
                return -1
            
            # collisio
            if collisions["bottom"]:
                self.velY = 0
                self.on_ground = True
            else:
                self.on_ground = False

            # player under block || top border
            if collisions["top"]:
                self.velY = 0

            # ===== COL =====
            for spike in spike_group:
                if self.outline.colliderect(spike.rect):
                    self.dead = True
                    self.velX = 0
                    self.velY = 0
                    self.frame = 0
                    game_over_sound.play()
                    self.action("death")
                    # print(game_over)
                    return -1
            
            for door in door_group:
                if self.outline.colliderect(door):
                    self.velX = 0
                    self.velY = 0
                    self.action("idle")
                    self.won = True

                    return 1
            
            for platform in platform_group:
                if self.outline.colliderect(platform):
                    if self.velY > 0 and self.outline.bottom <= platform.rect.bottom:
                        self.outline.bottom = platform.rect.top
                        self.velY = 0
                        self.on_ground = True
                        # top
                        self.outline.x += platform.move_direction * platform.move_x
                        self.outline.y += platform.move_direction * platform.move_y
                    # below
                    elif self.velY < 0 and self.outline.top >= platform.rect.top:
                        self.outline.top = platform.rect.bottom
                        self.velY = 0
                    # sides && sync moverect with platform
                    elif self.velX > 0:
                        self.outline.right = platform.rect.left
                    elif self.velX < 0:
                        self.outline.left = platform.rect.right
            
            # sync  player sprite + grid
            self.rect.center = self.outline.center
            self.x, self.y = self.rect.topleft
            
            global score
            for star in star_group.sprites():
                if self.outline.colliderect(star.rect):
                    star_sound.play()
                    star.kill()
                    score += 1
                    # print(score)
            
            # ===== ANIMATION =====
            if not self.on_ground:
                if self.velY < 0:
                    self.action("jump")
                else:
                    self.action("fall")
            else:
                if self.velX != 0:
                    self.action("run", self.direction)
                else:
                    self.action("idle")
                
            # print(self.current_action)
            image = self.anim_lists[self.current_action][self.frame]

            if self.direction == "left":
                image = pygame.transform.flip(image, True, False)
                image.set_colorkey(BLACK)

            self.image = image

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))
        # grid
        # pygame.draw.rect(surface, WHITE, self.outline, 2)

    def reset(self, x, y, sprite):
        self.sprite_sheet = sprite
        self.x = x
        self.y = y
        self.dead = False
        self.won = False

        self.velX = 0
        self.velY = 0
        self.speed = 5

        self.on_ground = False

        self.current_action = "idle"
        self.direction = "right"
        self.frame = 0

        self.last_update = pygame.time.get_ticks()
        self.anim_cooldown = 100 # millisecond

        self.anim_lists = {}
        for action, (frames, offset) in ANIMATIONS.items():
            self.anim_lists[action] = [
                get_image(sprite, i, 128, 128, 1.5, offset)
                for i in range(frames)
            ]

        self.image = self.anim_lists["idle"][0]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        # box
        self.outline = self.rect.inflate(-168, -144)

def levels(lvl_index):
    global world, spike_group, platform_group, door_group, star_group, current_lvl
    current_lvl = lvl_index
    spike_group = pygame.sprite.Group()
    platform_group = pygame.sprite.Group()
    door_group = pygame.sprite.Group()
    star_group = pygame.sprite.Group()
    world = World(MAP[lvl_index])

# score_star = Star(tile_size // 2, tile_size // 2)

# ==================== LOCATION ====================
player = Player(-50, SCREEN_HEIGHT - 100, character_sprite)
levels(0)
# world = World(MAP)

# button
restart_button = Button(SCREEN_WIDTH // 2 - 150, (SCREEN_HEIGHT // 2) + 100, restart_img)
start_button = Button(SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT // 2, start_img)
exit_button = Button(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2, exit_img)

clock = pygame.time.Clock()

# ==================== MAIN ====================
run = True
while run:
    clock.tick(FPS)

    # screen.fill(BROWN)
    if main_menu == True:
        screen.blit(bg[0], (0, 0))
        if start_button.draw():
            main_menu = False
        if exit_button.draw():
            run = False
    else:
        bg_index = min(current_lvl + 1, len(bg) - 1)
        screen.blit(bg[bg_index], (0, 0))

        # score
        screen.blit(star_icon, (10, 10))
        text("X " + str(score), font_score, WHITE, tile_size - 10, 10)

        GAME_OVER = player.update(world, game_over)
        # print(GAME_OVER)
        platform_group.update()

        world.draw()
        spike_group.draw(screen)
        platform_group.draw(screen)
        door_group.draw(screen)
        star_group.draw(screen)
        player.draw(screen)

        # if player died
        if GAME_OVER == -1:
            text("GAME OVER!", font, BLUE, (SCREEN_WIDTH // 2) - 200, SCREEN_HEIGHT // 2)
            if restart_button.draw():
                levels(current_lvl)
                score = 0
                player.reset(-50, SCREEN_HEIGHT - 100, character_sprite)
                GAME_OVER = 0

        # win ++ level
        if GAME_OVER == 1:
            level += 1
            if level <= len(MAP):
                levels(level - 1)
                score = 0
                player.reset(-50, SCREEN_HEIGHT - 100, character_sprite)
                GAME_OVER = 0
            else:
                text("YOU WIN!", font, BLUE, ((SCREEN_WIDTH // 2) - 140), SCREEN_HEIGHT // 2)
                if restart_button.draw():
                    level = 1
                    levels(0)
                    score = 0
                    player.reset(-50, SCREEN_HEIGHT - 100, character_sprite)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()