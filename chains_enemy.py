import pygame, sys
from utils import *
from settings import *
from math import *
from colors import *
from enemies import Enemy
from random import *
from player import Player

# lanza como una cadena, no sé muy bien lo que es... y si toca al player se ve reducida su velocidad durante x tiempo, podría lanzar la cadena y esperar a que el player la toque, a modo de trampa
class ParalyzerEnemy(Enemy):
    def __init__(self, x,y, img_path,player,left_side=False):
        super().__init__(x,y,img_path,left_side)
        self.player = player
        self.effect_duration = 0
        self.effect_interval = 4000
        self.player_rect = self.player.rect.copy()
        self.player_collision = False
        self.velocity_percentage = 0.4
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
            print("awaiting orders, sir")
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

player_sprite = pygame.sprite.GroupSingle()
player_sprite.add(Player(600,660))

enemy_sprite = pygame.sprite.Group()
#enemy_sprite.add(ParalyzerEnemy(100,300,'graphics/enemies/planes/plane_3/plane_3_red.png',player_sprite.sprite,True))
enemy_sprite.add(ParalyzerEnemy(SCREEN_WIDTH-100,620,'graphics/enemies/planes/plane_3/plane_3_red.png',player_sprite.sprite,False))
#enemy_sprite.add(Enemy(100,620,'graphics/enemies/planes/plane_3/plane_3_red.png',True))
#enemy_sprite.add(ParalyzerEnemy(SCREEN_WIDTH-100,320,'graphics/enemies/planes/plane_3/plane_3_red.png',player_sprite.sprite,False))


def collisions():
    for enemy in enemy_sprite.sprites():
        if enemy.player_collision:
            enemy.follow_player_and_reduce_his_velocity()
        else:
            enemy.update()

if __name__ == '__main__':   
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    vec = pygame.math.Vector2
    CHAIN_ENEMY = pygame.USEREVENT+1
    pygame.time.set_timer(CHAIN_ENEMY,1000) 
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_r: # cada x tiempo
            #         for enemy in enemy_sprite.sprites():
            #             if type(enemy).__name__ == 'ParalyzerEnemy':
            #                 if not enemy.player_collision and not enemy.collecting_chain:
            #                     enemy.player_rect = player_sprite.sprite.rect.copy()
            #                     enemy.offset = 0
            #                     enemy.awaiting_orders = False
                # if event.key == pygame.K_c:
                #     enemy_sprite.sprites()[-1].offset -= 45
                # if event.key == pygame.K_f:
                #     enemy_sprite.sprites()[-1].offset += 45
            if event.type == CHAIN_ENEMY:
                for enemy in enemy_sprite.sprites():
                    if type(enemy).__name__ == 'ParalyzerEnemy':
                        if not enemy.player_collision and not enemy.collecting_chain and enemy.finished:
                            enemy.player_rect = player_sprite.sprite.rect.copy()
                            enemy.offset = 0
                            enemy.awaiting_orders = False
                            enemy.finished = False
            
        screen.fill('white')        
        player_sprite.update()
        player_sprite.draw(screen)
        enemy_sprite.draw(screen)
        collisions()
        debug(str(player_sprite.sprite.velocity))
        pygame.display.update()
        clock.tick(60)
