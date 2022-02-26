import pygame, sys
from utils import *
from settings import *
from math import *
from colors import *
from missile import Missile
from random import *
from enemies import Enemy
from player import Player
from map import Water

player_sprite = pygame.sprite.GroupSingle()
player_sprite.add(Player(60,119))

pygame.init()
clock = pygame.time.Clock()
missiles = pygame.sprite.Group()
water = Water(speed=2)
# probar l´ñimites
class CleverEnemy(Enemy):
    def __init__(self, x,y, img_path, player, missiles, missile_velocity,left_side=False):
        super().__init__(x,y, img_path, left_side)
        self.shoot_interval = 500
        self.shoot_duration = 0
        self.missiles = missiles
        self.player = player
        self.missile_velocity = missile_velocity


    # dispara al jugador cuando está en el campo de visión
    def shoot_player_field_of_vision(self):
        if not self.shoot_duration:
            self.shoot_duration = pygame.time.get_ticks()
        if self.rect.y <= self.player.sprite.rect.top <= self.rect.bottom and pygame.time.get_ticks()-self.shoot_duration > self.shoot_interval:
            x,y = self.rect.bottomright
            velocity = self.missile_velocity
            if not self.left_side:
                x,y = self.rect.bottomleft
                velocity *= -1
            self.shoot_duration = 0
            self.missiles.add(Missile(x,y,velocity,'graphics/enemies/planes/missile/missile.png'))

    def update(self):
        self.move()
        self.shoot_player_field_of_vision()

class Heart(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.ind = 0
        self.animations = load_folder_images('graphics/heart')
        self.image = self.animations[0]
        self.pos = vec(pos)
        self.rect = self.image.get_rect(center=self.pos)
        self.opacity = 255
    
    def update(self):
        if int(self.ind) >= len(self.animations):
            self.ind = 0
        self.image = self.animations[int(self.ind)]
        self.rect = self.image.get_rect(center=self.pos)
        self.ind += 0.1
    

player_sprite = pygame.sprite.GroupSingle()
player_sprite.add(Player(60,119))
#normal_enemies = pygame.sprite.Group(Enemy(100,300,'graphics/enemies/planes/plane_1/plane_1_red.png',True))
normal_enemies = pygame.sprite.Group()
heart = pygame.sprite.GroupSingle(Heart((400,400)))


def collisions():
    for missile in missiles.sprites():
        if pygame.sprite.spritecollide(missile,player_sprite.sprite.missiles,True):
            missile.kill()
        if player_sprite.sprite.rect.colliderect(missile.rect):
            missile.kill()
            player_sprite.sprite.get_damage(10)
    if heart.sprite:
        if player_sprite.sprite.rect.colliderect(heart.sprite.rect):
            player_sprite.sprite.get_health(10)
            heart.sprite.kill()
        

if __name__ == '__main__':   
    start_following = False
    FOLLOW_PLAYER = pygame.USEREVENT+2
    pygame.time.set_timer(FOLLOW_PLAYER,3000)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player_sprite.sprite.shoot_key_pressed = True
                if event.key == pygame.K_n:
                    normal_enemies.add(CleverEnemy(SCREEN_WIDTH-100,300,'graphics/enemies/planes/plane_1/plane_1_red.png',player_sprite,missiles,10,False))
                if event.key == pygame.K_h:
                    heart.add(Heart((randint(300,400),randint(200,500))))
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    pass
        screen.fill('lightblue')
        pygame.draw.line(screen,'black',(200,0),(200,SCREEN_HEIGHT))
        pygame.draw.line(screen,'black',(SCREEN_WIDTH-200,0),(SCREEN_WIDTH-200,SCREEN_HEIGHT))

        pygame.draw.line(screen,'black',(0,100),(SCREEN_WIDTH,100))
        pygame.draw.line(screen,'black',(0,SCREEN_HEIGHT-250),(SCREEN_WIDTH,SCREEN_HEIGHT-250))
        water.draw_waves(screen)
        player_sprite.update()
        player_sprite.draw(screen)
        missiles.update()
        missiles.draw(screen)
        heart.update()
        heart.draw(screen)
        normal_enemies.update()
        normal_enemies.draw(screen)
        

        collisions()
        pygame.display.update()
        clock.tick(60)
