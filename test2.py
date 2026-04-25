import os
import pygame

pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60
TILE_SIZE = 64
LEVEL_WIDTH = 3200

LEVEL_BOTTOM = SCREEN_HEIGHT - 30

GRAVITY = 0.55
JUMP_STRENGTH = -13

WHITE = (245, 245, 245)
BLACK = (10, 10, 10)
GREEN = (0, 180, 0)
RED = (200, 35, 35)
GOLD = (240, 195, 40)
BROWN = (112, 78, 38)
SKY_BLUE = (90, 170, 255)
DARK_BLUE = (35, 70, 130)
GRAY = (90, 90, 90)
LEVEL_COUNT = 3
MENU_BG_PATH = "assets/Background/background4.jpg"
LEVEL_BG_PATHS = [
    "assets/Background/background1.jpg",
    "assets/Background/background2.jpg",
    "assets/Background/background3.jpg",
]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pathfinder - Platformer Level")
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


def safe_load_image(relative_path, fallback_size, fallback_color):
    full_path = os.path.join(BASE_DIR, relative_path)
    try:
        image = pygame.image.load(full_path).convert_alpha()
        return image
    except Exception:
        surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
        surf.fill(fallback_color)
        return surf


def safe_load_music(relative_path):
    full_path = os.path.join(BASE_DIR, relative_path)
    try:
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)
    except Exception:
        pass


def safe_load_sound(relative_path):
    full_path = os.path.join(BASE_DIR, relative_path)
    try:
        return pygame.mixer.Sound(full_path)
    except Exception:
        return None


def parse_raw_map(raw_map, block_size=48):
    platforms = []
    spikes = []
    coins = []
    chests = []
    start_flag = None
    exit_door = None

    max_width = max(len(row) for row in raw_map)
    raw_map = [row.ljust(max_width, ".") for row in raw_map]

    for row_idx, row in enumerate(raw_map):
        for col_idx, char in enumerate(row):
            x = col_idx * block_size + 40
            y = row_idx * block_size + 80
            if char == "#":
                platforms.append(pygame.Rect(x, y, block_size, block_size))
            elif char == "S":
                start_flag = pygame.Rect(x, y, block_size, block_size)
            elif char == "D":
                exit_door = pygame.Rect(x, y, block_size, block_size)
            elif char.lower() == "v":
                spikes.append(pygame.Rect(x, y + block_size - 16, block_size, 16))
            elif char == "o":
                coins.append(pygame.Rect(x + 15, y + 15, 18, 18))
            elif char == "X":
                chests.append(pygame.Rect(x + 7, y + block_size - 30, 34, 30))

    return platforms, spikes, coins, chests, start_flag, exit_door


def play_music(relative_path, volume=0.35, loop=-1):
    full_path = os.path.join(BASE_DIR, relative_path)
    try:
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loop)
    except Exception:
        pass


def draw_background(image, camera_x=0):
    if image:
        bg = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        offset = -int(camera_x * 0.25) % SCREEN_WIDTH
        screen.blit(bg, (offset - SCREEN_WIDTH, 0))
        screen.blit(bg, (offset, 0))
    else:
        draw_parallax_background(camera_x)


def draw_button(text, x, y, width, height, color, hover_color, font):
    rect = pygame.Rect(x, y, width, height)
    mouse = pygame.mouse.get_pos()
    mouse_down = pygame.mouse.get_pressed()[0]
    hovered = rect.collidepoint(mouse)
    pygame.draw.rect(screen, hover_color if hovered else color, rect, border_radius=12)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=12)
    text_surface = font.render(text, True, WHITE)
    screen.blit(text_surface, text_surface.get_rect(center=rect.center))
    return hovered and mouse_down


def get_image(sheet, frame, width, height, scale, y_offset):
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    image.blit(sheet, (0, 0), (frame * width, y_offset, width, height))
    return pygame.transform.scale(image, (int(width * scale), int(height * scale)))


