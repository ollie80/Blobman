import pygame
import sys

from pygame.image import load
from data.code.settings import *
from data.code.timer import *
import math
import cmath
from random import randint, randrange, choices
import random
from data.code.support import *


from pygame.math import Vector2 as vector

class Generic(pygame.sprite.Sprite):
	def __init__(self, pos, surf, group ,  z = LEVEL_LAYERS['main']):
		super().__init__(group)
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.z = z

class HatGeneric(pygame.sprite.Sprite):
	def __init__(self, pos, surf, group, id):
		super().__init__(group)
		self.image = surf
		self.rect = self.image.get_rect(center=pos)
		self.id = id
		self.base_image = surf

class Block(Generic):
	def __init__(self, pos, size, group, z=LEVEL_LAYERS['main']):
		surf = pygame.Surface(size)
		surf.set_alpha(0)
		super().__init__(pos, surf, group)

class Tile(pygame.sprite.Sprite):
	def __init__(self,size, x,y, pos, z = LEVEL_LAYERS['grass']):
		super().__init__()
		self.z = z
		self.image = pygame.Surface((size,size))
		self.rect = self.image.get_rect(bottomleft = (x,y))

class Wall(Generic):
	def __init__(self, pos, surf, group, collision_sprites, z=LEVEL_LAYERS['wall']):
		super().__init__(pos, surf, group, z)
		self.rect.bottomleft = pos

class StaticTile(Tile):
	def __init__(self,size,x,y,surface, z = LEVEL_LAYERS['grass'] ):
		super().__init__(size,x,y, z)
		self.image = surface

class Tree(Generic):
	def __init__(self, pos, group, collision_sprites, background):
		if not background:
			surf = load('data/graphics/decorations/0.png').convert_alpha()
		else:
			surf = load('data/graphics/decorations/5.png').convert_alpha()
		super().__init__(pos, surf, group, z = LEVEL_LAYERS['decorations'])
		self.rect.bottomleft = pos
		Block(self.rect.midleft, (64, 16), collision_sprites)

class Lamp(Generic):
	def __init__(self, pos, group, collision_sprites):
		surf = load('data/graphics/decorations/3.png').convert_alpha()
		super().__init__(pos, surf, group, z = LEVEL_LAYERS['decorations'])
		self.rect.bottomleft = pos
		Block((self.rect.centerx - 8, self.rect.centery + 4), (10,10), collision_sprites)

class Pumpkin(Generic):
	def __init__(self, pos, group, collision_sprites):
		surf = load('data/graphics/decorations/2.png').convert_alpha()
		super().__init__(pos, surf, group, z = LEVEL_LAYERS['decorations'])
		self.rect.bottomleft = pos
		Block((self.rect.topleft[0] + 16, self.rect.topleft[1] + 16), (32,16), collision_sprites)

class Animated(Generic):
	def __init__(self, assets, pos, group, z = LEVEL_LAYERS['main']):
		self.animation_frames = assets
		self.frame_index = 0
		self.z = z
		super().__init__(pos, self.animation_frames[self.frame_index], group, z)

	def animate(self, dt):
		self.frame_index += ANIMATION_SPEED * dt
		self.frame_index = 0 if self.frame_index >= len(self.animation_frames) else self.frame_index
		self.image = self.animation_frames[int(self.frame_index)]


	def update(self, dt):
		self.animate(dt)

class Particle(Animated):
	def __init__(self, assets, pos, group):
		super().__init__(assets, pos, group, z = LEVEL_LAYERS['particles'])
		self.rect = self.image.get_rect(center = pos)

	def animate(self, dt):
		self.frame_index += ANIMATION_SPEED * dt
		if self.frame_index < len(self.animation_frames):
			self.image = self.animation_frames[int(self.frame_index)]
		else:
			self.kill()

class Looping_Particle(Animated):
	def __init__(self, assets, pos, group):
		super().__init__(assets, pos, group, z = LEVEL_LAYERS['particles'])
		self.rect = self.image.get_rect(center = pos)

	def animate(self, dt):
		self.frame_index += ANIMATION_SPEED * dt
		if self.frame_index >= len(self.animation_frames):
			self.frame_index = 0
		self.image = self.animation_frames[int(self.frame_index)]

class Gas_Cloud(Particle):
	def __init__(self, size, pos, group, player, damage):
		assets = import_folder(f'data/graphics/gas/{size}')
		super().__init__(assets, pos, group)
		self.player = player
		self.damage = damage


	def attack(self):
		if self.rect.colliderect(self.player.rect):
			self.player.damage(self.damage)

	def update(self, dt):
		self.animate(dt)
		self.attack()

class Hat(Generic):
	def __init__(self, pos, group, id, player):
		surf = load(f'data/graphics/hats/{id}.png')
		super().__init__(pos, surf, group)
		self.player = player
		self.rect.midbottom = self.player.rect.midtop

		self.id = id
		self.stats = HAT_STATS[self.id]

	def update(self, dt):
		self.rect.centerx = self.player.rect.centerx
		self.rect.centery = self.player.rect.centery - 12

