import pygame, sys
from utils import *
from settings import *
from math import *
from colors import *
from missile import Missile
from random import *
from enemies import Enemy
from player import Player
from missile_explosion import MissileExplosion

player_sprite = pygame.sprite.GroupSingle()
player_sprite.add(Player(60,119))

pygame.init()
clock = pygame.time.Clock()
missiles = pygame.sprite.Group()

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
            ran = randint(0,1)
            if not ran:
                x,y = self.rect.bottomright
            else:
                x,y = self.rect.midright
            velocity = self.missile_velocity
            if not self.left_side:
                if not ran:
                    x,y = self.rect.bottomleft
                else:
                    x,y = self.rect.midleft
                velocity *= -1
            self.shoot_duration = 0
            self.missiles.add(Missile(x,y,velocity,'graphics/enemies/planes/missile/missile.png'))

    def update(self):
        self.move()
        self.shoot_player_field_of_vision()


player_sprite = pygame.sprite.GroupSingle()
player_sprite.add(Player(60,119))
#normal_enemies = pygame.sprite.Group(Enemy(100,300,'graphics/enemies/planes/plane_1/plane_1_red.png',True))
normal_enemies = pygame.sprite.Group()
animations = list()

def collisions():
    for missile in missiles.sprites():
        if pygame.sprite.spritecollide(missile,player_sprite.sprite.missiles,True):
            missile.kill()
        if player_sprite.sprite.rect.colliderect(missile.rect):
            animations.append(MissileExplosion(player_sprite.sprite.rect.center,'white'))
            missile.kill()

if __name__ == '__main__':   
    start_following = False
    FOLLOW_PLAYER = pygame.USEREVENT+2
    pygame.time.set_timer(FOLLOW_PLAYER,3000)
    enter = False
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
                if event.key == pygame.K_d:
                    enter = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    pass
        screen.fill('lightblue')
        player_sprite.update()
        player_sprite.draw(screen)
        for ani in animations:
            ani.update()
        if enter:
            missiles.update()
            missiles.draw(screen)

        normal_enemies.update()
        normal_enemies.draw(screen)
        

        collisions()
        pygame.display.update()
        clock.tick(60)
