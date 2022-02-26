import pygame
from math import sin
from settings import *
from utils import *
from missile import Missile
from health_bar import HealthBar
# movimiento diagonal disparar solo una vez aunque se tenga pulsado el espacio, como esto afectaría al archivo json
class Player(pygame.sprite.Sprite):
    def __init__(self,x=SCREEN_WIDTH//3,y=SCREEN_HEIGHT//2):
        super().__init__()
        self.missile_velocity = 12
        self.velocity = 6.9
        self.fly_animations = load_folder_images('graphics/player/Plane/fly')
        self.image = self.fly_animations[0]
        self.launched_missiles = 0
        self.rect = self.image.get_rect(center=(x,y))
        self.pos = self.rect.center
        self.offset_health_bar_y = 12
        self.health_bar = pygame.sprite.GroupSingle()
        player_x, player_y = self.rect.midtop
        self.health_bar.add(HealthBar(player_x,player_y-self.offset_health_bar_y,self.image.get_width()))
        self.invincible = False
        self.direction = pygame.math.Vector2(0,0)
        self.fly_animation_index = self.attack_animation_index = 0
        self.missiles = pygame.sprite.Group()
        self.hurt_time = 0
        # TODO: add a new animations is a tedious process and error prone...
        self.attack_animations = load_folder_images('graphics/player/Plane/shoot')
        self.shooting = False
        self.flip = False
        self.is_dead = False
        self.invincibility = True
        self.shoot_duration = 0
        self.shoot_interval = 220
        self.shoot_key_pressed = False
        self.keys_dict = read_json(JSON_PLAYER_CONTROLS) # TODO si el archivo no existe?
        #print(self.keys_dict)
        for key in self.keys_dict.keys():
            self.keys_dict[key] = pygame.key.key_code(self.keys_dict[key])
            #print(pygame.key.key_code(key))
        #assert len(self.keys_dict)
        

    def wave_value(self):
        value = sin(pygame.time.get_ticks())
        if value >= 0:
            return 255
        return 0
    
    def is_alive(self):
        return self.health_bar.sprite.current_health > 0

    def keyboard_events(self):
        keys = pygame.key.get_pressed()
        self.direction = vec(0,0)
        if keys[self.keys_dict["left"]]:
            self.direction.x = -self.velocity
        elif keys[self.keys_dict["right"]]:
            self.direction.x = self.velocity
        if keys[self.keys_dict["up"]]:
            self.direction.y = -self.velocity
        elif keys[self.keys_dict["down"]]:
            self.direction.y = self.velocity
        if self.direction.x and self.direction.y: # movimiento diagonal
            self.direction *=.7071
        if keys[self.keys_dict["flip"]]: # darse la vuelta para los enemigos que atacan por la izquierda
            self.flip = True
        if self.shoot_key_pressed and not self.shooting and (pygame.time.get_ticks()-self.shoot_duration) > self.shoot_interval:
            self.shooting = True
            self.shoot_duration = pygame.time.get_ticks()
            self.shoot_key_pressed = False

    def move(self):
        self.pos += self.direction
        self.rect.topleft = self.pos
    
    def check_boundaries(self):
        if self.rect.x < 0:
            self.rect.x = 0
            self.pos.x = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.pos.x = self.rect.x
        if self.rect.y-self.health_bar.sprite.height-self.offset_health_bar_y <= 0:
            self.rect.y = self.health_bar.sprite.height+self.offset_health_bar_y
            self.pos.y = self.rect.y
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.pos.y = self.rect.y

    def draw_health_bar(self):
        player_x, player_y = self.rect.midtop
        self.health_bar.sprite.rect.center = player_x,player_y-self.offset_health_bar_y
        self.health_bar.update()
        self.health_bar.draw(screen)

    def get_damage(self, attack):
        self.health_bar.sprite.get_damage(attack)
        # if not self.invincible:
        #     self.health_bar.sprite.get_damage(attack)
        #     self.invincible = True
        #     self.hurt_time = pygame.time.get_ticks() 
    
    def get_health(self, health):
        self.health_bar.sprite.get_health(health)

    def invincibility_timer(self):
        if self.invincible:
            if pygame.time.get_ticks() - self.hurt_time >= 2000:
                self.invincible = False

    def animate(self):
        # if self.invincibility:
        #     self.image.set_alpha(80)
        if self.shooting:
            if self.attack_animation_index >= len(self.attack_animations):
                self.attack_animation_index = 0    
            self.image = self.attack_animations[int(self.attack_animation_index)]
            self.attack_animation_index += 0.1
            x, y = self.rect.bottomright
            if self.flip:
                x,y = self.rect.bottomleft
            self.launched_missiles += 1
            # 1 pixel hace la diferencia, antes 12 ahora 11, para que el jugador no campé
            self.missiles.add(Missile(x,y-11,-self.missile_velocity if self.flip else self.missile_velocity,'graphics/player/missile/bullet.png'))
            if len(self.missiles.sprites()) > 1: # FIXME si lanzo varios misiles en la misma direccion se juntan y queda muy mal
                pass
                #print(self.missiles.sprites()[-1].rect.y,self.missiles.sprites()[-2].rect.y) # aqui esta el problema
            self.shooting = False
        else:
            if self.fly_animation_index >= len(self.fly_animations):
                self.fly_animation_index = 0
            self.image = self.fly_animations[int(self.fly_animation_index)]
            self.fly_animation_index += 0.1
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)
            self.flip = False

    def dead_animation(self):
        self.image.set_alpha(self.wave_value()) # para que parpadé la imagen

    def update(self):
        # if not self.is_alive():
        #     self.dead_animation()
        #     return
        self.keyboard_events()
        self.move()
        self.animate()
        self.check_boundaries()
        self.draw_health_bar()
        self.missiles.update()
        self.missiles.draw(screen)
        #self.invincibility_timer()
