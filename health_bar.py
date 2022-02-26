import pygame
from colors import *

class HealthBar(pygame.sprite.Sprite):
    def __init__(self,x,y,width):
        super().__init__()
        self.enemy_attack = 10 # debería ser siempre múltiplo de 10, puede haber enemigos que inflingan más daño pero tiene que ser múltiplo de 10
        self.height = 7
        self.current_health = 50
        self.maximum_health = 50
        self.health_bar_length = width
        self.image = pygame.Surface((self.health_bar_length,self.height))
        self.image.fill('white')
        self.rect = self.image.get_rect(center=(x,y))
        self.health_ratio = self.maximum_health/self.health_bar_length
        
    def update(self):
        # if self.rect.y <= 0:
        #     self.rect.y = 0
        self.image.fill('white')
        pygame.draw.rect(self.image,'green',(0,0,self.current_health/self.health_ratio,self.height))
        vertical_separation = self.health_bar_length/self.maximum_health*self.enemy_attack
        for i in range(1,self.maximum_health//self.enemy_attack):
            pygame.draw.line(self.image,'black',(vertical_separation*i,0),(vertical_separation*i,self.height),1)
        pygame.draw.rect(self.image,'black',(0,0,self.health_bar_length,self.height),1)

    def get_damage(self, amount):
        assert(amount > 0)
        if self.current_health:
            self.current_health -= amount
        if self.current_health <= 0:
            self.current_health = 0

    def get_health(self,amount):
        if self.current_health < self.maximum_health:
            self.current_health += amount
        if self.current_health >= self.maximum_health:
            self.current_health = self.maximum_health