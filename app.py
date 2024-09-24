import pygame
import pygame_textinput
from sys import exit
import random
from pygame import mixer
from lib.high_score_manager import Highscore

pygame.init()
screen = pygame.display.set_mode((1000, 800))

## part of the tank can't leave the screen
screen_rect = screen.get_rect()  
pygame.display.set_caption('Galactic Seige')
clock = pygame.time.Clock()

## Font 
title_font = pygame.font.Font("font/tank.ttf", 40)
title_font.set_bold(True)  # Make the font bold
title_surface = title_font.render("Galactic Seige", False, "White")  # Changed to white
title_rect = title_surface.get_rect(center=(500, 400))

high_score_surface = title_font.render("High Scores", False, "White")  # Changed to white
high_score_rect = high_score_surface.get_rect(center=(500, 50))

## Enter name stuff
manager = pygame_textinput.TextInputManager(validator=lambda input: len(input) <= 5)
textinput_custom = pygame_textinput.TextInputVisualizer(manager=manager, font_object=title_font, font_color="White")

textinput_custom_surface = textinput_custom.surface
textinput_custom_rect = textinput_custom_surface.get_rect(midbottom=(400, 200))

## Load surfaces
ground_surface = pygame.image.load('Graphics/road.png').convert()
sky_surface = pygame.image.load('Graphics/sky.png').convert()
sky_surface = pygame.transform.scale(sky_surface, (1000, 600))
ground_surface = pygame.transform.scale(ground_surface, (1000, 250))

## Load the background image for start and scoreboard screens
start_background = pygame.image.load('Graphics/city.png').convert()
start_background = pygame.transform.scale(start_background, (1000, 800))

alien_images = [
    'Graphics/ship2.png',
    'Graphics/ship1.png',
]

## Load explosion graphics
explosion_frames = [
    pygame.image.load('Graphics/explosions Vector/Explosion1jpeg-removebg-preview.png').convert_alpha(),
    pygame.image.load('Graphics/explosions Vector/Explosion2-removebg-preview.png').convert_alpha(),
    pygame.image.load('Graphics/explosions Vector/Explosion3-removebg-preview.png').convert_alpha(),
    pygame.image.load('Graphics/explosions Vector/Explosion4-removebg-preview.png').convert_alpha(),
    pygame.image.load('Graphics/explosions Vector/Explosion5-removebg-preview.png').convert_alpha(),
    pygame.image.load('Graphics/explosions Vector/Explosion7-removebg-preview.png').convert_alpha(),
    pygame.image.load('Graphics/explosions Vector/Explosion8-removebg-preview.png').convert_alpha()
]

## Load power-up images
health_powerup_image = pygame.image.load('Graphics/health_powerup.png').convert_alpha()
explosion_powerup_image = pygame.image.load('Graphics/explosion_powerup.png').convert_alpha()

## Score Board 
def display_high_score(score_font, user, score, disp):
    score_surface = score_font.render(f"{user}.......{score}", False, "White")  # Updated to white
    score_rect = score_surface.get_rect(center=(500, disp))
    screen.blit(score_surface, score_rect)

## Live Score 
def display_score(score_font, score):
    score_surface = score_font.render(f"Score: {score}", False, "White")  # Updated to white
    score_rect = score_surface.get_rect(center=(500, 25))
    screen.blit(score_surface, score_rect)

## Start page
high_scores = False
game_active = False
game_over = False

## INIT SCORE
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
        self.velocity = random.randint(2, 5)

    def update(self):
        self.rect.y += self.velocity
        if self.rect.top >= screen.get_height():
            tank.decrease_health(10)
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
background_music = mixer.music.load('sounds/background.wav')
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
        self.animation_speed = 0.1  
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

## Power-up Classes