class Player(Generic):
	def __init__(self, pos, group, collision_sprites, camera_group, enemy_sprites,assets, main, black_holes, boss_black_holes, boss_sprites):
		# animation
		self.animation_frames = assets
		self.frame_index = 0
		self.status = 'idle'
		self.orientation = 'right'
		surf = self.animation_frames[f'{self.status}_{self.orientation}'][self.frame_index]
		super().__init__(pos, surf, group)

		self.active = False
		self.main = main
		self.camera_group = camera_group
		self.boss_sprites = boss_sprites


		# health and damage
		self.max_health = 100
		self.health = self.max_health
		self.coins = self.main.coins

		# hat
		if self.main.hat != None:
			self.hat = Hat(self.rect.center, self.camera_group, self.main.hat, self)
		else:
			self.hat = None

		# movement
		self.direction = vector()
		self.pos = vector(self.rect.center)
		self.speed = 250 * self.hat.stats[1]
		self.black_hole_speed = 2
		self.gravity = 4
		self.speed_multiplier = 0
		self.old_direction = self.direction
		self.dash_timer = Timer(100)
		self.freeze_timer = Timer(5000)
		self.ability_cooldown = Timer(self.hat.stats[5])

		self.enemy_sprites = enemy_sprites
		self.black_holes = black_holes
		self.boss_black_holes = boss_black_holes

		# collision
		self.collision_sprites = collision_sprites
		self.hitbox = self.rect.inflate(0, 0)


		# weapon
		weapon_1_id = self.main.weapon_1
		weapon_2_id	= self.main.weapon_2
		staff_id = self.main.staff

		self.staff = None

		self.weapon_1 = Weapon(self.rect.center, self.camera_group, self, self.camera_group, self.collision_sprites, True, weapon_1_id, self.enemy_sprites, self.black_holes, self.boss_sprites)
		if weapon_2_id == None:
			self.weapon_2 =	None
		else:
			self.weapon_2 = Weapon(self.rect.center, self.camera_group, self, self.camera_group, self.collision_sprites,False, weapon_2_id, self.enemy_sprites, self.black_holes, self.boss_sprites)
		if not staff_id == None:
			self.staff = Weapon(self.rect.center, self.camera_group, self, self.camera_group, self.collision_sprites, True, staff_id, self.enemy_sprites, self.black_holes,self.boss_sprites, staff=True)





		# dash

		self.pick_up_cooldown = Timer(500)
		self.drop_cooldown = Timer(400)
		self.invul_timer = Timer(200)

		item_rect_surf = pygame.surface.Surface((100,100))
		self.item_rect = item_rect_surf.get_rect(center = self.rect.center)

		self.despawn_block = Block(self.rect.center, (DISPLAY_WIDTH * 2, DISPLAY_HEIGHT * 2), self.camera_group)

	def get_status(self):
		if self.direction.x == 0 and self.direction.y == 0:
			self.status = 'idle'
		elif self.direction.x != 0:
			self.status = 'walk'
		elif self.direction.y != 0:
			self.status = 'walk'

	def apply_max_health(self):
		if self.main.player_health >= self.main.player_max_health:
			self.main.player_health = self.main.player_max_health



	def animate(self, dt):
		global ANIMATION_SPEED
		self.current_animation = self.animation_frames[f'{self.status}_{self.orientation}']
		self.frame_index += ANIMATION_SPEED * dt
		if self.frame_index >= len(self.current_animation):
			self.frame_index = 0
		self.image = self.current_animation[int(self.frame_index)]

	def apply_ability(self):
		if self.dash_timer.active:
			self.speed = 1000
		elif self.freeze_timer.active:
			self.speed = 150
		else:
			self.speed = self.speed = 250 * self.hat.stats[1]



	def input(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]:

			if keys[pygame.K_a]:
				self.direction.x = -1
				self.orientation = 'left'
			elif keys[pygame.K_d]:
				self.direction.x = 1
				self.speed_multiplier = 1
				self.orientation = 'right'
			else:
				self.direction.y = 0

			if keys[pygame.K_w]:
				self.direction.y = -1

			elif keys[pygame.K_s]:
				self.direction.y = 1
			else:
				self.direction.y = 0

			if keys[pygame.K_d] and keys[pygame.K_a]:
				self.direction.x = 0
			if keys[pygame.K_w] and keys[pygame.K_s]:
				self.direction.y = 0

		else:
			self.direction.x = 0
			self.direction.y = 0

	def ability(self):
		if pygame.key.get_pressed()[pygame.K_SPACE] and not self.ability_cooldown.active:
			ability = HAT_STATS[self.hat.id][4]
			if ability != None:
				if ability == 'dash':

					self.dash_timer.activate()

				if ability == 'time':

					self.freeze_timer.activate()



			self.ability_cooldown.activate()



	def drop(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_q] and not self.drop_cooldown.active:
			self.drop_cooldown.activate()
			if self.weapon_2 != None:
				Item(self.rect.midbottom, self.camera_group, 'weapons', str(self.weapon_2.id), self, self.camera_group, self.boss_sprites)
				self.weapon_2.kill()
				self.weapon_2 = None
				self.main.weapon_2 = None
			elif self.staff != None:
				Item(self.rect.midbottom, self.camera_group, 'weapons', str(self.staff.id), self, self.camera_group, self.boss_sprites)
				self.staff.kill()
				self.staff = None
				self.main.staff = None
			else:
				if self.weapon_1 != None:
					Item(self.rect.midbottom, self.camera_group, 'weapons', str(self.weapon_1.id), self, self.camera_group, self.boss_sprites)
					self.main.weapon_1 = None
					self.weapon_1.kill()
					self.weapon_1 = None


	def damage(self, damage):
		if not self.invul_timer.active:
			self.main.player_health -= damage
			self.invul_timer.activate()



	def move(self, dt):

		# horizontal movement
		self.pos.x += self.direction.x * self.speed * dt
		self.hitbox.centerx = round(self.pos.x)
		self.rect.centerx = self.hitbox.centerx
		self.collision('horizontal')


		# vertical movement

		self.pos.y += self.direction.y * self.speed * dt
		self.hitbox.centery = round(self.pos.y)
		self.rect.centery = self.hitbox.centery
		self.collision('vertical')

		self.item_rect.center = self.rect.center
		self.despawn_block.rect.center = self.rect.center

	def collision(self, direction):
		for sprite in self.collision_sprites:
			if sprite.rect.colliderect(self.hitbox):
				if direction == 'horizontal':
					self.hitbox.right = sprite.rect.left if self.direction.x > 0 else self.hitbox.right
					self.hitbox.left = sprite.rect.right if self.direction.x < 0 else self.hitbox.left
					self.rect.centerx, self.pos.x = self.hitbox.centerx, self.hitbox.centerx
				else:  # vertical
					self.hitbox.top = sprite.rect.bottom if self.direction.y < 0 else self.hitbox.top
					self.hitbox.bottom = sprite.rect.top if self.direction.y > 0 else self.hitbox.bottom
					self.rect.centery, self.pos.y = self.hitbox.centery, self.hitbox.centery
					self.direction.y = 0


	def calculate_new_xy(self, old_xy, speed, angle_in_degrees):
		move_vec = pygame.math.Vector2()
		move_vec.from_polar((speed, angle_in_degrees))
		return old_xy + move_vec


	def death(self):

		if self.health <= 0:
			self.main.menu_active = True
			self.main.main_menu.main_active = True
			self.main.game_active = False
			self.main.reset()


	def update(self, dt):
		if self.active:
			self.apply_ability()
			self.ability()
			self.apply_max_health()
			self.health = self.main.player_health
			self.coins = self.main.coins
			self.death()
			self.invul_timer.update()
			self.get_status()
			self.animate(dt)
			self.drop()
			self.drop_cooldown.update()
			self.pick_up_cooldown.update()
			self.ability_cooldown.update()
			self.dash_timer.update()
			self.freeze_timer.update()
			self.input()
			self.move(dt)

			if self.boss_black_holes:

				for sprite in self.boss_black_holes:
					rel_x, rel_y = sprite.rect.centerx - self.rect.centerx, sprite.rect.centery - self.rect.centery
					self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)

				self.pos = self.calculate_new_xy(self.pos, self.black_hole_speed, -self.angle)
				self.rect.center = round(self.pos[0]), round(self.pos[1])
				self.death()

class VoidBoss(Generic):
	def __init__(self, pos, group, player, camera_group, boss_black_holes):
		super().__init__(pos, load('data/graphics/boss/singularity_sorcerer/0.png'), group)
		self.player = player
		self.phase = 1
		self.attack_timer = Timer(3000)
		self.attack_angle = 0
		self.camera_group = camera_group
		self.boss_black_hole = boss_black_holes

	def update_angle(self):
		rel_x, rel_y = self.player.rect.centerx - self.rect.centerx, self.player.rect.midbottom[1] - self.rect.centery

		self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)


	def attack(self):
		if not self.attack_timer.active:
			rand = random.choices(population=[1,2] , weights=(1, 1), k=1)[0]
			if rand == 1:
				BossBlackHole(self.rect.center, [self.camera_group, self.boss_black_hole], self.player, self.angle)
			elif rand == 2:
				pass
			self.attack_timer.activate()

	def update(self, dt):
		self.update_angle()
		self.attack_timer.update()
		self.attack()

class GhostBoss(Generic):
	def __init__(self, pos, group, player, spawn_sprites, enemy_sprites, camera_group, boss_sprites, collision_sprites, black_holes):
		surf = load('data/graphics/boss/ghost/0.png')
		super().__init__(pos, surf, group)
		self.id = 'ghost'
		self.spawn_sprites = spawn_sprites
		self.enemy_sprites = enemy_sprites
		self.player = player
		self.base_y = self.rect.y
		self.health = 80
		self.black_holes = black_holes
		self.can_take_damage = False
		self.spawn_timer = Timer(5500)
		self.spawn_timer.activate()
		self.camera_group = camera_group
		self.boss_sprites = boss_sprites
		self.collision_sprites = collision_sprites
		self.staff = EnemyGun(self.rect.center, self.camera_group, self.player, self, self.camera_group, self.collision_sprites, 15, True)
		self.boar_graphics = {folder: import_folder(f'data/graphics/enemies/boar/{folder}') for folder in list(walk('data/graphics/enemies/boar/'))[0][1]}

	def move(self):
		self.rect.y = self.base_y + 10 * math.sin(pygame.time.get_ticks() / 150)

	def death(self):
		if self.health <= 0:
			Item(self.rect.center, self.camera_group, 'weapons', '15', self.player, self.camera_group, self.boss_sprites)
			self.staff.kill()
			self.kill()
			for sprite in self.enemy_sprites:
				sprite.health = 0

	def spawn(self):
		if  not self.spawn_timer.active:
			for i in range(2):

				sprite = self.spawn_sprites.sprites()[randint(0, len(self.spawn_sprites) - 1)]


				sprite.spawn()

			Enemy(self.rect.center, self.boar_graphics, [self.camera_group, self.enemy_sprites], self.camera_group, self.collision_sprites, 1, self.player, self.black_holes, self.boss_sprites)

			self.spawn_timer.activate()

	def update(self, dt):
		self.death()
		self.spawn_timer.update()
		self.spawn()
		self.move()

