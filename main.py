import time

import pygame, sys
from pygame.locals import *

pygame.init()

vec = pygame.math.Vector2
HEIGHT = 500
WIDTH = 700
ACC = 0.5
FRIC = -0.10
FPS = 60
FPS_CLOCK = pygame.time.Clock()
COUNT = 0

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
PURPLE = (160, 32, 240)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

RUN = True

# Sound
blaster_sound = pygame.mixer.Sound('blaster.mp3')


def Get_Animation_List(sheet, width, height, scale, numFrames, flipped):
    frames = []
    frame = 0
    if (flipped == False):
        while frame < numFrames:
            image = pygame.Surface((width, height))

            image.blit(sheet, (0, 0), ((frame * width), 0, (width * (frame + 1)), height))
            image = pygame.transform.scale(image, (width * scale, height * scale))
            image = pygame.transform.scale(image, (image.get_width() / 2, image.get_height() / 2))
            image.set_colorkey(BLACK)
            for i in range(3):
                frames.append(image)
            frame += 1
    else:
        while frame < numFrames:
            image = pygame.Surface((width, height))
            image.blit(sheet, (0, 0), ((frame * width), 0, (width * (frame + 1)), height))
            image = pygame.transform.scale(image, (width * scale, height * scale))
            image = pygame.transform.scale(image, (image.get_width() / 2, image.get_height() / 2))
            image = pygame.transform.flip(image, True, False)
            image.set_colorkey(BLACK)
            for i in range(3):
                frames.append(image)
            frame += 1

    return frames


# Load Player Framess
player_idle_sprite_sheet = pygame.image.load("Gunner_Blue_Idle.png").convert_alpha()
player_running_sprite_sheet = pygame.image.load("Gunner_Blue_Run.png").convert_alpha()

player_running_animation_L = Get_Animation_List(player_running_sprite_sheet, 48, 48, 3, 6, True)

player_idle_animation_R = Get_Animation_List(player_idle_sprite_sheet, 48, 48, 3, 5, False)
player_idle_animation_L = Get_Animation_List(player_idle_sprite_sheet, 48, 48, 3, 5, True)

player_running_animation_R = Get_Animation_List(player_running_sprite_sheet, 48, 48, 3, 6, False)

# Load NPC Frames
NPC_idle_sprite_sheet = pygame.image.load("Gunner_Black_Idle.png").convert_alpha()
NPC_running_sprite_sheet = pygame.image.load("Gunner_Black_Run.png").convert_alpha()

NPC_running_animation_L = Get_Animation_List(NPC_running_sprite_sheet, 48, 48, 3, 6, True)

NPC_idle_animation_R = Get_Animation_List(NPC_idle_sprite_sheet, 48, 48, 3, 5, False)
NPC_idle_animation_L = Get_Animation_List(NPC_idle_sprite_sheet, 48, 48, 3, 5, True)

NPC_running_animation_R = Get_Animation_List(NPC_running_sprite_sheet, 48, 48, 3, 6, False)


class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Background.png")

    def render(self):
        WINDOW.blit(self.image, (0, 0))


