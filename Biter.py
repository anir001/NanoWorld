import pygame
import os
import math
import copy
import numpy as np
import neat
import pickle
import random

from settings import DISH_SIZE, MAX_AGE, MAX_ENERGY, MAX_FPS
from utils import randomize


IMG_PATH = os.path.join('image', 'biter', '32bit-octopus-dumbo1.png')

CONFIG = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     'config')


class Biter(pygame.sprite.Sprite):
    def __init__(self, traits, pos, genome=None):
        """
        :param:traits dict: speed, color
        """

        super().__init__()
        # self.image = pygame.image.load(IMG_PATH)
        # self.image = pygame.transform.scale(self.image, (16, 16))
        self.size = (15, 15)
        self.image = pygame.Surface(self.size)
        self.image.fill(traits['color'])
        self.rect = self.image.get_rect(center=pos)
        self.position = pygame.math.Vector2(pos)
        self.direction = pygame.math.Vector2((0, 0))
        self.distances = [[], []]
        self.neighbours = 0
        self.count = 0
        self.incubate = random.randint(1, 2 * MAX_FPS)
        self.infos = [0, 0, 0, 0]
        self.ate = 0
        # For life
        self.energy = MAX_ENERGY
        self.age = 0
        # Traits
        self.genome = genome
        self.genome.fitness = 0
        self.net = neat.nn.FeedForwardNetwork.create(self.genome, CONFIG)
        # self.net = neat.nn.RecurrentNetwork.create(self.genome, CONFIG)
        self.traits = traits
        # self.speed = traits['speed']

    def update(self, food_group, lives):
        """
        Main loop

        :param:need to calculate distance for input
        :param:need to reproduction
        :return:
        """
        if self.count <= self.incubate:
            self.count += 1
        else:

            self.foods = food_group

            self.energy -= 1
            self.age += 1

            # self.neighbour(lives)
            self.action(self.get_obs())
            self.move()

            if self.energy <= 0 or self.age >= MAX_AGE:
                self.die()

    def radar(self):
        # self.distances = [[], []]
        #
        # for food in self.foods:
        #     dx = food.rect.centerx - self.rect.centerx
        #     dy = self.rect.centery - food.rect.centery
        #     dist = math.hypot(dx, dy)
        #
        #     rads = math.atan2(dy, dx)
        #     # degs %= 2 * math.pi
        #     degs = math.degrees(rads)
        #
        #     # For normalize input 0 to 1
        #     dist = dist / MAX_DIST
        #     degs = degs / 180
        #
        #     self.distances[0].append(dist)
        #     self.distances[1].append(degs)

        # Alternatywna wersja obserwacji
        max_dist = 120

        #
        # 0 - sąsiedztwo food x = (0 - brak, 0.5 - lewa, 1 prawa,
        # 1 - sąsiedztwo food y = (0 - brak, 0.5 - góra, 1 dół
        # 2 - sąsiedztwo ścian x = (0 - brak, 0.5 - lewa, 1 prawa,
        # 3 - sąsiedztwo ścian y = (0 - brak, 0.5 - góra, 1 dół
        self.infos = [0, 0, 0, 0]
        previous_diff = max_dist
        # foods --------------
        for b in self.foods:
            diff = self.__dist2__(b.rect.center)
            if diff < max_dist and diff < previous_diff:
                if b.rect.centerx < self.rect.centerx:
                    self.infos[0] = -1
                if b.rect.centerx > self.rect.centerx:
                    self.infos[0] = 1
                if b.rect.centery < self.rect.centery:
                    self.infos[1] = -1
                if b.rect.centery > self.rect.centery:
                    self.infos[1] = 1
                previous_diff = diff
        # ściany ------------
        if self.rect.left < 5:
            self.infos[2] = -1

        if self.rect.right > DISH_SIZE[0] - 5:
            self.infos[2] = 1

        if self.rect.top < 5:
            self.infos[3] = -1

        if self.rect.bottom > DISH_SIZE[1] - 5:
            self.infos[3] = 1

    def get_obs(self):
        # obs = []
        self.radar()
        # index = self.distances[0].index(min(self.distances[0]))
        #
        # # Najbliższy element
        # obs.append(min(self.distances[0]))
        # # Kąt do najbliższego elementu
        # obs.append(self.distances[1][index])
        # # Ilość sąsiadów
        # obs.append(self.neighbours)
        # # for n in self.neighbours_direction:
        # #     obs.append(n)

        # return obs
        return self.infos

    def action(self, input):
        """
        Use neural network to predict next action
        input:
        output:
        0 - nothing
        1 - right
        2 - left
        3 - down
        4 - up

        :return:
        """
        output = self.net.activate(input)
        action = np.argmax(output)
        # action = max(zip(output, range(len(output))))[1]

        if action == 0:
            self.direction.x = 1
            self.direction.y = 0
        elif action == 1:
            self.direction.x = -1
            self.direction.y = 0
        elif action == 2:
            self.direction.y = 1
            self.direction.x = 0
        elif action == 3:
            self.direction.y = -1
            self.direction.x = 0

        # self.output = self.net.activate(input)
        #
        # if self.output[0] > 0.5:
        #     self.direction.x = 1
        #     self.direction.y = 0
        # if self.output[1] > 0.5:
        #     self.direction.x = -1
        #     self.direction.y = 0
        # if self.output[2] > 0.5:
        #     self.direction.y = 1
        #     self.direction.x = 0
        # if self.output[3] > 0.5:
        #     self.direction.y = -1
        #     self.direction.x = 0
        # # else:
        # #     self.direction.y = 0
        # #     self.direction.x = 0

        # Only for debug
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.direction.y = 0
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.direction.y = 0
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.direction.x = 0
        elif keys[pygame.K_UP]:
            self.direction.y = -1
            self.direction.x = 0

    def eat(self):
        """
        Function activated when sprite collide
        """
        self.genome.fitness += 1
        self.energy += 5

        if self.energy > MAX_ENERGY:
            self.energy = MAX_ENERGY

    def move(self):
        """
        Motion for Biter

        :return:
        """
        # self.position += self.direction * self.traits['speed']
        # self.rect.center = self.position
        self.rect.move_ip(self.direction.x * self.traits['speed'],
                          self.direction.y * self.traits['speed'])

        if self.rect.left < 0:
            self.rect.left = 0
            self.die()
        elif self.rect.right > DISH_SIZE[0]:
            self.rect.right = DISH_SIZE[0]
            self.die()
        elif self.rect.top < 0:
            self.rect.top = 0
            self.die()
        elif self.rect.bottom > DISH_SIZE[1]:
            self.rect.bottom = DISH_SIZE[1]
            self.die()

    def die(self):
        """
        Remove from Group

        :return:
        """
        self.kill()

    def mutate(self):
        """
        Mutate genome and traits

        :return: new genome
        """
        if random.random() < 0.2:
            new_genome = copy.deepcopy(self.genome)
            new_genome.mutate(CONFIG.genome_config)
            return new_genome
        else:
            return self.genome

    def reproduction(self):
        """

        :return: new species
        """

        if self.direction.x > 0:
            position = (self.rect.centerx
                        - self.size[0] - 2, self.rect.centery)
        elif self.direction.x < 0:
            position = (self.rect.centerx
                        + self.size[0] + 2, self.rect.centery)
        elif self.direction.y > 0:
            position = (self.rect.centerx,
                        self.rect.centery - self.size[1] - 2)
        elif self.direction.y < 0:
            position = (self.rect.centerx,
                        self.rect.centery + self.size[1] + 2)
        else:
            position = self.rect.center

        new = Biter(self.traits, position, self.mutate())

        return new

    def __dist2__(self, other_center):
        '''
        Calculates the distance squared between two points
        Parameters
        ----------
        other_center : float[]
            Array containing the x,y coords of the other object
        Returns
        -------
        float
            Squared distance between the two centers.
        '''
        dx = other_center[0] - self.rect.centerx
        dy = self.rect.centery - other_center[1]
        diff = math.fabs(math.hypot(dx, dy))

        return diff

    def neighbour(self, others):
        '''
        calculate neighbours for net input
        '''
        self.neighbours = 0
        self.min_dist_2 = 25
        # 0 - left, 1 - right, 2 - up, 3 down
        self.neighbours_direction = [0, 0, 0, 0]
        for b in others:
            if b != self and self.__dist2__(b.rect.center) < self.min_dist_2:
                self.neighbours += 1
                if b.rect.right < self.rect.left:
                    self.neighbours_direction[0] = 1
                elif b.rect.left > self.rect.right:
                    self.neighbours_direction[1] = 1
                elif b.rect.bottom < self.rect.top:
                    self.neighbours_direction[2] = 1
                elif b.rect.top > self.rect.bottom:
                    self.neighbours_direction[3] = 1


