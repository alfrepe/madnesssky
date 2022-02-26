import pygame, sys
from utils import *
from settings import *
from math import *
from colors import *
from missile import Missile
from random import *
from enemies import Enemy
from player import Player
# los disparos del jugador con KEYDOWN

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
clock = pygame.time.Clock()
vec = pygame.math.Vector2


class SeekingMissile(Enemy):
    def __init__(self, x,y, img_path, player,left_side=False):
        super().__init__(x,y, img_path,left_side)
        self.player = player
        self.max_speed = 9
        self.seek_force = 0.1
        self.is_dead = False
        self.pos = vec(self.rect.topleft)
        self.acc = vec(0, 0)
        self.vel = vec(self.max_speed, 0)
        self.rect = self.image.get_rect(topleft=self.pos+vec(0,-5))
        if not self.left_side:
            #self.image = pygame.transform.flip(self.image, True, False)
            self.vel = vec(-self.max_speed, 0)
            self.pos = vec(self.rect.topright)
            self.rect = self.image.get_rect(topright=self.pos+vec(3,-5))
            
        self.copy_img = self.image.copy()

    # rotate at a fixed position
    def blitRotate(self, originPos, angle):


        # x_pos = pos[0]-originPos[0]
        # y_pos = pos[0]-originPos[0]

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
            self.blitRotate((2, 8),ang)
        else:
            self.blitRotate((29, 8),ang)        

class Missile(pygame.sprite.Sprite):
    def __init__(self, x,y,velocity, img):
        super().__init__()
        self.velocity = velocity
        self.image = load_image(img)
        if self.velocity < 0:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(center=[x,y])

    def destroy(self):
        if self.rect.left <= -50 or self.rect.right >= SCREEN_WIDTH+50:
            self.kill()

    def move(self):
        self.rect.x += self.velocity

    def update(self):
        self.move()
        self.destroy()

enemies_missiles = pygame.sprite.Group()

player_sprite = pygame.sprite.GroupSingle()
player_sprite.add(Player(400,600))


hunter_missile = pygame.sprite.GroupSingle()
hunter_missile_img = 'graphics\enemies\planes\missile\missile31x17.png'
hunter_missile.add(SeekingEnemy(100,300,hunter_missile_img,player_sprite,True)) # left side
#hunter_missile.add(SeekingEnemy(1000,300,hunter_missile_img,player_sprite,False)) # right side


normal_enemies = pygame.sprite.Group()
normal_enemies.add(Enemy(SCREEN_WIDTH-Enemy.enemy_width,randint(50,150),'graphics/enemies/planes/plane_1/plane_1_red.png',False))
normal_enemies.add(Enemy(0,50,'graphics/enemies/planes/plane_1/plane_1_red.png',True))

def shoot_enemy_missile():
    # depende si esta en la retaguardia o no
    for enemy in normal_enemies.sprites():
        x, y = enemy.rect.bottomright
        velocity = -5
        if enemy.left_side:
            x, y = enemy.rect.bottomright
            velocity *= -1
        enemies_missiles.add(Missile(x,y-9,velocity,'graphics/enemies/planes/missile/missile.png'))

def collisions():
    for enemy_missile in enemies_missiles.sprites():
        # comprobar si alguno de los misiles de los enemigos chocan contra el jugador
        #debug(str(self.player_invincibility_timer))
        if player_sprite.sprite.rect.colliderect(enemy_missile):
            player_sprite.sprite.get_damage(10)
            enemy_missile.kill()
        # comprobar si alguno de los misiles de los enemigos chocan contra los misiles del jugador
        if pygame.sprite.spritecollide(enemy_missile,player_sprite.sprite.missiles,True):
            enemy_missile.kill()
    for enemy in normal_enemies.sprites():
        if hunter_missile.sprite and enemy.rect.colliderect(hunter_missile.sprite.rect): # cuidado con None
            print("BOOM!")
save = 0
if __name__ == '__main__':   
    start_following = False
    SHOOT_MISSILE = pygame.USEREVENT+1
    FOLLOW_PLAYER = pygame.USEREVENT+2
    pygame.time.set_timer(SHOOT_MISSILE,330)
    pygame.time.set_timer(FOLLOW_PLAYER,3000)

    while True:
        if hunter_missile.sprite:
            save = hunter_missile.sprite.left_side
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    start_following = True
                if event.key == pygame.K_SPACE:
                    player_sprite.sprite.shooting_key_pressed = True
                if event.key == pygame.K_r:
                        hunter_missile.add(SeekingEnemy(1000,300,hunter_missile_img,player_sprite,save))
            if event.type == pygame.MOUSEBUTTONDOWN:
                shoot_enemy_missile()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    player_sprite.sprite.shooting_key_pressed = False
        screen.fill('black')
        player_sprite.update()
        player_sprite.draw(screen)
        if start_following:
            hunter_missile.update()
        hunter_missile.draw(screen)
        #normal_enemies.update()
        normal_enemies.draw(screen)

        enemies_missiles.update()
        enemies_missiles.draw(screen)
        collisions()
        pygame.display.update()
        clock.tick(60)
