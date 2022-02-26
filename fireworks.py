import pygame
import math
from colors import *
from settings import *
from random import *
from utils import *

class Particle:
    def __init__(self, color, pos, angle,radius):
        self.color = color
        self.pos = vec(pos)
        self.radius = radius
        self.angle = angle
        self.dir = vec(pos).rotate(self.angle).normalize()
        self.velocity = 1.5
        self.duration = pygame.time.get_ticks()
        interval = 900
        self.lifespan = randint(interval,interval+200)

    def update(self):
        self.pos.x += self.dir.x * self.velocity
        self.pos.y += self.dir.y * self.velocity
        pygame.draw.circle(screen, self.color, self.pos, self.radius)
        if pygame.time.get_ticks()-self.duration >= self.lifespan:
            self.radius -= 0.2
        
class Firework:
    def __init__(self, pos, color):
        self.particles  =[]
        angle = 0
        self.color = color
        numberOfParticules = 10
        for i in range(numberOfParticules):
            angle = i/numberOfParticules*360
            #angle = i*360/numberOfParticules
            self.particles.append(Particle(self.color, pos,angle,2))

    def update(self):
        self.particles = [particle for particle in self.particles if particle.radius > 0]
        for particle in self.particles:
            particle.update()


if __name__ == '__main__':
    pygame.init()
    points = []
    ADD_FIREWORK = pygame.USEREVENT+1
    pygame.time.set_timer(ADD_FIREWORK,410) # cuánto más bajo más difícil es el juego
    fireworks_pos = [(528, 197), (515, 364), (627, 355), (670, 218), (816, 198), (862, 372), (758, 472), (636, 324), (644, 182), (845, 158), (997, 198), (900, 396), (778, 280)]
    finished = False
    clock = pygame.time.Clock()
    fireworks = list()
    index = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            # if event.type == ADD_FIREWORK and not finished:
            #     fireworks.append(Firework(fireworks_pos[index]))
            #     index += 1
            #     if index == len(fireworks_pos):
            #         finished = True
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                points.append(pos)
                fireworks.append(Firework(pos,choice(['red','purple','blue','green','violet'])))
                
        screen.fill('lightblue')
        print(points)
        debug(str(pygame.mouse.get_pos()))
        for firework in fireworks:
            firework.update()
        pygame.display.update()
        clock.tick(FPS)