class SpawnPoint(Generic):
	def __init__(self, pos, group, id, player, camera_group, enemy_sprites, collision_sprites, black_holes, boss_sprites):

		surf = pygame.surface.Surface((1,1))
		surf.set_alpha(0)
		super().__init__(pos, surf, group)
		self.id = id
		self.boss_sprites = boss_sprites
		self.camera_group = camera_group
		self.enemy_sprites = enemy_sprites
		self.collision_sprites = collision_sprites
		self.player = player
		self.black_holes = black_holes
		self.boar_graphics = {folder: import_folder(f'data/graphics/enemies/boar/{folder}') for folder in list(walk('data/graphics/enemies/boar/'))[0][1]}
		self.slug_graphics = {folder: import_folder(f'data/graphics/enemies/slug/{folder}') for folder in list(walk('data/graphics/enemies/slug/'))[0][1]}
		self.colliding = False


	def spawn(self):
		for sprite in self.enemy_sprites:
			if sprite.rect.colliderect(self.rect):
				self.colliding = True
			else:
				self.colliding = False
		if not self.colliding:
			if self.id == 1:
				Enemy(self.rect.center, self.boar_graphics, [self.camera_group, self.enemy_sprites], self.camera_group, self.collision_sprites, 1, self.player, self.black_holes, self.boss_sprites)
			if self.id == 2:
				SporeSlug(self.rect.center, self.slug_graphics, [self.camera_group, self.enemy_sprites], self.camera_group, self.collision_sprites, self.player, self.black_holes, self.boss_sprites)
			if self.id == 3:
				PumpkinEnemy(self.rect.center, [self.camera_group, self.enemy_sprites], self.player, self.camera_group, self.collision_sprites, self.boss_sprites)

class Weapon(Generic):
	def __init__(self, pos, group, player, camera_group, collision_sprites, weapon_1, id, enemy_sprites, black_holes, boss_sprites, staff = False):
		self.player = player
		self.id = id
		self.base_image = load(f'data/graphics/weapons/{self.id}.png').convert_alpha()
		surf = load(f'data/graphics/weapons/{self.id}.png').convert_alpha()
		super().__init__(pos, surf, group, z=LEVEL_LAYERS['weapons'])
		self.mouse_rect = None
		self.angle = 0
		self.boss_sprites = boss_sprites


		# groups
		self.camera_group = camera_group
		self.collision_sprites = collision_sprites
		self.enemy_sprites = enemy_sprites
		self.black_holes = black_holes

		# cooldown
		self.cooldown_timer = Timer(WEAPON_STATS[self.id][2] * self.player.hat.stats[2])

		# dual wielding
		if not staff and weapon_1:
			self.weapon_1 = weapon_1
		else:
			self.weapon_1 = False

		self.staff = staff


	def position(self):
		if self.weapon_1:
			self.rect.center = (self.player.rect.midright[0] + 2, self.player.rect.midright[1] + 10 )
		elif self.staff:
			self.rect.center = (self.player.rect.midbottom[0], self.player.rect.midbottom[1] + 10)
		else:
			self.rect.center = (self.player.rect.midleft[0] + 2, self.player.rect.midleft[1] + 10 )


	def rotate(self):

			mouse_x = pygame.mouse.get_pos()[0]
			mouse_y = pygame.mouse.get_pos()[1]
			rel_x, rel_y = mouse_x - WINDOW_WIDTH /2, mouse_y - WINDOW_HEIGHT /2
			self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
			self.image = pygame.transform.rotate(self.base_image, int(self.angle))
			self.rect = self.image.get_rect(center = self.rect.center)




	def shoot(self):
		if pygame.mouse.get_pressed()[0] and not self.cooldown_timer.active:
			self.cooldown_timer.activate()
			for i in range(WEAPON_STATS[self.id][6]):
				if WEAPON_STATS[self.id][4] == True:
					Projectile(self.rect.center, self.camera_group, self.id, self.angle, self.collision_sprites, self.camera_group, True, self.enemy_sprites, self.player, self.boss_sprites)
				elif self.id == 10:
					FireProjectile(self.rect.center, self.camera_group, self.player, self.angle, self.enemy_sprites)
				elif self.id == 13:
					TrackingRock(self.rect.center, self.camera_group, self.player, self.enemy_sprites)
				elif self.id == 14:
					BlackHole(self.rect.center, [self.camera_group, self.black_holes], self.player, self.angle, self.enemy_sprites)
				elif self.id == 15:
					Minion(self.rect.center, self.camera_group, self.player, self.collision_sprites, self.enemy_sprites)
				else:
					Projectile(self.rect.center, self.camera_group, self.id, self.angle, self.collision_sprites, self.camera_group, False, self.enemy_sprites, self.player, self.boss_sprites)


	def update(self, dt):
		self.rotate()
		self.cooldown_timer.update()
		self.shoot()
		self.position()

