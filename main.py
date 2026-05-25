import pygame, math, asyncio
from pygame import mixer

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pathfinder")

# font
font = pygame.font.Font("assets/Font/Tiny5-Regular.ttf", 70)
font_small = pygame.font.Font("assets/Font/Tiny5-Regular.ttf", 24)
font_medium = pygame.font.Font("assets/Font/Tiny5-Regular.ttf", 42)
font_large = pygame.font.Font("assets/Font/Tiny5-Regular.ttf", 110)

# Colors
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BROWN = (101, 67, 33)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

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
show_credits = False
wave_time = 0

def draw_grid():
    for x in range(0, SCREEN_WIDTH, tile_size):
        pygame.draw.line(screen, (255, 255, 255, 80), (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, tile_size):
        pygame.draw.line(screen, (255, 255, 255, 80), (0, y), (SCREEN_WIDTH, y), 1)

def draw_cross():
    pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, SCREEN_WIDTH), (SCREEN_WIDTH // 2, 0), 3)
    pygame.draw.line(screen, WHITE, (0, SCREEN_HEIGHT // 2), (SCREEN_WIDTH, SCREEN_HEIGHT // 2), 3)

# ==================== SPRITE SHEET IMAGES ====================
character_sprite = pygame.image.load("assets/MainCharacter/male_hero.png").convert_alpha()
enemy_sprite = pygame.image.load("assets/Enemy/enemies-spritesheet.png").convert_alpha()

# ===== MENU BUTTON
button_img = pygame.image.load("assets/Buttons/Blue_Buttons_Pixel.png").convert_alpha()

def get_button(sheet, x, y, w, h, scale=2):
    img = pygame.Surface((w, h), pygame.SRCALPHA)
    img.blit(sheet, (0, 0), (x, y, w, h))
    return pygame.transform.scale(img, (w * scale, h * scale))

# ========== STAR ==========
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

def draw_health_bar(x, y, health, max_health=100):
    bar_width = 40
    bar_height = 6
    fill = int(bar_width * (health / max_health))
    pygame.draw.rect(screen, (60, 0, 0), (x, y, bar_width, bar_height), border_radius=3)
    if fill > 0:
        color = (0, 200, 0) if health > 60 else (255, 165, 0) if health > 30 else (220, 0, 0)
        pygame.draw.rect(screen, color, (x, y, fill, bar_height), border_radius=3)
    pygame.draw.rect(screen, WHITE, (x, y, bar_width, bar_height), 1, border_radius=3)

# background images
menu_bg = pygame.image.load("assets/Background/menu.jpg")
menu_bg = pygame.transform.scale(menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

lvl_1 = pygame.image.load("assets/Background/background1.jpg")
lvl_1 = pygame.transform.scale(lvl_1, (SCREEN_WIDTH, SCREEN_HEIGHT))
lvl_2 = pygame.image.load("assets/Background/background2.jpg")
lvl_2 = pygame.transform.scale(lvl_2, (SCREEN_WIDTH, SCREEN_HEIGHT))
lvl_3 = pygame.image.load("assets/Background/background3.jpg")
lvl_3 = pygame.transform.scale(lvl_3, (SCREEN_WIDTH, SCREEN_HEIGHT))

bg = [menu_bg, lvl_1, lvl_2, lvl_3]

# ==================== SOUND ====================
pygame.mixer.music.load("assets/music/overworld.ogg")
pygame.mixer.music.play(-1, 0.0, 5000)
star_sound = pygame.mixer.Sound("assets/audio/notice.ogg")
star_sound.set_volume(0.5)
jump_sound = pygame.mixer.Sound("assets/audio/jump.ogg")
jump_sound.set_volume(0.5)
game_over_sound = pygame.mixer.Sound("assets/img/game_over.ogg")
game_over_sound.set_volume(0.5)

button_sound = pygame.mixer.Sound("assets/audio/emilianodleon-select-button-ui-395763.ogg")

# ==================== TITLE ====================
def draw_title(text_str, x, y, t):
    arc_depth = 30
    spacing = 3
    total_width = sum(font_large.size(c)[0] + spacing for c in text_str)
    cx = x - total_width // 2

    for i, char in enumerate(text_str):
        t_pos = (i / max(len(text_str) - 1, 1)) * 2 - 1
        offset_y = int(arc_depth * (1 - t_pos ** 2) * -1 + arc_depth)

        char_surf = font_large.render(char, True, YELLOW)
        outline = font_large.render(char, True, (120, 80, 0))
        screen.blit(outline, (cx + 2, y + offset_y + 2))
        screen.blit(char_surf, (cx, y + offset_y))
        cx += font_large.size(char)[0] + spacing

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

    for star in star_group.sprites():
        if star.grid_pos in collected_stars:
            star.kill()

    for check in checkpoint_group:
        if check.grid_pos in activated_checkpoints:
            check.activated = True

    for enemy in enemy_group.sprites():
        if enemy.grid_pos in killed_enemies:
            enemy.kill()

ANIMATIONS = {
    "idle": (10, 128),
    "run": (10, 768),
    "jump": (6, 1280),
    "fall": (4, 1408),
    "damage": (6, 2944),
    "death": (23, 3072)
}

# ==================== MAP ====================
MAP = [
    [
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,8,0,0,6,0,0,0,0,0,0,7],
        [0,0,2,2,0,0,0,2,9,0,0,0,0,0,3,0,0,2],
        [0,0,0,1,2,0,0,1,2,2,2,2,0,2,2,2,0,0],
        [2,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,6],
        [0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,2,1,0,0,0,0,0,0,0,0,0,0,2,0,0,0],
        [0,0,0,0,0,0,0,0,0,2,0,0,2,2,1,2,0,0],
        [2,0,0,8,2,0,2,0,0,1,0,0,0,0,0,0,0,0],
        [1,2,0,2,1,0,0,0,0,0,0,0,0,0,0,0,0,2],
        [0,0,0,0,6,0,0,0,0,0,8,0,9,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,2,2,0,2,2,2,2,0,0],
        [0,0,0,3,2,0,0,2,0,0,1,0,0,0,0,0,0,0],
        [2,2,2,2,1,2,0,0,0,0,0,0,0,0,0,0,0,0]
    ],
    [
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,8,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,2,1,0,9,0,0,0,0,0,0,0,2,0,8,6,3],
        [2,0,0,0,0,2,2,2,2,0,4,0,0,1,2,2,2,2],
        [3,0,0,0,0,0,1,6,0,0,0,0,3,0,0,0,0,0],
        [2,2,0,2,0,0,1,9,0,0,0,0,2,0,0,0,0,0],
        [0,0,0,0,0,5,1,2,2,2,2,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7],
        [0,0,2,3,2,0,0,0,0,0,0,0,0,0,0,2,2,2],
        [0,0,1,1,1,0,0,0,0,0,0,0,0,0,2,1,1,1],
        [5,0,0,0,0,0,0,0,0,0,0,0,8,0,0,0,0,0],
        [0,0,0,0,0,0,2,0,0,4,0,0,2,0,0,0,0,0],
        [0,0,0,0,0,2,1,3,3,3,3,3,1,5,0,9,3,6],
        [2,2,2,0,0,0,1,1,1,1,1,1,1,0,0,2,2,2]
    ],
    [
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [3,6,0,0,0,0,0,0,0,0,0,0,0,0,0,8,6,0],
        [2,2,0,9,0,0,0,0,2,3,0,0,0,0,3,2,2,0],
        [0,0,0,2,2,2,2,0,1,2,0,0,0,2,2,1,0,0],
        [0,0,5,0,0,1,0,0,0,0,0,9,0,0,0,0,0,3],
        [8,0,0,0,0,1,0,0,0,0,0,2,2,2,2,0,0,2],
        [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,3,0,0,0,2,2,0,0,0,0,0,0,0,0,7],
        [0,0,2,2,2,2,0,0,1,3,0,0,0,0,0,0,2,2],
        [0,0,0,0,0,0,0,0,1,2,2,0,0,4,0,0,0,0],
        [0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,6],
        [0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,5,0,0],
        [0,0,0,0,2,3,3,3,2,0,0,0,3,8,0,0,9,3],
        [2,2,2,0,1,1,1,1,1,0,0,2,2,2,0,0,2,2]
    ]
]

# ==================== TRANSITION ====================
class Transition:
    def __init__(self):
        self.active = False
        self.fading_out = False
        self.alpha = 0
        self.speed = 6
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surface.fill(BLACK)
        self.callback = None

    def start(self, callback):
        if self.active:
            return
        self.active = True
        self.fading_out = True
        self.alpha = 0
        self.callback = callback

    def update(self):
        if not self.active:
            return
        if self.fading_out:
            self.alpha = min(255, self.alpha + self.speed)
            if self.alpha >= 255:
                if self.callback:
                    self.callback()
                    self.callback = None
                self.fading_out = False
        else:
            self.alpha = max(0, self.alpha - self.speed)
            if self.alpha <= 0:
                self.active = False

    def draw(self):
        if not self.active:
            return
        self.surface.set_alpha(self.alpha)
        screen.blit(self.surface, (0, 0))

transition = Transition()

# ==================== BUTTON ====================
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
        self.click_time = 0
        self.cooldown = 300

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        current = pygame.time.get_ticks()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.click_time = current
                button_sound.play()

        if self.clicked and current - self.click_time >= self.cooldown:
            action = True
            self.clicked = False

        if pygame.mouse.get_pressed()[0] == 0:
            if not self.clicked:
                pass
            elif current - self.click_time < self.cooldown:
                pass
            else:
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
                    spike = Spike(x * tile_size, y * tile_size + (tile_size // 2))
                    spike_group.add(spike)
                if tile == 4:
                    platform = Platform(x * tile_size, y * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(x * tile_size, y * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 6:
                    star = Star(x * tile_size + (tile_size // 2), y * tile_size + (tile_size // 2))
                    star_group.add(star)
                if tile == 7:
                    door = Door(x * tile_size, y * tile_size - (tile_size // 2) + 10)
                    door_group.add(door)
                if tile == 8:
                    check = Checkpoint(x * tile_size + 15, y * tile_size - 15)
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

        rect.x += movement[0]
        hit_list = self.collision(rect)
        for tile in hit_list:
            if movement[0] > 0:
                rect.right = tile[1].left
                collision_types["right"] = True
            elif movement[0] < 0:
                rect.left = tile[1].right
                collision_types["left"] = True

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

# ==================== SPIKE ====================
class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("assets/Trap/Idle.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect(topleft=(x, y))

# ==================== PLATFORM ====================
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
        sheet = pygame.image.load("assets/Terrain/flag animation.png").convert_alpha()

        sheet_w, sheet_h = sheet.get_size()
        self.frame_count = 5
        frame_w = sheet_w // self.frame_count

        self.frames = []
        for i in range(self.frame_count):
            frame = pygame.Surface((frame_w, sheet_h), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), (i * frame_w, 0, frame_w, sheet_h))
            frame = pygame.transform.scale(frame, (tile_size, int(tile_size * 1.3)))
            self.frames.append(frame)

        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()
        self.anim_cooldown = 120

        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.grid_pos = (x, y)
        self.activated = False

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.anim_cooldown:
            self.frame_index = (self.frame_index + 1) % self.frame_count
            self.image = self.frames[self.frame_index]
            self.last_update = now

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
            image = self.anim_lists["death"][self.frame]
            if self.direction == "left":
                image = pygame.transform.flip(image, True, False)
                image.set_colorkey(BLACK)
            self.image = image
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

            self.outline.center = self.rect.center
            movement = [self.velX, self.velY]
            self.outline, collisions = world.move(self.outline, movement)

            if self.outline.left < 0:
                self.outline.left = 0
            if self.outline.right > SCREEN_WIDTH:
                self.outline.right = SCREEN_WIDTH
            if self.outline.top < 0:
                self.outline.top = 0
                self.velY = abs(self.velY) * 0.5  # bounce off top of screen
            if self.outline.bottom > GROUND:
                self.health = 0
                self.dead = True
                self.velX = 0
                self.velY = 0
                self.frame = 0
                game_over_sound.play()
                self.action("death")
                return -1

            if collisions["bottom"]:
                self.velY = 0
                self.on_ground = True
            else:
                self.on_ground = False

            if collisions["top"]:
                self.velY = 0

            for spike in spike_group:
                if self.outline.colliderect(spike.rect):
                    self.health = 0
                    self.dead = True
                    self.velX = 0
                    self.velY = 0
                    self.frame = 0
                    game_over_sound.play()
                    self.action("death")
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
                        self.outline.x += platform.move_direction * platform.move_x
                        self.outline.y += platform.move_direction * platform.move_y
                    elif self.velY < 0 and self.outline.top >= platform.rect.top:
                        self.outline.top = platform.rect.bottom
                        self.velY = 0
                    elif self.velX > 0:
                        self.outline.right = platform.rect.left
                    elif self.velX < 0:
                        self.outline.left = platform.rect.right

            self.rect.center = self.outline.center
            self.x, self.y = self.rect.topleft

            global score
            for star in star_group.sprites():
                if self.outline.colliderect(star.rect):
                    star_sound.play()
                    collected_stars.add(star.grid_pos)
                    star.kill()
                    score += 1

            for check in checkpoint_group:
                if self.outline.colliderect(check.rect):
                    if not check.activated:
                        check.activated = True
                        activated_checkpoints.add(check.grid_pos)
                    self.checkpoint_pos = (check.rect.centerx - self.rect.width // 2 - 10, check.rect.bottom - self.rect.height + 50)

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

            image = self.anim_lists[self.current_action][self.frame]
            if self.direction == "left":
                image = pygame.transform.flip(image, True, False)
                image.set_colorkey(BLACK)
            self.image = image

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

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
        self.anim_cooldown = 100

        self.anim_lists = {}
        for action, (frames, offset) in ANIMATIONS.items():
            self.anim_lists[action] = [
                get_image(sprite, i, 128, 128, 1.5, offset)
                for i in range(frames)
            ]

        self.image = self.anim_lists["idle"][0]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.outline = self.rect.inflate(-168, -144)

# ==================== LOCATION ====================
player = Player(-50, SCREEN_HEIGHT - 100, character_sprite)
levels(0)

# ========== MENU BUTTON ==========
start_btn = get_button(button_img, -16, 48, 48, 16)
start_btn = pygame.transform.scale(start_btn, (400, 100))
settings_btn = get_button(button_img, -16, 64, 64, 16)
settings_btn = pygame.transform.scale(settings_btn, (400, 100))
credits_btn = get_button(button_img, 48, 96, 32, 16)
credits_btn = pygame.transform.scale(credits_btn, (200, 100))

menu_btn = get_button(button_img, 32, 48, 32, 16)
menu_btn = pygame.transform.scale(menu_btn, (200, 100))

newgame_btn = get_button(button_img, -16, 112, 64, 16)
newgame_btn = pygame.transform.scale(newgame_btn, (400, 100))

# ========== RESTART BUTTON ==========
r_continue_btn = get_button(button_img, 0, 80, 48, 16)
r_continue_btn = pygame.transform.scale(r_continue_btn, (300, 100))

# ========== PAUSE BUTTON ==========
hamburger_btn = get_button(button_img, 32, 16, 16, 16)
hamburger_btn = pygame.transform.scale(hamburger_btn, (50, 50))

h_resume_btm = get_button(button_img, 0, 144, 64, 16)
h_resume_btm = pygame.transform.scale(h_resume_btm, (400, 100))

# ========== BUTTON POSITION ==========
start_btn = Button(SCREEN_WIDTH // 2 - 265, (SCREEN_HEIGHT // 2 - 100), start_btn)
settings_btn = Button(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 25, settings_btn)
credits_btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 150, credits_btn)
menu_btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 150, menu_btn)

r_continue_btn = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, r_continue_btn)

hamburger_btn = Button(SCREEN_WIDTH - 60, 10, hamburger_btn)
h_resume_btm = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, h_resume_btm)

newgame_btn = Button(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 100, newgame_btn)

# ========== LEVEL COMPLETE BUTTONS ==========
w_restart_btn = get_button(button_img, 144, 32, 16, 16)
w_restart_btn = pygame.transform.scale(w_restart_btn, (80, 80))
w_next_btn = get_button(button_img, 16, 0, 16, 16)
w_next_btn = pygame.transform.scale(w_next_btn, (80, 80))
w_settings_btn = get_button(button_img, 32, 0, 16, 16)
w_settings_btn = pygame.transform.scale(w_settings_btn, (80, 80))
w_home_btn = get_button(button_img, 32, 48, 32, 16)
w_home_btn = pygame.transform.scale(w_home_btn, (200, 80))

w_restart_btn = Button(SCREEN_WIDTH // 2 - 130, 370, w_restart_btn)
w_next_btn = Button(SCREEN_WIDTH // 2 - 40,  370, w_next_btn)
w_settings_btn = Button(SCREEN_WIDTH // 2 + 50,  370, w_settings_btn)
w_home_btn = Button(SCREEN_HEIGHT //  2, SCREEN_HEIGHT // 2 + 110, w_home_btn)

clock = pygame.time.Clock()
death_time = None
menu_return_time = None

# ==================== LEVEL COMPLETE STATE ====================
show_level_complete = False
level_start_time = pygame.time.get_ticks()
level_elapsed = 0

# ==================== SETTINGS ====================
show_settings = False
music_volume = 0.5
sfx_volume = 0.5

# ========== VOLUME ARROW BUTTONS ==========
volUP_img = get_button(button_img, 16, 32, 16, 16)
volUP_btn = pygame.transform.scale(volUP_img, (36, 36))
volDOWN_img = get_button(button_img, 32, 32, 16, 16)
volDOWN_btn = pygame.transform.scale(volDOWN_img, (36, 36))

def draw_volume_row(x, y, value, width=300):
    btn_size = 36
    minus_rect = pygame.Rect(x, y - 5, btn_size, btn_size)
    screen.blit(volDOWN_btn, minus_rect.topleft)

    bar_x = x + btn_size + 8
    bar_w = width - btn_size * 2 - 16
    track_rect = pygame.Rect(bar_x, y + 8, bar_w, 10)
    pygame.draw.rect(screen, GRAY, track_rect, border_radius=5)

    fill_w = int(bar_w * value)
    if fill_w > 0:
        pygame.draw.rect(screen, WHITE, pygame.Rect(bar_x, y + 8, fill_w, 10), border_radius=5)

    plus_rect = pygame.Rect(bar_x + bar_w + 8, y - 5, btn_size, btn_size)
    screen.blit(volUP_btn, plus_rect.topleft)

    pct = font_small.render(f"{int(value * 100)}%", True, WHITE)
    screen.blit(pct, (plus_rect.right + 8, y - 2))

    return minus_rect, plus_rect

def draw_settings_panel():
    global music_volume, sfx_volume

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 160, 440, 320)
    pygame.draw.rect(screen, (30, 30, 50), panel, border_radius=16)
    pygame.draw.rect(screen, (80, 160, 255), panel, 2, border_radius=16)

    title = font_medium.render("SETTINGS", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, panel.y + 20))

    sx = panel.x + 20
    text("Music Volume", font_small, WHITE, SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 60)
    music_minus, music_plus = draw_volume_row(sx, panel.y + 130, music_volume, width=340)

    text("SFX Volume", font_small, WHITE, SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 40)
    sfx_minus, sfx_plus = draw_volume_row(sx, panel.y + 230, sfx_volume, width=340)

    close_img = get_button(button_img, 0, 16, 16, 16)
    close_img = pygame.transform.scale(close_img, (64, 64))
    close_rect = pygame.Rect(panel.right - 80, panel.y + 10, 64, 64)
    screen.blit(close_img, close_rect.topleft)

    return close_rect, music_minus, music_plus, sfx_minus, sfx_plus

# ==================== LEVEL COMPLETE SCREEN ====================
def level_complete(elapsed_ms, stars_collected, max_stars=3, title="Level Completed", title_color=GREEN):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(SCREEN_WIDTH // 2 - 280, 60, 560, 500)
    pygame.draw.rect(screen, (20, 20, 40), panel, border_radius=20)
    pygame.draw.rect(screen, (80, 160, 255), panel, 3, border_radius=20)

    title_surf = font.render(title, True, title_color)
    screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 85))

    star_size = 70
    gap = 24
    total_w = max_stars * star_size + (max_stars - 1) * gap
    sx = SCREEN_WIDTH // 2 - total_w // 2
    for i in range(max_stars):
        img = pygame.transform.scale(star_yellow if i < stars_collected else star_gray, (star_size, star_size))
        screen.blit(img, (sx + i * (star_size + gap), 245))

def draw_info():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(SCREEN_WIDTH // 2 - 260, SCREEN_HEIGHT // 2 - 200, 520, 400)
    pygame.draw.rect(screen, (20, 20, 40), panel, border_radius=20)
    pygame.draw.rect(screen, (80, 160, 255), panel, 3, border_radius=20)

    title_surf = font_medium.render("HELP", True, YELLOW)
    screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, panel.y + 20))

    lines = [
        ("Controls", WHITE),
        ("A / Arrow Left  —  Walk left", (180, 180, 255)),
        ("D / Arrow Right  —  Walk right", (180, 180, 255)),
        ("Space  —  Jump", (180, 180, 255)),
        ("", WHITE),
        ("Built with Python pygame", (150, 150, 150)),
    ]
    y_offset = panel.y + 90
    for line, color in lines:
        surf = font_small.render(line, True, color)
        screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y_offset))
        y_offset += 30

    close_img = get_button(button_img, 0, 16, 16, 16)
    close_img = pygame.transform.scale(close_img, (48, 48))
    close_rect = pygame.Rect(panel.right - 58, panel.y + 10, 48, 48)
    screen.blit(close_img, close_rect.topleft)

    return close_rect

# ==================== MAIN ====================
GAME_OVER = 0

async def main():
    global run, GAME_OVER, wave_time, main_menu, show_settings, show_credits
    global game_paused, death_time, show_level_complete, level_elapsed
    global music_volume, sfx_volume, credits_close_rect

    run = True
    while run:
        clock.tick(FPS)
    
        if main_menu:
            screen.blit(bg[0], (0, 0))
            wave_time += clock.get_time() / 1000.0
            draw_title("PATHFINDER", SCREEN_WIDTH // 2, 50, wave_time)
            # draw_grid()
            # draw_cross()
            if not show_settings and not show_credits and not transition.active:
                if start_btn.draw():
                    def _start_game():
                        global main_menu, GAME_OVER, level_start_time
                        main_menu = False
                        GAME_OVER = 0
                        level_start_time = pygame.time.get_ticks()
                    transition.start(_start_game)
    
                if settings_btn.draw():
                    show_settings = True
                if credits_btn.draw():
                    show_credits = True
    
            if show_credits and not show_settings:
                credits_close_rect = draw_info()
    
            if show_settings:
                close_rect, music_minus, music_plus, sfx_minus, sfx_plus = draw_settings_panel()
    
        else:
            bg_index = min(level, len(bg) - 1)
            screen.blit(bg[bg_index], (0, 0))
            # draw_grid()
            # draw_cross()
    
            for i in range(3):
                img = star_yellow if i < score else star_gray
                screen.blit(img, (10 + i * 35, 42))
    
            draw_hearts(life)
    
            if not game_paused and not show_level_complete:
                GAME_OVER = player.update(world, game_over)
                platform_group.update()
                enemy_group.update()
                checkpoint_group.update()
    
            world.draw()
            spike_group.draw(screen)
            platform_group.draw(screen)
            door_group.draw(screen)
            star_group.draw(screen)
            checkpoint_group.draw(screen)
            enemy_group.draw(screen)
            player.draw(screen)
            if not player.dead and not player.won:
                draw_health_bar(player.x + player.rect.width // 2 - 20, player.y + 48, player.health)
    
            if not show_settings and not game_paused and not show_level_complete and not transition.active:
                if hamburger_btn.draw():
                    game_paused = True
    
            if game_paused and not show_settings:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                screen.blit(overlay, (0, 0))
                text("GAME PAUSED", font_large, YELLOW, SCREEN_WIDTH // 2 - 340, SCREEN_HEIGHT // 2 - 220)
                if h_resume_btm.draw():
                    game_paused = False
                if settings_btn.draw():
                    show_settings = True
                if not transition.active and menu_btn.draw():
                    def pause():
                        global main_menu, game_paused, life, level, score, GAME_OVER, death_time, menu_return_time
                        global show_level_complete, level_start_time
                        main_menu = True
                        game_paused = False
                        life = 3
                        level = 1
                        score = 0
                        GAME_OVER = 0
                        death_time = None
                        menu_return_time = None
                        show_level_complete = False
                        collected_stars.clear()
                        activated_checkpoints.clear()
                        levels(0)
                        player.reset(-50, SCREEN_HEIGHT - 100, character_sprite)
                        level_start_time = pygame.time.get_ticks()
                    transition.start(pause)
    
            if show_settings:
                close_rect, music_minus, music_plus, sfx_minus, sfx_plus = draw_settings_panel()
    
            # ===== PLAYER DIED =====
            if GAME_OVER == -1:
                current = pygame.time.get_ticks()
    
                if death_time is None:
                    death_time = current
    
                elapsed = current - death_time
    
                if life - 1 <= 0:
                    if not show_settings:
                        level_complete(level_elapsed if show_level_complete else 0, score, title="Game Over!", title_color=RED)
    
                        w_restart_btn.rect.centerx = SCREEN_WIDTH // 2 - 50
                        w_restart_btn.rect.y = 370
                        w_settings_btn.rect.centerx = SCREEN_WIDTH // 2 + 50
                        w_settings_btn.rect.y = 370
    
                        if not transition.active and w_restart_btn.draw():
                            def restart_game():
                                global life, level, score, GAME_OVER, death_time, show_level_complete, level_start_time
                                collected_stars.clear()
                                activated_checkpoints.clear()
                                level = 1
                                score = 0
                                life = 3
                                death_time = None
                                GAME_OVER = 0
                                show_level_complete = False
                                levels(0)
                                player.reset(-50, SCREEN_HEIGHT - 100, character_sprite)
                                level_start_time = pygame.time.get_ticks()
                            transition.start(restart_game)
    
                        if w_settings_btn.draw():
                            show_settings = True
    
                        if not transition.active and w_home_btn.draw():
                            def r_menu():
                                global main_menu, life, level, score, GAME_OVER, death_time, menu_return_time
                                global show_level_complete, level_start_time
                                main_menu = True
                                life = 3
                                level = 1
                                score = 0
                                GAME_OVER = 0
                                death_time = None
                                menu_return_time = None
                                show_level_complete = False
                                collected_stars.clear()
                                activated_checkpoints.clear()
                                levels(0)
                                player.reset(-50, SCREEN_HEIGHT - 100, character_sprite)
                                level_start_time = pygame.time.get_ticks()
                            transition.start(r_menu)
    
                else:
                    text("You Died", font_large, RED, (SCREEN_WIDTH // 2 - 210), SCREEN_HEIGHT // 2 - 45)
    
                    if elapsed >= 2000 and not transition.active:
                        spawn = player.checkpoint_pos if player.checkpoint_pos else (-50, SCREEN_HEIGHT - 100)
                        def r_respawn(spawn_pos):
                            def respawn():
                                global life, GAME_OVER, death_time, level_start_time
                                life -= 1
                                levels(current_lvl)
                                player.reset(spawn_pos[0], spawn_pos[1], character_sprite)
                                player.checkpoint_pos = spawn_pos
                                death_time = None
                                GAME_OVER = 0
                                level_start_time = pygame.time.get_ticks()
                            return respawn
                        transition.start(r_respawn(spawn))
    
            else:
                death_time = None
    
            # ===== WIN =====
            if GAME_OVER == 1:
                if not show_level_complete:
                    show_level_complete = True
                    level_elapsed = pygame.time.get_ticks() - level_start_time
    
                if not show_settings:
                    level_complete(level_elapsed, score)
    
                    is_last_level = level >= len(MAP)
    
                    if is_last_level:
                        w_restart_btn.rect.centerx = SCREEN_WIDTH // 2 - 50
                        w_restart_btn.rect.y = 370
                        w_settings_btn.rect.centerx = SCREEN_WIDTH // 2 + 50
                        w_settings_btn.rect.y = 370
    
                        if not transition.active and w_restart_btn.draw():
                            def w_restart():
                                global score, GAME_OVER, show_level_complete, level_start_time
                                show_level_complete = False
                                score = 0
                                collected_stars.clear()
                                levels(current_lvl)
                                player.reset(-50, SCREEN_HEIGHT - 100, character_sprite)
                                level_start_time = pygame.time.get_ticks()
                                GAME_OVER = 0
                            transition.start(w_restart)
    
                        if w_settings_btn.draw():
                            show_settings = True
    
                    else:
                        w_restart_btn.rect.centerx = SCREEN_WIDTH // 2 - 90
                        w_restart_btn.rect.y = 370
                        w_next_btn.rect.centerx = SCREEN_WIDTH // 2
                        w_next_btn.rect.y = 370
                        w_settings_btn.rect.centerx = SCREEN_WIDTH // 2 + 90
                        w_settings_btn.rect.y = 370
    
                        if not transition.active and w_restart_btn.draw():
                            def w_restart():
                                global score, GAME_OVER, show_level_complete, level_start_time
                                show_level_complete = False
                                score = 0
                                collected_stars.clear()
                                levels(current_lvl)
                                player.reset(-50, SCREEN_HEIGHT - 100, character_sprite)
                                level_start_time = pygame.time.get_ticks()
                                GAME_OVER = 0
                            transition.start(w_restart)
    
                        if not transition.active and w_next_btn.draw():
                            _next = level
                            def w_next(next_lvl):
                                def w_next():
                                    global level, score, GAME_OVER, show_level_complete, level_start_time
                                    saved_health = player.health
                                    level = next_lvl + 1
                                    collected_stars.clear()
                                    levels(next_lvl)
                                    score = 0
                                    player.reset(-50, SCREEN_HEIGHT - 100, character_sprite)
                                    player.health = saved_health
                                    show_level_complete = False
                                    level_start_time = pygame.time.get_ticks()
                                    GAME_OVER = 0
                                return w_next
                            transition.start(w_next(_next))
    
                        if w_settings_btn.draw():
                            show_settings = True
    
                    # home button always shown
                    if not transition.active and w_home_btn.draw():
                        def menu():
                            global main_menu, life, level, score, GAME_OVER, show_level_complete
                            global death_time, menu_return_time, level_start_time
                            main_menu = True
                            life = 3
                            level = 1
                            score = 0
                            GAME_OVER = 0
                            show_level_complete = False
                            death_time = None
                            menu_return_time = None
                            collected_stars.clear()
                            activated_checkpoints.clear()
                            levels(0)
                            player.reset(-50, SCREEN_HEIGHT - 100, character_sprite)
                            level_start_time = pygame.time.get_ticks()
                        transition.start(menu)
    
        # ==================== EVENTS ====================
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if show_credits:
                    if credits_close_rect.collidepoint(event.pos):
                        show_credits = False
                if show_settings:
                    if close_rect.collidepoint(event.pos):
                        button_sound.play()
                        show_settings = False
                    if music_minus.collidepoint(event.pos):
                        music_volume = max(0.0, round(music_volume - 0.1, 1))
                        pygame.mixer.music.set_volume(music_volume)
                    if music_plus.collidepoint(event.pos):
                        music_volume = min(1.0, round(music_volume + 0.1, 1))
                        pygame.mixer.music.set_volume(music_volume)
                    if sfx_minus.collidepoint(event.pos):
                        sfx_volume = max(0.0, round(sfx_volume - 0.1, 1))
                        star_sound.set_volume(sfx_volume)
                        jump_sound.set_volume(sfx_volume)
                        game_over_sound.set_volume(sfx_volume)
                    if sfx_plus.collidepoint(event.pos):
                        sfx_volume = min(1.0, round(sfx_volume + 0.1, 1))
                        star_sound.set_volume(sfx_volume)
                        jump_sound.set_volume(sfx_volume)
                        game_over_sound.set_volume(sfx_volume)
            if event.type == pygame.QUIT:
                run = False

        transition.update()
        transition.draw()

        pygame.display.update()
        await asyncio.sleep(0)


asyncio.run(main())