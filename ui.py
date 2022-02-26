import sys
import pygame
from settings import *
from random import choice, randint
from map import Water, Cloud
import os
from colors import *
from utils import *
from math import *
from player import Player
from podium import Podium
from game import main # cuidado al importar main c ss
import shared
from tutorial import Gameplay
''' 
TODO: 
'''
pygame.init()
WIRE_ENEMIES = pygame.USEREVENT+2
pygame.time.set_timer(WIRE_ENEMIES,2500)
clock = pygame.time.Clock()
# TODO: archivo settings
 

def update_window():
    pygame.display.update()
    clock.tick(FPS)

class Menu:
    FONT_SIZE = 40
    BACKGROUND = BLUE_SKY
    def __init__(self):
        # should be defined in a subclass
        self.current_button = 0
        self.buttons = None 

    # TODO: utilizar text_color
    def move_down(self):
        text = self.buttons[self.current_button].text
        self.buttons[self.current_button].text_surf = self.buttons[self.current_button].font.render(text, True, 'white')
        self.current_button = (self.current_button+1)%len(self.buttons)
        text = self.buttons[self.current_button].text
        self.buttons[self.current_button].text_surf = self.buttons[self.current_button].font.render(text, True, 'orange')

    def move_up(self):
        text = self.buttons[self.current_button].text
        self.buttons[self.current_button].text_surf = self.buttons[self.current_button].font.render(text, True, 'white')
        self.current_button -= 1
        if self.current_button < 0:
            self.current_button = 0
        text = self.buttons[self.current_button].text
        self.buttons[self.current_button].text_surf = self.buttons[self.current_button].font.render(text, True, 'orange')

class Button:
    def __init__(self, x, y, w, h, text, font_colour): # colour: color del rectángulo de fondo, por ahora el rectángulo será transparente
        self.font = pygame.font.Font(resource_path(FONT), Menu.FONT_SIZE)
        self.button_surf = pygame.Surface((w,h),pygame.SRCALPHA,32)
        #self.button_surf.fill('white')
        self.text = text
        self.font_colour = font_colour
        self.button = self.button_surf.get_rect(center=(x,y))
        self.text_surf = self.font.render(self.text, True, self.font_colour)
        self.text_rect = self.text_surf.get_rect(center=self.button.center)

    def draw(self, screen):        
        screen.blit(self.button_surf, self.button)
        screen.blit(self.text_surf, self.text_rect)

    def set_text(self,text,colour):
        self.text = text
        self.text_surf = self.font.render(text, True, colour)
        self.text_rect = self.text_surf.get_rect(center=self.button.center)

