import pygame
from utils import randomize
import os
import settings
IMG_PATH = os.path.join('image', 'food', 'food.png')


class Food(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((settings.CELL_SIZE, settings.CELL_SIZE))
        self.image.fill((0, 255, 0))
        # self.image = pygame.image.load(IMG_PATH)
        self.pos = randomize()
        self.rect = self.image.get_rect(topleft=self.pos)