class Lava(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        image = pygame.image.load("lava.png")
        self.image = pygame.transform.scale(image, (700, 50))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 0, HEIGHT - self.image.get_height()

    def render(self):
        WINDOW.blit(self.image, (self.rect.x, self.rect.y))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.active = True
        self.move_frame = 0
        self.idle_frame = 0

        self.image = player_idle_animation_R[0]
        self.rect = self.image.get_rect()

        # Position and Direction
        self.pos = vec((340, 200))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.direction = "RIGHT"

        # Movement
        self.jumping = False
        self.running = False

        # Combat
        self.atacking = False
        self.attack_frame = 0

        self.max_move_frame = len(player_running_animation_R) - 1
        self.max_idle_frame = len(player_idle_animation_R) - 1

        self.bullets = []

        # Health
        self.health = 100
        self.ratio = 0.5

    def move(self):
        # Keep a constant acceleration of y in the downwards direction to simulate gravity
        self.acc = vec(0, 0.5)

        # Sets running to false if player speed below certain threshold
        if abs(self.vel.x) > 0.3:
            self.running = True
        else:
            self.running = False

        # Return key presses
        pressed_keys = pygame.key.get_pressed()

        # Set acceleration to negative or positive depending on direction indicated by keys
        if pressed_keys[K_a]:
            self.acc.x = -ACC
        if pressed_keys[K_d]:
            self.acc.x = ACC

        # Formulas to calculate velocity while accounting for friction
        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc  # Updates Position with new values

        # This causes character warping from one point of the screen to the other
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos  # Update rect with new pos

    def update(self):
        # Reset frame sequence if end reached
        if self.move_frame > self.max_move_frame:
            self.move_frame = 0
        if self.idle_frame > self.max_idle_frame:
            self.idle_frame = 0

        # Switch to next frame if conditions are met
        if self.jumping == False and self.running == True:
            if self.vel.x > 0:
                self.image = player_running_animation_R[self.move_frame]
                self.direction = "RIGHT"
            else:
                self.image = player_running_animation_L[self.move_frame]
                self.direction = "LEFT"
            self.move_frame += 1

        # Set frame to idle sequence if player not moving
        if abs(self.vel.x) < 0.2:
            self.move_frame = 0
            if self.direction == "LEFT":
                self.image = player_idle_animation_L[self.idle_frame]
                self.idle_frame += 1
            else:
                self.image = player_idle_animation_R[self.idle_frame]
                self.idle_frame += 1
        # Update rect to current image
        self.rect = self.image.get_rect()

    def jump(self):
        self.rect.x += 1

        # Check if player is in contact with ground
        hits = pygame.sprite.spritecollide(self, ground_group, False)

        self.rect.x -= 1

        # If touching ground and not currently jumping, make player jump
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -12

    def gravity_check(self):
        hits = pygame.sprite.spritecollide(player, ground_group, False)
        if self.vel.y > 0:
            if hits:
                lowest = hits[0]
                if self.pos.y < lowest.rect.bottom:
                    self.pos.y = lowest.rect.top + 1
                    self.vel.y = 0
                    self.jumping = False

    def render(self):
        # Slight Adjustment to make player touch ground
        self.rect.y += 13

        WINDOW.blit(self.image, (self.rect.x, self.rect.y))

        # Render Healthbar
        self.healthbar()

    def healthbar(self):

        Color = GREEN
        if self.health >= 33 and self.health <= 66:
            Color = YELLOW
        if self.health <= 33:
            Color = RED

        pygame.draw.rect(WINDOW, BLACK, (player.rect.x + 6, player.rect.y - 3, self.health / 2, 8))
        pygame.draw.rect(WINDOW, Color, (player.rect.x + 2 + 6, player.rect.y + 2 - 3, (self.health / 2) - 4, 8 - 4))


class Platform(pygame.sprite.Sprite):
    def __init__(self, startX, startY, width, height):
        super().__init__()
        self.platform = pygame.Surface((width, height))
        self.platform.fill(PURPLE)
        self.rect = self.platform.get_rect()
        self.rect.x, self.rect.y = startX, startY

    def render(self):
        WINDOW.blit(self.platform, self.rect)


class PlayerBullets(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.bullets = []

    def add_bullet(self, DIRECTION):
        if DIRECTION == "RIGHT":
            if len(self.bullets) < 4:
                bullet = pygame.Rect(player.rect.x + 50, player.rect.y + 30, 20, 5)
                self.bullets.append([bullet, DIRECTION])
                blaster_sound.play()
        else:
            if len(self.bullets) < 4:
                bullet = pygame.Rect(player.rect.x, player.rect.y + 30, 20, 5)
                self.bullets.append([bullet, DIRECTION])
                blaster_sound.play()

    def update_bullets(self):
        for bullet, DIRECTION in self.bullets:
            if bullet.x > WIDTH or bullet.x < 0:
                self.bullets.remove([bullet, DIRECTION])

        for bullet, DIRECTION in self.bullets:
            if DIRECTION == "RIGHT":
                bullet.x += 20
            else:
                bullet.x -= 20

    def render_bullets(self):
        # Render Bullets
        for bullet, DIRECTION in self.bullets:
            pygame.draw.rect(WINDOW, RED, bullet)


class NPC(pygame.sprite.Sprite):
    def __init__(self, startX, startY, platformNum):
        super().__init__()
        self.frame = 0
        self.image = NPC_idle_animation_R[0]

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = startX, startY

        self.bullets = []

        self.platfornNum = platformNum
        self.active = False

        # Position and Direction
        self.direction = "RIGHT"

        self.max_frame = len(NPC_idle_animation_R) - 1

        # Time delay
        self.last_time = pygame.time.get_ticks()
        self.time_delay = 500  # 0.50 second

        self.health = 100

        self.active = True

    def fire(self):
        # Fire at player if within range
        if self.active:
            if self.direction == "RIGHT":
                # Check if player within range
                if player.rect.x - self.rect.x <= 300:
                    # Add time delay between bullets
                    current_time = pygame.time.get_ticks()
                    elapsed_time = current_time - self.last_time
                    if elapsed_time > self.time_delay:
                        bullet = pygame.Rect(self.rect.x + 50, self.rect.y + 30, 20, 5)
                        self.bullets.append([bullet, self.direction])
                        blaster_sound.play()
                        self.last_time = pygame.time.get_ticks()

            if self.direction == "LEFT":
                # Check if within range
                if self.rect.x - player.rect.x <= 300:
                    # add time delay between bullets
                    current_time = pygame.time.get_ticks()
                    elapsed_time = current_time - self.last_time
                    if elapsed_time > self.time_delay:
                        bullet = pygame.Rect(self.rect.x, self.rect.y + 30, 20, 5)
                        self.bullets.append([bullet, self.direction])
                        blaster_sound.play()
                        self.last_time = pygame.time.get_ticks()

    def update(self):
        # Check if player on same level as platform npc is on to determine whether npc should be active or not
        if self.platfornNum == 1:
            if player.rect.colliderect(platform1.rect):
                self.active = True
            else:
                self.active = False

        if self.platfornNum == 2:
            if player.rect.colliderect(platform2.rect):
                self.active = True
            else:
                self.active = False

        if self.platfornNum == 3:
            if player.rect.colliderect(platform3.rect):
                self.active = True
            else:
                self.active = False

        # Update Direction
        if self.active:
            if player.rect.x < self.rect.x:
                self.direction = 'LEFT'
            else:
                self.direction = 'RIGHT'

        # Update Frame
        if self.frame > self.max_frame:
            self.frame = 0

        if self.direction == 'RIGHT':
            self.image = NPC_idle_animation_R[self.frame]

        if self.direction == 'LEFT':
            self.image = NPC_idle_animation_L[self.frame]

        self.frame += 1

        # Update bullets
        for bullet, direction in self.bullets:
            if direction == "LEFT":
                bullet.x -= 5
            else:
                bullet.x += 5

    def render(self):
        # Render npc
        WINDOW.blit(self.image, self.rect)

        # Render npc bullets
        for bullet, direction in self.bullets:
            pygame.draw.rect(WINDOW, BLUE, bullet)

        # Render Healthbar
        self.healthbar()

    def healthbar(self):
        Color = GREEN
        if self.health >= 33 and self.health <= 66:
            Color = YELLOW
        if self.health <= 33:
            Color = RED

        pygame.draw.rect(WINDOW, BLACK, (self.rect.x + 6, self.rect.y - 3, self.health / 2, 8))
        pygame.draw.rect(WINDOW, Color, (self.rect.x + 2 + 6, self.rect.y + 2 - 3, (self.health / 2) - 4, 8 - 4))


background = Background()
lava = Lava()
player = Player()

ground_group = pygame.sprite.Group()
ground_group.add(lava)

# Setup Platforms
platform1 = Platform(0, 360, 700, 20)
platform2 = Platform(0, 230, 700, 20)
platform3 = Platform(0, 100, 700, 20)

ground_group.add(platform1)
ground_group.add(platform2)
ground_group.add(platform3)

player_bullets = PlayerBullets()

# Setup NPCs
NPC1 = NPC(350, 305, 1)
NPC2 = NPC(120, 175, 2)
NPC3 = NPC(400, 45, 3)

NPC_group = pygame.sprite.Group()

NPC_group.add(NPC1)
NPC_group.add(NPC2)
NPC_group.add(NPC3)


def collision_manager():
    # Check for collisions
    for NPC in NPC_group:
        for bullet, DIRECTION in player_bullets.bullets:
            if pygame.Rect.colliderect(bullet, NPC.rect):
                NPC.health -= 2

        for bullet, DIRECTION in NPC.bullets:
            if pygame.Rect.colliderect(bullet, player.rect):
                player.health -= 0.5

    # Check for deaths
    for NPC in NPC_group:
        if (NPC.health <= 0):
            NPC_group.remove(NPC)
    if player.health <= 0:
        player.active = False


while player.active:
    FPS_CLOCK.tick(60)
    background.render()
    player.gravity_check()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
            if event.key == pygame.K_s:
                player.pos.y += 20
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check for mouse click to shoot
            if pygame.mouse.get_pressed()[0]:
                if player.direction == "RIGHT":
                    player_bullets.add_bullet("RIGHT")
                else:
                    player_bullets.add_bullet("LEFT")

    for ground in ground_group:
        ground.render()

    for NPC in NPC_group:
        NPC.update()
        NPC.fire()
        NPC.render()

    player_bullets.update_bullets()
    player_bullets.render_bullets()

    player.update()
    player.move()
    player.render()

    collision_manager()

    pygame.display.update()


if len(NPC_group) <= 0:
    print("You Win!")
else:
    print("Game Over. Thanks for playing!")