class MainMenu(Menu):
    def __init__(self):
        offset =  50
        button1 = Button(SCREEN_WIDTH//2, 310,          420, 50, "start game", 'orange')
        button2 = Button(SCREEN_WIDTH//2, 310+offset,   420, 50, "how to play", 'white')
        button3 = Button(SCREEN_WIDTH//2, 310+offset*2, 420, 50, "high scores", 'white')
        button4 = Button(SCREEN_WIDTH//2, 310+offset*3, 420, 50, "settings", 'white')
        button5 = Button(SCREEN_WIDTH//2, 310+offset*4, 420, 50, "quit", 'white')
        # self.flag_animations = load_folder_images('graphics/flag')
        # self.flag_ind = 0
        self.buttons = [button1,button2,button3,button4,button5]
        self.current_button = 0
        if not os.path.exists(JSON_PLAYER_CONTROLS):
            write_json(PlayerControls.get_default_controls(),JSON_PLAYER_CONTROLS)
        
        self.player_sprite = pygame.sprite.GroupSingle()
        player_x, player_y = SCREEN_WIDTH//2,SCREEN_HEIGHT-280
        
        self.player_sprite.add(Player(player_x+8,player_y))
        # self.lightnings_sprite = pygame.sprite.Group()
        # self.lightnings_sprite.add(Lightening())
        self.frame_index = 0

    def draw(self):
        # self.lightnings_sprite.update()
        # self.lightnings_sprite.draw(screen)
        #self.player_sprite.sprite.animate()
        # self.flag_ind = (self.flag_ind+0.2)%len(self.flag_animations)
        # screen.blit(self.flag_animations[int(self.flag_ind)],(SCREEN_WIDTH//2-240,SCREEN_HEIGHT-380))
        self.player_sprite.sprite.draw_health_bar()
        self.player_sprite.draw(screen)
        for button in self.buttons:
            button.draw(screen)

    def action(self):
        if self.current_button == 0:
            main()
        elif self.current_button == 1:
            tutorial = HowToPlay()
            tutorial.event_loop()
        elif self.current_button == 2:
            scores = HighScores()
            scores.event_loop()
        elif self.current_button == 3:
            controls = PlayerControls()
            controls.event_loop()
        elif self.current_button == 4:
            pygame.quit()
            sys.exit()

    def event_loop(self):
        for event in pygame.event.get():
            # if event.type == ADD_LIGHTNING:
            #     self.lightnings_sprite.add(Lightening())
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.action()
                if event.key == pygame.K_DOWN:
                    self.move_down()
                if event.key == pygame.K_UP:
                    self.move_up()
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def update_window():
    pygame.display.update()
    clock.tick(FPS)

class HighScores:
    def __init__(self):
        self.podium = Podium()

    def event_loop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: # volver atrás
                        running = False                        
            screen.fill(HIGH_SCORES_BACKGROUND) 
            self.podium.update()
            update_window()

class HowToPlay:
    
    def __init__(self):
        self.gameplay = Gameplay()
        

    def event_loop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: # volver atrás
                        running = False 
                    if event.key == self.gameplay.player.sprite.keys_dict["shoot"]: 
                        self.gameplay.player.sprite.shoot_key_pressed = True
                    if event.key == pygame.K_RETURN and not self.gameplay.finished:
                        if self.gameplay.lessons[self.gameplay.ind].completed:
                            self.gameplay.ind += 1
                            if self.gameplay.ind >= len(self.gameplay.lessons):
                                self.gameplay.ind = len(self.gameplay.lessons)-1
                                self.gameplay.finished = True
                if event.type == WIRE_ENEMIES:
                    for enemy in self.gameplay.wire_enemies.sprites():
                        if not enemy.player_collision and not enemy.collecting_chain and enemy.finished:
                            enemy.player_rect = self.gameplay.player.sprite.rect.copy()
                            enemy.offset = 0
                            enemy.awaiting_orders = False
                            enemy.finished = False                       
            screen.fill(BLUE_SKY) 
            self.gameplay.update()
            update_window()

class PlayerControls(Menu):
    DEFAULT_KEYS_VALUES = [pygame.key.name(pygame.K_a),pygame.key.name(pygame.K_d),pygame.key.name(pygame.K_w),
            pygame.key.name(pygame.K_s),pygame.key.name(pygame.K_j),pygame.key.name(pygame.K_SPACE)]
    KEYS = ["left","right","up","down","flip","shoot"]
    def __init__(self):
        super().__init__()
        self.key_dict = read_json(JSON_PLAYER_CONTROLS)
        assert len(self.key_dict)
        button_height = 50
        button_width = 420
        offset = Menu.FONT_SIZE
        self.buttons = [Button(SCREEN_WIDTH//2,  280, button_width, button_height, 'Player name: '+shared.PLAYER_NAME, 'orange') ]
        for mapped_key in self.key_dict.items():
            self.buttons.append(Button(SCREEN_WIDTH//2,280+offset,button_width, button_height, f'{mapped_key[0]} : {mapped_key[1]}', 'white'))
            offset += Menu.FONT_SIZE
        self.buttons.append(Button(SCREEN_WIDTH//2,  290+offset, button_width, button_height, 'Restore default controls', 'white'))
        

    def get_default_controls():
        assert len(PlayerControls.DEFAULT_KEYS_VALUES) == len(PlayerControls.KEYS)
        zip_iter = zip(PlayerControls.KEYS,PlayerControls.DEFAULT_KEYS_VALUES) # PlayerControls.KEYS[1:] dichoso requisito de diferentes jugadores...
        keys_dict = dict(zip_iter)
        return keys_dict

    def change_key(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: # para volver atrás, la tecla esc está reservada para volver atrás y no podrá ser utilizada para controlar el jugador
                        return
                    keys_ind = self.current_button-1 # para que coincida con el índice de KEYS, como el primer botón es player name...
                    self.key_dict[PlayerControls.KEYS[keys_ind]] = pygame.key.name(event.key) # +1 para que coincida con current_button
                    key, value = PlayerControls.KEYS[keys_ind], pygame.key.name(event.key)
                    self.buttons[self.current_button].set_text(f'{key} : {value}','orange')
                    write_json(self.key_dict,JSON_PLAYER_CONTROLS) # TODO+1 guardar al salir de la ventana sería una mejor opción en lugar de guardar continuamente
                    return
            screen.fill(Menu.BACKGROUND) 
            show_centered_text(screen,"Enter a new key",(SCREEN_WIDTH//2,300),Menu.FONT_SIZE,'white')
            update_window()

    def change_buttons_to_default_config(self):
        self.key_dict = PlayerControls.get_default_controls()
        buttons_to_change = self.buttons[1:]
        for data in zip(self.key_dict,buttons_to_change): 
            #print(data)
            key = data[0]
            value = self.key_dict[key]
            data[1].set_text(f'{key} : {value}','white')

    def event_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: # volver atrás
                        return
                    if not self.current_button:
                        if event.key == pygame.K_BACKSPACE:
                            if shared.PLAYER_NAME:
                                shared.PLAYER_NAME = shared.PLAYER_NAME[:-1]
                        elif event.key == pygame.K_SPACE or event.unicode != " " and event.unicode>=u' ':
                            if len(shared.PLAYER_NAME) < 20:
                                shared.PLAYER_NAME += event.unicode
                        self.buttons[self.current_button].set_text("Player name: "+shared.PLAYER_NAME,'orange')
                    if event.key == pygame.K_RETURN:
                        if self.current_button == len(self.buttons)-1:
                            self.change_buttons_to_default_config() # FIXME no están centrados los botones
                            write_json(self.key_dict,JSON_PLAYER_CONTROLS)
                        elif self.current_button != 0:
                            self.change_key()
                    if event.key == pygame.K_DOWN:
                        self.move_down()
                    if event.key == pygame.K_UP:
                        self.move_up()
            screen.fill(Menu.BACKGROUND) 
            for button in self.buttons:
                button.draw(screen)
            show_centered_text(screen,"Press esc to go back",(SCREEN_WIDTH//2,SCREEN_HEIGHT-150),Menu.FONT_SIZE,'white')
            update_window()

water = Water(speed=8,min_amplitude=12)

clouds_sprite = pygame.sprite.Group()
clouds_sprite.add(Cloud(-160,-70))
clouds_sprite.add(Cloud(200,-70)) 
clouds_sprite.add(Cloud(560,-70))
clouds_sprite.add(Cloud(920,-70))
clouds_sprite.add(Cloud(1280,-70))

ui = MainMenu()
while True:
    screen.fill(Menu.BACKGROUND)
    water.draw_waves(screen)
    ui.event_loop()
    ui.draw()  
    # for drop in rain_drops:
    #     drop.draw()
    clouds_sprite.draw(screen)
    update_window()