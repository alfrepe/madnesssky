'''
estoy repitiendo mucho código para las animaciones mejor a crear una clase...
menú del principio que aprenda a jugar
pantalla completa
***************PRIORITARIO*****************

'''

import pygame, sys
from random import choice, randint
from map import Cloud, Sun, Water
from utils import *
from enemies import *
from missile import *
from player import Player
from settings import *
from colors import *
from podium import Podium
from fireworks import Firework
from missile_explosion import MissileExplosion
from heart import Heart
import shared
pygame.init()

# SUCESOS NO PREVISTOS:
'''
si el jugador choca contra el wire enemy la velocidad se mantiene, pero como al chocar contra un emeigo el jugador
muere en el acto, no importa mucho...
'''
clock = pygame.time.Clock()
MAX_NUMBER_OF_ENEMIES = 8
imgs_planes1 = import_folder('graphics/enemies/planes/plane_1')
imgs_planes2 = import_folder('graphics/enemies/planes/plane_2')
imgs_planes3 = import_folder('graphics/enemies/planes/plane_3')
game_over_img = load_image('graphics/player/Plane/dead/dead1.png')
game_over_rect = game_over_img.get_rect(center=[SCREEN_WIDTH//2,SCREEN_HEIGHT//4+200])

class Explosion(pygame.sprite.Sprite):
    def __init__(self,pos):
        super().__init__()
        self.frame_index = 0
        self.animation_speed = 0.5
        self.frames = load_folder_images('graphics/enemies/explosion_effect/keyframes',True,150,150)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)
    
    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]
    def update(self):
        self.animate()

