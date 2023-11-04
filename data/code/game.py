import pygame

from pygame.mouse import get_pos
from pygame.image import load
from data.code.settings import *
from data.code.sprites import *

from pygame.math import Vector2 as vector

from data.code.ui import UI
from data.code.timer import Timer


class Game:
    def __init__(self, display_surf, screen, main, level_data, level):
        self.display_surface = display_surf
        self.screen = screen
        self.clock = pygame.time.Clock()


        self.player_graphics = {folder: import_folder(f'data/graphics/player/{folder}') for folder in list(walk('data/graphics/player/'))[0][1]}
        self.boar_graphics = {folder: import_folder(f'data/graphics/enemies/boar/{folder}') for folder in list(walk('data/graphics/enemies/boar/'))[0][1]}
        self.slug_graphics = {folder: import_folder(f'data/graphics/enemies/slug/{folder}') for folder in list(walk('data/graphics/enemies/slug/'))[0][1]}

        self.player = None


        # groups
        self.mouse_rect = pygame.rect.Rect(get_pos()[0], get_pos()[1], 1, 1)
        self.camera_group = CameraGroup(self.display_surface, self.screen)
        self.collision_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.chest_sprites = pygame.sprite.Group()
        self.black_holes = pygame.sprite.GroupSingle()
        self.boss_black_hole = pygame.sprite.GroupSingle()
        self.spawn_sprites = pygame.sprite.Group()
        self.boss_sprites = pygame.sprite.Group()

        self.clock_hat_timer = Timer(600000)
        self.clock_hat_timer.activate()


        self.level_data = level_data


        self.main = main
        self.spawn_enemy_id = 1
        self.main.can_change_room = True
        self.ui = UI(self.display_surface, self.screen, self.main)
        self.pause_timer = Timer(400)


        player_layout = import_csv_layout(level_data['player'])
        self.player = self.player_setup(player_layout)




        wall_layout = import_csv_layout(level_data['wall'])
        self.create_level(wall_layout, 'wall')






        # constraint
        dirt_layout = import_csv_layout(level_data['dirt'])
        self.create_level(dirt_layout, 'dirt')

        # grass setup
        grass_layout = import_csv_layout(level_data['grass'])
        self.create_level(grass_layout, 'grass')

        # chest setup
        chest_layout = import_csv_layout(level_data['chest'])
        self.create_level(chest_layout, 'chest')

        # shadow
        shadow_layout = import_csv_layout(level_data['shadow'])
        self.create_level(shadow_layout, 'shadow')

        # enemies
        enemies_layout = import_csv_layout(level_data['enemies'])
        self.create_level(enemies_layout, 'enemies')


        if level == 3:
            # merchant
            merchant_layout = import_csv_layout(level_data['merchant'])
            self.create_level(merchant_layout, 'merchant')

        # decorations
        decorations_layout = import_csv_layout(level_data['decorations'])
        self.create_level(decorations_layout, 'decorations')

        self.player.active = True


    def create_level(self, layout, type):

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * TILE_SIZE

                    y = row_index * TILE_SIZE

                    if type == 'grass':
                        if val == '0': sprite = StaticTile(TILE_SIZE, x, y, load('data/graphics/terrain/2.png').convert_alpha())
                        if val == '1': sprite = StaticTile(TILE_SIZE, x, y,load('data/graphics/terrain/3.png').convert_alpha())
                        if val == '2': sprite = StaticTile(TILE_SIZE, x, y,load('data/graphics/terrain/0.png').convert_alpha())
                        if val == '3': sprite = StaticTile(TILE_SIZE, x, y,load('data/graphics/terrain/1.png').convert_alpha())
                        if val == '4': sprite = StaticTile(TILE_SIZE, x, y,load('data/graphics/terrain/4.png').convert_alpha())
                        if val == '6': sprite = StaticTile(TILE_SIZE, x, y,load('data/graphics/terrain/9.png').convert_alpha())
                        if val == '7': sprite = StaticTile(TILE_SIZE, x, y,load('data/graphics/terrain/6.png').convert_alpha())
                        if val == '8': sprite = StaticTile(TILE_SIZE, x, y,load('data/graphics/terrain/7.png').convert_alpha())
                        if val == '9': sprite = StaticTile(TILE_SIZE, x, y,load('data/graphics/terrain/8.png').convert_alpha())
                        if val == '10': sprite = StaticTile(TILE_SIZE, x, y,load('data/graphics/terrain/10.png').convert_alpha())
                        if val == '11': sprite = StaticTile(TILE_SIZE, x, y,load('data/graphics/terrain/12.png').convert_alpha())
                        if val == '12': sprite = StaticTile(TILE_SIZE, x, y,load('data/graphics/terrain/13.png').convert_alpha())
                        if val == '13': sprite = StaticTile(TILE_SIZE, x, y, load('data/graphics/terrain/11.png').convert_alpha())


                    if type == 'shadow':
                        sprite = StaticTile(TILE_SIZE, x,y, load('data/graphics/shadow/0.png').convert_alpha(), z= LEVEL_LAYERS['shadow'])

                    if type == 'chest':

                        sprite = Chest((x,y), [self.camera_group, self.chest_sprites], self.player, self.camera_group, self.boss_sprites)

                    if type == 'decorations':
                        if val == '0':
                            sprite = Tree((x,y), self.camera_group, self.collision_sprites, False)
                        if val == '1':
                            sprite = StaticTile(TILE_SIZE, x,y,load('data/graphics/decorations/1.png').convert_alpha(), z = LEVEL_LAYERS['decorations'])
                            self.collision_sprites.add(sprite)
                        if val == '2':
                            sprite = Pumpkin((x,y), self.camera_group, self.collision_sprites)

                        if val == '3':
                            sprite = Lamp((x,y), self.camera_group, self.collision_sprites)

                        if val == '4':
                            sprite = Generic((x,y), load('data/graphics/decorations/4.png').convert_alpha(), [self.camera_group, self.collision_sprites])

                        if val == '5':
                            sprite = Tree((x,y), self.camera_group, self.collision_sprites, True)

                    if type == 'enemies':
                        if val == '0':
                            sprite = Enemy((x,y), self.boar_graphics, [self.camera_group, self.enemy_sprites], self.camera_group, self.collision_sprites,1, self.player, self.black_holes, self.boss_sprites)
                        if val == '1':
                            sprite = SporeSlug((x,y), self.slug_graphics, [self.camera_group, self.enemy_sprites], self.camera_group, self.collision_sprites, self.player, self.black_holes, self.boss_sprites)
                        if val == '2':
                            sprite = Crow((x, y), [self.camera_group, self.enemy_sprites], self.player, self.camera_group)
                        if val == '3':
                            sprite = VoidBoss((x,y), [self.camera_group, self.boss_sprites], self.player, self.camera_group, self.boss_black_hole)
                        if val == '4':
                            sprite = PumpkinEnemy((x,y), [self.camera_group, self.enemy_sprites], self.player, self.camera_group, self.collision_sprites, self.boss_sprites)
                        if val == '5':
                            sprite = GhostBoss((x,y), [self.camera_group, self.boss_sprites], self.player, self.spawn_sprites, self.enemy_sprites, self.camera_group, self.boss_sprites, self.collision_sprites, self.black_holes)
                        if val == '6':

                            sprite = SpawnPoint((x,y), [self.camera_group, self.spawn_sprites], self.spawn_enemy_id, self.player, self.camera_group, self.enemy_sprites, self.collision_sprites, self.black_holes, self.boss_sprites)
                            self.spawn_enemy_id += 1
                            if self.spawn_enemy_id > 3:
                                self.spawn_enemy_id = 1

                        if val == '7':
                            sprite = DemonBoss((x,y), [self.camera_group, self.boss_sprites], self.player, self.camera_group, self.boss_sprites, self.collision_sprites)

                    if type == 'merchant':
                        sprite = Merchant((x,y), self.camera_group, self.player, self.collision_sprites, self.camera_group, self.boss_sprites)

                    if type == 'wall':
                        sprite = Wall((x,y),load('data/graphics/wall/0.png').convert_alpha(),[self.camera_group,self.collision_sprites], self.collision_sprites)
                        self.collision_sprites.add(sprite)

                    if type == 'doors':
                        sprite = Teleporter((x,y), self.camera_group, self.player, self.main)

                    if type == 'dirt':
                        sprite = StaticTile(TILE_SIZE, x, y, load('data/graphics/terrain/5.png').convert_alpha(), z = LEVEL_LAYERS['dirt'])



                    self.camera_group.add(sprite)

    def mouse_rect_update(self):
        self.mouse_rect.center = (get_pos()[0] / ZOOM, get_pos()[1] / ZOOM)

    def escape_menu(self):
        if pygame.key.get_pressed()[pygame.K_ESCAPE] and not self.pause_timer.active:
            self.ui.pause_menu_active = not self.ui.pause_menu_active
            self.pause_timer.activate()


    def player_setup(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                if val == '0':
                    player = Player((x, y), self.camera_group, self.collision_sprites, self.camera_group, self.enemy_sprites, self.player_graphics, self.main,self.black_holes, self.boss_black_hole, self.boss_sprites)

                    return player

    def enemies_killed(self):
        if not self.enemy_sprites and not self.boss_sprites:
            doors_layout = import_csv_layout(self.level_data['doors'])
            self.create_level(doors_layout, 'doors')
            for chest in self.chest_sprites:
                chest.locked = False

    def run(self, dt):

        self.clock_hat_timer.update()
        if not self.clock_hat_timer.active:
            self.main.clock_hat_timer = True
        self.pause_timer.update()
        self.escape_menu()
        if not self.ui.pause_menu_active:
            self.mouse_rect_update()
            self.display_surface.fill(GRASS_COLOUR)
            self.enemies_killed()
            self.camera_group.custom_draw(self.player, self.mouse_rect)
            self.camera_group.update(dt)
        self.ui.update()
        for sprite in self.boss_sprites:
            boss = sprite
            boss_id = sprite.id
        if self.boss_sprites:
            self.ui.boss_bar(boss.health, boss_id)
        self.screen.blit(pygame.transform.scale(self.display_surface, (self.screen.get_size())), (0, 0))



class CameraGroup(pygame.sprite.Group):
    def __init__(self, display_surf, screen):
        super().__init__()
        self.screen = screen
        self.display_surface = display_surf
        self.offset = vector()


    def custom_draw(self, player, mouse_rect):

        self.offset.x = player.rect.centerx - DISPLAY_WIDTH / 2
        self.offset.y = player.rect.centery - DISPLAY_HEIGHT / 2

        range_x = range(player.rect.centerx - WINDOW_WIDTH, player.rect.centerx + WINDOW_WIDTH)
        range_y = range(player.rect.centery - WINDOW_HEIGHT, player.rect.centery + WINDOW_HEIGHT)


        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.z):
            if sprite.z != LEVEL_LAYERS['tracking_arrow']:
                if sprite.rect.centerx in range_x and sprite.rect.centery in range_y:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
            else:
                offset_rect = sprite.rect.copy()
                offset_rect.center -= self.offset
                sprite.offset_rect = offset_rect

                self.display_surface.blit(sprite.image, offset_rect)
