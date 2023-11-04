import sys

import pygame
from data.code.settings import *

from pygame.image import load
from data.code.timer import Timer

class UI:
    def __init__(self, display_surface, screen, main):
        self.display_surf = display_surface
        self.screen = screen
        self.main = main

        # container
        self.stats_container = pygame.surface.Surface((500,15))
        self.stats_container.fill('grey')
        self.stats_container.set_colorkey('grey')
        self.stats_container_rect = self.stats_container.get_rect(midleft = (DISPLAY_WIDTH /2 - 90, 10))



        # health bar
        self.health_bar_surf = load('data/graphics/ui/health_bar.png').convert_alpha()
        self.health_bar_rect = self.health_bar_surf.get_rect(topleft = (0,0))
        self.health_bar_fill_topleft = (self.health_bar_rect.x + 12, self.health_bar_rect.y + 4)
        self.bar_max_width = 53
        self.bar_height = 7

        # boss bar
        self.boss_bar_surf = load('data/graphics/ui/boss_bar.png').convert_alpha()
        self.boss_bar_rect = self.boss_bar_surf.get_rect(center=(DISPLAY_WIDTH /2, DISPLAY_HEIGHT / 2 + 110))
        self.boss_bar_fill_topleft = (self.boss_bar_rect.x + 2, self.boss_bar_rect.y + 2)
        self.boss_bar_max_width = 236
        self.boss_bar_height = 11

        # hat
        self.hat = 'Top Hat'
        self.unlock_hat_timer = Timer(1000)

        # coins
        self.font = pygame.font.Font('data/graphics/fonts/public-pixel-font/PublicPixel.ttf', 8)
        self.coin_icon = pygame.transform.scale2x(load('data/graphics/coin/0.png').convert_alpha())
        self.coin_rect = self.coin_icon.get_rect(topleft = (self.health_bar_rect.topright[0] + 10, self.health_bar_rect.topright[1] + 3))

        # pause menu
        self.pause_font = pygame.font.Font('data/graphics/fonts/public-pixel-font/PublicPixel.ttf', 10)
        self.pause_menu_active = False
        self.back_to_menu_button = self.pause_font.render('Back To Menu', False, 'white')
        self.back_to_menu_rect = self.back_to_menu_button.get_rect(center = (DISPLAY_WIDTH /2, DISPLAY_HEIGHT /2))

        self.quit_button = self.pause_font.render('Save And Quit', False, 'white')
        self.quit_rect = self.quit_button.get_rect(center = (DISPLAY_WIDTH/2, DISPLAY_HEIGHT /2 + DISPLAY_HEIGHT /5))

    def health_bar(self):

        current_health_ratio = self.main.player_health / self.main.player_max_health
        current_bar_width = self.bar_max_width * current_health_ratio
        health_bar_rect = pygame.Rect((self.health_bar_fill_topleft), (current_bar_width, self.bar_height))
        pygame.draw.rect(self.stats_container, '#ac3232', health_bar_rect)
        self.stats_container.blit(self.health_bar_surf, self.health_bar_rect)

    def boss_bar(self, boss_health, boss_id):
        current_health_ratio = boss_health / BOSS_STATS[boss_id][0]
        current_bar_width = self.boss_bar_max_width * current_health_ratio
        boss_bar_rect = pygame.Rect((self.boss_bar_fill_topleft), (current_bar_width, self.boss_bar_height))
        pygame.draw.rect(self.display_surf, '#ac3232', boss_bar_rect)
        self.display_surf.blit(self.boss_bar_surf, self.boss_bar_rect)

    def current_room(self):
        room_text = self.font.render(f'Current Room: {self.main.rooms_completed}', False, 'white')
        text_rect = room_text.get_rect(topleft = ((self.health_bar_rect.topright[0] + 100, self.health_bar_rect.topright[1] + 3)))
        self.stats_container.blit(room_text, text_rect)

    def coins(self):
        text = self.font.render(str(self.main.coins), False, 'white')
        text_rect = text.get_rect(topleft = (self.health_bar_rect.topright[0] + 25, self.health_bar_rect.topright[1] + 3))
        self.stats_container.blit(self.coin_icon, self.coin_rect)
        self.stats_container.blit(text, text_rect)


    def pause_menu(self):
        self.display_surf.blit(self.back_to_menu_button, self.back_to_menu_rect)
        self.display_surf.blit(self.quit_button, self.quit_rect)

        mouse_pos = (pygame.mouse.get_pos()[0] / ZOOM,pygame.mouse.get_pos()[1] / ZOOM)
        if self.back_to_menu_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.main.menu_active = True
            self.main.main_menu.main_active = True
            self.main.game_active = False
            self.main.reset()
        elif self.quit_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            self.main.save()
            pygame.quit()
            sys.exit()

    def hat_unlocked(self):
        if self.unlock_hat_timer.active:
            unlock_text = self.font.render(f'{self.hat} Unlocked', False, 'white')
            unlock_text_rect = unlock_text.get_rect(center = (DISPLAY_WIDTH /2, DISPLAY_HEIGHT / 2 + DISPLAY_HEIGHT /3))
            self.display_surf.blit(unlock_text, unlock_text_rect)

    def update(self):
        self.stats_container.fill('grey')

        self.unlock_hat_timer.update()
        self.hat_unlocked()
        if not self.pause_menu_active:
            self.current_room()
            self.coins()
            self.health_bar()
            self.display_surf.blit(self.stats_container, self.stats_container_rect)
        else:
            self.pause_menu()
