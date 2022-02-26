from random import uniform
import pygame
from colors import *
from settings import *
from utils import *
from math import *
from missile import *

class Enemy(pygame.sprite.Sprite):
    enemy_height = 32
    enemy_width = 55
    def __init__(self, x,y, img_path, left_side=False):
        super().__init__()
        self.left_side = left_side
        self.attack = 10
        self.vi = uniform(5,6.5)
        self.in_combat = True
        self.image = load_image(img_path)
        if not self.left_side: # right side so it's facing left
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(bottomleft=[x,y])
        self.pos = self.rect.y

    def move(self):
        self.pos += self.vi
        self.rect.y = int(self.pos)
        if self.rect.bottom > SCREEN_HEIGHT or self.rect.top < 0:
            self.vi *= -1

    def update(self):
        self.move()
       
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
            ran = randint(0,1) # para que el jugador no campé
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
    
# este enemigo no puedo ser destruido salvo por el misil que persigue al jugador
class ProtectorEnemy(Enemy):
    action_ratio = 120
    def __init__(self, x,y, img_path, player,enemy_missiles, left_side=False):
        super().__init__(x,y, img_path,left_side)
        self.player_spr = player.sprite
        self.left_side = left_side
        self.enemy_missiles = enemy_missiles
        self.player_missiles = player.sprite.missiles
        self.missile_velocity = self.player_spr.missile_velocity-1
        self.max_player_missiles_destroyed_at_time = 500
        self.destroyed = 0
        self.pretend_to_destroy = pygame.sprite.Group()
        self.pos = self.rect.y
        self.start_time = 0
        self.vi = 5
        self.duration = 3 # duracion en segundos para volver a destruir los misiles del jugador
        self.ratio = (y-ProtectorEnemy.action_ratio,y+ProtectorEnemy.action_ratio) # ratio de accion para destruir los misiles del jugador sino si el enemigo está arriba de todo en la pantalla y el jugador abajo del todo, los misiles de este enemigo tiene que recorrer mucho espacio y queda muy poco real

    def shoot_missile(self, target_missile):
        x, y = self.rect.bottomright
        if not self.left_side:
            x, y = self.rect.bottomleft
        self.enemy_missiles.add(GuidedMissile(x,y,self.missile_velocity,'graphics/enemies/planes/missile/missile.png',target_missile,self.player_spr))
    
    def move(self):
        self.pos += self.vi
        self.rect.y = int(self.pos)
        if self.rect.bottom > self.ratio[1] or self.rect.top < self.ratio[0]:
            self.vi *= -1

    def update(self):
        self.move()
        # pygame.draw.line(screen,'blue',self.rect.center,self.rect.center-vec(0,25))
        # pygame.draw.circle(screen,'blue',self.rect.center-vec(0,30),6,1)
        if self.player_missiles:  
            if self.destroyed >= self.max_player_missiles_destroyed_at_time:
                if not self.start_time:
                    self.start_time = pygame.time.get_ticks()
                if (pygame.time.get_ticks() - self.start_time)/1000 >= self.duration:
                    #print("se termino la espera")
                    self.destroyed = 0
                    self.start_time = 0
            for target_missile in self.player_missiles.sprites():
                # if target_missile.rect.colliderect(self.rect): # por si acaso, podría ocurrir que justo un misil colisiona con el enemigo cuando el enemigo justo va a lanzar el misil de destruccion de los misiles del jugador
                #     self.kill()
                if self.destroyed >= self.max_player_missiles_destroyed_at_time:
                    #print("no puedo!")
                    break
                #print("ahora si puedo")
                if self.ratio[0] <= target_missile.rect.y <= self.ratio[1] and ((not self.left_side and target_missile.rect.right < self.rect.left) or (self.left_side and target_missile.rect.left > self.rect.right)):
                    if target_missile in self.pretend_to_destroy or (self.left_side and target_missile.velocity > 0) or (not self.left_side and target_missile.velocity < 0):
                        continue
                    self.pretend_to_destroy.add(target_missile)
                    self.shoot_missile(target_missile)
                    self.destroyed += 1

