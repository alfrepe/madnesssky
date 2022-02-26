import pygame, sys
from utils import *
from settings import *
from math import *
from colors import *
from missile import *
from random import *
from player import Player
from enemies import Enemy
from missile_smoke import Smoke

# si el misil que iba a destruir un misil del jugador y el misil del jugador ya fue destruido, hay dos caminos: que el misil siga su trayectoria o que la cambia hacia la posicion del jugador, sin seguirlo, solo la posicion actual y que siga su trayectoria, esto habría que hacerlo con seeking behaviors porque sino queda muy artificial
# este enemigo es muy fácil de matar si me acerco mucho a él y disparo
class ProtectorEnemy(Enemy):
    guided_missiles = pygame.sprite.Group()
    def __init__(self, x,y, img_path, player,left_side=False,ratio=120):
        super().__init__(x,y, img_path,left_side)
        self.player_spr = player.sprite
        self.left_side = left_side
        self.player_missiles = player.sprite.missiles
        self.missile_velocity = self.player_spr.missile_velocity+0.5
        self.max_player_missiles_destroyed_at_time = 500
        self.destroyed = 0
        self.pretend_to_destroy = pygame.sprite.Group()
        #self.rect = self.image.get_rect(topleft=(x,y))
        self.pos = self.rect.y
        self.start_time = 0
        self.vi = 5
        self.duration = 3 # duracion en segundos para volver a destruir los misiles del jugador
        self.action_ratio = [y-ratio,y+ratio] # ratio de accion para destruir los misiles del jugador sino si el enemigo está arriba de todo en la pantalla y el jugador abajo del todo, los misiles de este enemigo tiene que recorrer mucho espacio y queda muy poco real
        # if self.action_ratio[1] >= SCREEN_HEIGHT:
        #     self.action_ratio[0] = SCREEN_HEIGHT-ratio*2
        #     self.action_ratio[1] = SCREEN_HEIGHT
        #     self.rect.bottom = SCREEN_HEIGHT
        #     self.pos = self.rect.y
            

    def shoot_missile(self, target_missile):
        x, y = self.rect.bottomright
        if not self.left_side:
            x, y = self.rect.bottomleft
        ProtectorEnemy.guided_missiles.add(GuidedMissile(x,y,self.missile_velocity,'graphics/enemies/planes/missile/missile.png',target_missile,self.player_spr))
    
    def move(self):
        self.pos += self.vi
        self.rect.y = round(self.pos)
        if self.rect.bottom > self.action_ratio[1] or self.rect.top < self.action_ratio[0]: # con el >= <= se queda parpadeando
            self.vi *= -1

    def update(self):
        self.move()
        pygame.draw.line(screen,'red',(300,self.action_ratio[0]),(300,self.action_ratio[1]))
        # pygame.draw.line(screen,'blue',self.rect.center,self.rect.center-vec(0,25))
        # pygame.draw.circle(screen,'blue',self.rect.center-vec(0,30),6,1)
        if self.player_missiles:  
            if self.destroyed >= self.max_player_missiles_destroyed_at_time:
                if not self.start_time:
                    self.start_time = pygame.time.get_ticks()
                if (pygame.time.get_ticks() - self.start_time)/1000 >= self.duration:
                    #print("se termino la espera")
                    self.destroyed = 0
                    self.start_time = 0
            for target_missile in self.player_missiles.sprites():
                # if target_missile.rect.colliderect(self.rect): # por si acaso, podría ocurrir que justo un misil colisiona con el enemigo cuando el enemigo justo va a lanzar el misil de destruccion de los misiles del jugador
                #     self.kill()
                if self.destroyed >= self.max_player_missiles_destroyed_at_time:
                    #print("no puedo!")
                    break
                #print("ahora si puedo")
                if self.action_ratio[0] <= target_missile.rect.y <= self.action_ratio[1] and ((not self.left_side and target_missile.rect.right < self.rect.left) or (self.left_side and target_missile.rect.left > self.rect.right)):
                    if target_missile in self.pretend_to_destroy or (self.left_side and target_missile.velocity > 0) or (not self.left_side and target_missile.velocity < 0):
                        continue
                    self.pretend_to_destroy.add(target_missile)
                    self.shoot_missile(target_missile)
                    self.destroyed += 1
        

def collisions():
    # enemigos especiales
    for guided_missile in ProtectorEnemy.guided_missiles.sprites():
        if pygame.sprite.spritecollide(guided_missile,player_sprite.sprite.missiles,True):
            guided_missile.kill()
        if player_sprite.sprite.rect.colliderect(guided_missile.rect):
            guided_missile.kill()

class SeekingEnemy(Enemy):
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
        self.big_rect = pygame.Rect(*self.pos,self.image.get_width()*2,self.image.get_width()*2)

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
        self.big_rect.center = self.pos
        ################# 
        #pygame.draw.line(screen, 'green', self.pos, (self.pos + self.vel * 25), 5)
        #self.smoke_rect.topleft = self.rect.topleft
        #pygame.draw.rect(screen,'red',self.smoke_rect,4)




if __name__ == '__main__':   
    pygame.init()
    normal_enemies = pygame.sprite.Group()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    vec = pygame.math.Vector2
    #si el jugador entrea en su ratio de accion explota?
    start_following = False
    SHOOT_MISSILE = pygame.USEREVENT+1
    FOLLOW_PLAYER = pygame.USEREVENT+2
    pygame.time.set_timer(SHOOT_MISSILE,330)
    pygame.time.set_timer(FOLLOW_PLAYER,3000)
    player_sprite = pygame.sprite.GroupSingle()
    player_sprite.add(Player(60,119))
    normal_enemies.add(ProtectorEnemy(120,120,'graphics/enemies/planes/plane_1/plane_1_red.png',player_sprite,True)) # left side
    normal_enemies.add(ProtectorEnemy(SCREEN_WIDTH-120,SCREEN_HEIGHT-120,'graphics/enemies/planes/plane_1/plane_1_red.png',player_sprite,False)) # right side
    hunter_missile = pygame.sprite.GroupSingle()
    hunter_missile_img = 'graphics\enemies\planes\missile\missile31x17.png'
    #hunter_missile.add(SeekingEnemy(100,300,hunter_missile_img,player_sprite,True)) # left side
    #hunter_missile.add(SeekingEnemy(1100,300,hunter_missile_img,player_sprite,False)) # right side
    smoke = Smoke()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    start_following = True
                if event.key == pygame.K_SPACE:
                    player_sprite.sprite.shoot_key_pressed = True
            if event.type == pygame.MOUSEBUTTONDOWN: # probar que cuando un misil del jugador es destruido los misiles del enemigo destructor no se quedan oscilando
                mi = choice(player_sprite.sprite.missiles.sprites())
                mi.kill()
                #shoot_enemy_missile()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    pass
        screen.fill('lightblue')
        if start_following:
            hunter_missile.update()
        if hunter_missile.sprite:
            posi = hunter_missile.sprite.pos
            smoke.add_smoke_right(posi)
            smoke.draw()
        hunter_missile.draw(screen)
        player_sprite.update()
        player_sprite.draw(screen)

        ProtectorEnemy.guided_missiles.update()
        ProtectorEnemy.guided_missiles.draw(screen)

        normal_enemies.update()
        normal_enemies.draw(screen)
        

        collisions()
        pygame.display.update()
        clock.tick(60)