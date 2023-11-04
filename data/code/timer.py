import pygame

class Timer:
	def __init__(self, duration):
		self.duration = duration
		self.active = False
		self.start_time = 0

	def activate(self):
		self.active = True
		self.start_time = pygame.time.get_ticks()

	def deactivate(self):
		self.active = False
		self.start_time = 0

	def update(self):
		current_time = pygame.time.get_ticks()
		if current_time - self.start_time >= self.duration:
			self.deactivate()

class Speedrun:
	def __init__(self):
		self.start_time = pygame.time.get_ticks()
		self.can_get_time = True

	def get_time(self):
		time = (self.start_time - pygame.time.get_ticks()) / 1000
		return time

	def get_final_time(self):
		if self.can_get_time:
			time = (self.start_time - pygame.time.get_ticks()) / 1000
			self.can_get_time = False
			return time
