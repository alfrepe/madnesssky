import pygame
import sys
from settings import *
from utils import *
from random import *
from player import Player
from map import Water
from game import Game, Explosion
from enemies import *
from missile_explosion import MissileExplosion
from collections import namedtuple
from confetti2nd_try import Confetti


 
'''
TODO:
utilizo los CleverEnemies porque disparan ellos solos, para los Enemy habría que utilizar la función shoot_enemy_missile
'''

# recibe una instancia a la clase para coger los atributos
# TODO: usar la clase game de main.py
# def shoot_enemy_missile(pointer):
#     if pointer.enemies_with_missiles.sprites():
#         random_enemy = choice(pointer.enemies_with_missiles.sprites())
#         velocity = pointer.missile_velocity
#         x, y = random_enemy.rect.midright
#         if not random_enemy.left_side:
#             x, y = random_enemy.rect.midleft
#             velocity *= -1
#         pointer.enemies_missiles.add(Missile(x,y,velocity,'graphics/enemies/planes/missile/missile.png'))


class Gameplay():
    def __init__(self):
        self.player = pygame.sprite.GroupSingle(Player(SCREEN_WIDTH//2,SCREEN_HEIGHT//2))
        self.enter_key_img = load_image('graphics/enter_key_resized.png')
        self.time = pygame.time.get_ticks()
        self.alpha = 85
        self.explosion_sprites = pygame.sprite.Group()
        self.finished = False
        self.water = None
        self.confetti = pygame.sprite.Group()
        self.start_confetti = False
        self.ind = 0
        self.missile_velocity = Game.missile_velocity
        self.opacity = 255
        self.score = 0
        self.enemies_missiles = pygame.sprite.Group()
        self.enemies_with_missiles = pygame.sprite.Group()
        self.protector_enemy = pygame.sprite.GroupSingle()
        lesson = namedtuple('Lesson','text completed type',defaults=[None])

        self.lessons = [
            lesson("in this guide you are invencible don't be afraid if your health gets zero and you don't die!",completed=True), 
            lesson("Let's start with the player, the player movement, use adsw keys. You can change all the player controlls in the main menu",completed=True),
            lesson("The key to shoot is SPACE, shoot some missiles to go to the next lesson!",completed=False,type='shoot_missiles'), 
            lesson("Now, let's start with the enemies...",completed=True), 
            lesson("let's start adding water",completed=True,type='water'),
            lesson("and a ship, i should mention that it is immortal...",completed=True,type='ship'),
            lesson("be careful with it, it always knows your position and it'll shoot if you don't move! it never misses a shot!",completed=True,type='ship_cannonball'),
            lesson("Watch out! An enemy plane have arrived! There are 4 types, each time you kill one, you add up 1 point in your score! ",completed=True,type='right_enemy'),
            lesson("Be careful! if you get too close to the plane enemies they'll explode and you'll die instantly! ",completed=True),
            lesson("This type of plane shoots missiles when you are in their range of vision. They are of various colors.",completed=True),# quitar vida al jugador
            lesson("You can destroy the enemies missiles. Try it!",completed=False,type='collision_between_missiles'), 
            lesson("Kill the enemy and add up 1 point to your score!",completed=False,type='collision_right_enemy'), 
            lesson("Oh no! Another enemy has appeared in the left side, just behind the player!",completed=True,type='left_enemy'), 
            lesson("No problem! press j to flip and kill the enemy!",completed=False,type='collision_left_enemy'),
            lesson("Another type of enemy has arrived!", completed=True),
            lesson("if the wire touch you, your velocity will be reduced for a certain amount of time",completed=True,type='wire_enemy'),
            lesson("This effect will also stop if you kill the enemy, kill the enemy!", completed=False,type='collision_wire_enemy'),
            lesson("Another type of enemy has arrived! It's mission is to protect other planes from your missiles",completed=True,type='protector_enemy'), 
            lesson("You cannot kill it with your own missiles, you need a special missile",completed=True),
            lesson("Here comes!  Mislead it or take advantage of it to kill enemies!",completed=True,type='seeking_missile'),
            lesson("Kill the protector enemy with this missile!",completed=False,type='kill_enemy_with_seeking_missile'),
            lesson("You can also kill this missile with your own missiles just as we have seen before, try it!",completed=False,type="kill_seeking_with_missile"),
            lesson("Now you are ready, do you accept the challenge? Press ESC to return to the main menu",completed=True,type="end")        
        ]
        self.wire_enemies = pygame.sprite.Group()
        # for lesson in self.lesson:
        #     lesson.number += 1
        self.ship = pygame.sprite.GroupSingle()
        self.missiles_explosions = list()
        self.seeking_missile = pygame.sprite.GroupSingle()

    def draw_enter_key_next_lesson(self, rect): # dibuja la imagen como parpadeando
        if pygame.time.get_ticks()-self.time > 450:
            self.time = pygame.time.get_ticks()
            self.enter_key_img.set_alpha(self.opacity)
            self.opacity -= self.alpha
            if self.opacity <= 85:
                self.opacity = 255
        screen.blit(self.enter_key_img,rect.center+vec(-self.enter_key_img.get_width()//2,20))
    
    def next_lesson(self):
        if self.lessons[self.ind].type == 'end':
            if not self.start_confetti:
                for _ in range(80):
                    self.confetti.add(Confetti([randint(0,SCREEN_WIDTH),randint(0,SCREEN_HEIGHT)],[uniform(1,2),uniform(1,2)],rand_color()))
                self.start_confetti = True
        if self.lessons[self.ind].type == 'shoot_missiles':
            if self.player.sprite.missiles:
                self.lessons[self.ind] = self.lessons[self.ind]._replace(completed=True)
        if self.lessons[self.ind].type == 'water':
            if not self.water:
                self.water = Water(speed=2)
        if self.lessons[self.ind].type == 'ship':
            if not self.ship:
                self.ship.add(Ship((-250,100),screen,self.water,self.player.sprite))
        if self.lessons[self.ind].type == 'ship_cannonball':
            self.ship.sprite.shoot_cannonball()
        if self.lessons[self.ind].type == 'right_enemy':
            if not self.enemies_with_missiles:
                if len(self.enemies_with_missiles.sprites()) < 1:
                    self.enemies_with_missiles.add(CleverEnemy(SCREEN_WIDTH-100,60,'graphics/enemies/planes/plane_1/plane_1_red.png',self.player,self.enemies_missiles,self.missile_velocity))
        if self.lessons[self.ind].type == 'left_enemy':
            if not self.enemies_with_missiles:
                if len(self.enemies_with_missiles.sprites()) < 1:
                    self.enemies_with_missiles.add(CleverEnemy(100,120,'graphics/enemies/planes/plane_1/plane_1_red.png',self.player,self.enemies_missiles,self.missile_velocity,True))
        if self.lessons[self.ind].type == 'wire_enemy':
            if len(self.wire_enemies.sprites()) < 1:
                self.wire_enemies.add(ParalyzerEnemy(SCREEN_WIDTH-100,120,'graphics/enemies/planes/plane_1/plane_1_red.png',self.player.sprite))
        if self.lessons[self.ind].type == 'protector_enemy':
            if len(self.protector_enemy.sprites()) < 1:
                self.protector_enemy.add(ProtectorEnemy(SCREEN_WIDTH-150,SCREEN_HEIGHT//2,'graphics/enemies/planes/plane_1/plane_1_red.png',self.player,self.enemies_missiles))
        if self.lessons[self.ind].type == 'seeking_missile':
            if not self.seeking_missile:
                s = SeekingMissile(100,SCREEN_HEIGHT//2,'graphics/enemies/planes/missile/seeking_resized.png',Game.missile_velocity,self.player,True)
                self.seeking_missile.add(s)
                self.enemies_missiles.add(s)
        if self.lessons[self.ind].type == 'kill_seeking_with_missile':
            if not self.seeking_missile and not self.lessons[self.ind].completed:
                    s = SeekingMissile(100,SCREEN_HEIGHT//2,'graphics/enemies/planes/missile/seeking_resized.png',Game.missile_velocity,self.player,True)
                    self.seeking_missile.add(s)
                    self.enemies_missiles.add(s)

    def update(self):
        self.next_lesson()
        draw_topleft_text(screen,"Score: "+str(self.score),10,5,30,'black')
        
        rect = show_centered_text(screen,self.lessons[self.ind].text,(SCREEN_WIDTH//2,100),20,'black')
        if self.lessons[self.ind].completed:
            self.draw_enter_key_next_lesson(rect)
        else:
            self.opacity = 255
            self.enter_key_img.set_alpha(self.opacity)
            screen.blit(self.enter_key_img,rect.center+vec(-self.enter_key_img.get_width()//2,20))
        
        if self.water:
            self.water.update_amplitude()
            self.water.draw(screen)
        self.player.update()
        self.player.draw(screen)
        self.ship.update()  
        self.ship.draw(screen) 
        self.enemies_missiles.update()
        self.enemies_missiles.draw(screen)
        self.enemies_with_missiles.update()
        self.enemies_with_missiles.draw(screen) 
        
        self.confetti.update()
        self.confetti.draw(screen)

        for enemy in self.wire_enemies:
            if enemy.player_collision:
                enemy.follow_player_and_reduce_his_velocity()
            else:
                enemy.update() 
        self.wire_enemies.draw(screen)
        self.explosion_sprites.update()
        self.protector_enemy.update()
        self.protector_enemy.draw(screen)
        self.explosion_sprites.draw(screen)
        for explosion in self.missiles_explosions:
            explosion.update()

        self.collisions()
    
    def collisions(self):
        # FIXME
        # darle vida al jugador si llega a cero
        if not self.player.sprite.is_alive():
            self.player.sprite.get_health(self.player.sprite.health_bar.sprite.maximum_health)
        if self.lessons[self.ind].type == 'collision_right_enemy' or self.lessons[self.ind].type == 'collision_left_enemy' or self.lessons[self.ind].type == 'collision_wire_enemy':
            for enemy in self.enemies_with_missiles.sprites():                     
                if pygame.sprite.spritecollide(enemy,self.player.sprite.missiles,True):
                    self.explosion_sprites.add(Explosion(enemy.rect.center))
                    enemy.kill()
                    self.lessons[self.ind] = self.lessons[self.ind]._replace(completed=True)
                    self.score += 1
            for enemy in self.wire_enemies.sprites():
                if pygame.sprite.spritecollide(enemy,self.player.sprite.missiles,True):
                    self.explosion_sprites.add(Explosion(enemy.rect.center))
                    if enemy.apply_velocity_reduction:
                        self.player.sprite.velocity += enemy.velocity_ratio
                    self.lessons[self.ind] = self.lessons[self.ind]._replace(completed=True)
                    enemy.kill()
                    self.score += 1
        
        for missile in self.enemies_missiles:
            if pygame.sprite.spritecollide(missile,self.player.sprite.missiles,True):
                if self.lessons[self.ind].type == 'collision_between_missiles' or self.lessons[self.ind].type == 'protector_enemy' or self.lessons[self.ind].type == 'kill_seeking_with_missile':
                    self.lessons[self.ind] = self.lessons[self.ind]._replace(completed=True)
                self.missiles_explosions.append(MissileExplosion(missile.rect.center))
                missile.kill()
        # quitar vida al jugador, y si la pierde toda, que la recupere toda
        for missile in self.enemies_missiles:
            if self.player.sprite.rect.colliderect(missile):
                self.player.sprite.get_damage(missile.attack)
                self.missiles_explosions.append(MissileExplosion(self.player.sprite.rect.center,'red'))
                missile.kill()
        # con los cañones del barco
        if self.ship.sprite and self.ship.sprite.ball_sprite.sprite:
            if self.player.sprite.rect.colliderect(self.ship.sprite.ball_sprite.sprite):
                self.player.sprite.get_damage(self.ship.sprite.ball_sprite.sprite.damage)
                self.ship.sprite.ball_sprite.sprite.kill()
            elif pygame.sprite.spritecollide(self.ship.sprite.ball_sprite.sprite,self.player.sprite.missiles,True):
                self.ship.sprite.ball_sprite.sprite.kill()
        
        if self.seeking_missile and self.lessons[self.ind].type == 'kill_enemy_with_seeking_missile':
            if pygame.sprite.spritecollide(self.seeking_missile.sprite,self.protector_enemy,True):
                self.explosion_sprites.add(Explosion(self.seeking_missile.sprite.rect.center))
                self.seeking_missile.sprite.kill()
                self.lessons[self.ind] = self.lessons[self.ind]._replace(completed=True)
    

if __name__ == '__main__':
    pygame.init()
    gameplay = Gameplay()
    WIRE_ENEMIES = pygame.USEREVENT+1
    pygame.time.set_timer(WIRE_ENEMIES,2500)
    clock = pygame.time.Clock()
    running = True
    
    while running:
        screen.fill('lightblue')
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == gameplay.player.sprite.keys_dict["shoot"]: 
                    gameplay.player.sprite.shoot_key_pressed = True
                if event.key == pygame.K_RETURN and not gameplay.finished:
                    if gameplay.lessons[gameplay.ind].completed:
                        gameplay.ind += 1
                        if gameplay.ind >= len(gameplay.lessons):
                            gameplay.ind = len(gameplay.lessons)-1
                            gameplay.finished = True
            if event.type == WIRE_ENEMIES:
                for enemy in gameplay.wire_enemies.sprites():
                    if not enemy.player_collision and not enemy.collecting_chain and enemy.finished:
                        enemy.player_rect = gameplay.player.sprite.rect.copy()
                        enemy.offset = 0
                        enemy.awaiting_orders = False
                        enemy.finished = False
        gameplay.update()
        pygame.display.update()
        clock.tick(FPS)
