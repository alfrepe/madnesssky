import pygame
from settings import *
from utils import *
from missile_smoke import Smoke
vec = pygame.math.Vector2

# TODO: en lugar de velocity con left_side para que SeekingMissile pueda heredar
class Missile(pygame.sprite.Sprite):
    attack = 10
    def __init__(self, x,y,velocity, img):
        super().__init__()
        self.velocity = velocity
        self.attack = Missile.attack
        self.image = load_image(img)
        if self.velocity < 0:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(center=[x,y])
        self.pos = vec(self.rect.center)
        self.acc = 0 # una pequeña aceleracion al principio?

    def destroy(self):
        if self.rect.left <= -50 or self.rect.right >= SCREEN_WIDTH+50:
            self.kill()

    def move(self):
        self.pos.x += self.velocity+self.acc
        self.rect.centerx = round(self.pos.x)

    def update(self):
        self.move()
        self.destroy()


class GuidedMissile(Missile):
    def __init__(self,x,y,velocity, img, main_target, secondary_target):
        super().__init__(x,y,velocity, img)
        self.main_target = main_target
        self.secondary_target = secondary_target
        self.pos = vec(self.rect.center)
        self.vel = vec(self.velocity)
        self.copy_img = self.image.copy()
        self.follow_secondary_target = False
        self.target = main_target.rect.copy() # hacer una copia del rectangulo, si el misil que el jugador disparó muere demasiado rápido el misil de lo contrario permanecería quieto
        # self.image = pygame.transform.rotozoom(self.image,rotation,1)
        # self.rect = self.image.get_rect(center=[x,y])

    def follow_target(self):
        # self.target.rect.center
        if not self.main_target.alive(): # si el misil que intentabamos eliminar fue eliminado por otro misil, seguimos con la dirección que teníamos, pero esto queda bastante artificial y extraño en el juego porque los misiles, la mayoría son horizontales
            return
        
        target_pos = vec(self.main_target.rect.center)        
        # if self.follow_secondary_target:
        #     target_pos = vec(self.secondary_target.rect.center)
         # pygame.mouse.get_pos()
        self.target = (target_pos-self.pos).normalize() # cuánto mayor es el valor menos tarda en darse la vuelta, pasar de aceleracion positiva a negativa o viceversa
        
        ang = self.target.angle_to(vec(1,0))
        #print(ang)
        self.image = pygame.transform.rotozoom(self.copy_img,ang,1) # use rotoozom it provides better results when rotating the image
        self.rect = self.image.get_rect(center=self.pos)

    def destroy(self):
        if self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT or self.rect.left <= -50 or self.rect.right >= SCREEN_WIDTH+50:
            self.kill()

    def move(self):
        self.follow_target()
        if self.target:
            self.pos.x += self.target.x*self.vel.x
            self.pos.y += self.target.y*self.vel.y
            self.rect.center = self.pos
        

class SeekingMissile(pygame.sprite.Sprite):
    def __init__(self, x,y, img_path, velocity, player,left_side=False):
        super().__init__()
        self.smoke = Smoke()
        self.attack = Missile.attack
        self.image = load_image(img_path)
        self.left_side = left_side
        self.player = player
        self.max_speed = velocity
        self.seek_force = 0.1 # con 0.2 se nota diferencia
        self.is_dead = False
        self.pos = vec(x,y)
        self.acc = vec(0, 0)
        self.vel = vec(self.max_speed, 0)
        self.rect = self.image.get_rect(midleft=self.pos)
        if not self.left_side:
            self.image = pygame.transform.flip(self.image,True,False)
            self.vel = vec(-self.max_speed, 0)
            self.rect = self.image.get_rect(midright=self.pos)
        self.copy_img = self.image.copy()

    # rotate at a fixed position
    def blitRotate(self, originPos, angle):

        image_rect = self.copy_img.get_rect(topleft = vec(self.pos.x-originPos[0],self.pos.y-originPos[1]))
        offset_center_to_pivot = pygame.math.Vector2(self.pos) - image_rect.center
        
        # roatated offset from pivot to center
        rotated_offset = offset_center_to_pivot.rotate(-angle)

        # roatetd image center
        rotated_image_center = (self.pos.x - rotated_offset.x, self.pos.y - rotated_offset.y)

        # get a rotated image
        self.image = pygame.transform.rotozoom(self.copy_img, angle,1)
        self.rect = self.image.get_rect(center = rotated_image_center)
        

    def seek(self, target):
        self.desired = (target-self.pos).normalize()*self.max_speed
        steer = vec(self.desired - self.vel)
        if steer.length() > self.seek_force:
            steer.scale_to_length(self.seek_force)
        return steer

    def destroy(self):
        if self.rect.x < -20 or self.rect.x > SCREEN_WIDTH+20 or self.rect.y < -20 or self.rect.y > SCREEN_HEIGHT+20:
            self.is_dead = True
            self.kill()

    def update(self):
        #self.destroy()
        if self.is_dead:
            return
        
        self.acc = self.seek(self.player.sprite.rect.center) 
        self.vel += self.acc
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)
        
        self.pos += self.vel
        ang = self.desired.angle_to(vec(1,0))
        if not self.left_side:
            ang = self.desired.angle_to(vec(-1,0))

        if self.left_side:
            self.blitRotate((2, 5),ang)
        else:
            self.blitRotate((22, 5),ang)
        self.smoke.add_smoke_left(self.pos)
        self.smoke.draw()  