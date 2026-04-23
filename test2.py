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

# Physics
GRAVITY = 0.5
JUMP_STRENGTH = -10
GROUND_LEVEL = SCREEN_HEIGHT - 80

# character sprite
sprite_sheet_image = pygame.image.load("assets/MainCharacter/male_hero.png").convert_alpha()

# bg
bg_image = pygame.image.load("assets/Background/menu_bg.jpg").convert_alpha()
bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

def get_image(sheet, frame, width, height, scale, y_offset):
    image = pygame.Surface((width, height)).convert_alpha()

    # vertical of the image animation:
    # idle = 128 || run = 768 || jump = 1280 || fall = 1408 || death = 3072
    image.blit(sheet, (0, 0), ((frame * width), y_offset, width, height))
    image = pygame.transform.scale(image, (width * scale, height * scale))
    image.set_colorkey(BLACK)

    return image

# animations: frames, vertical position
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
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        
        # jump and gravity
        self.is_jumping = False
        self.is_falling = False
        self.on_ground = True
        
        # create animation lists for each action
        self.anim_lists = {}
        for action_name, (anim_step, y_offset) in ANIMATIONS.items():
            anim_list = []
            for x in range(anim_step):
                anim_list.append(get_image(sprite_sheet, x, 128, 128, 1.5, y_offset))
            self.anim_lists[action_name] = anim_list
        
        # initial sprite
        self.image = self.anim_lists[self.current_action][self.frame]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
    
    def update_animation(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.anim_cooldown:
            self.frame += 1
            self.last_update = current_time

            # reset frame
            if self.frame >= len(self.anim_lists[self.current_action]):
                self.frame = 0 # reset to 0 for loop animation
    
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
            self.vel_y = JUMP_STRENGTH
            self.is_jumping = True
            self.is_falling = False
            self.on_ground = False
            self.current_action = "jump"
            self.frame = 0
    
    def update(self):
        self.update_animation()
        
        # gravity
        self.vel_y += GRAVITY
        
        self.x += self.vel_x
        self.y += self.vel_y
        
        # boders
        if self.x < -64:
            self.x = -64
        if self.x > SCREEN_WIDTH - 128:
            self.x = SCREEN_WIDTH - 128

        if self.y >= GROUND_LEVEL:
            self.y = GROUND_LEVEL
            self.vel_y = 0
            self.on_ground = True
            self.is_jumping = False
            
            if self.is_falling:
                self.is_falling = False
        else:
            self.on_ground = False
            
            if self.vel_y > 0 and self.is_jumping:
                self.is_jumping = False
                self.is_falling = True
                self.current_action = "fall"
                self.frame = 0
     
        # current frame image
        current_image = self.anim_lists[self.current_action][self.frame]
        
        # flip the image if facing left
        if self.direction == "left":
            current_image = pygame.transform.flip(current_image, True, False)
            current_image.set_colorkey(BLACK)
        
        self.image = current_image
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
    
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

# ==================== POSITIONS ====================
player = Player(0, 500, sprite_sheet_image)
clock = pygame.time.Clock()

# ==================== MAIN LOOP ====================
run = True
while run:
    clock.tick(FPS)

    # Update player
    player.update()

    screen.blit(bg_image, (0, 0))

    player.draw(screen)
        
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player.action("run", "left")
        player.vel_x = -player.speed
    elif keys[pygame.K_RIGHT]:
        player.action("run", "right")
        player.vel_x = player.speed
    else:
        if player.on_ground:
            player.action("idle")
        player.vel_x = 0
    
    # Jump
    if keys[pygame.K_SPACE]:
        player.jump()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        

    pygame.display.flip()

pygame.quit()