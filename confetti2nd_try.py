import pygame, sys
sys.path.append('..')
from random import *
from utils import *
from math import *
from settings import *

class Confetti(pygame.sprite.Sprite):
    def __init__(self, pos, vel, color):
        super().__init__()
        self.vel = vec(vel)
        self.pos = vec(pos)
        self.rad = radians(randint(20,160))
        self.dir = vec(cos(self.rad),sin(self.rad))

        self.images = load_folder_images('graphics/confetti')
        
        for ind,img in enumerate(self.images):
            self.images[ind] = pygame.transform.scale(img,(10,10))
            w,h = self.images[ind].get_width(),self.images[ind].get_height()
            for x in range(w):
                for y in range(h):
                    opacity = self.images[ind].get_at((x, y))[3] # devuelve una tupla con el color, la poscion 4 es la opacidad de la imagen
                    self.images[ind].set_at((x,y),(*color,opacity))
        self.original_imgs = [img.copy() for img in self.images]
        # for ind,img in enumerate(self.images):
        #     img = pygame.transform.rotozoom(img,degrees(self.rad),1)
        #     self.images[ind] = img

        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=self.pos)
        self.ani_index = 0
        self.gravity = 0.2
        self.max_vel = 7
        self.ini_pos = self.pos
        self.orientation = 0
        self.ang = 5

    def remove(self):
        if self.rect.right < 0 or self.rect.y >= SCREEN_HEIGHT or self.rect.x > SCREEN_WIDTH:
            self.kill()

    def update(self):
        if self.ani_index >= len(self.images):
            self.ani_index = 0
        self.image = self.images[int(self.ani_index)]
        self.image = pygame.transform.rotozoom(self.original_imgs[int(self.ani_index)],self.orientation,1)
        self.rect = self.image.get_rect(center=self.pos)
        self.orientation = (self.orientation+self.ang)%360
        self.vel.y += self.gravity
        self.vel.y = min(self.vel.y,self.max_vel)
        self.pos.x += self.dir.x*self.vel.x
        self.pos.y += self.dir.y*self.vel.y
        self.rect.center = self.pos
        self.ani_index += 0.1
        self.remove()

if __name__ == '__main__':
    pygame.init()
    clock = pygame.time.Clock()
    confetti_sprites = pygame.sprite.Group()

    for _ in range(150):
        confetti_sprites.add(Confetti([randint(0,SCREEN_WIDTH),randint(0,SCREEN_HEIGHT)],[uniform(1,2),uniform(1,2)],rand_color()))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        screen.fill('black')
        # for circle in circles:
        #     pygame.draw.circle(screen,circle[0],circle[1],2)
        if confetti_sprites and len(confetti_sprites.sprites()) < 150:
            confetti_sprites.add(Confetti([randint(0,SCREEN_WIDTH),randint(-80,0)],[uniform(1,3),uniform(1,4)],rand_color()))
        confetti_sprites.update()
        confetti_sprites.draw(screen)
        pygame.display.update()
        clock.tick(FPS)