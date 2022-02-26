import sys
from math import sin,atan2,degrees,cos,radians
import pygame
from utils import *
from pygame.locals import *
from player import Player
from colors import *

pygame.init()
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

class Water:
    MIN_AMPLITUDE = 2
    MAX_AMPLITUDE = 35
    def __init__(self, y = SCREEN_HEIGHT-170):
        self.amplitude = Water.MAX_AMPLITUDE # MIN_AMPLITUDE
        self.move_x = 0
        self.speed = 2
        self.min_x = -300
        self.watter_levels =   {i:0 for i in range(self.min_x,SCREEN_WIDTH) } # usar dictionary
        self.y = y
        self.increment_amplitude = 0.1
        
    def draw(self, surface):
        for x in range(self.min_x,SCREEN_WIDTH):
            y = sin((x+self.move_x)*0.01) * self.amplitude+self.y
            self.watter_levels[x] = y
            pygame.draw.line(surface,WATER_COLOR,(x,round(y)),(x,SCREEN_HEIGHT))

    def update(self):
        self.move_x += self.speed # como si el barco estuviera navegando a la deriva
        self.amplitude += self.increment_amplitude
        if self.amplitude >= Water.MAX_AMPLITUDE or self.amplitude <= Water.MIN_AMPLITUDE:
            self.increment_amplitude *= -1

    def get_water_level(self,index):
        # assert index in self.watter_levels
        if index >= SCREEN_WIDTH:
            return self.watter_levels[-1]
        return self.watter_levels[index]

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
        self.move = pygame.math.Vector2(x,y)
        self.speed = (speed*cos(radians(self.angle)), -speed*sin(radians(self.angle)))
        
    def destroy(self):
        if self.rect.y < -20 or self.rect.right > SCREEN_WIDTH+20:
            self.kill()

    def update(self):
        self.move.x += self.speed[0]
        self.move.y += self.speed[1]
        self.rect.topleft = round(self.move.x),round(self.move.y)
        self.destroy()


class Game:
    def __init__(self):
        self.player = pygame.sprite.GroupSingle()
        self.player.add(Player(SCREEN_WIDTH//2,SCREEN_HEIGHT//2))
        self.water = Water()
        self.ship_sprite = pygame.sprite.GroupSingle()
        

    def update(self):
        # self.player.update()
        # self.player.draw(screen)
        #self.water.update()
        self.water.draw(screen)
        self.ship_sprite.update()
        self.ship_sprite.draw(screen) 

game = Game()
CANNONBALL = pygame.USEREVENT+1
pygame.time.set_timer(CANNONBALL,2000)

while True:
    screen.fill((200,210,255,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == pygame.K_s:
                game.ship_sprite.sprite.shoot_cannonball()
            if event.key == pygame.K_a:
                game.ship_sprite.add(Ship((-150,100),screen,game.water,game.player.sprite))
    #debug(str(pygame.mouse.get_pos()),600)
    game.update()
    clock.tick(60)
    pygame.display.update()