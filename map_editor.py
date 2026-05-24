import pygame
import pyperclip
import json
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename, askopenfilename

pygame.init()

# --------------------------
# SETTINGS
# --------------------------
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 750
TILE_SIZE = 50
GRID_WIDTH = 18
GRID_HEIGHT = 14

# Colors
BG_COLOR = (20, 20, 40)
GRID_COLOR = (80, 80, 80)
PANEL_COLOR = (40, 40, 60)
HIGHLIGHT_COLOR = (80, 160, 255)
BTN_COLOR = (60, 120, 220)
BTN_GREEN = (40, 180, 80)
BTN_RED = (200, 60, 60)
BTN_YELLOW = (200, 160, 0)
TEXT_COLOR = (255, 255, 255)

# Tile Types
TILE_TYPES = [
    {"id": 0, "name": "Empty", "color": (0, 0, 0)},
    {"id": 1, "name": "Dirt", "color": (139, 69, 19)},
    {"id": 2, "name": "Grass", "color": (34, 139, 34)},
    {"id": 3, "name": "Spike", "color": (255, 0, 0)},
    {"id": 4, "name": "H-Move Plat", "color": (0, 191, 255)},
    {"id": 5, "name": "V-Move Plat", "color": (255, 165, 0)},
    {"id": 6, "name": "Star", "color": (255, 215, 0)},
    {"id": 7, "name": "Door", "color": (128, 0, 128)},
    {"id": 8, "name": "Checkpoint", "color": (0, 255, 0)},
    {"id": 9, "name": "Enemy", "color": (255, 0, 0)}
]

# --------------------------
# INITIALIZE
# --------------------------
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Map Editor — Draw • Save • Copy")
font = pygame.font.Font(None, 28)
font_large = pygame.font.Font(None, 36)

map_data = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
current_tile = 1
scroll_x = 0
scroll_y = 0
panel_w = 300

# Buttons
clear_btn     = pygame.Rect(SCREEN_WIDTH - panel_w + 20, 520, 260, 40)
save_btn      = pygame.Rect(SCREEN_WIDTH - panel_w + 20, 570, 260, 40)
load_btn      = pygame.Rect(SCREEN_WIDTH - panel_w + 20, 620, 260, 40)
copy_btn      = pygame.Rect(SCREEN_WIDTH - panel_w + 20, 670, 260, 40)

# --------------------------
# FUNCTIONS
# --------------------------
def draw_grid():
    """Draw the editable grid"""
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tid = map_data[y][x]
            color = next(t["color"] for t in TILE_TYPES if t["id"] == tid)
            rx = x * TILE_SIZE + 40 + scroll_x
            ry = y * TILE_SIZE + 40 + scroll_y
            r = pygame.Rect(rx, ry, TILE_SIZE - 2, TILE_SIZE - 2)
            pygame.draw.rect(screen, color, r)
            pygame.draw.rect(screen, GRID_COLOR, r, 1)

def draw_side_panel():
    """Side panel with tiles + buttons — no overlap"""
    pygame.draw.rect(screen, PANEL_COLOR, (SCREEN_WIDTH - panel_w, 0, panel_w, SCREEN_HEIGHT))

    # Title
    title = font_large.render("TILES", True, TEXT_COLOR)
    screen.blit(title, (SCREEN_WIDTH - panel_w//2 - title.get_width()//2, 20))

    # Tile list — clean blocks
    for i, tile in enumerate(TILE_TYPES):
        y_pos = 70 + (i * 50)
        block = pygame.Rect(SCREEN_WIDTH - panel_w + 10, y_pos, 280, 45)

        if tile["id"] == current_tile:
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, block, border_radius=6)
        else:
            pygame.draw.rect(screen, (50, 50, 70), block, border_radius=6)

        # Color swatch
        color_rect = pygame.Rect(SCREEN_WIDTH - panel_w + 20, y_pos + 8, 28, 28)
        pygame.draw.rect(screen, tile["color"], color_rect)
        pygame.draw.rect(screen, GRID_COLOR, color_rect, 1)

        # Text
        text = font.render(f"{tile['id']} — {tile['name']}", True, TEXT_COLOR)
        screen.blit(text, (SCREEN_WIDTH - panel_w + 60, y_pos + 12))

    # Buttons
    def draw_btn(rect, color, text):
        pygame.draw.rect(screen, color, rect, border_radius=8)
        t_surf = font.render(text, True, TEXT_COLOR)
        screen.blit(t_surf, (rect.centerx - t_surf.get_width()//2, rect.y + 10))

    draw_btn(clear_btn, BTN_RED, "CLEAR MAP")
    draw_btn(save_btn, BTN_YELLOW, "SAVE MAP")
    draw_btn(load_btn, BTN_COLOR, "LOAD MAP")
    draw_btn(copy_btn, BTN_GREEN, "COPY MAP CODE")

def get_grid_pos(mx, my):
    """Get grid position only inside drawing area"""
    if 40 < mx < SCREEN_WIDTH - panel_w and 40 < my < SCREEN_HEIGHT:
        gx = (mx - 40 - scroll_x) // TILE_SIZE
        gy = (my - 40 - scroll_y) // TILE_SIZE
        if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
            return int(gx), int(gy)
    return None, None

def export_map():
    """Export as compact playable format"""
    lines = ["["]
    for row in map_data:
        lines.append(f"    [{','.join(map(str, row))}],")
    lines.append("]")
    return "\n".join(lines)

def save_map_file():
    """Save map to .json file"""
    Tk().withdraw()
    path = asksaveasfilename(defaultextension=".json", filetypes=[("Map Files", "*.json")])
    if path:
        with open(path, "w") as f:
            json.dump(map_data, f)

def load_map_file():
    """Load map from .json file"""
    Tk().withdraw()
    path = askopenfilename(filetypes=[("Map Files", "*.json")])
    if path:
        try:
            with open(path, "r") as f:
                global map_data
                map_data = json.load(f)
        except:
            pass

# --------------------------
# MAIN LOOP
# --------------------------
running = True
mouse_down = False
erase_mode = False

while running:
    screen.fill(BG_COLOR)
    draw_grid()
    draw_side_panel()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse input
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if event.button == 1:
                mouse_down = True
                erase_mode = False

                if mx > SCREEN_WIDTH - panel_w:
                    # Select tile
                    for i, tile in enumerate(TILE_TYPES):
                        y_pos = 70 + (i * 50)
                        if y_pos < my < y_pos + 45:
                            current_tile = tile["id"]
                    # Buttons
                    if clear_btn.collidepoint((mx, my)):
                        map_data = [[0]*GRID_WIDTH for _ in range(GRID_HEIGHT)]
                    if save_btn.collidepoint((mx, my)):
                        save_map_file()
                    if load_btn.collidepoint((mx, my)):
                        load_map_file()
                    if copy_btn.collidepoint((mx, my)):
                        pyperclip.copy(export_map())
                        print("✅ Map copied to clipboard!")

            elif event.button == 3:
                mouse_down = True
                erase_mode = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button in (1, 3):
                mouse_down = False

        # Scroll
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT: scroll_x += TILE_SIZE
            if event.key == pygame.K_RIGHT: scroll_x -= TILE_SIZE
            if event.key == pygame.K_UP: scroll_y += TILE_SIZE
            if event.key == pygame.K_DOWN: scroll_y -= TILE_SIZE

    # Draw/Erase while dragging
    if mouse_down:
        gx, gy = get_grid_pos(*pygame.mouse.get_pos())
        if gx is not None and gy is not None:
            map_data[gy][gx] = 0 if erase_mode else current_tile

    pygame.display.flip()

pygame.quit()