class Projectile(Generic):
	def __init__(self, pos, group, weapon_id, angle, collision_sprites, camera_sprites, ricochet, enemy_sprites, player, boss_sprites):
		self.id = weapon_id
		self.base_image = load(f'data/graphics/projectiles/{self.id}.png').convert_alpha()
		surf = load(f'data/graphics/projectiles/{self.id}.png').convert_alpha()
		super().__init__(pos, surf, group)

		self.player = player
		self.boss_sprites = boss_sprites
		# movement
		self.speed = WEAPON_STATS[self.id][3]
		self.base_speed = self.speed
		self.friction = WEAPON_STATS[self.id][7]
		self.angle = angle + randint(-WEAPON_STATS[self.id][5], WEAPON_STATS[self.id][5])
		self.pos = pos
		self.damage = WEAPON_STATS[self.id][0] * player.hat.stats[0]

		# groups
		self.collision_sprites = collision_sprites
		self.camera_sprites = camera_sprites
		self.enemy_sprites = enemy_sprites

		# ricochet
		self.ricochet = ricochet
		self.has_ricocheted = False

		# explosion
		self.does_exlpode = WEAPON_STATS[self.id][8]
		if self.does_exlpode:
			self.explosion_timer = Timer(1000)
			self.explosion_timer.activate()
			self.explosion_rect = self.rect.inflate(+WEAPON_STATS[self.id][9], +WEAPON_STATS[self.id][9])

		self.image = pygame.transform.rotate(self.base_image, int(self.angle))
		self.rect = self.image.get_rect(center=self.rect.center)


	def flip_angle(self):
		self.angle = -self.angle
		self.has_ricocheted = True

	def rotate(self):
			self.image = pygame.transform.rotate(self.base_image, int(self.angle))
			self.rect = self.image.get_rect(center = self.rect.center)


	def calculate_new_xy(self, old_xy, speed, angle_in_degrees):
		move_vec = pygame.math.Vector2()
		move_vec.from_polar((speed, angle_in_degrees))
		return old_xy + move_vec

	def collision(self):
		for sprite in self.collision_sprites:
			if sprite.rect.colliderect(self.rect):
				if self.ricochet and (not self.has_ricocheted or self.does_exlpode):
					self.flip_angle()
				elif self.does_exlpode:
					Particle(import_folder('data/graphics/particles/large_explosion'), self.rect.center, self.camera_sprites)
					self.kill()
				else:
					Particle(import_folder('data/graphics/particles/small_explosion'), self.rect.center, self.camera_sprites)

					self.kill()

	def attack(self):
		for sprite in self.enemy_sprites:
			if sprite.rect.colliderect(self.rect):
				if not self.does_exlpode:
					sprite.health -= self.damage
					Particle(import_folder('data/graphics/particles/small_explosion'), self.rect.center, self.camera_sprites)
					self.kill()
				else:
					sprite.health -= self.damage
					Particle(import_folder('data/graphics/particles/large_explosion'), self.rect.center, self.camera_sprites)
					self.kill()
		if self.boss_sprites:
			for sprite in self.boss_sprites:
				if sprite.can_take_damage:
					if sprite.rect.colliderect(self.rect):
						if not self.does_exlpode:
							sprite.health -= self.damage
							Particle(import_folder('data/graphics/particles/small_explosion'), self.rect.center,
									 self.camera_sprites)
							self.kill()
						else:
							sprite.health -= self.damage
							Particle(import_folder('data/graphics/particles/large_explosion'), self.rect.center,
									 self.camera_sprites)
							self.kill()






	def explode(self):
		for enemy in self.enemy_sprites:
			if enemy.rect.colliderect(self.explosion_rect):
				enemy.health -= self.damage
		Particle(import_folder('data/graphics/particles/large_explosion'), self.rect.center, self.camera_sprites)
		self.kill()



	def update(self, dt):
		if not self.player.freeze_timer.active:
			self.rotate()
			self.attack()

			if self.does_exlpode:
				self.explosion_timer.update()
				self.explosion_rect.center = self.rect.center
			if self.does_exlpode and not self.explosion_timer.active:
				self.explode()
			if self.friction != 0:
				self.speed *= self.friction
			self.collision()
			self.pos = self.calculate_new_xy(self.pos, self.speed, -self.angle)
			self.rect.center = round(self.pos[0]), round(self.pos[1])

class FireProjectile(Particle):
	def __init__(self, pos, group, player, angle, enemy_sprites):
		super().__init__(import_folder('data/graphics/particles/large_explosion'), pos, group)
		self.speed = 3
		self.player = player
		self.angle = angle + randint(-WEAPON_STATS[10][5],  WEAPON_STATS[10][5])
		self.pos = pos
		self.damage = WEAPON_STATS[10][0] *  player.hat.stats[0]
		self.enemy_sprites = enemy_sprites

	def calculate_new_xy(self, old_xy, speed, angle_in_degrees):
		move_vec = pygame.math.Vector2()
		move_vec.from_polar((speed, angle_in_degrees))
		return old_xy + move_vec



	def attack(self):
		for sprite in self.enemy_sprites:
			if self.rect.colliderect(sprite.rect):
				sprite.health -= self.damage


	def update(self, dt):
		if not self.player.freeze_timer.active:
			self.attack()
			self.animate(dt)
			self.pos = self.calculate_new_xy(self.pos, self.speed, -self.angle)
			self.rect.center = round(self.pos[0]), round(self.pos[1])

class BlackHole(Looping_Particle):
	def __init__(self, pos, group, player, angle, enemy_sprites):
		super().__init__(import_folder('data/graphics/particles/black_hole'), pos, group)
		self.player = player
		self.speed = 3
		self.angle = angle
		self.pos = pos
		self.kills = 0
		self.damage = WEAPON_STATS[14][0] * player.hat.stats[0]
		self.enemy_sprites = enemy_sprites

	def calculate_new_xy(self, old_xy, speed, angle_in_degrees):
		move_vec = pygame.math.Vector2()
		move_vec.from_polar((speed, angle_in_degrees))
		return old_xy + move_vec

	def attack(self):
		for sprite in self.enemy_sprites:
			if self.rect.colliderect(sprite.rect):
				sprite.health -= self.damage
				if sprite.health <= 0:
					self.kills += 1


	def update(self, dt):
		if not self.player.freeze_timer.active:
			if self.kills >= 2:
				self.kill()
			self.attack()
			self.animate(dt)
			self.pos = self.calculate_new_xy(self.pos, self.speed, -self.angle)
			self.rect.center = round(self.pos[0]), round(self.pos[1])
			self.speed *= 0.98

class BossBlackHole(Looping_Particle):
	def __init__(self, pos, group, player, angle):
		super().__init__(import_folder('data/graphics/particles/black_hole'), pos, group)
		self.speed = 3
		self.angle = angle
		self.pos = pos
		self.damage = WEAPON_STATS[14][0]
		self.player = player
		self.death_timer = Timer(900)
		self.death_timer.activate()


	def calculate_new_xy(self, old_xy, speed, angle_in_degrees):
		move_vec = pygame.math.Vector2()
		move_vec.from_polar((speed, angle_in_degrees))
		return old_xy + move_vec



	def attack(self):
		if self.rect.colliderect(self.player.rect):
			self.player.main.player_health -= self.damage


	def update(self, dt):
		if not self.player.freeze_timer.active:
			self.death_timer.update()
			if not self.death_timer.active:
				self.kill()
			self.attack()
			self.animate(dt)
			self.pos = self.calculate_new_xy(self.pos, self.speed, -self.angle)
			self.rect.center = round(self.pos[0]), round(self.pos[1])
			self.speed *= 0.98

class TrackingRock(Generic):
	def __init__(self, pos, group, player, enemy_sprites):
		self.base_image = load('data/graphics/boss_rocks/1.png').convert_alpha()
		super().__init__(pos, load('data/graphics/boss_rocks/1.png').convert_alpha(), group, z=LEVEL_LAYERS['tracking_arrow'])
		self.speed = 4
		self.angle = 0
		self.pos = pos
		self.damage = WEAPON_STATS[10][0]
		self.enemy_sprites = enemy_sprites
		self.base_speed= self.speed
		self.reset_speed = False
		self.multiplier = 1.005
		self.offset_rect = None


	def calculate_new_xy(self, old_xy, speed, angle_in_degrees):
		move_vec = pygame.math.Vector2()
		move_vec.from_polar((speed, angle_in_degrees))
		return old_xy + move_vec

	def rotate(self):
		mouse_x = pygame.mouse.get_pos()[0] / ZOOM
		mouse_y = pygame.mouse.get_pos()[1] / ZOOM
		rel_x, rel_y = mouse_x - self.offset_rect.centerx, mouse_y - self.offset_rect.centery
		self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
		self.image = pygame.transform.rotate(self.base_image, int(self.angle))
		self.rect = self.image.get_rect(center = self.rect.center)

	def attack(self):
		for sprite in self.enemy_sprites:
			if self.rect.colliderect(sprite.rect):
				sprite.health -= self.damage

	def check_speed(self):
		if self.offset_rect.collidepoint([pygame.mouse.get_pos()[0] / ZOOM, pygame.mouse.get_pos()[1] / ZOOM]):
			self.speed = 0
			self.reset_speed = True
		else:
			if self.reset_speed:
				self.speed = self.base_speed
				self.reset_speed = False
			self.speed *= self.multiplier


	def update(self, dt):
		self.rotate()
		self.attack()
		self.check_speed()
		self.pos = self.calculate_new_xy(self.pos, self.speed, -self.angle)
		self.rect.center = round(self.pos[0]), round(self.pos[1])

