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
MAX_HEALTH = 100

tile_size = 50
game_over = 0
main_menu = True
level = 1
score = 0
current_lvl = 0
life = 3
game_paused = False

def draw_grid():
    for x in range(0, SCREEN_WIDTH, tile_size):
        pygame.draw.line(screen, (255, 255, 255, 80), (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, tile_size):
        pygame.draw.line(screen, (255, 255, 255, 80), (0, y), (SCREEN_WIDTH, y), 1)

def draw_cross():
    pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, SCREEN_WIDTH), (SCREEN_WIDTH // 2, 0), 3)
    pygame.draw.line(screen, WHITE, (0, SCREEN_HEIGHT // 2), (SCREEN_WIDTH, SCREEN_HEIGHT // 2), 3)

# ==================== SPRITE ShEET IMAGES ====================
character_sprite = pygame.image.load("assets/MainCharacter/male_hero.png").convert_alpha()
enemy_sprite = pygame.image.load("assets/Enemy/enemies-spritesheet.png").convert_alpha()

# button image
button_img = pygame.image.load("assets/Buttons/Blue_Buttons_Pixel.png").convert_alpha()

def get_button(sheet, x, y, w, h, scale=2):
    img = pygame.Surface((w, h), pygame.SRCALPHA)
    img.blit(sheet, (0, 0), (x, y, w, h))
    return pygame.transform.scale(img, (w * scale, h * scale))

start_btn = get_button(button_img,  -16, 48, 48, 16)
start_btn = pygame.transform.scale(start_btn, (400, 100))

settings_btn = get_button(button_img,  -16, 64, 64, 16)
settings_btn = pygame.transform.scale(settings_btn, (400, 100))

quit_btn = get_button(button_img, 80, 32, 32, 16)
quit_btn = pygame.transform.scale(quit_btn, (200, 100))

continue_btn_img = get_button(button_img, -16, 80, 64, 16)
continue_btn_img = pygame.transform.scale(continue_btn_img, (400, 100))

menu_btn_img = get_button(button_img, 32, 48, 32, 16)
menu_btn_img = pygame.transform.scale(menu_btn_img, (200, 100))

# ========== STAR ==========
# stars images
star_gray = pygame.image.load("assets/img/s2.png")
star_gray = pygame.transform.scale(star_gray, (30, 30))

star_yellow = pygame.image.load("assets/img/s1.png")
star_yellow = pygame.transform.scale(star_yellow, (30, 30))

# ========== HEART ==========
heart_sheet = pygame.image.load("assets/img/hearts.png").convert_alpha()

def heart(frame):
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    surf.blit(heart_sheet, (0, 0), (frame * 16, 0, 16, 16))
    return pygame.transform.scale(surf, (32, 32))

heart_full  = heart(0)
heart_empty = heart(1)

def draw_hearts(lives, max_lives=3):
    for i in range(max_lives):
        img = heart_full if i < lives else heart_empty
        screen.blit(img, (8 + i * (32 + 4), 8))

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

collected_stars = set()
activated_checkpoints = set()
killed_enemies = set()
def levels(lvl_index):
    global world, spike_group, platform_group, door_group, star_group, checkpoint_group, enemy_group, current_lvl
    current_lvl = lvl_index
    spike_group = pygame.sprite.Group()
    platform_group = pygame.sprite.Group()
    door_group = pygame.sprite.Group()
    star_group = pygame.sprite.Group()
    checkpoint_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    world = World(MAP[lvl_index])

    # restore collected stars
    for star in star_group.sprites():
        if star.grid_pos in collected_stars:
            star.kill()

    # restore activated checkpoints
    for check in checkpoint_group:
        if check.grid_pos in activated_checkpoints:
            check.activated = True

    # restore killed enemies
    for enemy in enemy_group.sprites():
        if enemy.grid_pos in killed_enemies:
            enemy.kill()

ANIMATIONS = {
    "idle": (10, 128),
    "run": (10, 768),
    "jump": (6, 1280),
    "fall": (4, 1408),
    "damage" : (6, 2944),
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
        [2,0,0,0,0,0,0,6,0,0,9,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,8,0,0,0,2,2,2,2,0,0,0,0],
        [0,0,2,0,0,0,2,2,0,0,0,0,0,0,0,0,0,2],
        [0,2,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,6,0,0,0,0,0,2,2,0,0,0,2,0],
        [0,0,0,0,0,0,0,0,2,0,2,1,0,0,0,2,1,0],
        [0,0,2,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0],
        [2,2,1,2,2,1,2,0,0,0,0,0,0,0,0,0,0,0]
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
        [2,2,2,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,6],
        [2,2,2,2,0,0,4,0,0,2,0,0,0,0,0,2,2,2]
    ],
    [
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [3,6,0,0,0,0,3,0,0,0,0,0,0,3,0,0,0,6],
        [2,2,0,0,2,2,2,2,0,0,0,0,0,2,2,0,0,2],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,5,3,0,0,0,0,0,0,0,0,5,0,0,0,5,0],
        [0,0,0,2,2,0,0,0,0,0,2,2,0,0,0,0,0,0],
        [3,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,2,2],
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
                if tile == 8:
                    check = Checkpoint(x * tile_size, y * tile_size - 15)
                    checkpoint_group.add(check)
                if tile == 9:
                    enemy = Enemy(x * tile_size, y * tile_size + 10, enemy_sprite)
                    enemy_group.add(enemy)

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
            # screen.blit(tile[0], tile[1])
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
        self.grid_pos = (x, y)

# ==================== CHECKPOINT ====================
class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("assets/Terrain/flag.gif")
        self.image = pygame.transform.scale(img, (tile_size, tile_size * 1.3))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.grid_pos = (x, y)
        self.activated = False
        
# ==================== ENEMY ====================
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_sheet):
        pygame.sprite.Sprite.__init__(self)
        self.sprite_sheet = sprite_sheet
        self.grid_pos = (x, y)
        self.anim_frames = [
            get_image(sprite_sheet, i, 20, 20, 2, 200)
            for i in range(4)
        ]
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.anim_cooldown = 120

        self.image = self.anim_frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.outline = self.rect.inflate(-20, -10)

        self.speed = 1
        self.direction = 1
        self.move_distance = 150
        self.start_x = x
        self.move_count = 0

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.anim_cooldown:
            self.frame = (self.frame + 1) % len(self.anim_frames)
            self.last_update = current_time

        self.rect.x += self.speed * self.direction
        self.outline.center = self.rect.center
        self.move_count += self.speed

        if abs(self.move_count) >= self.move_distance:
            self.direction *= -1
            self.move_count = 0

        img = self.anim_frames[self.frame]
        if self.direction == -1:
            img = pygame.transform.flip(img, True, False)
            img.set_colorkey(BLACK)
        self.image = img

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
        if self.won:
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

            # player  hitbox
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
                self.health = 0
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
                    self.health = 0
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
                    if len(star_group) == 0:
                        self.velX = 0
                        self.velY = 0
                        self.action("idle")
                        self.won = True

                        return 1
                    else:
                        self.at_locked_door = True
            
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
                    collected_stars.add(star.grid_pos)
                    star.kill()
                    score += 1
                    # print(score)

            for check in checkpoint_group:
                if self.outline.colliderect(check.rect):
                    if not check.activated:
                        check.activated = True
                        activated_checkpoints.add(check.grid_pos)
                        self.checkpoint_pos = (check.rect.centerx - self.rect.width // 2, check.rect.bottom - self.rect.height)
                    
            for enemy in enemy_group:
                if self.outline.colliderect(enemy.outline):
                    current_time = pygame.time.get_ticks()
                    if current_time - self.last_hit > self.hit_cooldown:
                        self.last_hit = current_time
                        self.health -= 30
                        if self.health <= 0:
                            self.health = 0
                            self.dead = True
                            self.velX = 0
                            self.velY = 0
                            self.frame = 0
                            game_over_sound.play()
                            self.action("death")
                            return -1
                        else:
                            game_over_sound.play()
                            self.taking_damage = True
                            self.action("damage")
            
            # ===== ANIMATION =====
            if self.taking_damage:
                if self.frame >= len(self.anim_lists["damage"]) - 1:
                    self.taking_damage = False
                    self.frame = 0
                else:
                    image = self.anim_lists[self.current_action][self.frame]
                    if self.direction == "left":
                        image = pygame.transform.flip(image, True, False)
                        image.set_colorkey(BLACK)
                    self.image = image

                    return
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
        self.health = MAX_HEALTH
        self.x = x
        self.y = y
        self.dead = False
        self.won = False
        self.checkpoint_pos = None

        self.velX = 0
        self.velY = 0
        self.speed = 5
        self.taking_damage = False
        self.last_hit = 0
        self.hit_cooldown = 1500

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

# score_star = Star(tile_size // 2, tile_size // 2)

# ==================== LOCATION ====================
player = Player(-50, SCREEN_HEIGHT - 100, character_sprite)
levels(0)

start_btn = Button(SCREEN_WIDTH // 2 - 275, (SCREEN_HEIGHT // 2 - 100), start_btn)
settings_btn = Button(SCREEN_WIDTH // 2 - 255, SCREEN_HEIGHT // 2 + 25, settings_btn)
quit_btn = Button(SCREEN_WIDTH // 2 - 105, SCREEN_HEIGHT // 2 + 150, quit_btn)
continue_btn = Button(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 80, continue_btn_img)
menu_btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 150,  menu_btn_img)

clock = pygame.time.Clock()
death_time = None
menu_return_time = None

# ==================== SETTINGS ====================
show_settings = False
music_volume = 0.5
sfx_volume = 0.5

def draw_volume_row(label, x, y, value, width=300):
    font_small = pygame.font.SysFont("Bauhaus 93", 24)
    btn_size = 32

    # label
    lbl = font_small.render(label, True, WHITE)
    screen.blit(lbl, (x, y - 28))

    # minus button
    minus_rect = pygame.Rect(x, y - 8, btn_size, btn_size)
    minus_hover = minus_rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, (180, 60, 60) if minus_hover else (120, 40, 40), minus_rect, border_radius=6)
    m_lbl = font_small.render("-", True, WHITE)
    screen.blit(m_lbl, (minus_rect.x + 10, minus_rect.y + 4))

    # bar track
    bar_x = x + btn_size + 10
    bar_w = width - btn_size * 2 - 20
    track_rect = pygame.Rect(bar_x, y, bar_w, 10)
    pygame.draw.rect(screen, GRAY, track_rect, border_radius=5)

    # bar fill
    fill_w = int(bar_w * value)
    if fill_w > 0:
        pygame.draw.rect(screen, (80, 160, 255), pygame.Rect(bar_x, y, fill_w, 10), border_radius=5)

    # plus button
    plus_rect = pygame.Rect(bar_x + bar_w + 10, y - 8, btn_size, btn_size)
    plus_hover = plus_rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, (60, 160, 80) if plus_hover else (40, 110, 55), plus_rect, border_radius=6)
    p_lbl = font_small.render("+", True, WHITE)
    screen.blit(p_lbl, (plus_rect.x + 8, plus_rect.y + 4))

    # percent
    pct = font_small.render(f"{int(value * 100)}%", True, WHITE)
    screen.blit(pct, (plus_rect.right + 10, y - 6))

    return minus_rect, plus_rect

def draw_settings_panel():
    global music_volume, sfx_volume

    # dim overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # panel box
    panel = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 160, 440, 320)
    pygame.draw.rect(screen, (30, 30, 50), panel, border_radius=16)
    pygame.draw.rect(screen, (80, 160, 255), panel, 3, border_radius=16)

    # title
    font_med = pygame.font.SysFont("Bauhaus 93", 42)
    title = font_med.render("SETTINGS", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, panel.y + 20))

    # rows
    sx = panel.x + 40
    music_minus, music_plus = draw_volume_row("Music Volume", sx, panel.y + 115, music_volume, width=340)
    sfx_minus,   sfx_plus   = draw_volume_row("SFX Volume",   sx, panel.y + 210, sfx_volume,   width=340)

    # apply volumes live
    pygame.mixer.music.set_volume(music_volume)
    star_sound.set_volume(sfx_volume)
    jump_sound.set_volume(sfx_volume)
    game_over_sound.set_volume(sfx_volume)

    # close button
    font_small = pygame.font.SysFont("Bauhaus 93", 26)
    close_rect = pygame.Rect(panel.right - 48, panel.y + 10, 34, 34)
    pygame.draw.rect(screen, RED, close_rect, border_radius=6)
    x_lbl = font_small.render("X", True, WHITE)
    screen.blit(x_lbl, (close_rect.x + 8, close_rect.y + 4))

    return close_rect, music_minus, music_plus, sfx_minus, sfx_plus

# ==================== MAIN ====================
run = True
while run:
    clock.tick(FPS)

    if main_menu:
        screen.blit(bg[0], (0, 0))
        if not show_settings:
            if start_btn.draw():
                main_menu = False
            if settings_btn.draw():
                show_settings = True
            if quit_btn.draw():
                run = False

        if show_settings:
            close_rect, music_minus, music_plus, sfx_minus, sfx_plus = draw_settings_panel()
    else:
        bg_index = min(level, len(bg) - 1)
        screen.blit(bg[bg_index], (0, 0))
        draw_grid()
        draw_cross()

        for i in range(3):
            img = star_yellow if i < score else star_gray
            screen.blit(img, (10 + i * 35, 42))

        draw_hearts(life)

        if not game_paused:
            GAME_OVER = player.update(world, game_over)
            platform_group.update()
            enemy_group.update()

        world.draw()
        spike_group.draw(screen)
        platform_group.draw(screen)
        door_group.draw(screen)
        star_group.draw(screen)
        checkpoint_group.draw(screen)
        enemy_group.draw(screen)
        player.draw(screen)

        if show_settings:
            close_rect, music_minus, music_plus, sfx_minus, sfx_plus = draw_settings_panel()

        # ===== PLAYER DIED =====
        if GAME_OVER == -1:
            now = pygame.time.get_ticks()

            if death_time is None:
                death_time = now

            elapsed = now - death_time

            if life - 1 <= 0:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))

                text("GAME OVER!", font, RED, SCREEN_WIDTH // 2 - 190, SCREEN_HEIGHT // 2 - 200)

                if continue_btn.draw():
                    life -= 1
                    collected_stars.clear()
                    activated_checkpoints.clear()
                    level = 1
                    levels(0)
                    score = 0
                    life = 3
                    death_time = None
                    player.reset(-50, SCREEN_HEIGHT - 100, character_sprite)
                    GAME_OVER = 0

                if menu_btn.draw():
                    if menu_return_time is None:
                        menu_return_time = pygame.time.get_ticks()
                elif menu_return_time is not None:
                    if pygame.time.get_ticks() - menu_return_time >= 300:
                        life = 3
                        level = 1
                        score = 0
                        collected_stars.clear()
                        activated_checkpoints.clear()
                        levels(0)
                        player.reset(-50, SCREEN_HEIGHT - 100, character_sprite)
                        GAME_OVER = 0
                        main_menu = True
                        death_time = None
                        menu_return_time = None

            else:
                text("You Died", font, RED, (SCREEN_WIDTH // 2 - 140), SCREEN_HEIGHT // 2 - 45)

                if elapsed >= 2000:
                    life -= 1
                    spawn = player.checkpoint_pos if player.checkpoint_pos else (-50, SCREEN_HEIGHT - 100)
                    levels(current_lvl)
                    player.reset(spawn[0], spawn[1], character_sprite)
                    player.checkpoint_pos = spawn
                    death_time = None
                    GAME_OVER = 0

        else:
            death_time = None

        # win ++ level
        if GAME_OVER == 1:
            level += 1
            if level <= len(MAP):
                collected_stars.clear()
                levels(level - 1)
                score = 0
                player.reset(-50, SCREEN_HEIGHT - 100, character_sprite)
                GAME_OVER = 0
            else:
                text("YOU WIN!", font, BLUE, (SCREEN_WIDTH // 2) - 140, SCREEN_HEIGHT // 2)
                if start_btn.draw():
                    level = 1
                    levels(0)
                    score = 0
                    player.reset(-50, SCREEN_HEIGHT - 100, character_sprite)

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if not main_menu:
                    if show_settings:
                        show_settings = False
                        continue_btn.draw()
                    else:
                        game_paused = not game_paused
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if show_settings:
                if close_rect.collidepoint(event.pos):
                    show_settings = False
                    game_paused = False
                if music_minus.collidepoint(event.pos):
                    music_volume = max(0.0, round(music_volume - 0.1, 1))
                if music_plus.collidepoint(event.pos):
                    music_volume = min(1.0, round(music_volume + 0.1, 1))
                if sfx_minus.collidepoint(event.pos):
                    sfx_volume = max(0.0, round(sfx_volume - 0.1, 1))
                if sfx_plus.collidepoint(event.pos):
                    sfx_volume = min(1.0, round(sfx_volume + 0.1, 1))
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()