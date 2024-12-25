import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Battle")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Player tank class
class PlayerTank(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.speed = 5
        self.last_shot_time = 0
        self.shoot_cooldown = 500  # in milliseconds

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def can_shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            self.last_shot_time = current_time
            return True
        return False

# AI tank class
class AITank(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(0, HEIGHT // 2)
        self.speed = random.randint(2, 4)
        self.last_shot_time = 0
        self.shoot_cooldown = 1000  # in milliseconds
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])

    def update(self, player_rect, obstacles):
        # Dodge incoming projectiles
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                self.direction_x *= -1
                self.direction_y *= -1

        # Randomly change direction
        if random.randint(1, 100) > 98:
            self.direction_x = random.choice([-1, 1])
            self.direction_y = random.choice([-1, 1])

        # Move horizontally
        self.rect.x += self.speed * self.direction_x
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.direction_x *= -1

        # Move vertically
        self.rect.y += self.speed * self.direction_y
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT // 2:
            self.direction_y *= -1

    def can_shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            self.last_shot_time = current_time
            return True
        return False

    def shoot(self, player_rect):
        # Calculate direction toward the player
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        distance = (dx**2 + dy**2)**0.5
        speed_x = (dx / distance) * 5
        speed_y = (dy / distance) * 5
        return Projectile(self.rect.centerx, self.rect.centery, speed_y, speed_x)

# Projectile class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_y, speed_x=0):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_y = speed_y
        self.speed_x = speed_x

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.left < 0 or self.rect.right > WIDTH:
            self.kill()
        # Destroy obstacles on hit
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                obstacle.kill()
                self.kill()

# Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# Groups for sprites
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
ai_group = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
obstacles = pygame.sprite.Group()

# Create player tank
player = PlayerTank()
player_group.add(player)
all_sprites.add(player)

# Create AI tanks
while len(ai_group) < 3:
    ai_tank = AITank()
    if not pygame.sprite.spritecollide(ai_tank, ai_group, False):
        ai_group.add(ai_tank)
        all_sprites.add(ai_tank)

# Create obstacles
while len(obstacles) < 5:
    obstacle = Obstacle(random.randint(100, 700), random.randint(100, 400), 50, 50)
    if not pygame.sprite.spritecollide(obstacle, obstacles, False):
        obstacles.add(obstacle)
        all_sprites.add(obstacle)

# Game loop variables
running = True
score = 0

# Game loop
while running:
    clock.tick(60)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player controls
    keys = pygame.key.get_pressed()
    player.update(keys)

    # Change direction of all tanks with arrow keys
    if keys[pygame.K_LEFT]:
        for ai_tank in ai_group:
            ai_tank.direction_x = -1
    if keys[pygame.K_RIGHT]:
        for ai_tank in ai_group:
            ai_tank.direction_x = 1

    # AI tank behavior
    for ai_tank in ai_group:
        ai_tank.update(player.rect, obstacles)
        if ai_tank.can_shoot():
            projectile = ai_tank.shoot(player.rect)
            projectiles.add(projectile)
            all_sprites.add(projectile)

    # Update projectiles
    projectiles.update()

    # Check collisions
    for projectile in projectiles:
        if pygame.sprite.spritecollide(projectile, player_group, False):
            print("Game Over! Final Score:", score)
            running = False

    # Check for player shooting
    if keys[pygame.K_SPACE] and player.can_shoot():
        projectile = Projectile(player.rect.centerx, player.rect.top, -7)
        projectiles.add(projectile)
        all_sprites.add(projectile)

    # Destroy AI tanks
    for ai_tank in ai_group:
        if pygame.sprite.spritecollide(ai_tank, projectiles, True):
            score += 1
            ai_tank.kill()

    # Redraw screen
    screen.fill(WHITE)
    all_sprites.draw(screen)

    # Display score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    # Update display
    pygame.display.flip()

pygame.quit()



   