class Generate():
    """
    To generate population
    """

    def __init__(self, pop_size=1):
        self.pop_size = pop_size
        self.population = []
        self.traits = {'speed': 2, 'color': (255, 255, 255)}

    def randomly(self):
        for i in range(self.pop_size):
            genome = neat.genome.DefaultGenome(i)
            genome.configure_new(CONFIG.genome_config)

            # for k in traits:
            #     traits[k] = random.randint(1, 3)
            self.traits['color'] = tuple(np.random.choice(range(256), size=3))
            self.population.append(Biter(traits=self.traits.copy(),
                                         pos=randomize(),
                                         genome=genome
                                         ))

    def crossover(self):

        for i in range(self.pop_size):
            file1 = random.choice(self.files)
            file2 = random.choice(self.files)

            with open(os.path.join('genome', file1), 'rb') as f:
                genome0 = pickle.load(f)
            with open(os.path.join('genome', file2), 'rb') as f:
                genome1 = pickle.load(f)

            genome = neat.genome.DefaultGenome(i)
            genome.configure_crossover(
                genome0, genome1, CONFIG.genome_config)
            if random.random() < 0.5:
                genome.mutate(CONFIG.genome_config)
            # for k in traits:
            #     traits[k] = random.randint(1, 3)
            self.traits['color'] = tuple(np.random.choice(range(256), size=3))
            self.population.append(Biter(traits=self.traits.copy(),
                                         pos=randomize(),
                                         genome=genome
                                         ))

    def generate(self):
        path = 'genome'
        self.files = os.listdir(path)

        if len(self.files) > 2:
            self.crossover()
        else:
            self.randomly()

        return self.population
