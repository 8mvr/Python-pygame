import pygame

pygame.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pathfinder")

# Colors
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BROWN = (101, 67, 33)
BLACK = (0, 0, 0)

# Custom color
CUSTOM_1 = ("#663300")
CUSTOM_2 = ("#C6C6C6")
CUSTOM_3 = ("#00550A")

FPS = 60

GRAVITY = 0.5
JUMP = -10.5
GROUND = SCREEN_HEIGHT

tile_size = 50
game_over = 0

character_sprite = pygame.image.load("assets/MainCharacter/male_hero.png").convert_alpha()

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
MAP1 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,2,0],
    [0,2,0,0,1,0,0,2,0,0,2,2,0,0,2,0,0,0],
    [0,0,0,0,1,0,2,1,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,2,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,2,2,1,2,0,0,0,0],
    [0,0,0,2,0,0,2,2,0,0,0,0,0,0,0,0,2,0],
    [0,0,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,2,2,0,0,2,2,0],
    [0,0,0,0,0,0,0,0,2,0,2,1,0,0,0,0,0,0],
    [0,0,2,0,0,2,3,0,0,0,0,0,0,0,0,0,0,0],
    [2,2,1,2,2,1,2,0,0,0,0,0,0,0,0,0,0,0]
]

# ==================== WORLD ====================
class World(pygame.sprite.Sprite):
    def __init__(self, tiles):
        self.tile_list = []

        dirt = pygame.image.load("assets/img/dirt.png")
        grass = pygame.image.load("assets/img/grass.png")
        spike = pygame.image.load("assets/Trap/Idle.png")

        y = 0
        for row in MAP1:
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
                    img = pygame.transform.scale(spike, (tile_size, tile_size - 25))
                    img_rect = img.get_rect()
                    img_rect.x = x * tile_size
                    img_rect.y = y * tile_size + 25
                    tile = (img, img_rect, 3)
                    self.tile_list.append(tile)

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
            # pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

# ==================== PLAYER ====================
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite):
        self.sprite_sheet = sprite
        self.x = x
        self.y = y

        self.velX = 0
        self.velY = 0
        self.speed = 5

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

        # box
        self.outline = self.rect.inflate(-144, -144)

    def update_anim(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.anim_cooldown:
            self.frame += 1
            self.last_update = now
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
            self.velY = JUMP
            self.on_ground = False
            self.action("jump")

    def update(self, world):
        self.update_anim()

        if game_over == 0:
            keys = pygame.key.get_pressed()
            player.velX = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player.velX = -player.speed
                player.direction = "left"
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player.velX = player.speed
                player.direction = "right"
            if keys[pygame.K_SPACE]:
                player.jump()

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
                self.outline.bottom = GROUND
                self.velY = 0
                self.on_ground = True
            
            # collisio
            if collisions["bottom"]:
                self.velY = 0
                self.on_ground = True
            else:
                self.on_ground = False

            if collisions["top"]:
                self.velY = 0

            # player sprite + grid
            self.rect.center = self.outline.center
            self.x, self.y = self.rect.topleft

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

            img = self.anim_lists[self.current_action][self.frame]

            if self.direction == "left":
                img = pygame.transform.flip(img, True, False)
                img.set_colorkey(BLACK)

            self.image = img

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))
        # grid
        # pygame.draw.rect(surface, WHITE, self.outline, 2)

# ==================== LOC ====================
player = Player(-50, GROUND, character_sprite)
world = World(MAP1)

clock = pygame.time.Clock()

# ==================== MAIN ====================
def main():
    run = True
    while run:
        clock.tick(FPS)

        screen.fill(BROWN)
        
        player.update(world)

        world.draw()
        # spike_group.draw(screen)
        player.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
