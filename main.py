import pygame
from player import Player # Import the Player class
from map import Map # Import the Map class
from enemy import Enemy # Import the Enemy class

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Set screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600 # Adjusted to 19 * 32 = 608, or keep 600 and have a small bottom margin
TILE_SIZE = 32 # Define TILE_SIZE

# Map dimensions
MAP_WIDTH = SCREEN_WIDTH // TILE_SIZE  # 25 tiles
MAP_HEIGHT = SCREEN_HEIGHT // TILE_SIZE # 18.75, so effectively 18 or 19. Let's use 19.
# SCREEN_HEIGHT = MAP_HEIGHT * TILE_SIZE # Optional: Adjust screen height to perfectly fit map

# Initialize Pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set window caption
pygame.display.set_caption("Roguelike Game")

# Font setup
game_font = pygame.font.Font(None, TILE_SIZE) # Using TILE_SIZE for font size for consistency
ui_font = pygame.font.Font(None, TILE_SIZE * 2) # Larger font for messages
message_font = pygame.font.Font(None, TILE_SIZE) # Font for sub-messages like "Press Q"

# Helper function to draw text centered
def draw_text_centered(screen, text, font, color):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text_surface, text_rect)

# Helper function to draw text at a specific location (can be used for stats or sub-messages)
def draw_text(screen, text, font, color, x, y, center_x_on_y=False):
    text_surface = font.render(text, True, color)
    if center_x_on_y: # Primarily for messages below centered messages
        text_rect = text_surface.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
    else:
        text_rect = text_surface.get_rect(x=x, y=y)
    screen.blit(text_surface, text_rect)


# Create map instance
game_map = Map(MAP_WIDTH, MAP_HEIGHT)

# Create player instance
# Ensure player starts on a walkable tile, e.g., center of the map
player_start_x = MAP_WIDTH // 2
player_start_y = MAP_HEIGHT // 2
player = Player(x=player_start_x, y=player_start_y, smiley='@')

# Game state
game_state = 'playing'

# Create enemies list
enemies = []
enemy_color = (255, 0, 0) # Red for enemies

# Spawn enemies at valid locations
enemy_positions = [(3, 3), (MAP_WIDTH - 4, MAP_HEIGHT - 4), (3, MAP_HEIGHT - 4)]
for pos_x, pos_y in enemy_positions:
    if game_map.is_walkable(pos_x, pos_y) and not (pos_x == player_start_x and pos_y == player_start_y):
        enemies.append(Enemy(pos_x, pos_y, 'E', 25, enemy_color))
    # Fallback if preset positions are not ideal (e.g. map too small)
    # This is a simple fallback, a more robust solution might be needed for very small maps
    elif game_map.is_walkable(player_start_x + 2, player_start_y + 2) and not (player_start_x + 2 == player_start_x and player_start_y + 2 == player_start_y):
         enemies.append(Enemy(player_start_x + 2, player_start_y + 2, 'E', 25, enemy_color))


# Game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == 'playing':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.move(0, -1, game_map, enemies)
                elif event.key == pygame.K_DOWN:
                    player.move(0, 1, game_map, enemies)
                elif event.key == pygame.K_LEFT:
                    player.move(-1, 0, game_map, enemies)
                elif event.key == pygame.K_RIGHT:
                    player.move(1, 0, game_map, enemies)
                elif event.key == pygame.K_e:
                    player.eat(20)
        elif game_state == 'game_over' or game_state == 'victory':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False # Quit the game

    if game_state == 'playing':
        # Enemy turn
        for enemy in enemies:
            if not enemy.is_dead:
                enemy.move(player.x, player.y, game_map, player)

        # Remove dead enemies
        enemies = [enemy for enemy in enemies if not enemy.is_dead]

        # Check for game over
        if player.health <= 0:
            game_state = 'game_over'
            print("Game Over!") # Console message for now

        # Check for victory
        if not enemies and player.health > 0: # Ensure player is alive for victory
            game_state = 'victory'
            print("You Win!") # Console message for now

        # Drawing for 'playing' state
        screen.fill(BLACK)
        game_map.draw(screen, game_font, TILE_SIZE)
        for enemy in enemies:
            enemy.draw(screen, game_font, TILE_SIZE)
        player.draw(screen, game_font, TILE_SIZE)

        # UI Text Rendering (Health and Hunger)
        health_text = f"Health: {player.health}/{player.max_health}"
        draw_text(screen, health_text, game_font, WHITE, 10, 10)
        hunger_text = f"Hunger: {player.hunger}/{player.max_hunger}"
        draw_text(screen, hunger_text, game_font, WHITE, 10, 10 + TILE_SIZE // 2 + 5)

    elif game_state == 'game_over':
        screen.fill(BLACK)
        draw_text_centered(screen, "Game Over", ui_font, WHITE)
        draw_text(screen, "Press Q to Quit", message_font, WHITE, 0, SCREEN_HEIGHT // 2 + TILE_SIZE, center_x_on_y=True)
    
    elif game_state == 'victory':
        screen.fill(BLACK)
        draw_text_centered(screen, "You Win!", ui_font, WHITE)
        draw_text(screen, "Press Q to Quit", message_font, WHITE, 0, SCREEN_HEIGHT // 2 + TILE_SIZE, center_x_on_y=True)

    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()