class Game:
    font_size = 50
    missile_velocity = 10
    def __init__(self):
        self.score = 0
        self.missiles_explosions = list()
        self.explosion_sprites = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.player.add(Player())
        self.enemies = pygame.sprite.Group()
        self.wire_enemies = pygame.sprite.Group()
        self.protector_enemies = pygame.sprite.Group()
        self.enemies_with_missiles = pygame.sprite.Group()
        self.heart = pygame.sprite.GroupSingle()
        self.enemies_missiles = pygame.sprite.Group()
        self.clouds_sprites = pygame.sprite.Group()
        self.create_initial_clouds()
        self.time_playing = 0
        self.sun_sprite = pygame.sprite.GroupSingle()
        self.sun_sprite.add(Sun(SCREEN_WIDTH-100,110))
        self.water = Water(speed=2)
        self.game_over = False
        self.seeking_missile = pygame.sprite.GroupSingle()
        self.played_seconds = 0
        self.pause_time = 0
        self.ship_sprite = pygame.sprite.GroupSingle()
        self.score_saved = False
        self.data_scores = get_player_profile(JSON_SCORES,shared.PLAYER_NAME)
        if not self.data_scores:
            self.data_scores = create_player_profile(JSON_SCORES,shared.PLAYER_NAME)
        self.new_record = False
        self.fireworks = list()
        self.firework_index = 0
        self.start_fireworks = False
        self.fireworks_pos =[(718, 166), (854, 178), (1070, 212), (976, 386), (829, 441), (623, 377), (566, 235), (738, 150), (782, 275), (1043, 176), (1097, 166), (1025, 328), (850, 452), (596, 390), (643, 197), (864, 173), (797, 292), (1076, 176), (972, 311), (757, 416), (639, 192)]
        # cuando aparezcan nuevos los enemigos, los límites donde pueden aparecer
        self.right_side_new_enemies_x = (SCREEN_WIDTH-200,SCREEN_WIDTH-Enemy.enemy_width)
        self.left_side_new_enemies_x = (15,70)
        self.new_enemies_y = (Enemy.enemy_height,SCREEN_HEIGHT-Enemy.enemy_height) 
        self.create_initial_enemies()

    def create_initial_clouds(self):
        offset_x = 400
        for x in range(0,SCREEN_WIDTH+offset_x,offset_x):
            x,y = randint(x,offset_x), randint(0,MAX_BOTTOM_CLOUDS)
            self.clouds_sprites.add(Cloud(x,y))
            offset_x += 400

    def rand_pos_enemy(self,left_side=False):
        if left_side:
            return randint(*self.left_side_new_enemies_x),randint(*self.new_enemies_y) 
        return randint(*self.right_side_new_enemies_x),randint(*self.new_enemies_y) 

    # necesitan estar lo más a la izquierda posible o derecha, sino los misiles podrían colisionar contra los enemigos sin haber perseguido al jugador
    def rand_pos_seeking_enemy(self,left_side=False):
        if left_side:
            return self.left_side_new_enemies_x[1],randint(*self.new_enemies_y) 
        return self.right_side_new_enemies_x[0],randint(*self.new_enemies_y) 
    
    def rand_pos_protector_enemy(self,left_side=False):
        if left_side:
            return self.left_side_new_enemies_x[1],randint(ProtectorEnemy.action_ratio,SCREEN_HEIGHT-ProtectorEnemy.action_ratio) 
        return self.right_side_new_enemies_x[0],randint(ProtectorEnemy.action_ratio,SCREEN_HEIGHT-ProtectorEnemy.action_ratio) 

    def game_over_setup(self):
        if not self.score_saved:
            Podium.write_new_score(self.score,shared.PLAYER_NAME)
            self.score_saved = True
        #screen.fill('black')
        screen.fill('black')
        show_centered_text(screen,"GAME OVER!",(SCREEN_WIDTH//2,SCREEN_HEIGHT//4),Game.font_size,'white')
        offset_y = 130
        screen.blit(game_over_img,game_over_rect)
        show_centered_text(screen,"Press r to restart the game",(SCREEN_WIDTH//2,SCREEN_HEIGHT//2+offset_y),30,'white')
        show_centered_text(screen,"Press esc to come back to the menu screen",(SCREEN_WIDTH//2,SCREEN_HEIGHT//2+offset_y+40),30,'white')

    def get_time_played(self):
        # si estamos en pausa el tiempo sigue contando
        self.played_seconds = (pygame.time.get_ticks()-self.time_playing)
        return str(self.played_seconds)

    def run(self):
        
        if not self.new_record and self.score > int(self.data_scores["gold"]):
            self.start_fireworks = True
            self.new_record = True
        
        self.sun_sprite.update()
        self.sun_sprite.draw(screen)
        self.clouds_sprites.update()
        self.clouds_sprites.draw(screen)
        draw_topleft_text(screen,"Score: "+str(self.score),10,5,30,'black')
        self.water.update_amplitude()
        self.water.draw(screen)
        self.ship_sprite.update()  
        self.ship_sprite.draw(screen) 
        self.heart.update()
        self.heart.draw(screen)
        self.player.update()
        self.player.draw(screen)
        # al dibujar primero los misiles antes que los enemigos, los misiles estarán detrás de las naves enemigas
        self.enemies_missiles.update()
        self.enemies_missiles.draw(screen)
        self.enemies_with_missiles.update() # actualizamos todos los enemigos con misiles, pero no todos los enemigos ya que el enemiog de las cadenas tiene su propia forma de hacer el update
        self.enemies.draw(screen) # dibujamos todos los enemigos
        self.explosion_sprites.update()
        self.explosion_sprites.draw(screen)
        
        self.protector_enemies.update()
        for firework in self.fireworks:
            firework.update()
        for explosion in self.missiles_explosions:
            explosion.update()
        self.check_collisions()
        

    # finalizar el juego sin más?
    def setup_player_dead(self): # no se me ocurre otra manera para saber si el player esta mirando a la izquierda, de manera que la animación de la muerte mire también hacia la izquierda
        #self.player.sprite.get_input()
        self.game_over = True
        self.player.sprite.is_dead = True

    def create_initial_enemies(self):
        for _ in range(3):
            x,y = self.rand_pos_enemy()
            enemy = Enemy(x,y,choice(imgs_planes1))
            self.enemies.add(enemy)
            self.enemies_with_missiles.add(enemy)
        
        for _ in range(3):
            x,y = self.rand_pos_enemy(left_side=True)
            enemy = Enemy(x,y,choice(imgs_planes1),True)
            self.enemies.add(enemy)
            self.enemies_with_missiles.add(enemy)

    # hacerla genérica para el how to play, como está allí este método
    def shoot_enemy_missile(self):
        if self.enemies_with_missiles.sprites():
            random_enemy = choice(self.enemies_with_missiles.sprites())
            velocity = Game.missile_velocity
            x, y = random_enemy.rect.midright
            if not random_enemy.left_side:
                x, y = random_enemy.rect.midleft
                velocity *= -1
            self.enemies_missiles.add(Missile(x,y,velocity,'graphics/enemies/planes/missile/missile.png'))

    def shoot_seeking_missile(self, enemy):
         if self.enemies_with_missiles.sprites():
            x, y = enemy.rect.midleft -vec(5,0) # por si acaso, por si choca contra algún enemigo antes de perseguir al jugador
            if enemy.left_side:
                x, y = enemy.rect.midright+vec(5,0)
            seeking_missile = SeekingMissile(x,y,'graphics/enemies/planes/missile/seeking_resized.png',Game.missile_velocity,self.player,enemy.left_side)
            self.enemies_missiles.add(seeking_missile)
            self.seeking_missile.add(seeking_missile)

    def check_collisions(self):
        if not self.player.sprite.is_alive():
            self.setup_player_dead()
            return
        for enemy in self.enemies.sprites():
            # si chocamos contra una nave morimos en el acto
            if self.player.sprite.rect.colliderect(enemy):
                self.explosion_sprites.add(Explosion(enemy.rect.center))
                enemy.kill()
                self.setup_player_dead()
                return
            
            if type(enemy).__name__ == 'ProtectorEnemy':
                continue
            # comprobar si los misiles del jugador chocan contra las naves enemigas   
            if pygame.sprite.spritecollide(enemy,self.player.sprite.missiles,True):
                self.explosion_sprites.add(Explosion(enemy.rect.center))
                if type(enemy).__name__ == 'ParalyzerEnemy':
                    #print("resturar velocidad del jugador ")
                    if enemy.apply_velocity_reduction:
                        self.player.sprite.velocity += enemy.velocity_ratio
                enemy.kill()
                self.score += 1
                if type(enemy).__name__ == 'ProtectorEnemy':
                    self.score += 1
        for enemy in self.wire_enemies:
            if enemy.player_collision:
                enemy.follow_player_and_reduce_his_velocity()
            else:
                enemy.update() 
        for enemy_missile in self.enemies_missiles.sprites():
            # comprobar si alguno de los misiles de los enemigos chocan contra el jugador
            if self.player.sprite.rect.colliderect(enemy_missile):
                self.player.sprite.get_damage(enemy_missile.attack)
                self.missiles_explosions.append(MissileExplosion(self.player.sprite.rect.center,'red'))
                enemy_missile.kill()
                #return
            # comprobar si alguno de los misiles de los enemigos chocan contra los misiles del jugador
            if pygame.sprite.spritecollide(enemy_missile,self.player.sprite.missiles,True):
                self.missiles_explosions.append(MissileExplosion(enemy_missile.rect.center,'white'))
                enemy_missile.kill()
        #si la bola del cañon del barco colisiona con el jugador
        if self.ship_sprite.sprite and self.ship_sprite.sprite.ball_sprite.sprite:
            if self.player.sprite.rect.colliderect(self.ship_sprite.sprite.ball_sprite.sprite):
                self.player.sprite.get_damage(self.ship_sprite.sprite.ball_sprite.sprite.damage)
                self.ship_sprite.sprite.ball_sprite.sprite.kill()
                #return
            # comprobar si los misiles del jugador chocan contra la bola de cañón del barco
            elif pygame.sprite.spritecollide(self.ship_sprite.sprite.ball_sprite.sprite,self.player.sprite.missiles,True):
                self.ship_sprite.sprite.ball_sprite.sprite.kill()

        # comprobar si el misil que persigue al jugador choca contra alguna de las naves
        if self.seeking_missile:
            for enemy in self.enemies.sprites():
                if self.seeking_missile.sprite is not None:
                    if self.seeking_missile.sprite.rect.colliderect(enemy):
                        if type(enemy).__name__ == 'ParalyzerEnemy':
                            #print("resturar velocidad del jugador ")
                            if enemy.apply_velocity_reduction:
                                self.player.sprite.velocity += enemy.velocity_ratio
                        self.explosion_sprites.add(Explosion(self.seeking_missile.sprite.rect.center))
                        self.seeking_missile.sprite.kill()
                        self.score += 1
                        enemy.kill()
                
            # if pygame.sprite.spritecollide(self.seeking_missile.sprite,self.enemies,True):
            #     self.explosion_sprites.add(Explosion(self.seeking_missile.sprite.rect.center))
            #     self.seeking_missile.sprite.kill()
        if self.heart.sprite:
            if self.player.sprite.rect.colliderect(self.heart.sprite.rect):
                self.player.sprite.get_health(Missile.attack)
                self.heart.sprite.kill()

    def welcome_window(self):
        screen.fill(BLUE_SKY)
        show_centered_text(screen,"Press ENTER to play!",(SCREEN_WIDTH//2,SCREEN_HEIGHT//2),Game.font_size,'white')

    def add_protector_enemy_group(self, left_side=False):
        if not left_side:
            x,y= self.rand_pos_protector_enemy()
            protector_enemy = ProtectorEnemy(x,y,choice(imgs_planes2),self.player,self.enemies_missiles)
            self.enemies.add(protector_enemy)
            self.protector_enemies.add(protector_enemy)
        else:
            x,y= self.rand_pos_protector_enemy(left_side=True)
            protector_enemy = ProtectorEnemy(x,y,choice(imgs_planes2),self.player,self.enemies_missiles,left_side=True)
            self.enemies.add(protector_enemy)
            self.protector_enemies.add(protector_enemy)

    def add_paralyzer_enemy_group(self,left_side=False):
        if not left_side:
            x,y = self.rand_pos_enemy()
            enemy = ParalyzerEnemy(x,y,choice(imgs_planes3),self.player.sprite)
            self.enemies.add(enemy)
            self.wire_enemies.add(enemy)
        else:
            x,y = self.rand_pos_enemy(left_side=True)
            enemy = ParalyzerEnemy(x,y,choice(imgs_planes3),self.player.sprite,True)
            self.enemies.add(enemy)
            self.wire_enemies.add(enemy)

    # uno por cada lado, máximo 2 para que no se solapen
    # TODO: hacerla genérica, para no repetir código con paralyzer enemy
    def add_protector_enemy(self):
        size = len(self.protector_enemies.sprites())
        if size < 2: # limitar estos enemigos a dos en cada lado, para que no se solapen, sería raro pero puede ocurrir...
            if not size:
                n = randint(0,1)
                if not n:
                    self.add_protector_enemy_group()
                else:
                    self.add_protector_enemy_group(left_side=True)
            else:
                # si está en la izquierda lo ponemos a la derecha y viceversa
                left_side = [spr.left_side for spr in self.protector_enemies.sprites()][0]
                if left_side:
                    self.add_protector_enemy_group()
                else:
                    self.add_protector_enemy_group(left_side=True)

    # uno por cada lado, máximo 2 para que no se solapen, este es un enemigo que no se mueve
    def add_paralyzer_enemy(self):
        size = len(self.wire_enemies.sprites())
        if size < 2: # limitar estos enemigos a dos en cada lado, para que no se solapen, sería raro pero puede ocurrir...
            if not size:
                n = randint(0,1)
                if not n:
                    self.add_paralyzer_enemy_group()
                else:
                    self.add_paralyzer_enemy_group(left_side=True)
            else:
                # si está en la izquierda lo ponemos a la derecha y viceversa
                left_side = [spr.left_side for spr in self.wire_enemies.sprites()][0]
                if left_side:
                    self.add_paralyzer_enemy_group()
                else:
                    self.add_paralyzer_enemy_group(left_side=True)

# error prone
SHOOT_MISSILE = pygame.USEREVENT+1
ADD_ENEMY_RIGHT_SIDE = pygame.USEREVENT+2
ADD_CLOUD = pygame.USEREVENT+3
SHOOT_SHIP_CANNONBAL = pygame.USEREVENT+4
ADD_SHIP = pygame.USEREVENT+5
ADD_ENEMY_LEFT_SIDE = pygame.USEREVENT+6
ADD_FIREWORK = pygame.USEREVENT+7
WIRE_ENEMIES = pygame.USEREVENT+8
ADD_HEART = pygame.USEREVENT+9

# FIXME: por si quiero modificarlos para la jugabilidad
pygame.time.set_timer(SHOOT_MISSILE,500) # cuánto más bajo más difícil es el juego
pygame.time.set_timer(ADD_ENEMY_LEFT_SIDE,3000)
pygame.time.set_timer(ADD_CLOUD,1500)
pygame.time.set_timer(ADD_ENEMY_RIGHT_SIDE,2000) 
pygame.time.set_timer(ADD_SHIP,5*1000) 
pygame.time.set_timer(SHOOT_SHIP_CANNONBAL,1000)
pygame.time.set_timer(ADD_FIREWORK,610)
pygame.time.set_timer(WIRE_ENEMIES,2500) # cuando se lanza el cable se tiene que completar hasta que llega al destino, cuánto tiempo tiene que pasar para volver a lanzar el cable
pygame.time.set_timer(ADD_HEART,randint(25000,30000)) # FIXME jugabilidad

MAX_BOTTOM_CLOUDS = SCREEN_HEIGHT-500
def main():
    print("yes",shared.PLAYER_NAME)
    pause = False
    game_action = False
    game = Game()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # if event.key == pygame.K_r: # probar la pantalla de game over
                #     game.game_over = True
                #     break
                if event.key == pygame.K_ESCAPE: # volver atrás
                    return
                if event.key == pygame.K_r and game.game_over: # reinciar el juego
                    game = Game()
                if event.key == pygame.K_p and game_action and not game.game_over:
                    pause = not pause
                if event.key == pygame.K_RETURN:
                    game_action = True
                if event.key == game.player.sprite.keys_dict["shoot"]:
                    game.player.sprite.shoot_key_pressed = True

            # if event.type == pygame.KEYUP:
            #     if event.key == game.player.sprite.keys_dict["shoot"]: # no haría falta porque ya se pone a false en la clase Player
            #         game.player.sprite.shoot_key_pressed = False
            if event.type == pygame.MOUSEBUTTONDOWN: # probar protector enemy
                if game.player.sprite.missiles:
                    game.player.sprite.missiles.sprites()[-1].kill()
           
            if not pause and game_action and not game.game_over:
                if event.type == SHOOT_MISSILE:
                    game.shoot_enemy_missile()
                # the worst part
                if len(game.enemies.sprites()) < MAX_NUMBER_OF_ENEMIES:
                    if event.type == ADD_ENEMY_RIGHT_SIDE:
                        num = choice([3,4,4]) 
                        if game.score > randint(20,30): # FIXME
                            num = choice([0,1,2])
                        if game.score > randint(30,45):
                            num = choice([0,1,2,3,4])
                        if not num:
                            x,y = game.rand_pos_seeking_enemy()
                            enemy = Enemy(x,y,choice(imgs_planes1))
                            game.enemies.add(enemy)
                            game.enemies_with_missiles.add(enemy) 
                            if not game.seeking_missile:
                                game.shoot_seeking_missile(enemy)
                        elif num == 1 : # protector enemy
                           game.add_protector_enemy()
                                
                        elif num == 2:
                            game.add_paralyzer_enemy()
                        elif num == 3:
                            x,y = game.rand_pos_enemy()
                            enemy = Enemy(x,y,choice(imgs_planes1))
                            game.enemies.add(enemy)
                            game.enemies_with_missiles.add(enemy)
                        else:
                            x,y = game.rand_pos_enemy()
                            enemy = CleverEnemy(x,y,choice(imgs_planes1),game.player,game.enemies_missiles,Game.missile_velocity)
                            game.enemies.add(enemy)
                            game.enemies_with_missiles.add(enemy)

                    if event.type == ADD_ENEMY_LEFT_SIDE:
                        num = choice([3,4,4])
                        if game.score > randint(20,30): # FIXME
                            num = choice([0,1,2])
                        if game.score > randint(30,45):
                            num = choice([0,1,2,3,4])
                        if not num:
                            left_side = True
                            x,y = game.rand_pos_seeking_enemy(left_side)
                            enemy = Enemy(x,y,choice(imgs_planes1),left_side)
                            game.enemies.add(enemy)
                            game.enemies_with_missiles.add(enemy) 
                            if not game.seeking_missile:
                                game.shoot_seeking_missile(enemy)
                        elif num == 1:
                            game.add_protector_enemy()
                        elif num == 2:
                            game.add_paralyzer_enemy()
                        elif num == 3:
                            x,y = game.rand_pos_enemy(left_side=True)
                            enemy = Enemy(x,y,choice(imgs_planes1),left_side=True)
                            game.enemies.add(enemy)
                            game.enemies_with_missiles.add(enemy)
                        else:
                            x,y = game.rand_pos_enemy(left_side=True)
                            enemy = CleverEnemy(x,y,choice(imgs_planes1),game.player,game.enemies_missiles,Game.missile_velocity,left_side=True)
                            game.enemies.add(enemy)
                            game.enemies_with_missiles.add(enemy)

                if game.score > randint(30,40): # FIXME: JUGABILIDAD
                    if game.ship_sprite.sprite is None:
                        game.ship_sprite.add(Ship((-250,100),screen,game.water,game.player.sprite))
                if event.type == SHOOT_SHIP_CANNONBAL:
                     if game.ship_sprite.sprite:
                         game.ship_sprite.sprite.shoot_cannonball()
                if event.type == ADD_HEART:
                    if not game.heart:
                        game.heart.add(Heart((randint(330,SCREEN_WIDTH-330),randint(200,SCREEN_HEIGHT-250))))
                if event.type == ADD_CLOUD:
                    x,y = randint(SCREEN_WIDTH,SCREEN_WIDTH+300), randint(0,MAX_BOTTOM_CLOUDS)
                    game.clouds_sprites.add(Cloud(x,y))
                if event.type == ADD_FIREWORK and game.start_fireworks:
                    game.fireworks.append(Firework(game.fireworks_pos[game.firework_index],choice(['red','purple','blue','green','violet'])))
                    game.firework_index += 1
                    if game.firework_index == len(game.fireworks_pos):
                        game.start_fireworks = False
                if event.type == WIRE_ENEMIES:
                    for enemy in game.wire_enemies.sprites():
                        if not enemy.player_collision and not enemy.collecting_chain and enemy.finished:
                            enemy.player_rect = game.player.sprite.rect.copy()
                            enemy.offset = 0
                            enemy.awaiting_orders = False
                            enemy.finished = False

        if not game_action:
            game.welcome_window()
        elif game.game_over:
            game.game_over_setup()
        elif not pause:
            screen.fill(BLUE_SKY)
            game.run()
        elif pause:
            show_centered_text(screen,"PAUSE",(SCREEN_WIDTH//2,SCREEN_HEIGHT//2),60,'black')
        #debug(game.player.sprite.velocity)
        pygame.display.update()
        
        clock.tick(FPS)
#main()