class Item(Generic):
	def __init__(self, pos, group, category, id, player, camera_group, boss_sprites, z=LEVEL_LAYERS['items']):
		self.category = category
		self.id = id

		self.highlight_image = load(f'data/graphics/highlight/{self.category}/{self.id}.png').convert_alpha()
		self.base_image = load(f'data/graphics/items/{self.category}/{self.id}.png').convert_alpha()
		surf = load(f'data/graphics/items/{self.category}/{self.id}.png').convert_alpha()
		super().__init__(pos, surf,group, z)
		self.player = player
		self.camera_group = camera_group
		self.mask = pygame.mask.from_surface(self.image)
		self.boss_sprites = boss_sprites


	def pick_up(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_e] and not self.player.pick_up_cooldown.active and self.rect.colliderect(self.player.rect):
			if self.category == 'weapons':
				if not (self.id == '13'  or self.id == '14' or self.id == '15'):
					if self.player.weapon_1 == None:
						self.player.weapon_1 = Weapon(self.player.rect.center, self.camera_group, self.player,self.camera_group, self.player.collision_sprites, True, int(self.id), self.player.enemy_sprites, self.player.black_holes, self.boss_sprites)
						self.kill()
						self.player.pick_up_cooldown.activate()
						self.player.main.weapon_1 = int(self.id)


					elif self.player.weapon_2 != None:
						self.kill()
						self.player.weapon_2.kill()
						Item(self.player.rect.midbottom, self.camera_group, 'weapons', self.player.weapon_2.id, self.player, self.camera_group, self.boss_sprites)
						self.player.weapon_2 = Weapon(self.player.rect.center, self.camera_group, self.player,self.camera_group, self.player.collision_sprites, False, int(self.id),self.player.enemy_sprites, self.player.black_holes, self.boss_sprites)
						self.player.pick_up_cooldown.activate()
						self.player.main.weapon_2 = int(self.id)


					elif self.player.weapon_2 == None:
						self.player.weapon_2 = Weapon(self.player.rect.center, self.camera_group, self.player, self.camera_group, self.player.collision_sprites, False, int(self.id), self.player.enemy_sprites, self.player.black_holes, self.boss_sprites)
						self.kill()
						self.player.pick_up_cooldown.activate()
						self.player.main.weapon_2 = int(self.id)
				else:

					if self.player.staff == None:
						self.player.staff = Weapon(self.player.rect.center, self.camera_group, self.player,self.camera_group, self.player.collision_sprites, True, int(self.id), self.player.enemy_sprites, self.player.black_holes, self.boss_sprites, True)
						self.kill()
						self.player.pick_up_cooldown.activate()
						self.player.main.staff = int(self.id)
					else:
						self.player.staff = Weapon(self.player.rect.center, self.camera_group, self.player, self.camera_group, self.player.collision_sprites, True, int(self.id), self.player.enemy_sprites, self.player.black_holes, self.boss_sprites , True)
						self.kill()
						self.player.pick_up_cooldown.activate()
						self.player.main.staff = int(self.id)
						Item(self.player.rect.midbottom, self.camera_group, 'weapons', self.player.staff.id, self.player, self.camera_group, self.boss_sprites)

			elif self.category == 'heal':
				self.player.main.player_health += 25
				self.kill()

	def highlight(self):
		if self.player.rect.colliderect(self.rect):
			self.image = self.highlight_image

		else:
			self.image = self.base_image

	def update(self, dt):

		self.pick_up()
		self.highlight()

class Enemy(Generic):
	def __init__(self, pos,assets, group, camera_group, collision_sprites, id, player, black_holes, boss_sprites):
		# animation
		self.animation_frames = assets
		self.frame_index = 0
		self.status = 'idle'
		self.orientation = 'left'
		surf = self.animation_frames[f'{self.status}_{self.orientation}'][self.frame_index]
		super().__init__(pos, surf, group, z=LEVEL_LAYERS['enemies'])
		self.id = id
		self.camera_group = camera_group
		self.black_holes = black_holes
		self.boss_sprites = boss_sprites


		# attacking
		self.player = player
		self.health = ENEMY_STATS[self.id][0] * self.player.main.room_multiplier
		self.damage = ENEMY_STATS[self.id][2] * self.player.main.room_multiplier
		self.attacking = False
		self.attack_block = Block(self.rect.center, (400, 400), camera_group)

		# movement
		self.collision_sprites = collision_sprites
		self.hitbox = self.rect.inflate(0, 0)
		self.direction = vector()
		self.pos = vector(self.rect.center)
		self.speed = ENEMY_STATS[self.id][1]
		self.base_speed = ENEMY_STATS[self.id][1]



	def get_status(self):
		if self.direction.x == 0 and self.direction.y == 0:
			self.status = 'idle'
		elif self.direction.x != 0:
			self.status = 'walk'
		elif self.direction.y != 0:
			self.status = 'walk'


	def animate(self, dt):
		global ANIMATION_SPEED
		self.current_animation = self.animation_frames[f'{self.status}_{self.orientation}']
		self.frame_index += ANIMATION_SPEED * dt
		if self.frame_index >= len(self.current_animation):
			self.frame_index = 0
		self.image = self.current_animation[int(self.frame_index)]

	def check_movement(self):
		if self.attacking:
			if self.rect.x != self.player.rect.x:
				if self.rect.x < self.player.rect.x -5:
					self.direction.x = 1
					self.orientation = 'right'
				elif self.rect.x > self.player.rect.x +5:
					self.direction.x = -1
					self.orientation = 'left'
				else:
					self.direction.y = 0
			if self.rect.y != self.player.rect.y:
				if self.rect.y < self.player.rect.y -5:
					self.direction.y = 1
				elif self.rect.y > self.player.rect.y +5:
					self.direction.y = -1
				else:
					self.direction.y = 0


	def calculate_new_xy(self, old_xy, speed, angle_in_degrees):
		move_vec = pygame.math.Vector2()
		move_vec.from_polar((speed, angle_in_degrees))
		return old_xy + move_vec


	def check_attacking(self):
		if self.player.rect.colliderect(self.attack_block.rect):
			self.attacking = True

	def move(self, dt):

		# horizontal movement
		self.pos.x += self.direction.x * self.speed * dt
		self.hitbox.centerx = round(self.pos.x)
		self.rect.centerx = self.hitbox.centerx
		self.collision('horizontal')

		# vertical movement

		self.pos.y += self.direction.y * self.speed * dt
		self.hitbox.centery = round(self.pos.y)
		self.rect.centery = self.hitbox.centery
		self.collision('vertical')

		self.attack_block.rect.center = self.rect.center



	def collision(self, direction):
		for sprite in self.collision_sprites:
			if sprite.rect.colliderect(self.hitbox):
				if direction == 'horizontal':
					self.hitbox.right = sprite.rect.left if self.direction.x > 0 else self.hitbox.right
					self.hitbox.left = sprite.rect.right if self.direction.x < 0 else self.hitbox.left
					self.rect.centerx, self.pos.x = self.hitbox.centerx, self.hitbox.centerx
				else:  # vertical
					self.hitbox.top = sprite.rect.bottom if self.direction.y < 0 else self.hitbox.top
					self.hitbox.bottom = sprite.rect.top if self.direction.y > 0 else self.hitbox.bottom
					self.rect.centery, self.pos.y = self.hitbox.centery, self.hitbox.centery
					self.direction.y = 0

	def attack(self):
		if self.player.rect.colliderect(self.rect):
			self.player.damage(self.damage)



	def death(self):
		if self.health <= 0:
			Coin(self.rect.center, self.camera_group, self.player, ENEMY_STATS[self.id][3])
			if randint(0, 100) >= 70:
				Item(self.rect.center, self.camera_group, 'heal', '0', self.player, self.camera_group, self.boss_sprites)
			if self.boss_sprites:
				for sprite in self.boss_sprites:
					sprite.health -= 10
			self.player.main.kills += 1
			self.kill()

	def update(self, dt):
		if not self.player.freeze_timer.active:
			if self.black_holes:
				self.speed = 7
				for sprite in self.black_holes:
					rel_x, rel_y = sprite.rect.centerx - self.rect.centerx, sprite.rect.centery - self.rect.centery
					self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)

				self.pos = self.calculate_new_xy(self.pos, self.speed, -self.angle)
				self.rect.center = round(self.pos[0]), round(self.pos[1])
				self.speed *= 1.08
				self.death()

			else:

				self.attack()
				self.check_attacking()
				self.get_status()
				if not self.player.freeze_timer.active:
					self.animate(dt)
				self.move(dt)
				self.check_movement()
				self.death()