def draw_parallax_background(camera_x):
    for i in range(2):
        layer_rect = pygame.Rect(i * SCREEN_WIDTH, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(screen, SKY_BLUE, layer_rect)
    pygame.draw.circle(
        screen,
        (255, 235, 120),
        (SCREEN_WIDTH - 120 - int(camera_x * 0.03), 90),
        50,
    )
    for idx in range(5):
        cloud_x = (idx * 260 - int(camera_x * 0.2)) % (SCREEN_WIDTH + 260) - 130
        pygame.draw.ellipse(screen, WHITE, (cloud_x, 80 + (idx % 2) * 70, 120, 45))
    pygame.draw.rect(screen, DARK_BLUE, (0, SCREEN_HEIGHT - 200, SCREEN_WIDTH, 200))


class Player:
    def __init__(self, x, y, sprite_sheet):
        self.sprite_sheet = sprite_sheet
        self.animations = {
            "idle": (10, 128),
            "run": (10, 768),
            "jump": (6, 1280),
            "fall": (4, 1408),
        }
        self.anim_lists = {}
        for action_name, (frames, y_offset) in self.animations.items():
            self.anim_lists[action_name] = [
                get_image(sprite_sheet, i, 128, 128, 0.95, y_offset) for i in range(frames)
            ]

        self.current_action = "idle"
        self.direction = "right"
        self.frame = 0
        self.anim_cooldown = 90
        self.last_update = pygame.time.get_ticks()

        self.start_pos = pygame.Vector2(x, y)
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.speed = 5.2
        self.on_ground = False
        self.lives = 3

        self.image = self.anim_lists["idle"][0]
        self.rect = self.image.get_rect(topleft=(x, y))

    def respawn(self):
        self.pos.x = self.start_pos.x
        self.pos.y = self.start_pos.y
        self.vel.x = 0
        self.vel.y = 0
        self.on_ground = False

    def update_animation(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.anim_cooldown:
            self.last_update = now
            self.frame = (self.frame + 1) % len(self.anim_lists[self.current_action])

    def set_action(self, action):
        if action != self.current_action:
            self.current_action = action
            self.frame = 0

    def handle_input(self, keys):
        self.vel.x = 0
        if keys[pygame.K_LEFT]:
            self.vel.x = -self.speed
            self.direction = "left"
        elif keys[pygame.K_RIGHT]:
            self.vel.x = self.speed
            self.direction = "right"

    def jump(self):
        if self.on_ground:
            self.vel.y = JUMP_STRENGTH
            self.on_ground = False

    def update(self, platforms):
        self.vel.y += GRAVITY
        if self.vel.y > 15:
            self.vel.y = 15

        self.pos.x += self.vel.x
        self.rect.x = int(self.pos.x)
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel.x > 0:
                    self.rect.right = platform.left
                elif self.vel.x < 0:
                    self.rect.left = platform.right
                self.pos.x = self.rect.x

        self.pos.y += self.vel.y
        self.rect.y = int(self.pos.y)
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel.y > 0:
                    self.rect.bottom = platform.top
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.rect.top = platform.bottom
                self.vel.y = 0
                self.pos.y = self.rect.y

        if self.vel.y < -1:
            self.set_action("jump")
        elif self.vel.y > 1 and not self.on_ground:
            self.set_action("fall")
        elif abs(self.vel.x) > 0.1:
            self.set_action("run")
        else:
            self.set_action("idle")

        self.update_animation()
        image = self.anim_lists[self.current_action][self.frame]
        if self.direction == "left":
            image = pygame.transform.flip(image, True, False)
        self.image = image

    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))


