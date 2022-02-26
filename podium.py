import pygame
import sys
from settings import *
from utils import *
from random import *
import shared
from confetti2nd_try import Confetti
 

class Podium():
    def __init__(self):
        self.confetti_spr = pygame.sprite.Group()
        for _ in range(200):
            self.confetti_spr.add(Confetti([randint(0,SCREEN_WIDTH),randint(0,SCREEN_HEIGHT)],[uniform(1,2),uniform(1,2)],rand_color()))
        self.floor_color = (205,21,54)
        self.trophies_imgs = load_folder_images('graphics/trophies/game')
        self.podium_img = load_image('graphics/podium/podium.png')

        self.podium_rect = self.podium_img.get_rect(midbottom=(SCREEN_WIDTH//2,SCREEN_HEIGHT-45))
        self.podium_surf = pygame.Surface((self.podium_img.get_width(),self.podium_img.get_height()+self.trophies_imgs[0].get_height()),pygame.SRCALPHA)
        self.podium_surf_rect = self.podium_surf.get_rect(midbottom=self.podium_rect.midbottom)

        self.background = pygame.Surface((SCREEN_WIDTH,100))
        self.background.fill(self.floor_color)
        self.rect_gold_trophy = self.trophies_imgs[0].get_rect(midbottom=(430,self.podium_surf.get_height()-190))
        self.rect_silver_trophy = self.trophies_imgs[1].get_rect(midbottom=(140,self.podium_surf.get_height()-115))
        self.rect_bronze_trophy = self.trophies_imgs[2].get_rect(midbottom=(725,self.podium_surf.get_height()-100))  
        self.data_scores = get_player_profile(JSON_SCORES,shared.PLAYER_NAME)
        if not self.data_scores:
            self.data_scores = create_player_profile(JSON_SCORES,shared.PLAYER_NAME)
        self.podium_surf.blit(self.trophies_imgs[0],self.rect_gold_trophy.topleft)
        self.podium_surf.blit(self.trophies_imgs[1],self.rect_silver_trophy.topleft)
        self.podium_surf.blit(self.trophies_imgs[2],self.rect_bronze_trophy.topleft)
        self.load_scores()

    def write_new_score(score, player_name):
        try:
            ind, data_scores = get_player_ind(JSON_SCORES,player_name)
        except ValueError:
            ind, data_scores = create_player_profile(JSON_SCORES,player_name), -1
        all_content = read_json(JSON_SCORES)
        categories = list(data_scores.keys())[1:] # NOTE: en caso de añadir nuevos campos modfiicar los indices!
        scores = list(data_scores.values())[1:]
        scores = [int(score) for score in scores]
        scores.append(score)
        scores.sort(reverse=True)
        for category, score in zip(categories,scores):
            data_scores[category] = str(score)
        all_content[ind] = data_scores
        write_json(all_content,JSON_SCORES)
        
    def load_scores(self):
        font_size = 25        
        show_centered_text(self.podium_surf,self.data_scores["gold"],self.rect_gold_trophy.midtop-vec(0,14),font_size,'white')
        show_centered_text(self.podium_surf,self.data_scores["silver"],self.rect_silver_trophy.midtop-vec(0,14),font_size,'white')
        show_centered_text(self.podium_surf,self.data_scores["bronze"],self.rect_bronze_trophy.midtop-vec(0,14),font_size,'white')

    def update(self):
        screen.blit(self.background,(0,SCREEN_HEIGHT-50))
        #pygame.draw.rect(screen,'red',self.podium_surf_rect,2)
        #screen.blit(self.podium_img,(SCREEN_WIDTH//2-self.podium_img.get_width()//2,SCREEN_HEIGHT-self.podium_img.get_height()-45))
        screen.blit(self.podium_img,self.podium_rect)
        screen.blit(self.podium_surf,self.podium_surf_rect)        
        if self.confetti_spr and len(self.confetti_spr.sprites()) < 200:
            self.confetti_spr.add(Confetti([randint(0,SCREEN_WIDTH),randint(0,SCREEN_HEIGHT)],[uniform(1,3),uniform(1,4)],rand_color()))
        self.confetti_spr.update()
        self.confetti_spr.draw(screen)

    

if __name__ == '__main__':
    pygame.init()
    podium = Podium()
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        screen.fill((50,130,255))
        for e in pygame.event.get():
            if e.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
        
        podium.update()
        
        pygame.display.update()
        clock.tick(FPS)