class ParalyzerEnemy(Enemy):
    def __init__(self, x,y, img_path,player,left_side=False):
        super().__init__(x,y,img_path,left_side)
        self.player = player
        self.effect_duration = 0
        self.effect_interval = 4000
        self.player_rect = self.player.rect.copy()
        self.player_collision = False
        self.velocity_percentage = 0.33
        self.apply_velocity_reduction = False
        self.collecting_chain = False
        self.velocity_ratio = 0
        self.radius = 6
        self.player_vec = vec(self.player_rect.center)
        self.offset = 0 # ir dibujando la cadena
        self.offset_interval = 20
        self.offset_duration = 0
        self.awaiting_orders = False
        self.finished = False
        self.enemy_vec = vec(self.rect.bottomleft)
        self.enemy_vec.update(self.enemy_vec.x+15,self.enemy_vec.y-4) # adjust position
        if self.left_side:
            self.enemy_vec = vec(self.rect.bottomright)
            self.enemy_vec.update(self.enemy_vec.x-15,self.enemy_vec.y-4) # adjust position
    
    def collision_with_player(self):
        player_corners = [self.player.rect.bottomright,self.player.rect.bottomleft,self.player.rect.topright,self.player.rect.topleft,]
        if self.player.rect.collidepoint(self.player_vec) or any(pygame.math.Vector2(self.player_vec).distance_to(p) <= self.radius for p in player_corners):
            self.player_collision = True

    # obtener un vector pero con una longitud más corta, sería como obtener un triángulo semejante a otro, todo esto para dibujar ir dibujando la línea a trozos
    def update(self):  
        if self.awaiting_orders:
            # hubo colision con el jugador y se le redujo la velocidad
            #print("awaiting orders, sir")
            self.finished = True
            return          
        if not self.offset_duration:
            self.offset_duration = pygame.time.get_ticks()
        if pygame.time.get_ticks()-self.offset_duration > self.offset_interval:
            if self.collecting_chain:
                self.offset -= 25
                if self.offset <= 0:
                    self.collecting_chain = False
                    self.awaiting_orders = True
                    return
            else:
                self.offset += 45
                if self.offset >= SCREEN_WIDTH:
                    self.offset = SCREEN_WIDTH
            self.offset_duration = 0
        self.player_vec = pygame.math.Vector2(self.player_rect.center)
        vec_dir = pygame.math.Vector2(self.player_vec-self.enemy_vec)
        start_len = vec_dir.length()
        final_len = min(start_len,self.offset)
        if final_len >= start_len:
            self.finished = True
        ratio = final_len / start_len
        self.player_vec.x = self.enemy_vec.x + (self.player_vec.x - self.enemy_vec.x) * ratio
        self.player_vec.y = self.enemy_vec.y + (self.player_vec.y - self.enemy_vec.y) * ratio
        self.draw_trap()
        if not self.collecting_chain:
            self.collision_with_player()
    
    def draw_trap(self):
        pygame.draw.line(screen, 'black', self.enemy_vec, self.player_vec, 2)
        pygame.draw.circle(screen,'red', self.player_vec, self.radius)        

    def restore_player_velocity(self):
        if not self.collecting_chain:
            self.apply_velocity_reduction = False
            self.player.velocity += self.velocity_ratio
            self.player_collision = False
            self.collecting_chain = True
            self.player_rect = self.player.rect.copy()
            self.effect_duration = 0

    def reduce_player_velocity(self):
        if not self.apply_velocity_reduction:
            self.velocity_ratio = self.player.velocity*self.velocity_percentage
            self.player.velocity -= self.velocity_ratio
            self.apply_velocity_reduction = True

    def follow_player_and_reduce_his_velocity(self):
        if not self.effect_duration:
            self.effect_duration = pygame.time.get_ticks()
        if pygame.time.get_ticks()-self.effect_duration >= self.effect_interval:
            self.restore_player_velocity()
            return
        self.reduce_player_velocity()
        self.player_vec = pygame.math.Vector2(self.player.rect.center)
        self.draw_trap()