def build_level(level_index):
    raw_levels = [
        {
            "background": LEVEL_BG_PATHS[0],
            "raw_map": [
                "S###..............",
                "....#..o.o.......",
                "....#.....V.o....",
                "....#####..o.....",
                "...........##..o..",
                "...###...##..o....",
                "....o......###....",
                "...###.......##..D",
            ],
        },
        {
            "background": LEVEL_BG_PATHS[1],
            "raw_map": [
                "S###.......V......",
                "....#....o.o......",
                "....#.............",
                "....#####....###..",
                "...........##..V..",
                "...###...##.......",
                "...........###..X.",
                "...###.......##..D",
            ],
        },
        {
            "background": LEVEL_BG_PATHS[2],
            "raw_map": [
                "S###..V.....V......",
                "....#..V..###..V...",
                "....#...V...##.....",
                "....#####...###....",
                "...........##..V...",
                "...###...##..V.....",
                ".....V.....###..X..",
                "...###.......##..D",
            ],
        },
    ]

    level = raw_levels[level_index % len(raw_levels)]
    platforms, spikes, coins, chests, start_flag, exit_door = parse_raw_map(level["raw_map"])
    level_width = len(level["raw_map"][0]) * 48 + 80
    return platforms, spikes, coins, chests, start_flag, exit_door, level["background"], level_width


def draw_world(platforms, spikes, coins, chests, start_flag, exit_door, camera_x, tile_image, trap_image):
    for platform in platforms:
        draw_rect = pygame.Rect(platform.x - camera_x, platform.y, platform.width, platform.height)
        if tile_image:
            tile = pygame.transform.scale(tile_image, (draw_rect.width, draw_rect.height))
            screen.blit(tile, draw_rect)
            pygame.draw.line(screen, BLACK, (draw_rect.left, draw_rect.centery), (draw_rect.right, draw_rect.centery), 3)
            pygame.draw.line(screen, BLACK, (draw_rect.centerx, draw_rect.top), (draw_rect.centerx, draw_rect.bottom), 3)
            pygame.draw.line(screen, BLACK, (draw_rect.left, draw_rect.top + 8), (draw_rect.right, draw_rect.top + 8), 2)
        else:
            pygame.draw.rect(screen, BROWN, draw_rect)
            pygame.draw.line(screen, BLACK, (draw_rect.left, draw_rect.centery), (draw_rect.right, draw_rect.centery), 3)
            pygame.draw.line(screen, BLACK, (draw_rect.centerx, draw_rect.top), (draw_rect.centerx, draw_rect.bottom), 3)
            pygame.draw.line(screen, BLACK, (draw_rect.left, draw_rect.top + 8), (draw_rect.right, draw_rect.top + 8), 2)
        pygame.draw.rect(screen, WHITE, draw_rect, 2)

    for spike in spikes:
        draw_x = spike.x - camera_x
        spike_rect = pygame.Rect(draw_x, spike.y, spike.width, spike.height)
        if trap_image:
            trap_icon = pygame.transform.scale(trap_image, (spike.width, spike.height + 12))
            screen.blit(trap_icon, (draw_x, spike.y - 10))
            pygame.draw.line(screen, BLACK, (draw_x, spike_rect.top), (draw_x + spike_rect.width, spike_rect.top), 3)
        else:
            points = [
                (draw_x, spike_rect.bottom),
                (draw_x + spike_rect.width / 2, spike_rect.top),
                (draw_x + spike_rect.width, spike_rect.bottom),
            ]
            pygame.draw.polygon(screen, RED, points)
            pygame.draw.polygon(screen, WHITE, points, 2)
            pygame.draw.line(screen, BLACK, (draw_x, spike_rect.top), (draw_x + spike_rect.width, spike_rect.top), 3)

    for coin in coins:
        pygame.draw.ellipse(
            screen,
            GOLD,
            pygame.Rect(coin.x - camera_x, coin.y, coin.width, coin.height),
        )

    for chest in chests:
        chest_rect = pygame.Rect(chest.x - camera_x, chest.y, chest.width, chest.height)
        pygame.draw.rect(screen, (160, 90, 30), chest_rect)
        pygame.draw.rect(screen, GOLD, (chest_rect.x + 8, chest_rect.y + 10, 18, 8))
        pygame.draw.rect(screen, WHITE, chest_rect, 2)

    start_rect = pygame.Rect(start_flag.x - camera_x, start_flag.y, start_flag.width, start_flag.height)
    if tile_image:
        tile = pygame.transform.scale(tile_image, (start_rect.width, start_rect.height))
        screen.blit(tile, start_rect)
    else:
        pygame.draw.rect(screen, GREEN, start_rect)
    pygame.draw.rect(screen, WHITE, (start_rect.x + 8, start_rect.y + 8, 20, 16))

    exit_rect = pygame.Rect(exit_door.x - camera_x, exit_door.y, exit_door.width, exit_door.height)
    if tile_image:
        tile = pygame.transform.scale(tile_image, (exit_rect.width, exit_rect.height))
        screen.blit(tile, exit_rect)
    else:
        pygame.draw.rect(screen, GRAY, exit_rect)
    pygame.draw.rect(screen, WHITE, (exit_rect.x + 12, exit_rect.y + 14, 26, 36), 2)
    pygame.draw.circle(screen, GOLD, (exit_rect.x + 38, exit_rect.y + 42), 3)


