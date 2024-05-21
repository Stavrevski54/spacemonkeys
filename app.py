import math
import random
import pygame
from pygame import mixer
import os

# Initialize the pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((800, 500))

# Background
background = pygame.image.load('background.png')

# Sound
mixer.music.load("background.mp3")
mixer.music.play(-1)

# Caption and Icon
pygame.display.set_caption("Space Invader")
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)

# Player
playerImg = pygame.image.load('player.png')
playerX = 370
playerY = 380
playerX_change = 0

# Enemy
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 6


def initialize_enemies():
    for i in range(num_of_enemies):
        enemyImg.append(pygame.image.load('enemy.png'))
        enemyX.append(random.randint(0, 736))
        enemyY.append(random.randint(50, 150))
        enemyX_change.append(2)  # Adjusted speed to 2 pixels per frame
        enemyY_change.append(40)


initialize_enemies()

# Bullet
bulletImg = pygame.image.load('bullet.png')
bulletX = 0
bulletY = 380
bulletX_change = 0
bulletY_change = 10
bullet_state = "ready"

# Score
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)
textX = 10
textY = 10

# Game Over
over_font = pygame.font.Font('freesansbold.ttf', 64)


def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))


def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (200, 250))


def restart_text():
    restart = font.render("Press R to Restart", True, (255, 255, 255))
    screen.blit(restart, (270, 350))


def player(x, y):
    screen.blit(playerImg, (x, y))


def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))


def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))


def isPlayerCollision(playerX, playerY, enemyX, enemyY):
    distance = math.sqrt((playerX - enemyX) ** 2 + (playerY - enemyY) ** 2)
    if distance < 27:  # Adjusted based on image size
        return True
    else:
        return False


def reset_game():
    global playerX, playerY, playerX_change, bulletX, bulletY, bullet_state, score_value
    playerX = 370
    playerY = 380
    playerX_change = 0
    bulletX = 0
    bulletY = 380
    bullet_state = "ready"
    score_value = 0
    enemyImg.clear()
    enemyX.clear()
    enemyY.clear()
    enemyX_change.clear()
    enemyY_change.clear()
    initialize_enemies()


def save_score(name, score):
    with open('scores.txt', 'a') as file:
        file.write(f"{name},{score}\n")


def display_leaderboard():
    if not os.path.exists('scores.txt'):
        return []
    with open('scores.txt', 'r') as file:
        scores = [line.strip().split(',') for line in file]
    scores = sorted(scores, key=lambda x: int(x[1]), reverse=True)
    return scores[:5]


def show_leaderboard():
    leaderboard = display_leaderboard()
    y_offset = 50
    for i, (name, score) in enumerate(leaderboard):
        entry_text = font.render(f"{i + 1}. {name} - {score}", True, (255, 255, 255))
        screen.blit(entry_text, (10, 50 + y_offset * i))


# Game Loop
running = True
game_state = "running"
player_name = ""
name_input_active = False

while running:
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "running":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    playerX_change = -5
                if event.key == pygame.K_RIGHT:
                    playerX_change = 5
                if event.key == pygame.K_SPACE:
                    if bullet_state == "ready":
                        bulletSound = mixer.Sound("laser.wav")
                        bulletSound.play()
                        bulletX = playerX
                        fire_bullet(bulletX, bulletY)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    playerX_change = 0

        elif game_state == "game_over":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_state = "running"
                    reset_game()

        elif game_state == "name_input":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    save_score(player_name, score_value)
                    game_state = "game_over"
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    player_name += event.unicode

    if game_state == "running":
        playerX += playerX_change
        if playerX <= 0:
            playerX = 0
        elif playerX >= 736:
            playerX = 736

        for i in range(num_of_enemies):
            enemyX[i] += enemyX_change[i]
            if enemyX[i] <= 0:
                enemyX_change[i] = 2
                enemyY[i] += enemyY_change[i]
            elif enemyX[i] >= 736:
                enemyX_change[i] = -2
                enemyY[i] += enemyY_change[i]

            # Check for collisions between player and enemies
            if isPlayerCollision(playerX, playerY, enemyX[i], enemyY[i]):
                game_state = "name_input"
                break

            enemy(enemyX[i], enemyY[i], i)

        # Check for collisions between bullet and enemies
        for i in range(num_of_enemies):
            collision = isPlayerCollision(bulletX, bulletY, enemyX[i], enemyY[i])
            if collision:
                bulletY = 380
                bullet_state = "ready"
                score_value += 1
                enemyX[i] = random.randint(0, 736)
                enemyY[i] = random.randint(50, 150)

            enemy(enemyX[i], enemyY[i], i)

        if bulletY <= 0:
            bulletY = 380
            bullet_state = "ready"

        if bullet_state == "fire":
            fire_bullet(bulletX, bulletY)
            bulletY -= bulletY_change

        player(playerX, playerY)
        show_score(textX, textY)

    elif game_state == "name_input":
        game_over_text()
        input_text = font.render(f"Enter your name: {player_name}", True, (255, 255, 255))
        screen.blit(input_text, (200, 300))

    elif game_state == "game_over":
        game_over_text()
        restart_text()
        show_leaderboard()

    pygame.display.update()

pygame.quit()
