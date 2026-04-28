import pygame
import os

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
JUMP = -10
GROUND = SCREEN_HEIGHT - 92

# character sprite
character_sprite = pygame.image.load("assets/MainCharacter/male_hero.png").convert_alpha()

# bg
menu = "assets/Background/background4.jpg"
bg = [
    "assets/Background/background1.jpg",
    "assets/Background/background2.jpg",
    "assets/Background/background3.jpg"
]

tile_size = 50
# def grid():
#     for line in range(0, 20):
#         pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (SCREEN_WIDTH, line * tile_size))
#         pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, SCREEN_HEIGHT))

def get_image(sheet, frame, width, height, scale, offsetY):
    image = pygame.Surface((width, height)).convert_alpha()

    # vertical of the image animation:
    # idle = 128 || run = 768 || jump = 1280 || fall = 1408 || death = 3072
    image.blit(sheet, (0, 0), ((frame * width), offsetY, width, height))
    image = pygame.transform.scale(image, (width * scale, height * scale))
    image.set_colorkey(BLACK)

    return image

# def Block(size):
#     image = pygame.image.load("assets/Terrain/Terrain.png").convert_alpha()
#     surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
#     rect = pygame.Rect(96, 64, size, size)
#     surface.blit(image, (0, 0), rect)

#     return surface

# action, frames, vertical position
ANIMATIONS = {
    "idle": (10, 128),
    "run": (10, 768),
    "jump": (6, 1280),
    "fall": (4, 1408),
    "death": (23, 3072)
}

# ==================== WORLD ====================
class World(pygame.sprite.Sprite):
    def __init__(self, data):
        self.tile_list = []

        dirt = pygame.image.load("assets/img/dirt.png")
        grass = pygame.image.load("assets/img/grass.png")
        exit = pygame.image.load("assets/img/exit.png")

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    img = pygame.transform.scale(exit, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

MAP1 = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
    [1, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 0, 2, 0, 0, 1],
    [1, 0, 0, 2, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 2, 0, 0, 0, 1],
    [1, 0, 0, 2, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
    [1, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 2, 2, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
]

# MAP2 = [
#     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1]
# ]

# MAP3 = [
#     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1]
# ]

# ==================== PLAYER ====================
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_sheet):
        super().__init__()
        self.sprite_sheet = sprite_sheet
        self.x = x
        self.y = y
        self.current_action = "idle"
        self.direction = "right"
        self.frame = 0 # starting animation

        self.last_update = pygame.time.get_ticks()
        self.anim_cooldown = 100  # milliseconds
        
        # movement
        self.velX = 0
        self.velY = 0
        self.speed = 5
        
        # jump and gravity
        self.is_jumping = False
        self.is_falling = False
        self.on_ground = True
        
        # create animation lists for each action
        self.anim_lists = {}
        for action_name, (anim_step, offsetY) in ANIMATIONS.items():
            anim_list = []
            for x in range(anim_step):
                anim_list.append(get_image(sprite_sheet, x, 128, 128, 1.5, offsetY))
            self.anim_lists[action_name] = anim_list
        
        self.image = self.anim_lists[self.current_action][self.frame]
        
        self.rect = self.image.get_rect(topleft=(self.x, self.y)) # original 128
        self.collision_rect = self.rect.inflate(-40, -80)  # inside resize
    
    def update_anim(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.anim_cooldown:
            self.frame += 1
            self.last_update = current_time
            # reset frame
            if self.frame >= len(self.anim_lists[self.current_action]):
                self.frame = 0 # start again at  0
    
    def action(self, action, direction=None):
        # when jump only jump & fall anim
        if self.is_jumping or self.is_falling:
            return
        
        if action != self.current_action:
            self.current_action = action
            self.frame = 0
        if direction:
            self.direction = direction
    
    def jump(self):
        if self.on_ground:
            self.velY = JUMP
            self.is_jumping = True
            self.is_falling = False
            self.on_ground = False
            self.current_action = "jump"
            self.frame = 0
    
    def update(self):
        self.update_anim()
        
        # gravity
        self.velY += GRAVITY
        
        self.x += self.velX # horizontal moove
        self.y += self.velY # vertical move
        
        # boders
        # if self.x < -16: # left
        #     self.x = -16
        # if self.x > SCREEN_WIDTH - 176: # right
        #     self.x = SCREEN_WIDTH - 176
        # if self.y < -16: # top
        #     self.y = -16
        # if self.y > GROUND: # bottom
        #     self.y = GROUND

        # current frame image
        current_image = self.anim_lists[self.current_action][self.frame]
        
        # flip the image if facing left
        if self.direction == "left":
            current_image = pygame.transform.flip(current_image, True, False)
            current_image.set_colorkey(BLACK)
        
        self.image = current_image
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.collision_rect = self.rect.inflate(-160, -136)

        if self.y >= GROUND:
            self.y = GROUND
            self.velY = 0
            self.on_ground = True
            self.is_jumping = False
            
            if self.is_falling:
                self.is_falling = False
        elif not self.on_ground:
            
            if self.velY > 0 and self.is_jumping:
                self.is_jumping = False
                self.is_falling = True
                self.current_action = "fall"
                self.frame = 0
    
    def collisions(self, world):
        for tile in world.tile_list:
            tile_rect = tile[1]
            
            if self.collision_rect.colliderect(tile_rect):
                # Determine collision direction
                # player top
                if self.velY > 0 and self.rect.bottom > tile_rect.top:
                    self.y = tile_rect.top - (self.collision_rect.height // 2) - 92
                    self.velY = 0
                    self.on_ground = True
                    self.is_jumping = False
                    self.is_falling = False
                    self.collision_rect.y = self.y + (self.rect.height - self.collision_rect.height) // 2
                
                # player bottom
                elif self.velY < 0:
                    self.y = tile_rect.bottom - self.collision_rect.height
                    self.velY = 0
                    self.collision_rect.y = self.y + (self.rect.height - self.collision_rect.height) // 2
                
                # horizontal || left & right
                elif self.velX != 0:
                    if self.velX < 0:  # moving left, hit right side of tile
                        self.x = (tile_rect.right - self.rect.width) - 64
                    elif self.velX > 0:  # moving right, hit left side of tile
                        self.x = (tile_rect.left - self.rect.width) + 64
                    
                    self.collision_rect.x = self.x + (self.rect.width - self.collision_rect.width)
    
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))
        pygame.draw.rect(surface, (255, 255, 255), self.collision_rect, 2)



map1 = World(MAP1)
# map2 = World(MAP2)
# map3 = World(MAP3)

# ==================== POSITIONS ====================
player = Player(100, GROUND - 128, character_sprite)
clock = pygame.time.Clock()

# ==================== MAIN LOOP ====================
def main():
    
    run = True
    while run:
        clock.tick(FPS)
        
        player.update()
        player.collisions(map1)  # Check collisions with tiles
        screen.fill(BROWN)
        
        # grid()
        map1.draw()
        player.draw(screen)
            
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.action("run", "left")
            player.velX = -player.speed
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.action("run", "right")
            player.velX = player.speed
        else:
            if player.on_ground:
                player.action("idle")
            player.velX = 0
        if keys[pygame.K_SPACE]:
            player.jump()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