class Ship(pygame.sprite.Sprite):
    def __init__(self, posi,surface, water, plane):
        super().__init__()
        self.surface = surface
        self.animation_index = 0
        self.animations = load_folder_images('graphics/enemies/boat')
        for ind in range(len(self.animations)):
            self.animations[ind] = pygame.transform.flip(self.animations[ind], True, False)
        self.image = self.animations[0]
        self.rect = self.image.get_rect(topleft = posi)
        self.copy_imgs = [img.copy() for img in self.animations  ]
        self.copy_rect = pygame.Rect(self.rect)
        self.velocity = 4
        self.shoot = False
        self.water = water # referencia a la instancia water
        self.shoot_angle = 0
        self.plane = plane
        self.pos = vec(0,0)
        self.ball_speed = 8
        self.ball_sprite = pygame.sprite.GroupSingle()

    def rotate(self, angle):
        
        self.image = pygame.transform.rotozoom(self.copy_imgs[int(self.animation_index)], round(angle),1)
        self.rect = self.image.get_rect(center = (self.copy_rect.center))

    def update(self):
        if self.rect.x < 300:
            self.copy_rect.x += 1 
        #self.get_input()
        #self.draw_trajectory(self.shoot_angle)
        self.ball_sprite.update()
        self.ball_sprite.draw(self.surface)
        #debug("shoot angle: "+str(self.shoot_angle))
        self.copy_rect.bottom = round(self.water.get_water_level(self.copy_rect.centerx)) # dirty offset que no haya huecos entre el mar y el barco
        left_y = self.water.get_water_level(self.copy_rect.left)
        right_y = self.water.get_water_level(self.copy_rect.right)
        self.image = self.animations[int(self.animation_index)]
        self.animation_index = (self.animation_index+0.15)%len(self.animations)
        angle = degrees(atan2(left_y-right_y, self.image.get_width()))
        self.rotate(angle)
    
    def update_shoot_angle(self):
        plane_x, plane_y = self.plane.rect.center
        self.pos = self.copy_rect.midbottom  
        boat_x, boat_y = self.pos
        angle = degrees(atan2(boat_y-plane_y,plane_x-boat_x))
        self.shoot_angle = angle

    def shoot_cannonball(self):
        if self.ball_sprite.sprite is None:
            self.update_shoot_angle()
            self.pos = self.copy_rect.midbottom  
            boat_x, boat_y = self.pos
            self.ball_sprite.add(Ball(boat_x,boat_y-20,self.shoot_angle,self.ball_speed))
        
    def draw_trajectory(self, angle):
        self.update_shoot_angle()
        velocity = (self.ball_speed*cos(radians(angle)), self.ball_speed*sin(radians(angle)))
        x, y = self.pos
        points = [[x,y]]
        for _ in range(250):
            x += velocity[0]
            y -= velocity[1]
            points.append([x,y])
        pygame.draw.lines(self.surface,(255,0,0),False,points) # surface, color, closed, points, width=1

    def get_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.copy_rect.x -= self.velocity
        if keys[pygame.K_RIGHT]:
            self.copy_rect.x += self.velocity
        # if self.copy_rect.left <= 0:
        #     self.copy_rect.left = 0
        # if self.copy_rect.right >= SCREEN_WIDTH:
        #     self.copy_rect.right = SCREEN_WIDTH

class Ball(pygame.sprite.Sprite):
    def __init__(self,x,y,angle, speed):
        super().__init__()
        self.image = load_image('graphics/enemies/cannonball.png')
        self.rect = self.image.get_rect(midbottom=(x,y))
        self.angle = angle
        self.damage = 10
        self.move = pygame.math.Vector2(x,y)
        self.speed = (speed*cos(radians(self.angle)), -speed*sin(radians(self.angle)))
        
    def destroy(self):
        if self.rect.y < -20 or self.rect.right > SCREEN_WIDTH+20 or self.rect.x < -20:
            self.kill()

    def update(self):
        self.move.x += self.speed[0]
        self.move.y += self.speed[1]
        self.rect.topleft = round(self.move.x),round(self.move.y)
        self.destroy()

# seeking missile