class SporeSlug(Enemy):
	def __init__(self, pos, assets, group, camera_group, collision_sprites, player, black_holes, boss_sprites):
		super().__init__(pos, assets, group, camera_group, collision_sprites, 2, player, black_holes, boss_sprites)
		self.camera_group = camera_group


	def attack(self):
		if self.player.rect.colliderect(self.rect):
			Gas_Cloud('small', self.rect.center, self.camera_group, self.player, self.damage)
			self.kill()
	def death(self):
		if self.health <= 0:
			Gas_Cloud('small', self.rect.center, self.camera_group, self.player, self.damage)
			Coin(self.rect.center, self.camera_group, self.player, ENEMY_STATS[self.id][3])
			if randint(0, 100) >= 70:
				Item(self.rect.center, self.camera_group, 'heal', '0', self.player, self.camera_group, self.boss_sprites)
			if self.boss_sprites:
				for sprite in self.boss_sprites:
					sprite.health -= 10
			self.player.main.kills += 1
			self.kill()

class Crow(Generic):
	def __init__(self, pos, group, player, camera_group):
		surf = load('data/graphics/enemies/crow/0.png').convert_alpha()
		super().__init__(pos, surf, group, z=LEVEL_LAYERS['crow'])
		self.base_image = surf
		self.player = player
		self.camera_group = camera_group
		self.swoop_timer = Timer(3500)
		self.swoop_timer.activate()
		self.angle = 0
		self.health = ENEMY_STATS[3][0]  * self.player.main.room_multiplier
		self.speed = ENEMY_STATS[3][1]
		self.pos = pos
		self.damage = ENEMY_STATS[3][2] * self.player.main.room_multiplier



	def rotate(self):
		rel_x, rel_y = self.player.rect.centerx - self.rect.centerx, self.player.rect.midbottom[1] - self.rect.centery

		self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)

		self.image = pygame.transform.rotate(self.base_image, int(self.angle))
		self.rect = self.image.get_rect(center=self.rect.center)

	def calculate_new_xy(self, old_xy, speed, angle_in_degrees):
		move_vec = pygame.math.Vector2()
		move_vec.from_polar((speed, angle_in_degrees))
		return old_xy + move_vec

	def attack(self):
		if self.rect.colliderect(self.player.rect):
			self.player.damage(self.damage)

	def despawn(self):
		if not self.rect.colliderect(self.player.despawn_block.rect):
			self.kill()

	def death(self):
		if self.health <= 0:
			Coin(self.rect.center, self.camera_group, self.player, ENEMY_STATS[3][3])
			self.player.main.kills += 1
			self.kill()



	def update(self,dt):
		self.death()
		self.despawn()
		if not self.player.freeze_timer.active:
			self.swoop_timer.update()
			if self.swoop_timer.active:
				self.rotate()
			else:
				self.attack()
				self.pos = self.calculate_new_xy(self.pos, self.speed, -self.angle)
				self.rect.center = round(self.pos[0]), round(self.pos[1])

class PumpkinEnemy(Generic):
	def __init__(self, pos, group, player, camera_group, collision_sprites, boss_sprites):
		surf = load('data/graphics/enemies/pumpkin/0.png').convert_alpha()
		super().__init__(pos, surf,group)
		self.id = 4
		self.player = player
		self.health = ENEMY_STATS[self.id][0] * self.player.main.room_multiplier
		self.boss_sprites = boss_sprites
		self.camera_group = camera_group
		self.collision_sprites = collision_sprites
		self.weapon = EnemyGun(self.rect.center, self.camera_group, self.player, self, self.camera_group, self.collision_sprites, 2, False)


	def death(self):
		if self.health <= 0:
			if self.boss_sprites:
				for sprite in self.boss_sprites:
					sprite.health -= 10
			self.player.main.kills += 1

			self.kill()
			self.weapon.kill()


	def update(self, dt):
		self.death()

class EnemyGun(Generic):
	def __init__(self, pos, group, player, parent, camera_group, collision_sprites, id, prop):
		surf = load(f'data/graphics/weapons/{id}.png')
		self.base_image = surf
		super().__init__(pos, surf, group, z=LEVEL_LAYERS['enemy_weapons'])
		self.player = player
		self.parent = parent
		self.cooldown = Timer(WEAPON_STATS[2][2] * 3)
		self.angle = 0
		self.camera_group = camera_group
		self.collision_sprites = collision_sprites
		self.prop = prop


	def position(self):
		self.rect.center = (self.parent.rect.centerx, self.parent.rect.centery)

	def shoot(self):
		if not self.cooldown.active:
			EnemyProjectile(self.rect.center, self.camera_group, self.player, self.angle, self.collision_sprites)
			self.cooldown.activate()

	def rotate(self):


			rel_x, rel_y = self.player.rect.centerx - self.rect.centerx, self.player.rect.centery - self.rect.centery
			self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
			self.image = pygame.transform.rotate(self.base_image, int(self.angle))
			self.rect = self.image.get_rect(center = self.rect.center)

	def update(self, dt):
		if not self.player.freeze_timer.active:
			if not self.prop:
				self.shoot()
				self.cooldown.update()
			self.position()
			self.rotate()

class EnemyProjectile(Generic):
	def __init__(self, pos, group, player, angle, collision_sprites):
		surf = load('data/graphics/projectiles/2.png').convert_alpha()
		super().__init__(pos, surf, group)
		self.angle = angle
		self.player = player
		self.speed = WEAPON_STATS[2][3]
		self.damage= ENEMY_STATS[4][2] * self.player.main.room_multiplier
		self.pos = pos
		self.collision_sprites = collision_sprites

	def calculate_new_xy(self, old_xy, speed, angle_in_degrees):
		move_vec = pygame.math.Vector2()
		move_vec.from_polar((speed, angle_in_degrees))
		return old_xy + move_vec

	def collision(self):
		for sprite in self.collision_sprites:
			if sprite.rect.colliderect(self.rect):
				self.kill()

	def attack(self):
		if self.rect.colliderect(self.player.rect):
			self.player.damage(self.damage)
			self.kill()


	def update(self, dt):
		self.attack()
		self.collision()
		if not self.player.freeze_timer.active:
			self.pos = self.calculate_new_xy(self.pos, self.speed, -self.angle)
			self.rect.center = round(self.pos[0]), round(self.pos[1])

