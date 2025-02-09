import pygame
import sys
import random
import os

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Super Mario Clone')

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
BLACK = (0, 0, 0)
GRAY = (192, 192, 192)

font = pygame.font.SysFont('Arial', 24)
large_font = pygame.font.SysFont('Arial', 48)

# Adjust the dimensions to match the character sprite size
mario = pygame.Rect(100, 500, 32, 32)
mario_speed = 5
gravity = 0.5
jump_speed = -10
velocity_y = 0
is_jumping = False
score = 0

camera_x = 0
camera_y = 0

ground_height = 20
ground_y = screen_height - ground_height

def create_platforms():
    return [pygame.Rect(x * 200, 500 - y * 30, random.randint(100, 250), 20) for x, y in zip(range(30), range(30))]

platforms = create_platforms()

def create_mushrooms():
    return [pygame.Rect(random.randint(platform.x, platform.x + platform.width - 20),
                        platform.y - 20, 20, 20) for platform in platforms]

def create_monsters():
    return [{"rect": pygame.Rect(random.randint(platforms[i + 1].x, platforms[i + 1].x + platforms[i + 1].width - 30),
                                 platforms[i + 1].y - 30, 30, 30),
             "speed": (i + 2) * random.choice([-1, 1]),
             "platform_index": i + 1}
            for i in range(len(platforms) - 1)]

mushrooms = create_mushrooms()
monsters = create_monsters()

downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
high_score_file = os.path.join(downloads_folder, 'high_score.txt')

def read_high_score():
    try:
        with open(high_score_file, 'r') as file:
            return int(file.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

def write_high_score(score):
    with open(high_score_file, 'w') as file:
        file.write(str(score))

high_score = read_high_score()

def reset_game():
    global mario, velocity_y, is_jumping, score, camera_x, camera_y, platforms, mushrooms, monsters
    mario = pygame.Rect(100, 500, 32, 32)
    velocity_y = 0
    is_jumping = False
    score = 0
    camera_x = 0
    camera_y = 0
    platforms = create_platforms()
    mushrooms = create_mushrooms()
    monsters = create_monsters()

def show_start_screen():
    try:
        screen.fill(WHITE)
        heading_text = large_font.render("Who wants to be a Greg's disciple? 😉", True, BLACK)
        play_button = pygame.Rect(screen_width // 2 - 100, screen_height // 2 - 25, 200, 50)
        play_text = font.render("Play", True, BLACK)

        screen.blit(heading_text, (screen_width // 2 - heading_text.get_width() // 2, screen_height // 2 - 150))
        pygame.draw.rect(screen, GRAY, play_button)
        screen.blit(play_text, (play_button.x + play_button.width // 2 - play_text.get_width() // 2, 
                                play_button.y + play_button.height // 2 - play_text.get_height() // 2))

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and play_button.collidepoint(event.pos):
                    return
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
        sys.exit()

def show_game_over():
    screen.fill(WHITE)
    game_over_text = large_font.render("Game Over", True, RED)
    retry_button = pygame.Rect(screen_width // 2 - 100, screen_height // 2 - 25, 200, 50)
    retry_text = font.render("Retry", True, BLACK)

    screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - 100))
    pygame.draw.rect(screen, GRAY, retry_button)
    screen.blit(retry_text, (retry_button.x + retry_button.width // 2 - retry_text.get_width() // 2, 
                             retry_button.y + retry_button.height // 2 - retry_text.get_height() // 2))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and retry_button.collidepoint(event.pos):
                reset_game()
                return

show_start_screen()

while True:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_d]:
        mario.x += mario_speed
        score += mario_speed
    if keys[pygame.K_a]:
        mario.x -= mario_speed
        score -= mario_speed
    if keys[pygame.K_SPACE] and not is_jumping:
        velocity_y = jump_speed
        is_jumping = True

    velocity_y += gravity
    mario.y += velocity_y

    if mario.y + mario.height >= ground_y:
        show_game_over()

    for platform in platforms:
        if mario.colliderect(platform) and velocity_y >= 0:
            mario.y = platform.y - mario.height
            velocity_y = 0
            is_jumping = False

    for mushroom in mushrooms[:]:
        if mario.colliderect(mushroom):
            mushrooms.remove(mushroom)
            score += 500

    for monster_info in monsters[:]:
        monster = monster_info["rect"]
        speed = monster_info["speed"]

        if mario.colliderect(monster):
            # Check if Mario collides with the monster from the top
            if velocity_y > 0 and mario.y + mario.height - velocity_y <= monster.y:
                monsters.remove(monster_info)
                score += 50  # Increase score by 50 for killing a monster
                velocity_y = jump_speed  # Bounce Mario up slightly after killing the monster
            else:
                show_game_over()

    for monster_info in monsters:
        monster = monster_info["rect"]
        speed = monster_info["speed"]
        platform = platforms[monster_info["platform_index"]]
        monster.x += speed
        if monster.x <= platform.x or monster.x + monster.width >= platform.x + platform.width:
            monster_info["speed"] = -speed

    camera_x = mario.x - screen_width // 2
    camera_y = mario.y - screen_height // 2

    # Update drawing to match new dimensions
    pygame.draw.rect(screen, RED, (mario.x - camera_x, mario.y - camera_y, mario.width, mario.height))

    for platform in platforms:
        pygame.draw.rect(screen, BROWN, (platform.x - camera_x, platform.y - camera_y, platform.width, platform.height))

    pygame.draw.rect(screen, BLUE, (0 - camera_x, ground_y - camera_y, screen_width, ground_height))

    for mushroom in mushrooms:
        pygame.draw.rect(screen, GREEN, (mushroom.x - camera_x, mushroom.y - camera_y, mushroom.width, mushroom.height))

    for monster_info in monsters:
        pygame.draw.rect(screen, BLUE, (monster_info["rect"].x - camera_x, monster_info["rect"].y - camera_y,
                                        monster_info["rect"].width, monster_info["rect"].height))

    legend_text = f"High Score: {high_score}"
    legend_surface = font.render(legend_text, True, BLACK)
    screen.blit(legend_surface, (10, 10))

    current_score_text = f"Score: {score}"
    current_score_surface = font.render(current_score_text, True, BLACK)
    screen.blit(current_score_surface, (screen_width - current_score_surface.get_width() - 10, 10))

    if score > high_score:
        high_score = score
        write_high_score(high_score)

    pygame.display.update()
    pygame.time.Clock().tick(30)
