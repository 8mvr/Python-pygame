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

# Physics
GRAVITY = 0.5
JUMP = -10
GROUND = SCREEN_HEIGHT - 80

DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(DIR, "assets")

# character sprite
sprite_sheet_image = pygame.image.load("assets/MainCharacter/male_hero.png").convert_alpha()

# bg
menu = "assets/Background/background4.jpg"
bg = [
    "assets/Background/background1.jpg",
    "assets/Background/background2.jpg",
    "assets/Background/background3.jpg"
]

def get_image(sheet, frame, width, height, scale, offsetY):
    image = pygame.Surface((width, height)).convert_alpha()

    # vertical of the image animation:
    # idle = 128 || run = 768 || jump = 1280 || fall = 1408 || death = 3072
    image.blit(sheet, (0, 0), ((frame * width), offsetY, width, height))
    image = pygame.transform.scale(image, (width * scale, height * scale))
    image.set_colorkey(BLACK)

    return image

def Block(size):
    image = pygame.image.load("assets/Terrain/Terrain.png").convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 64, size, size)
    surface.blit(image, (0, 0), rect)

    return surface

# action, frames, vertical position
ANIMATIONS = {
    "idle": (10, 128),
    "run": (10, 768),
    "jump": (6, 1280),
    "fall": (4, 1408),
    "death": (23, 3072)
}

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
        
        # initial sprite
        self.image = self.anim_lists[self.current_action][self.frame]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
    
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
    
    def check_vertical_collision(self, blocks):
        """Handle vertical collisions (landing on platforms from above)"""
        if self.on_ground:
            return
            
        player_mask = pygame.mask.from_surface(self.image)
        player_rect = self.rect
        
        for block in blocks:
            if player_rect.colliderect(block.rect):
                offsetX = block.rect.x - player_rect.x
                offsetY = block.rect.y - player_rect.y
                
                try:
                    if player_mask.overlap(block.mask, (offsetX, offsetY)):
                        # Landing on block from above
                        if self.velY > 0:  # Moving downward
                            self.y = block.rect.y - self.rect.height
                            self.velY = 0
                            self.on_ground = True
                            self.is_jumping = False
                            self.is_falling = False
                            return
                except:
                    pass
    
    def check_horizontal_collision(self, blocks):
        """Handle horizontal collisions (hitting blocks from sides)"""
        player_mask = pygame.mask.from_surface(self.image)
        player_rect = self.rect
        
        for block in blocks:
            if player_rect.colliderect(block.rect):
                offsetX = block.rect.x - player_rect.x
                offsetY = block.rect.y - player_rect.y
                
                try:
                    if player_mask.overlap(block.mask, (offsetX, offsetY)):
                        # Collision from the left side
                        if self.velX > 0:  # Moving right
                            self.x = block.rect.x - self.rect.width
                        # Collision from the right side
                        elif self.velX < 0:  # Moving left
                            self.x = block.rect.x + block.rect.width
                        
                        self.velX = 0
                except:
                    pass

    def collision(self, blocks):
        # Create mask for current player image
        player_mask = pygame.mask.from_surface(self.image)
        player_rect = self.rect
        
        for block in blocks:
            # Check if rectangles overlap first (faster check)
            if player_rect.colliderect(block.rect):
                # Calculate offset between player and block for mask collision
                offsetX = block.rect.x - player_rect.x
                offsetY = block.rect.y - player_rect.y
                
                # Check pixel-perfect collision with mask
                try:
                    if player_mask.overlap(block.mask, (offsetX, offsetY)):
                        # Only land on block if falling from above
                        if self.velY > 0:  # Player moving downward
                            self.y = block.rect.y - self.rect.height
                            self.velY = 0
                            self.on_ground = True
                            self.is_jumping = False
                            self.is_falling = False
                except:
                    pass

    def update(self, blocks):
        self.update_anim()
        
        # gravity
        self.velY += GRAVITY
        
        self.x += self.velX # horizontal moove
        self.y += self.velY # vertical move
        
        # boders
        if self.x < -64:
            self.x = -64
        if self.x > SCREEN_WIDTH - 128:
            self.x = SCREEN_WIDTH - 128

        # current frame image
        current_image = self.anim_lists[self.current_action][self.frame]
        
        # flip the image if facing left
        if self.direction == "left":
            current_image = pygame.transform.flip(current_image, True, False)
            current_image.set_colorkey(BLACK)
        
        self.image = current_image
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        
        # Check collision with blocks (pixel-perfect)
        self.collision(blocks)

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
    
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

# ==================== OBSJECTS====================
class Objects(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

class Blocks(Objects):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = Block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

# ==================== POSITIONS ====================
player = Player(0, 500, sprite_sheet_image)
clock = pygame.time.Clock()

# ==================== LEVEL ====================
block_size = 48
blocks = [
    # ground block
    Blocks(i * block_size, SCREEN_HEIGHT - block_size, block_size)
    for i in range(10)
] + [
    # block 2
    Blocks(block_size * 11, SCREEN_HEIGHT - 150, block_size),
    Blocks(block_size * 12, SCREEN_HEIGHT - 150, block_size),
    
    # block 3
    Blocks(block_size * 14, SCREEN_HEIGHT - 250, block_size),
    Blocks(block_size * 15, SCREEN_HEIGHT - 250, block_size),
    Blocks(block_size * 16, SCREEN_HEIGHT - 250, block_size),
    
    # block 4
    Blocks(block_size * 18, SCREEN_HEIGHT - 250, block_size),
    
]

# ==================== MAIN LOOP ====================
def main():
    run = True
    while run:
        clock.tick(FPS)

        # Update player
        player.update(blocks)
        screen.fill(BROWN)

        # Draw all blocks/platforms
        for block in blocks:
            block.draw(screen)
        
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