class Chest(Generic):
	
	def __init__(self, pos, group, player, camera_group, boss_sprites):
		self.frame_index = 0
		self.rank = choices([1, 2, 3], weights=(1, 0.1, 0.03  * player.main.room_multiplier), k=1)[0]
		self.animation_frames = import_folder('data/graphics/chest')
		surf = self.animation_frames[self.frame_index]
		super().__init__(pos, surf, group, z=LEVEL_LAYERS['items'])
		self.player = player
		self.animating = False
		self.has_opened = False
		self.boss_sprites = boss_sprites
		self.locked = True
		self.camera_group = camera_group

	def animate(self, dt):
		if self.animating:
			self.frame_index += ANIMATION_SPEED * dt
			if self.frame_index >= len(self.animation_frames):
				self.animating = False
				self.frame_index  = 4
			self.image = self.animation_frames[int(self.frame_index)]


	def open(self):
		if self.player.rect.colliderect(self.rect) and pygame.key.get_pressed()[pygame.K_e] and not self.has_opened and not self.locked:
			self.animating = True
			self.has_opened = True
			self.player.pick_up_cooldown.activate()
			if self.rank == 1:
				rand = randint(1, 4)
				if  rand == 1:
					Item((self.rect.midbottom), self.camera_group, 'weapons', '1', self.player, self.camera_group, self.boss_sprites)
				elif rand == 2:
					Item((self.rect.midbottom), self.camera_group, 'weapons', '2', self.player, self.camera_group, self.boss_sprites)
				elif  rand == 3:
					Item((self.rect.midbottom), self.camera_group, 'weapons', '6', self.player, self.camera_group, self.boss_sprites)
				elif rand == 4:
					Item((self.rect.midbottom), self.camera_group, 'weapons', '7', self.player, self.camera_group, self.boss_sprites)
			if self.rank == 2:
				rand = randint(1, 2)
				if rand == 1:
					Item((self.rect.midbottom), self.camera_group, 'weapons', '4', self.player, self.camera_group, self.boss_sprites)
				elif rand == 2:
					Item((self.rect.midbottom), self.camera_group, 'weapons', '8', self.player, self.camera_group, self.boss_sprites)
				elif  rand == 3:
					Item((self.rect.midbottom), self.camera_group, 'weapons', '9', self.player, self.camera_group, self.boss_sprites)

			if self.rank == 3:
				Item((self.rect.midbottom), self.camera_group, 'weapons', '3', self.player, self.camera_group, self.boss_sprites)


	def update(self, dt):
		self.open()
		self.animate(dt)

class MerchantItem(Item):
	def __init__(self, pos, group ,player, camera_group, boss_sprites):
		rand = choices([5, 10, 11, 12], weights=(0.02 ,0.5, 1, 0.5), k=1)[0]
		super().__init__(pos, group, 'weapons', str(rand), player, camera_group, boss_sprites,z=LEVEL_LAYERS['enemies'],)
		self.price = WEAPON_STATS[int(self.id)][10]


	def pick_up(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_e] and not self.player.pick_up_cooldown.active and self.rect.colliderect(self.player.rect) and self.player.coins >= self.price:
			self.player.main.coins -= self.price
			if self.category == 'weapons':
				if self.player.weapon_1 == None:
					self.player.weapon_1 = Weapon(self.player.rect.center, self.camera_group, self.player,self.camera_group, self.player.collision_sprites, True, int(self.id), self.player.enemy_sprites, self.player.black_holes, self.boss_sprites)
					self.kill()
					self.player.pick_up_cooldown.activate()
					self.player.main.weapon_1 = int(self.id)


				elif self.player.weapon_2 != None:
					self.kill()
					self.player.weapon_2.kill()
					Item(self.player.rect.midbottom, self.camera_group, 'weapons', self.player.weapon_2.id, self.player, self.camera_group, self.boss_sprites)
					self.player.weapon_2 = Weapon(self.player.rect.center, self.camera_group, self.player,self.camera_group, self.player.collision_sprites, False, int(self.id),self.player.enemy_sprites, self.player.black_holes, self.boss_sprites)
					self.player.pick_up_cooldown.activate()
					self.player.main.weapon_2 = int(self.id)


				elif self.player.weapon_2 == None:
					self.player.weapon_2 = Weapon(self.player.rect.center, self.camera_group, self.player, self.camera_group, self.player.collision_sprites, False, int(self.id), self.player.enemy_sprites, self.player.black_holes, self.boss_sprites)
					self.kill()
					self.player.pick_up_cooldown.activate()
					self.player.main.weapon_2 = int(self.id)

class Merchant(Animated):
	def __init__(self, pos, group, player, collision_sprites, camera_group, boss_sprites):
		super().__init__(import_folder('data/graphics/merchant'), pos, group,z=LEVEL_LAYERS['enemies'])

		self.rect.bottomleft = pos
		self.block = Block(self.rect.center, (64,64), [camera_group, collision_sprites], z=LEVEL_LAYERS['crow'])
		self.block.rect.midtop = self.rect.midtop
		self.block.rect.y -= 20

		item = MerchantItem((self.rect.centerx, self.rect.centery + 8), camera_group, player, camera_group, boss_sprites)
		item.rect.centerx = self.rect.centerx

class Minion(Generic):
	def __init__(self, pos, group, player, collision_sprites, enemy_sprites):
		# animation
		self.animation_frames = {folder: import_folder(f'data/graphics/minion/{folder}') for folder in list(walk('data/graphics/minion/'))[0][1]}
		self.frame_index = 0
		self.status = 'walk'
		self.orientation = 'left'
		surf = self.animation_frames[f'{self.status}_{self.orientation}'][self.frame_index]
		super().__init__(pos, surf, group)
		self.player = player
		self.enemy_sprites = enemy_sprites

		# movement
		self.collision_sprites = collision_sprites
		self.hitbox = self.rect.inflate(0, 0)
		self.direction = vector()
		self.pos = vector(self.rect.center)
		self.speed = 3
		self.kills = 0
		self.base_speed = 3
		self.angle = 0
		self.damage = WEAPON_STATS[15][0]
		self.reset_speed = False
		if self.enemy_sprites:
			self.target = random.choice(self.enemy_sprites.sprites())
		else:
			self.target = self.player

	def animate(self, dt):
		global ANIMATION_SPEED
		self.current_animation = self.animation_frames[f'{self.status}_{self.orientation}']
		self.frame_index += ANIMATION_SPEED * dt
		if self.frame_index >= len(self.current_animation):
			self.frame_index = 0
		self.image = self.current_animation[int(self.frame_index)]

	def attack(self):
		for sprite in self.enemy_sprites:
			if sprite.rect.colliderect(self.rect):
				sprite.health -= self.damage
				if sprite.health <= 0:
					self.kills += 1

	def calculate_new_xy(self, old_xy, speed, angle_in_degrees):
		move_vec = pygame.math.Vector2()
		move_vec.from_polar((speed, angle_in_degrees))
		return old_xy + move_vec



	def support(self):
		if self.rect.colliderect(self.target.rect):
			self.speed = 0
			self.reset_speed = True
		else:
			if self.reset_speed:
				self.speed = self.base_speed
				self.reset_speed = False
			self.speed *= 1.003

		if self.target.health <= 0:
			if self.enemy_sprites:
				self.target = random.choice(self.enemy_sprites.sprites())
			else:
				self.target = self.player

		if self.kills >= 2:
			self.kill()

	def update(self, dt):
		self.attack()
		self.animate(dt)
		self.support()
		rel_x, rel_y = self.target.rect.topleft[0] - self.rect.centerx, self.target.rect.topleft[1] - self.rect.centery
		self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)


		self.pos = self.calculate_new_xy(self.pos, self.speed, -self.angle)
		self.rect.center = round(self.pos[0]), round(self.pos[1])

class Teleporter(Generic):
	def __init__(self, pos, group, player, main):
		super().__init__(pos, load('data/graphics/teleporter/0.png').convert_alpha(),group, z=LEVEL_LAYERS['shadow'])
		self.player = player
		self.main = main
		self.has_teleported = False

	def teleport(self):
		if self.player.rect.colliderect(self.rect) and pygame.key.get_pressed()[pygame.K_e]:
			self.main.changing_room = True
			self.kill()
	def update(self,dt):
		self.teleport()

