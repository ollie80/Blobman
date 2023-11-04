import sys

import pygame
from data.code.settings import *
from pygame.image import load
from data.code.support import *
from data.code.sprites import HatGeneric
from data.code.timer import Timer

class MainMenu:
    def __init__(self, screen, display_surface, main):
        self.screen = screen
        self.display_surf = display_surface
        title_font = pygame.font.Font('data/graphics/fonts/public-pixel-font/PublicPixel.ttf', 150)
        self.button_font = pygame.font.Font('data/graphics/fonts/public-pixel-font/PublicPixel.ttf', 35)
        self.title_text = title_font.render('BLOBMAN', False, 'white')
        self.title_text_rect = self.title_text.get_rect(center = (WINDOW_WIDTH /2, 300))
        self.back_ground = load('data/graphics/ui/background.png').convert_alpha()
        self.back_ground_rect = self.back_ground.get_rect(topleft = (0,0))
        self.main = main
        self.main_active = True
        self.hats_menu_active = False
        self.back_ground_direction = 'down'

        # main
        self.m_button_1 = self.button_font.render('PLAY', False, 'white')
        self.m_button_1_rect = self.m_button_1.get_rect(center = (WINDOW_WIDTH /4 + 330, WINDOW_HEIGHT /2 + WINDOW_HEIGHT /4))

        self.m_button_2 = self.button_font.render('HATS', False, 'white')
        self.m_button_2_rect = self.m_button_2.get_rect(center=(WINDOW_WIDTH / 4 + WINDOW_WIDTH/ 2 - 330, WINDOW_HEIGHT /2 + WINDOW_HEIGHT /4))

        self.m_button_3 = self.button_font.render('SAVE AND QUIT', False, 'white')
        self.m_button_3_rect = self.m_button_3.get_rect(center = (WINDOW_WIDTH /2, WINDOW_HEIGHT /2 + WINDOW_HEIGHT /4 + 150))

        self.equip_button = self.button_font.render('EQUIP', False, 'white')
        self.equip_button_rect = self.equip_button.get_rect(topleft = (WINDOW_WIDTH /2 - 20, WINDOW_HEIGHT /2 + 250))

        self.equipped_button = self.button_font.render('EQUIPPED', False, '#399972')
        self.equipped_button_rect = self.equipped_button.get_rect(topleft=(WINDOW_WIDTH / 2 - 60, WINDOW_HEIGHT / 2 + 250))

        self.back_ground_timer = Timer(400)
        self.change_hat_timer = Timer(250)


        # hats
        self.id = 0
        self.active_id = 0
        self.hat_group = pygame.sprite.Group()
        self.hat_spawn_pos = (WINDOW_WIDTH /2, WINDOW_HEIGHT /2)
        for image in import_folder('data/graphics/ui/hats'):
            sprite = HatGeneric(self.hat_spawn_pos, pygame.transform.scale2x(image), self.hat_group, self.id)
            sprite.rect.center = self.hat_spawn_pos
            self.hat_spawn_pos = (self.hat_spawn_pos[0] + 350, self.hat_spawn_pos[1])
            self.id += 1

    def main_buttons(self):
        self.screen.blit(self.m_button_1, self.m_button_1_rect)
        self.screen.blit(self.m_button_2, self.m_button_2_rect)
        self.screen.blit(self.m_button_3, self.m_button_3_rect)

        if self.m_button_1_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.main.start_game()
            self.main_active = False

        elif self.m_button_2_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.back_ground_direction = 'down'
            self.back_ground_timer.activate()
            self.hats_menu_active = True
            self.main_active = False

        elif self.m_button_3_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.main.save()
            pygame.quit()
            sys.exit()


    def back(self):
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            if self.hats_menu_active:
                self.hats_menu_active = False
                self.main_active = True
                self.back_ground_direction = 'up'
                self.back_ground_timer.activate()


    def move_background(self):
        if self.back_ground_timer.active:
            if self.back_ground_direction == 'down':
                self.back_ground_rect.y -= 25
            else:
                self.back_ground_rect.y += 25

        if self.back_ground_rect.y > 0 and not self.back_ground_timer.active and self.back_ground_direction == 'up':
            self.back_ground_rect.y = 0



    def hats_menu(self):
        self.hat_group.draw(self.screen)
        locked_text = self.button_font.render('LOCKED', False, 'white')
        locked_rect = locked_text.get_rect(topleft = (WINDOW_WIDTH /2 - 30, WINDOW_HEIGHT /2 - 110))

        if pygame.key.get_pressed()[pygame.K_RIGHT] and not self.change_hat_timer.active and not self.active_id == len(self.hat_group) - 1:
            self.active_id += 1
            self.change_hat_timer.activate()
            for sprite in self.hat_group:
                sprite.rect.x -= 350
        elif pygame.key.get_pressed()[pygame.K_LEFT] and not self.change_hat_timer.active and self.active_id != 0:
            self.active_id -= 1
            self.change_hat_timer.activate()
            for sprite in self.hat_group:
                sprite.rect.x += 350




        for sprite in self.hat_group:
            if sprite.id == self.active_id:

                sprite.image = pygame.transform.scale2x(sprite.base_image)

            else:
                sprite.image = sprite.base_image

        if self.active_id == self.main.hat:
            self.screen.blit(self.equipped_button, self.equipped_button_rect)
        else:
            self.screen.blit(self.equip_button, self.equip_button_rect)

        if pygame.key.get_pressed()[pygame.K_RETURN]:
            self.main.hat = self.active_id

        if self.equip_button_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0] and self.main.data[str(self.active_id)]:
            self.main.hat = self.active_id

        if not self.main.data[str(self.active_id)]:
            self.screen.blit(locked_text, locked_rect)


    def title(self):

        self.screen.blit(self.title_text, self.title_text_rect)

    def update(self):
        self.change_hat_timer.update()
        self.screen.fill('black')
        self.back_ground_timer.update()
        self.move_background()
        self.screen.blit(self.back_ground, self.back_ground_rect)
        if not self.back_ground_timer.active:
            if self.main_active:
                self.title()
                self.main_buttons()
            if self.hats_menu_active:
                self.hats_menu()

            self.back()



