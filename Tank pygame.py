import pygame
import pygame_textinput
from sys import exit
import random
from pygame import mixer
from lib.high_score_manager import Highscore

pygame.init()
screen = pygame.display.set_mode((1000, 800))
screen_rect = screen.get_rect()  # part of tank can't leave screen
pygame.display.set_caption('Tankzzzz')
clock = pygame.time.Clock()

## Font ##
title_font = pygame.font.Font("font/tank.ttf", 40)
title_surface = title_font.render("Tankzzz", False, "Purple")
title_rect = title_surface.get_rect(center=(500, 400))

high_score_surface = title_font.render("High Scores", False, "Purple")
high_score_rect = high_score_surface.get_rect(center=(500, 50))

## Enter name stuff
manager = pygame_textinput.TextInputManager(validator=lambda input: len(input) <= 5)
textinput_custom = pygame_textinput.TextInputVisualizer(manager=manager, font_object=title_font, font_color="White")

textinput_custom_surface = textinput_custom.surface
textinput_custom_rect = textinput_custom_surface.get_rect(midbottom=(400, 200))

# Load surfaces
ground_surface = pygame.image.load('Graphics/road.png').convert()
sky_surface = pygame.image.load('Graphics/sky.png').convert()

# Resize the sky_surface image
sky_surface = pygame.transform.scale(sky_surface, (1000, 600))
ground_surface = pygame.transform.scale(ground_surface, (1000, 250))

alien_images = [
    'Graphics/KlaedDreadnougtBase.png',
    'Graphics/KlaedBattlecruiserBase.png',
]

# Load explosion graphics
explosion_frames = [
    pygame.image.load('Graphics/explosions Vector/Explosion1jpeg-removebg-preview.png').convert_alpha(),
    pygame.image.load('Graphics/explosions Vector/Explosion2-removebg-preview.png').convert_alpha(),
    pygame.image.load('Graphics/explosions Vector/Explosion3-removebg-preview.png').convert_alpha(),
    pygame.image.load('Graphics/explosions Vector/Explosion4-removebg-preview.png').convert_alpha(),
    pygame.image.load('Graphics/explosions Vector/Explosion5-removebg-preview.png').convert_alpha(),
    pygame.image.load('Graphics/explosions Vector/Explosion7-removebg-preview.png').convert_alpha(),
    pygame.image.load('Graphics/explosions Vector/Explosion8-removebg-preview.png').convert_alpha()  # Add more frames if you have them
]

#### Score Board ####
def display_high_score(score_font, user, score, disp):
    score_surface = score_font.render(f"{user}.......{score}", False, "White")
    score_rect = score_surface.get_rect(center=(500, disp))
    screen.blit(score_surface, score_rect)

#### Live Score ####
def display_score(score_font, score):
    score_surface = score_font.render(f"Score: {score}", False, "White")
    score_rect = score_surface.get_rect(center=(500, 25))
    screen.blit(score_surface, score_rect)

#### States/screens ####
# Start page
high_scores = False
game_active = False
game_over = False

# ## INIT SCORE
score = 0

class HealthBar:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.max_health = 100
        self.current_health = self.max_health

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), self.rect)
        health_bar_width = int(self.rect.width * (self.current_health / self.max_health))
        pygame.draw.rect(surface, (255, 0, 0), (self.rect.x, self.rect.y, health_bar_width, self.rect.height))

    def decrease_health(self, amount):
        self.current_health -= amount
        if self.current_health < 0:
            self.current_health = 0

class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0):
        super().__init__()
        image_path = random.choice(alien_images)
        original_alien_img = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.rotate(original_alien_img, angle)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity = random.randint(1, 1)

    def update(self):
        self.rect.y += self.velocity
        if self.rect.top >= screen.get_height():
            self.reset_position()

    def reset_position(self):
        self.rect.y = -self.rect.height
        self.rect.x = random.randint(0, screen.get_width() - self.rect.width)

alien_group = pygame.sprite.Group()

def spawn_aliens(count=10):
    for i in range(count):
        x = random.randint(0, screen.get_width() - 100)
        y = random.randint(-150, -50)
        angle = 180
        alien = Aliens(x, y, angle)
        alien_group.add(alien)

spawn_aliens()

mixer.init()
laser_sound = mixer.Sound('sounds/mixkit-laser-gun-shot-3110.wav')
background_music = mixer.music.load('sounds/mixkit-game-level-music-689.wav')
explosion_sound = mixer.Sound('sounds/mixkit-arcade-game-explosion-2759.wav')
mixer.music.play(-1)