class Coin(Generic):
	def __init__(self, pos, group, player, value):

		super().__init__(pos, load('data/graphics/coin/0.png'), group)
		self.base_image = load('data/graphics/coin/0.png')
		self.player = player
		self.value = value * self.player.hat.stats[3]


		# movement
		self.hitbox = self.rect.inflate(0, 0)
		self.direction = vector()
		self.pos = vector(self.rect.center)
		self.speed = 0.3
		self.multiplier = 1.05

	def rotate(self):
		rel_x, rel_y = self.player.rect.centerx - self.rect.centerx, self.player.rect.midbottom[1] - self.rect.centery

		self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)

		self.image = pygame.transform.rotate(self.base_image, int(self.angle))
		self.rect = self.image.get_rect(center=self.rect.center)

	def calculate_new_xy(self, old_xy, speed, angle_in_degrees):
		move_vec = pygame.math.Vector2()
		move_vec.from_polar((speed, angle_in_degrees))
		return old_xy + move_vec

	def collect(self):
		if self.player.rect.colliderect(self.rect):
			self.player.main.coins += self.value
			self.kill()

	def update(self, dt):
		self.speed *= self.multiplier
		self.collect()
		self.rotate()
		self.pos = self.calculate_new_xy(self.pos, self.speed, -self.angle)
		self.rect.center = round(self.pos[0]), round(self.pos[1])

class DemonBoss(Animated):
	def __init__(self, pos, group, player, camera_group, boss_sprites, collision_sprites):
		assets = import_folder('data/graphics/boss/demon')
		super().__init__(assets, pos, group, z=LEVEL_LAYERS['crow'])
		self.id = 'demon'
		self.health = BOSS_STATS[self.id][0]

		self.camera_group = camera_group
		self.player = player
		self.swap_timer = Timer(10000)
		self.swap_timer.activate()


		self.can_take_damage = True
		self.target_pos = (self.player.rect.centery, self.player.rect.midtop[1] - 40)
		self.pos = vector(self.rect.center)
		self.collided_starting_point = False
		self.angle = 0
		self.speed = 0.5
		self.starting_pos = pos
		self.base_speed = self.speed
		self.multiplier = 1.03
		self.reset_speed = False
		self.following_player = True
		self.boss_sprites = boss_sprites
		self.collision_sprites = collision_sprites
		self.rock_1 = None
		self.rock_2 = None
		self.rock_3 = None
		self.rock_4 = None

	def rocks(self):
		if self.rock_1 == None and self.rock_2 == None and self.rock_3 == None and self.rock_4 == None:
			self.rock_1 = BossRock(self.rect.center, self.camera_group, 1, self, self.player)

			self.rock_2 = BossRock(self.rect.center, self.camera_group, 2, self, self.player)

			self.rock_3 = BossRock(self.rect.center, self.camera_group, 3, self, self.player)

			self.rock_4 = BossRock(self.rect.center, self.camera_group, 4, self, self.player)



	def death(self):
		if self.health <= 0:
			Item(self.rect.center, self.camera_group, 'weapons', '13', self.player, self.camera_group,
				 self.boss_sprites)
			Coin(self.rect.center, self.camera_group, self.player, 500)
			if self.rock_1 != None:
				self.rock_1.kill()
			if self.rock_2 != None:
				self.rock_2.kill()
			if self.rock_3 != None:
				self.rock_3.kill()
			if self.rock_4 != None:
				self.rock_4.kill()
			self.kill()

	def swap(self):
		if not self.swap_timer.active:
			self.following_player = not self.following_player
			self.swap_timer.activate()

	def calculate_new_xy(self, old_xy, speed, angle_in_degrees):
		move_vec = pygame.math.Vector2()
		move_vec.from_polar((speed, angle_in_degrees))
		return old_xy + move_vec

	def find_angle(self):
		rel_x, rel_y = self.target_pos[0] - self.rect.centerx, self.target_pos[1] - self.rect.centery

		self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)

	def apply_sine_wave(self):

		self.rect.y = self.target_pos[1] + 10 * math.sin(pygame.time.get_ticks() / 150)


	def update_speed(self):
		if self.rect.collidepoint(self.target_pos):
			self.speed = 0
			self.reset_speed = True
		else:
			if self.reset_speed:
				self.base_speed = 0.5
				self.reset_speed = False
			self.speed = self.base_speed

	def position(self):
		if self.rect.collidepoint(self.target_pos) or self.collided_starting_point:
			self.apply_sine_wave()
			self.collided_starting_point = True
		elif not self.collided_starting_point:

			self.pos = self.calculate_new_xy(self.pos, self.speed, -self.angle)
			self.rect.center = round(self.pos[0]), round(self.pos[1])


	def update(self, dt):
		self.death()
		self.swap_timer.update()
		self.swap()
		self.animate(dt)
		self.find_angle()
		self.rocks()
		self.update_speed()
		if self.following_player:
			self.base_speed *= self.multiplier
			self.target_pos = (self.player.rect.centerx, self.player.rect.midtop[1] - 90)
			self.pos = self.calculate_new_xy(self.pos, self.speed, -self.angle)
			self.rect.center = round(self.pos[0]), round(self.pos[1])

		else:
			self.base_speed *= self.multiplier
			self.target_pos = self.starting_pos
			self.position()

class BossRock(Generic):
	def __init__(self, pos, group, id, parent, player):
		surf = load(f'data/graphics/boss_rocks/{str(randint(0, 2))}.png')
		self.base_image = surf
		super().__init__(pos, surf, group, z=LEVEL_LAYERS['particles'])
		self.parent = parent
		self.player = player
		self.id = id
		if self.id == 1:
			self.rect.bottomright = self.parent.rect.topleft
		if self.id == 2:
			self.rect.bottomleft = self.parent.rect.topright
		if self.id == 3:
			self.rect.topright = self.parent.rect.bottomleft
		if self.id == 4:
			self.rect.topleft = self.parent.rect.bottomright
		self.attack_timer = Timer(randint(2000, 5000))
		self.attack_timer.activate()
		self.speed = 6
		self.pos = pos
		self.damage = 8


	def calculate_new_xy(self, old_xy, speed, angle_in_degrees):
		move_vec = pygame.math.Vector2()
		move_vec.from_polar((speed, angle_in_degrees))
		return old_xy + move_vec

	def rotate(self):
		rel_x, rel_y = self.player.rect.centerx - self.rect.centerx, self.player.rect.midbottom[1] - self.rect.centery
		self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)

		self.image = pygame.transform.rotate(self.base_image, int(self.angle))
		self.rect = self.image.get_rect(center=self.rect.center)

	def position(self):
		if self.id == 1:
			self.rect.bottomright = self.parent.rect.topleft
		if self.id == 2:
			self.rect.bottomleft = self.parent.rect.topright
		if self.id == 3:
			self.rect.topright = self.parent.rect.bottomleft
		if self.id == 4:
			self.rect.topleft = self.parent.rect.bottomright
		self.pos = self.rect.topleft

	def attack(self):
		if self.rect.colliderect(self.player.rect):
			self.player.damage(self.damage)
			match self.id:
				case 1:
					self.parent.rock_1 = None
				case 2:
					self.parent.rock_2 = None
				case 3:
					self.parent.rock_3 = None
				case 4:
					self.parent.rock_4 = None
			self.kill()


	def despawn(self):
		if not self.rect.colliderect(self.player.despawn_block.rect):
			match self.id:
				case 1:
					self.parent.rock_1 = None
				case 2:
					self.parent.rock_2 = None
				case 3:
					self.parent.rock_3 = None
				case 4:
					self.parent.rock_4 = None
			self.kill()



	def update(self, dt):

		self.attack_timer.update()
		if self.attack_timer.active:
			self.position()
			self.rotate()
		else:
			self.pos = self.calculate_new_xy(self.pos, self.speed, -self.angle)
			self.rect.center = round(self.pos[0]), round(self.pos[1])
			self.attack()
			self.despawn()