def draw_collection_effects(effects, camera_x):
    for effect in effects[:]:
        effect["timer"] -= 1
        if effect["timer"] <= 0:
            effects.remove(effect)
            continue
        radius = 12 + (18 - effect["timer"]) // 2
        alpha = int(255 * effect["timer"] / 18)
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 255, 255, alpha), (radius, radius), radius, 3)
        screen.blit(surf, (effect["x"] - camera_x - radius, effect["y"] - radius))


def draw_hud(font, small_font, score, circle_count, lives, state):
    title = font.render("PATHFINDER", True, WHITE)
    screen.blit(title, (20, 12))
    screen.blit(small_font.render(f"Score: {score}", True, WHITE), (20, 56))
    screen.blit(small_font.render(f"Circles: {circle_count}", True, WHITE), (20, 84))
    screen.blit(small_font.render(f"Lives: {lives}", True, WHITE), (20, 112))
    screen.blit(
        small_font.render("Move: Left/Right  Jump: Space", True, WHITE),
        (20, SCREEN_HEIGHT - 34),
    )
    if state == "won":
        msg = font.render("LEVEL COMPLETE! Press R to play again", True, GOLD)
        screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH // 2, 90)))
    elif state == "lost":
        msg = font.render("GAME OVER! Press R to retry", True, RED)
        screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH // 2, 90)))


def load_level(level_index, player):
    platforms, spikes, coins, chests, start_flag, exit_door, background_path, level_width = build_level(level_index)
    player.start_pos = pygame.Vector2(start_flag.x, start_flag.y - player.rect.height)
    player.respawn()
    background = safe_load_image(background_path, (SCREEN_WIDTH, SCREEN_HEIGHT), SKY_BLUE)
    return (platforms, spikes, coins, chests, start_flag, exit_door), background, level_width