class HealthPowerup(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(health_powerup_image, (50,50))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity = random.randint(1, 3)

    def update(self):
        self.rect.y += self.velocity
        if self.rect.top >= screen.get_height():
            self.kill()

    def apply_effect(self, tank):
        if tank.health_bar.current_health < tank.health_bar.max_health:
            tank.health_bar.current_health = min(tank.health_bar.max_health, tank.health_bar.current_health + 10)
        self.kill()

    def hit_by_laser(self, tank, laser):
        self.apply_effect(tank)
        laser.kill()

class ExplosionPowerup(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(explosion_powerup_image, (50,50))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity = random.randint(1, 3)

    def update(self):
        self.rect.y += self.velocity
        if self.rect.top >= screen.get_height():
            self.kill()

    def apply_effect(self, aliens, explosion_group):
        global score  
        for alien in aliens:
            explosion = Explosion(alien.rect.centerx, alien.rect.centery)
            explosion_group.add(explosion)
            explosion_sound.play()  
            alien.kill()
            score += 1  
        
        ## Heal the tank if any health power-ups are destroyed by the explosion
        for powerup in powerup_group:
            if isinstance(powerup, HealthPowerup):
                powerup.apply_effect(tank)
        
        self.kill()

    def hit_by_laser(self, aliens, explosion_group, laser):
        self.apply_effect(aliens, explosion_group)
        laser.kill()

## Initialize tank
tank = Tank(100, 600)
tank_group = pygame.sprite.GroupSingle(tank)
explosion_group = pygame.sprite.Group()

## Power-up Group
powerup_group = pygame.sprite.Group()

def spawn_powerups():
    ## Small chance to spawn a health power-up
    if random.random() < 0.005:  
        x = random.randint(0, screen.get_width() - 40)
        y = random.randint(-100, -40)
        health_powerup = HealthPowerup(x, y)
        powerup_group.add(health_powerup)
    ## Small chance to spawn an explosion power-up
    if random.random() < 0.005: 
        x = random.randint(0, screen.get_width() - 40)
        y = random.randint(-100, -40)
        explosion_powerup = ExplosionPowerup(x, y)
        powerup_group.add(explosion_powerup)

def reset_aliens():
    alien_group.empty() 
    spawn_aliens()  
    
## Main game loop
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

                        ## Reset
                        game_over = False
                        game_active = False
                        high_scores = True
                        score = 0
                        textinput_custom.value = ""
                        ## Reset tank health and aliens
                        tank.health_bar.current_health = 100
                        reset_aliens()  

                if event.key == pygame.K_TAB:
                    game_active = False
                    game_over = False
                    high_scores = False
                    tank.health_bar.current_health = 100
                    score = 0
                    reset_aliens()  

    ## Check for game over condition
    if tank.health_bar.current_health <= 0:
        game_active = False
        game_over = True
        reset_aliens()  

    if game_active:
        tank.update()
        screen.blit(sky_surface, (0, 0))
        screen.blit(ground_surface, (0, 550))
        display_score(title_font, score)

        ## Spawn power-ups randomly
        spawn_powerups()

        ## Update and draw aliens
        alien_group.update()
        alien_group.draw(screen)

        tank_group.update()
        tank_group.draw(screen)
        tank.lasers_group.draw(screen)

        ## Update and draw power-ups
        powerup_group.update()
        powerup_group.draw(screen)

        ## Update and draw explosions
        explosion_group.update()
        explosion_group.draw(screen)

        ## Check for collisions between the tank and power-ups
        for powerup in powerup_group:
            if pygame.sprite.spritecollide(tank, powerup_group, False):
                if isinstance(powerup, HealthPowerup):
                    powerup.apply_effect(tank)
                elif isinstance(powerup, ExplosionPowerup):
                    powerup.apply_effect(alien_group, explosion_group)

        ## Check for collisions between lasers and power-ups
        for laser in tank.lasers_group:
            for powerup in powerup_group:
                if pygame.sprite.spritecollide(laser, powerup_group, False):
                    if isinstance(powerup, HealthPowerup):
                        powerup.hit_by_laser(tank, laser)
                    elif isinstance(powerup, ExplosionPowerup):
                        powerup.hit_by_laser(alien_group, explosion_group, laser)

        ## Check for collisions between lasers and aliens
        for laser in tank.lasers_group:
            collided_aliens = pygame.sprite.spritecollide(laser, alien_group, True)
            for alien in collided_aliens:
                explosion = Explosion(alien.rect.centerx, alien.rect.centery)
                explosion_group.add(explosion)
                explosion_sound.play()
                laser.kill()
                score += 1

        ## Check for collisions between the tank and aliens
        collided_aliens_with_tank = pygame.sprite.spritecollide(tank, alien_group, True)
        for alien in collided_aliens_with_tank:
            ## Trigger explosion
            explosion = Explosion(alien.rect.centerx, alien.rect.centery)
            explosion_group.add(explosion)
            explosion_sound.play() 

            tank.decrease_health(10)

        ## Check for game over condition
        if tank.health_bar.current_health <= 0:
            game_active = False
            game_over = True

    elif high_scores:
        screen.blit(start_background, (0, 0))  
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
        textinput_custom.update(events) 
        screen.blit(textinput_custom.surface, textinput_custom_rect)  

        line_length = 28
        line_gap = 13
        y_position = 205

        pygame.draw.line(screen, "White", (380, y_position), (380 + line_length, y_position), width=2)
        pygame.draw.line(screen, "White", (380 + line_length + line_gap, y_position), (380 + 2 * line_length + line_gap, y_position), width=2)
        pygame.draw.line(screen, "White", (380 + 2 * (line_length + line_gap), y_position), (380 + 3 * line_length + 2 * line_gap, y_position), width=2)
        pygame.draw.line(screen, "White", (380 + 3 * (line_length + line_gap), y_position), (380 + 4 * line_length + 3 * line_gap, y_position), width=2)
        pygame.draw.line(screen, "White", (380 + 4 * (line_gap + line_length), y_position), (380 + 5 * line_length + 4 * line_gap, y_position), width=2)

    elif not game_active and not high_scores:
        screen.blit(start_background, (0, 0))  
        screen.blit(title_surface, title_rect)

    ## Respawn aliens if necessary
    if len(alien_group) < 6:
        spawn_aliens(7)

    pygame.display.update()
    clock.tick(60)
