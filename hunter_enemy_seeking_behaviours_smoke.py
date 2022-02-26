import pygame, sys
from utils import *
from settings import *
from math import *
from colors import *
from random import *
from enemies import Enemy
from player import Player
from missile_smoke import Smoke

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
clock = pygame.time.Clock()
vec = pygame.math.Vector2

# un torpedo que sigue al jugador y que el jugador tiene que despistar o puede aprovecharlo para matar a enemigos
class SeekingMissile(pygame.sprite.Sprite):
    def __init__(self, x,y, img_path, velocity, player,left_side=False):
        super().__init__()
        self.smoke = Smoke()
        self.image = load_image(img_path)
        self.left_side = left_side
        self.player = player
        self.max_speed = velocity
        self.seek_force = 0.12 # con 0.2 se nota diferencia
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

    # TODO: ajustar mejor los límites
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

        if self.left_side:
            self.smoke.add_smoke_left(self.pos)
        else:
            #self.smoke.add_smoke_left(self.pos)
            self.smoke.add_smoke_left(self.pos)
        self.smoke.draw()    

# necesitan estar los más a la izquierda posible o derecha, sino los misiles podrían colisionar contra los enemigos sin haber perseguido al jugador
def rand_pos_seeking_enemy_(left_side=False):
        if left_side:
            return 50,randint(Enemy.enemy_height,SCREEN_HEIGHT-Enemy.enemy_height) 
        return SCREEN_WIDTH-200,randint(Enemy.enemy_height,SCREEN_HEIGHT-Enemy.enemy_height) 

player_sprite = pygame.sprite.GroupSingle()
player_sprite.add(Player(SCREEN_WIDTH//2,600))

seeking_missile = pygame.sprite.Group()
seeking_missile_img = 'graphics\enemies\planes\missile\seeking_resized.png'
enemy1= Enemy(*rand_pos_seeking_enemy_(False),'graphics/enemies/planes/plane_1/plane_1_blue.png',False) # right side
enemy2= Enemy(*rand_pos_seeking_enemy_(True),'graphics/enemies/planes/plane_1/plane_1_blue.png',True) # left side
enemies = pygame.sprite.Group(enemy1,enemy2)

def collisions():
    pass
    # if seeking_missile:
    #     if pygame.sprite.spritecollide(seeking_missile.sprites(),enemies,True):
    #         print("collision")
    #         seeking_missile.sprite.kill()

if __name__ == '__main__':   
    start_following = False
    FOLLOW_PLAYER = pygame.USEREVENT+2
    pygame.time.set_timer(FOLLOW_PLAYER,3000)
    smoke = Smoke()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    enemy = enemies.sprites()[0]
                    x,y = enemy.rect.midleft
                    left_side = False
                    if enemy.left_side:
                        x,y = enemy.rect.midright
                        left_side = True
                    seeking_missile.add(SeekingMissile(x,y,seeking_missile_img,10,player_sprite,left_side))
                if event.key == pygame.K_l:
                    enemy = enemies.sprites()[1]
                    x,y = enemy.rect.midleft
                    left_side = False
                    if enemy.left_side:
                        x,y = enemy.rect.midright
                        left_side = True
                    seeking_missile.add(SeekingMissile(x,y,seeking_missile_img,10,player_sprite,left_side))
                # if event.key == pygame.K_c:
                #     for enemy in seeking_missile.sprites():
                #         enemy.kill()
        screen.fill('lightblue')            
        seeking_missile.update()
        if seeking_missile.sprites():
            pygame.draw.rect(screen,'red',seeking_missile.sprites()[-1].rect)
        seeking_missile.draw(screen)
        # pygame.draw.rect(screen,'black',enemies.sprites()[-1].rect)
        # if seeking_missile.sprite:
        #     pygame.draw.rect(screen,'red',seeking_missile.sprite.rect)
        
        
        enemies.update()
        enemies.draw(screen)
        player_sprite.update()
        player_sprite.draw(screen)
        collisions()
        pygame.display.update()
        clock.tick(60)
