import pygame, sys
from colors import *
from settings import *
from player import Player
from utils import *
from math import *

class Cloud(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()    
        self.image = load_image("graphics/decoration/clouds/1_resized.png")
        self.rect = self.image.get_rect(topleft=(x,y))
        self.speed = 6
        self.width = self.image.get_width()

    def update(self):
        self.rect.x -= self.speed
        if self.rect.left < -self.width:
            self.kill()

class Sun(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()  
        self.x = x
        self.y = y  
        self.image = load_image('graphics/decoration/sun/sun.png')
        #self.image = pygame.transform.scale(self.image,(220,220))
        self.rect = self.image.get_rect(center=(x,y))
        self.angle = 0
        self.img_copy = self.image.copy()

    def update(self):
        pass
        # self.image = pygame.transform.rotate(self.img_copy, self.angle)
        # self.rect = self.image.get_rect(center=(self.x,self.y))
        # self.angle = (self.angle+0.4)%360

class Water:
    def __init__(self, speed, min_amplitude=2, max_amplitude=35, height = SCREEN_HEIGHT-170):
        self.min_amplitude = min_amplitude
        self.max_amplitude = max_amplitude
        self.amplitude = self.min_amplitude
        self.move_x = 0
        self.speed = speed
        self.min_x = -300
        self.watter_levels =   {i:0 for i in range(self.min_x,SCREEN_WIDTH) }
        self.height = height
        self.increment_amplitude = 0.1
        
    def draw(self, surface):
        for x in range(self.min_x,SCREEN_WIDTH):
            y = sin((x+self.move_x)*0.01) * self.amplitude+self.height
            self.watter_levels[x] = y
            pygame.draw.line(surface,WATER_COLOR,(x,round(y)),(x,SCREEN_HEIGHT))

    def move(self):
        self.move_x += self.speed # el barco se mueve solo como si estuviera navegando a la deriva
    
    # dibuja solo las olas sin actualizar la amplitud
    def draw_waves(self, surface):
        self.move()
        self.draw(surface)
    
    def update_amplitude(self):
        self.move()
        self.amplitude += self.increment_amplitude
        if self.amplitude >= self.max_amplitude or self.amplitude <= self.min_amplitude:
            self.increment_amplitude *= -1

    def get_water_level(self,index):
        # assert index in self.watter_levels
        if index >= SCREEN_WIDTH:
            return self.watter_levels[-1]
        return self.watter_levels[index]


if __name__=='__main__':
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    font = pygame.font.Font(None,30)

    PARTICLE_EVENT = pygame.USEREVENT+2
    pygame.time.set_timer(PARTICLE_EVENT,150)

    clock = pygame.time.Clock()
    cloud_sprites = pygame.sprite.Group()
    sun_sprite = pygame.sprite.GroupSingle()
    sun_sprite.add(Sun(SCREEN_WIDTH//2,SCREEN_HEIGHT//2))
    ADDCLOUD = pygame.USEREVENT+1
    pygame.time.set_timer(ADDCLOUD,1000)

    water = Water(6,12)

    player_sprite = pygame.sprite.GroupSingle()
    player_sprite.add(Player(500,SCREEN_HEIGHT-220))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ADDCLOUD:
                cloud_sprites.add(Cloud(SCREEN_WIDTH,SCREEN_HEIGHT-440)) 
        
        screen.fill(BLUE_SKY) # blue sky
        water.draw_waves(screen)
        player_sprite.update()
        player_sprite.draw(screen)
        cloud_sprites.update()
        cloud_sprites.draw(screen)

        pygame.display.update()
        clock.tick(60)