def main():
    menu_font = pygame.font.SysFont("arial", 48, bold=True)
    font = pygame.font.SysFont("arial", 36, bold=True)
    small_font = pygame.font.SysFont("arial", 26)

    hero_sheet = safe_load_image(
        "assets/MainCharacter/male_hero.png",
        (1280, 3328),
        (220, 80, 80, 255),
    )
    terrain_tile = safe_load_image("assets/Terrain/Terrain.png", (TILE_SIZE, TILE_SIZE), BROWN)
    trap_image = safe_load_image("assets/Trap/Idle.png", (TILE_SIZE, TILE_SIZE), RED)
    start_sound = safe_load_sound("assets/audio/notice.wav")
    exit_sound = safe_load_sound("assets/audio/notice.wav")
    menu_bg = safe_load_image(MENU_BG_PATH, (SCREEN_WIDTH, SCREEN_HEIGHT), (28, 35, 52))

    play_music("assets/music/overworld.ogg")

    player = Player(70, 380, hero_sheet)
    current_level = 0
    score = 0
    circle_count = 0
    collection_effects = []
    player.lives = 5
    (platforms, spikes, coins, chests, start_flag, exit_door), level_background, current_level_width = load_level(current_level, player)
    game_state = "menu"

    in_menu = True
    running = True
    jump_pressed = False

    while running:
        dt = clock.tick(FPS)
        _ = dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    jump_pressed = True
                if event.key == pygame.K_r and game_state in ("won", "lost"):
                    current_level = 0
                    score = 0
                    circle_count = 0
                    collection_effects = []
                    player.lives = 5
                    (platforms, spikes, coins, chests, start_flag, exit_door), level_background, current_level_width = load_level(current_level, player)
                    game_state = "playing"
                    in_menu = False
                    play_music("assets/music/time_for_adventure.mp3")
                if event.key == pygame.K_ESCAPE:
                    in_menu = True
                    game_state = "menu"
                    play_music("assets/music/overworld.ogg")

        if in_menu:
            draw_background(menu_bg)
            title = menu_font.render("PATHFINDER", True, WHITE)
            screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 170)))
            if draw_button("START", 370, 300, 220, 68, GREEN, (30, 210, 30), small_font):
                if start_sound:
                    start_sound.play()
                current_level = 0
                score = 0
                circle_count = 0
                collection_effects = []
                player.lives = 5
                (platforms, spikes, coins, chests, start_flag, exit_door), level_background, current_level_width = load_level(current_level, player)
                game_state = "playing"
                in_menu = False
                play_music("assets/music/time_for_adventure.mp3")
            if draw_button("EXIT", 370, 395, 220, 68, BROWN, (150, 102, 40), small_font):
                if exit_sound:
                    exit_sound.play()
                pygame.time.delay(120)
                running = False
            pygame.display.flip()
            continue

        if game_state == "playing":
            keys = pygame.key.get_pressed()
            player.handle_input(keys)
            if jump_pressed:
                player.jump()
            player.update(platforms)

            if player.rect.top > SCREEN_HEIGHT:
                player.lives -= 1
                if player.lives <= 0:
                    game_state = "lost"
                else:
                    player.respawn()

            for spike in spikes:
                if player.rect.colliderect(spike):
                    player.lives -= 1
                    if player.lives <= 0:
                        game_state = "lost"
                    else:
                        player.respawn()
                    break

            for coin in coins[:]:
                if player.rect.colliderect(coin):
                    coins.remove(coin)
                    score += 10
                    circle_count += 1
                    collection_effects.append({
                        "x": coin.x + coin.width // 2,
                        "y": coin.y + coin.height // 2,
                        "timer": 18,
                    })

            for chest in chests[:]:
                if player.rect.colliderect(chest):
                    chests.remove(chest)
                    score += 30

            if player.rect.colliderect(exit_door):
                if current_level < LEVEL_COUNT - 1:
                    score += 100
                    current_level += 1
                    (platforms, spikes, coins, chests, start_flag, exit_door), level_background, current_level_width = load_level(current_level, player)
                    if start_sound:
                        start_sound.play()
                else:
                    game_state = "won"
                    if exit_sound:
                        exit_sound.play()

        jump_pressed = False
        camera_x = max(0, min(int(player.rect.centerx - SCREEN_WIDTH * 0.4), current_level_width - SCREEN_WIDTH))

        if in_menu:
            draw_background(menu_bg)
        else:
            draw_background(level_background)
        draw_world(platforms, spikes, coins, chests, start_flag, exit_door, camera_x, terrain_tile, trap_image)
        draw_collection_effects(collection_effects, camera_x)
        player.draw(screen, camera_x)

        level_text = small_font.render(f"Level {current_level + 1} / {LEVEL_COUNT}", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH - 240, 16))

        if draw_button("MENU", SCREEN_WIDTH - 142, 14, 128, 42, (165, 45, 45), (220, 65, 65), small_font):
            if exit_sound:
                exit_sound.play()
            in_menu = True
            game_state = "menu"
            play_music("assets/music/overworld.ogg")

        draw_hud(font, small_font, score, circle_count, player.lives, game_state)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
