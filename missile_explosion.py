import pygame
import math
from colors import *
from settings import *
from random import *
from utils import *
from enemies import *

class Particle:
    def __init__(self, color, pos, angle,radius):
        self.color = color
        self.pos = vec(pos)
        self.radius = radius
        self.angle = angle
        self.dir = vec(pos).rotate(self.angle).normalize()
        self.velocity = 1.5
        self.duration = pygame.time.get_ticks()
        interval = 50
        self.lifespan = randint(interval,interval+50)

    def update(self):
        self.pos.x += self.dir.x * self.velocity
        self.pos.y += self.dir.y * self.velocity
        pygame.draw.circle(screen, self.color, self.pos, self.radius)
        if pygame.time.get_ticks()-self.duration >= self.lifespan:
            self.radius -= 0.2
        
class MissileExplosion:
    def __init__(self, pos, color='white'):
        self.particles  =[]
        angle = 0
        self.color = color
        numberOfParticules = 14
        for i in range(numberOfParticules):
            angle = i/numberOfParticules*360
            #angle = i*360/numberOfParticules
            self.particles.append(Particle(self.color, pos,angle,2))

    def update(self):
        self.particles = [particle for particle in self.particles if particle.radius > 0]
        for particle in self.particles:
            particle.update()


if __name__ == '__main__':
    def collisions():
        for missil in collision1.sprites():
            if pygame.sprite.spritecollide(missil,collision2,True):
                explosions.append(MissileExplosion(missil.rect.center,'white'))
                missil.kill()
    pygame.init()
    clock = pygame.time.Clock()
    explosions = list()
    running = True
    enemies = pygame.sprite.Group(Enemy(100,400,'graphics/enemies/planes/plane_1/plane_1_red.png',True))
    enemies.add(Enemy(SCREEN_WIDTH-100,400,'graphics/enemies/planes/plane_1/plane_1_red.png',False))
    missiles = pygame.sprite.Group()
    collision1 = pygame.sprite.Group()
    collision2 = pygame.sprite.Group()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    for enemy in enemies.sprites():
                        x,y = enemy.rect.center
                        if enemy.left_side:
                            m = Missile(x,y,10,'graphics/enemies/planes/missile/missile.png')
                            missiles.add(m)
                            collision1.add(m)
                        else:
                            m = Missile(x,y,-10,'graphics/enemies/planes/missile/missile.png')
                            missiles.add(m)
                            collision2.add(m)
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                explosions.append(MissileExplosion(pos,'white'))
                
        screen.fill('lightblue')
        debug(str(pygame.mouse.get_pos()))
        
        #enemies.update()
        enemies.draw(screen)
        missiles.update()
        missiles.draw(screen)
        collisions()
        for explosion in explosions:
            explosion.update()
        pygame.display.update()
        clock.tick(FPS)