import pygame
import pyperclip  # For one-click copy

pygame.init()

# --------------------------
# SETTINGS (MATCHES YOUR GAME)
# --------------------------
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 750
TILE_SIZE = 50
GRID_WIDTH = 18   # Same as your map width
GRID_HEIGHT = 14  # Same as your map height

# Colors
BG_COLOR = (20, 20, 40)
GRID_COLOR = (80, 80, 80)
PANEL_COLOR = (40, 40, 60)
HIGHLIGHT_COLOR = (80, 160, 255)
TEXT_COLOR = (255, 255, 255)

# Tile IDs — EXACT same as your game
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
pygame.display.set_caption("Map Editor — Pathfinder")
font = pygame.font.Font(None, 28)
font_large = pygame.font.Font(None, 36)

# Map data — empty by default
map_data = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
current_tile = 1
scroll_x = 0
scroll_y = 0
panel_w = 300  # Fixed width for side panel

# Button positions — EXACTLY placed, no overlap
clear_btn_rect = pygame.Rect(SCREEN_WIDTH - panel_w + 20, 570, 260, 45)
copy_btn_rect = pygame.Rect(SCREEN_WIDTH - panel_w + 20, 630, 260, 45)

# --------------------------
# FUNCTIONS
# --------------------------
def draw_grid():
    """Draw editable grid — fills left area completely"""
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
    """Side panel — perfect tile UI, clean blocks, no misalignment"""
    # Panel background
    pygame.draw.rect(screen, PANEL_COLOR, (SCREEN_WIDTH - panel_w, 0, panel_w, SCREEN_HEIGHT))

    # Title — centered, top
    title_surf = font_large.render("TILES", True, TEXT_COLOR)
    screen.blit(title_surf, (SCREEN_WIDTH - panel_w//2 - title_surf.get_width()//2, 20))

    # Tile list — each tile in its own clean block
    for i, tile in enumerate(TILE_TYPES):
        y_pos = 70 + (i * 50)  # Fixed spacing per tile block

        # Highlight block (full size, perfect fit)
        block_rect = pygame.Rect(SCREEN_WIDTH - panel_w + 10, y_pos, 280, 45)
        if tile["id"] == current_tile:
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, block_rect, border_radius=6)
        else:
            pygame.draw.rect(screen, (50, 50, 70), block_rect, border_radius=6)

        # Tile color swatch — perfectly inside block, left side
        color_rect = pygame.Rect(SCREEN_WIDTH - panel_w + 20, y_pos + 8, 28, 28)
        pygame.draw.rect(screen, tile["color"], color_rect)
        pygame.draw.rect(screen, GRID_COLOR, color_rect, 1)  # small border around color

        # Tile text — aligned next to color swatch
        text_surf = font.render(f"{tile['id']} — {tile['name']}", True, TEXT_COLOR)
        screen.blit(text_surf, (SCREEN_WIDTH - panel_w + 60, y_pos + 12))

    # Clear Button
    pygame.draw.rect(screen, (60, 120, 220), clear_btn_rect, border_radius=8)
    clear_text = font.render("CLEAR MAP", True, TEXT_COLOR)
    screen.blit(clear_text, (clear_btn_rect.centerx - clear_text.get_width()//2, clear_btn_rect.y + 12))

    # Copy Button
    pygame.draw.rect(screen, (40, 180, 80), copy_btn_rect, border_radius=8)
    copy_text = font.render("COPY MAP CODE", True, TEXT_COLOR)
    screen.blit(copy_text, (copy_btn_rect.centerx - copy_text.get_width()//2, copy_btn_rect.y + 12))

def get_grid_pos(mx, my):
    """Only allow drawing on grid area — not on panel"""
    if 40 < mx < SCREEN_WIDTH - panel_w and 40 < my < SCREEN_HEIGHT:
        gx = (mx - 40 - scroll_x) // TILE_SIZE
        gy = (my - 40 - scroll_y) // TILE_SIZE
        if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
            return int(gx), int(gy)
    return None, None

def export_map():
    """Format exactly like your game's MAP list"""
    lines = ["["]
    for row in map_data:
        lines.append(f"    {row},")
    lines.append("]")
    return "\n".join(lines)

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

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse input
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            if event.button == 1:
                mouse_down = True
                erase_mode = False

                # Select tile / click buttons
                if mx > SCREEN_WIDTH - panel_w:
                    # Tile selection — click anywhere in tile block
                    for i, tile in enumerate(TILE_TYPES):
                        block_y = 70 + (i * 50)
                        if block_y < my < block_y + 45:
                            current_tile = tile["id"]

                    # Button actions
                    if clear_btn_rect.collidepoint((mx, my)):
                        map_data = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
                    if copy_btn_rect.collidepoint((mx, my)):
                        pyperclip.copy(export_map())
                        print("✅ Map copied to clipboard!")

            elif event.button == 3:
                mouse_down = True
                erase_mode = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button in (1, 3):
                mouse_down = False

        # Keyboard scroll
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT: scroll_x += TILE_SIZE
            if event.key == pygame.K_RIGHT: scroll_x -= TILE_SIZE
            if event.key == pygame.K_UP: scroll_y += TILE_SIZE
            if event.key == pygame.K_DOWN: scroll_y -= TILE_SIZE

    # Draw while dragging
    if mouse_down:
        gx, gy = get_grid_pos(*pygame.mouse.get_pos())
        if gx is not None and gy is not None:
            map_data[gy][gx] = 0 if erase_mode else current_tile

    pygame.display.flip()

pygame.quit()

