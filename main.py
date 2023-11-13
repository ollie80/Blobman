import sys
import json
from random import randint

import pygame
from pygame.math import Vector2 as vector
from data.code.settings import *
from data.code.support import *

from pygame.image import load
from data.code.game import Game
import random
from data.code.game_data import *
from os import walk

from data.code.main_menu import MainMenu

class Main:
    def __init__(self):
        pygame.init()


        with open('data/save/save_data.txt') as save_data:
            self.data = json.load(save_data)



        flags = pygame.FULLSCREEN | pygame.DOUBLEBUF

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags, 16)
        self.display_surface = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))

        pygame.event.set_allowed((pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN))

        self.main_menu = MainMenu(self.screen, self.display_surface, self)

        self.game_active = False
        self.menu_active = True
        self.clock_hat_timer = False


        # player
        self.weapon_1 = 6
        self.weapon_2 = None
        self.staff = None
        self.hat = 15



        self.boss_kills = 0
        self.kills = 0
        self.coins = 0
        self.player_max_health = 100
        self.player_health = self.player_max_health
        self.current_room = 0
        self.rooms_completed = 0
        self.room_multiplier = 1 + self.rooms_completed / 50

        self.changing_room = False
        self.can_change_room = True

        self.clock = pygame.time.Clock()

        pygame.display.set_caption("Digital Tech Term 4")


    def start_game(self):
        self.game = Game(self.display_surface, self.screen, self, room_0, 0)
        self.game_active = True


    def new_room(self):
        if self.changing_room and self.can_change_room:
            rand = random.choices(population=[1,2,3,4, 5, 6, 7, 8] , weights=(1, 1, 0.6, 0.8, 0, 0.2, 0.2, 0.6), k=1)[0]
            while rand == self.current_room:
                rand = random.choices(population=[1, 2, 3, 4, 5, 6,7, 8], weights=(1, 1, 0.6, 0.8, 0, 0.2, 0.2, 0.6), k=1)[0]
            if rand == 1:
                room = room_1
            elif rand == 2:
                room = room_2
            elif rand == 3:
                room = room_3
            elif rand == 4:
                room = room_4
            elif rand == 5:
                room = room_5
            elif rand == 6:
                room = room_6
            elif rand == 7:
                room = room_7
            elif rand == 8:
                room = room_8

            self.rooms_completed += 1
            self.current_room = rand
            self.can_change_room = False
            self.changing_room = False
            self.game = None
            self.game = Game(self.display_surface, self.screen, self, room, rand)



    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def save(self):
        with open('data/save/save_data.txt', 'w') as save_data:
            json.dump(self.data, save_data)

    def reset(self):
        self.weapon_1 = 6
        self.weapon_2 = None
        self.staff = None
        self.boss_kills = 0
        self.kills = 0
        self.coins = 0
        self.player_max_health = 100
        self.player_health = self.player_max_health
        self.current_room = 0
        self.rooms_completed = 0

    def check_achievement(self):
        if self.coins >= 10000 and self.boss_kills >= 3 and not self.data['3'] == True:
            self.data['3'] = True
            self.game.ui.hat = 'Crown'
            self.game.ui.unlock_hat_timer.activate()

        if self.kills >= 100 and not self.data['2'] == True:
            self.data['2'] = True
            self.game.ui.hat = 'Traffic Cone'
            self.game.ui.unlock_hat_timer.activate()

        if self.kills >= 50 and self.coins >= 1000 and not self.data['0'] == True:
            self.data['0'] = True
            self.game.ui.hat = 'Top Hat'
            self.game.ui.unlock_hat_timer.activate()

        if self.boss_kills >= 1 and not self.data['1'] == True:
            self.data['1'] = True
            self.game.ui.hat = 'Propeller Hat'
            self.game.ui.unlock_hat_timer.activate()

        if self.clock_hat_timer and not self.data['4'] == True:
            self.data['4'] = True
            self.game.ui.hat = 'Clock'
            self.game.ui.unlock_hat_timer.activate()

    def run(self):
        while True:
            self.room_multiplier = 1 + self.rooms_completed / 50
            self.check_achievement()


            self.event_loop()
            dt = self.clock.tick() / 1000
            if self.game_active:
                self.game.run(dt)
                self.new_room()
            elif self.menu_active:
                self.main_menu.update()



            pygame.display.update()





if __name__ == '__main__':

    main = Main()
    main.run()