class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, speed, screen_height, offset_x=-24, offset_y=-95):
        super().__init__()
        self.image = pygame.Surface((5, 20))
        self.image.fill((255, 0, 0))
        adjusted_pos = (pos[0] + offset_x, pos[1] + offset_y)
        self.rect = self.image.get_rect(center=adjusted_pos)
        self.speed = speed
        self.screen_height = screen_height

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        original_image = pygame.image.load('Graphics/green.png').convert_alpha()
        self.image = pygame.transform.scale(original_image, (300, 196))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.lasers_group = pygame.sprite.Group()
        self.screen_height = pygame.display.get_surface().get_height()
        self.laser_ready = True
        self.laser_time = 0
        self.laser_delay = 300
        self.health_bar = HealthBar(10, 10, 200, 20)

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.rect.x += 10
        if keys[pygame.K_LEFT]:
            self.rect.x -= 10
        if self.rect.left > screen.get_width():
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = screen.get_width()
        if self.rect.bottom < 0:
            self.rect.top = screen.get_height()
        elif self.rect.top > screen.get_height():
            self.rect.bottom = 0
        if keys[pygame.K_SPACE] and self.laser_ready:
            self.shoot_laser()

    def shoot_laser(self):
        self.laser_ready = False
        laser = Laser(self.rect.center, 5, self.screen_height)
        self.lasers_group.add(laser)
        self.laser_time = pygame.time.get_ticks()
        laser_sound.play()

    def recharge_laser(self):
        if not self.laser_ready:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time >= self.laser_delay:
                self.laser_ready = True

    def update(self):
        self.move()
        self.lasers_group.update()
        self.recharge_laser()
        self.health_bar.draw(screen)

    def decrease_health(self, amount):
        self.health_bar.decrease_health(amount)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = explosion_frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_speed = 0.1  # Adjust this for speed of the explosion animation
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed * 1000:
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.current_frame]
                self.last_update = now

# Initialize tank
tank = Tank(100, 600)
tank_group = pygame.sprite.GroupSingle(tank)
explosion_group = pygame.sprite.Group()

# Main game loop
while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_active and not high_scores:
                    high_scores = True
                elif high_scores and not game_active:
                    high_scores = False
                    game_active = True

            if event.key == pygame.K_RETURN:
                if game_over:
                    if len(textinput_custom.value) > 0:
                        user_name = textinput_custom.value
                        user = Highscore(user_name, score)
                        user.add_score()

                        # Reset
                        game_over = False
                        game_active = False
                        high_scores = True
                        score = 0
                        textinput_custom.value = ""
                        # Need to reset tank health and aliens
                        tank.health_bar.current_health = 100
                if event.key == pygame.K_TAB:
                    game_active = False
                    game_over = False
                    high_scores = False
                    tank.health_bar.current_health = 100
                    score = 0

    if game_active:
        tank.update()
        screen.blit(sky_surface, (0, 0))
        screen.blit(ground_surface, (0, 550))
        display_score(title_font, score)

        # Update and draw aliens
        alien_group.update()
        alien_group.draw(screen)

        tank_group.update()
        tank_group.draw(screen)
        tank.lasers_group.draw(screen)

        # Update and draw explosions
        explosion_group.update()
        explosion_group.draw(screen)

        # Check for collisions between aliens and tank
        for alien in alien_group:
            if pygame.sprite.spritecollide(alien, tank_group, False):
                tank.decrease_health(10)
                alien.kill()

        # Check for collisions between lasers and aliens
        for laser in tank.lasers_group:
            collided_aliens = pygame.sprite.spritecollide(laser, alien_group, True)
            for alien in collided_aliens:
                explosion = Explosion(alien.rect.centerx, alien.rect.centery)
                explosion_group.add(explosion)
                explosion_sound.play()
                laser.kill()
                score += 1

        # Check for game over condition
        if tank.health_bar.current_health <= 0:
            game_active = False
            game_over = True

    elif high_scores:
        screen.fill("Grey")
        screen.blit(high_score_surface, high_score_rect)

        display = 200
        for i in range(0, 5):
            user, high_score = Highscore.get_high_scores()[i]
            display_high_score(title_font, user, high_score, display)
            display += 100
    elif game_over:
        screen.blit(sky_surface, (0, 0))
        screen.blit(ground_surface, (0, 600))

        game_over_surface = title_font.render("Game Over", False, "White")
        game_over_rect = game_over_surface.get_rect(center=(500, 100))
        screen.blit(game_over_surface, game_over_rect)
        textinput_custom.update(events)  # Captures initials input
        screen.blit(textinput_custom.surface, textinput_custom_rect)  # Renders initials input

        # Draw underscores for user initials input
        line_length = 28
        line_gap = 13
        y_position = 205

        pygame.draw.line(screen, "White", (380, y_position), (380 + line_length, y_position), width=2)
        pygame.draw.line(screen, "White", (380 + line_length + line_gap, y_position), (380 + 2 * line_length + line_gap, y_position), width=2)
        pygame.draw.line(screen, "White", (380 + 2 * (line_length + line_gap), y_position), (380 + 3 * line_length + 2 * line_gap, y_position), width=2)
        pygame.draw.line(screen, "White", (380 + 3 * (line_length + line_gap), y_position), (380 + 4 * line_length + 3 * line_gap, y_position), width=2)
        pygame.draw.line(screen, "White", (380 + 4 * (line_gap + line_length), y_position), (380 + 5 * line_length + 4 * line_gap, y_position), width=2)

    elif not game_active and not high_scores:
        screen.fill("Grey")
        screen.blit(title_surface, title_rect)

    # Respawn aliens if necessary
    if len(alien_group) == 6:
        spawn_aliens(5)

    pygame.display.update()
    clock.tick(60)