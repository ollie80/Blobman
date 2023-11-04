import pygame
from pygame.image import load

from pyautogui import size

# general setup
ZOOM = 4
TILE_SIZE = 32
WINDOW_WIDTH = size()[0]
WINDOW_HEIGHT = size()[1]
DISPLAY_WIDTH = WINDOW_WIDTH / ZOOM
DISPLAY_HEIGHT = WINDOW_HEIGHT / ZOOM

ANIMATION_SPEED = 8

GRASS_COLOUR = '#8a441c'
SKY_COLOUR = '#00E9FF'
CURRENT_ROOM = 1



# health, speed, damage, Coins Dropped

ENEMY_STATS = {
	1: [20, 130, 15, 10],
	2: [5, 200, 15, 25],
	3: [10, 5, 25, 25],
	4: [20, 50, 5, 25]
}


# Health, Damage
BOSS_STATS = {
	'ghost': [80, None],
	'void': [2500, None],
	'demon': [3000, 10]


}

# boosts: Damage, Speed, Cooldown, Coin Multiplier, Special Ability

HAT_STATS = {
	15: [1,1,1, 1, None, 100],
	0: [1.2, 1.2, 0.8, 1, None, 100],
	1: [0.8, 1.3, 0.6, 1, 'dash', 2500],
	2: [1.4, 0.8, 0.6, 1, None, 100],
	3: [1, 1, 1, 3, None, 100],
	4: [1,1,1,1, 'time', 10000],
	5: [2, 1.5, 0.5, 2, None, 100]
}


LEVEL_LAYERS = {
	'map': 0,
	'dirt': 1,
	'grass': 2,
	'shadow': 3,
    'items': 4,
	'enemies': 5,
	'main': 6,
	'particles': 7,
	'weapons': 8,
	'wall': 10,
	'crow': 10,
	'enemy_weapons': 11,
	'decorations': 11,
	'tracking_arrow': 12

}

# weapon stats
# Structure: Damage, Range (Pixels), Shoot Cooldown (Miliseconds), Bullet Speed, Ricochet, Accuracy (Lower Is Better), Bullets Shot, Friction, Does Explode, Explosion Size, Price

WEAPON_STATS =	{
	1: [2, 30, 1000, 10, False, 10, 4, 1, False, None, 100],
	2: [5, 30, 250, 10, False, 3, 1, 1, False, None, 200],
	3: [3, 30, 0, 10, True, 0, 1,1, False, None, 1500],
	4: [80, 30, 1800, 10, False, 0, 1,1, False, None, 500],
	5: [160, 30, 1200, 3, True, 25, 5, 0.98, True, 60, 1250],
	6: [3, 30, 150, 10, False, 2, 1, 1, False, None, 150],
	7: [7, 30, 500, 10, False, 0, 1, 1, False, None, 150],
	8: [1, 30, 30, 10, False, 2, 1, 1, False, None, 150],
	9: [70, 30, 1800, 3, True, 2, 1, 0.98, True, 60, 625],
	10: [0.2, 30, 100, 3, False, 25, 4, 1, False, None, 700],
	11: [4, 30, 500, 8, False, 0, 4, 1, False, None, 450],
	12: [30, 30, 500, 8, False, 0, 4, 1, True, 40, 450],
	13: [4, 30, 99999999999, 8, False, 0, 4, 1, False, None, 150],
	14: [5, 30, 99999999999, 5, False, 0, 1, 1, False, None, 150],
	15: [20, 30, 99999999999, 5, False, 0, 1, 1, False, None, 150]

}





def get_range(sprite):
	rangex = range(sprite.rect.centerx - round(DISPLAY_WIDTH / 2), sprite.rect.centerx + round(DISPLAY_WIDTH /2))
	rangey = range(sprite.rect.centery - round(DISPLAY_HEIGHT / 2), sprite.rect.centery + round(DISPLAY_HEIGHT /2))
	return (rangex, rangey)
