import pygame
from random import *
import sys
from settings import *
from utils import *

class Particle():
    def __init__(self, pos, vel, radius, color, gravity=None):
        self.pos = vec(pos)
        self.radius = radius
        self.image = pygame.Surface((self.radius*2,self.radius*2),pygame.SRCALPHA)
        #self.image.fill('white')
        self.rect = self.image.get_rect(center=pos)
        self.vel = vec(vel)
        self.opacity = 255
        self.color = (*color,self.opacity)
        self.gravity = gravity
        pygame.draw.circle(self.image, self.color, (self.radius,self.radius), self.radius)

    def render(self):
        
        self.pos += self.vel
        if self.gravity != None:
            self.vel.y += self.gravity
        
        self.rect.center = self.pos
        screen.blit(self.image,self.rect.center)

class Smoke():
    def __init__(self) -> None:
        self.particles = []

    def add_smoke_left(self, pos,):
        if len(self.particles) < randint(10,15):
            particle = Particle(pos, [randint(-4,-2), uniform(-0.5,0.5) ], randint(3, 5) ,[169, 169, 169])
            self.particles.append(particle)

    def add_smoke_right(self, pos):
        if len(self.particles) < randint(10,15):
            particle = Particle(pos, [randint(3,6), uniform(-0.5,0.5) ], randint(3, 5) ,[169, 169, 169])
            self.particles.append(particle)
    
    def add_smoke_down(self, pos):
        if len(self.particles) < randint(10,15):
            particle = Particle(pos, [uniform(-0.5,0.5), uniform(1,5) ], randint(3, 5) ,[169, 169, 169])
            self.particles.append(particle)

    def add_smoke_up(self, pos):
        if len(self.particles) < randint(10,15):
            particle = Particle(pos, [uniform(-0.5,0.5), uniform(-5,-1) ], randint(3, 5) ,[169, 169, 169])
            self.particles.append(particle)

    def add_smoke(self, pos):
        if len(self.particles) < randint(10,15):
            particle = Particle(pos, [uniform(-1,1), uniform(-0.5,0.5) ], randint(3, 5) ,[169, 169, 169])
            self.particles.append(particle)

    def draw(self):
        for particle in self.particles:
            particle.render()
            particle.opacity -= 10
            particle.image.set_alpha(particle.opacity)
            if particle.opacity <= 0:
                self.particles.remove(particle)

if __name__ == '__main__':
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption("Particles")
    
    missile_img = load_image('graphics\enemies\planes\missile\missile31x17.png')
    missile_img = pygame.transform.rotate(missile_img,270)
    #missile_img = pygame.transform.flip(missile_img,True,False)
    missile_rect = missile_img.get_rect(topleft=(300,300))
    smoke = Smoke()
    while True:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    pass

        screen.fill('black')
        screen.blit(missile_img,missile_rect)
        #pos = missile_rect.midleft-vec(2,2)
        #pos = missile_rect.midbottom-vec(2,2)
        pos = missile_rect.midbottom-vec(3,26)
        smoke.add_smoke_up(pos)
        #smoke.add_smoke_right(pos+vec(28,0))
        smoke.draw()
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            missile_rect.x += 6
        if keys[pygame.K_LEFT]:
            missile_rect.x -= 6
        if keys[pygame.K_DOWN]:
            missile_rect.y += 6
        if keys[pygame.K_UP]:
            missile_rect.y -= 6
    
        debug(clock.get_fps())
        pygame.display.update()
        clock.tick(60)
    
    
    