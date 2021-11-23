import pygame
from sys import exit
from pygame import Color

import datetime

from Biter import Generate
from Food import Food
import settings
import pickle
import random


class World:
    def __init__(self,
                 screen_width=settings.SCREEN_WIDTH,
                 screen_height=settings.SCREEN_HEIGHT
                 ):
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.max_fps = settings.MAX_FPS
        self.screen = pygame.display.set_mode((self.screen_width,
                                               self.screen_height))

        self.font = pygame.font.Font(settings.FONT_PATH, 16)

        self.dump = False
        self.start_time = datetime.datetime.now()
        self.paused = False
        self.game_over = False
        self.regenerate_amount = 0
        # simulation location - surface
        self.dish = pygame.surface.Surface((settings.DISH_SIZE))

        self.genome_info = None

    def init(self):
        """
        Initialize population, foods etc.

        :return:
        """
        self.lives = pygame.sprite.Group()
        self.foods = pygame.sprite.Group()

        population = Generate(pop_size=settings.POP_SIZE).generate()

        for sprite in population:
            self.lives.add(sprite)
        del(population)

        for i in range(settings.FOOD_AMOUNT):
            food_sprite = Food()
            self.foods.add(food_sprite)

    def add_new(self, new):
        self.lives.add(new)

    def genome_stats(self, pos):

        for genoms in self.lives.sprites():
            if genoms.rect.left < pos[0] and genoms.rect.right > pos[0] and \
                    genoms.rect.top < pos[1] and genoms.rect.bottom > pos[1]:
                print(genoms.genome)
                self.genome_info = genoms.infos

    def handle_events(self):
        """
        Handle any keypresses
        s - start/stop (pause) the game
        q - quit

        :return:
        """
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.unicode == 's':
                    print("Toggling pause")
                    if self.paused:
                        self.paused = False
                    else:
                        self.paused = True
                if event.unicode == 'q':
                    self.game_over = True
                if event.unicode == 'd':
                    print('Dump genomes and reproduce')
                    self.dump = True
                    self.save_genome()
                    self.init()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_presses = pygame.mouse.get_pressed()
                if mouse_presses[0]:
                    self.genome_stats(pygame.mouse.get_pos())
                if mouse_presses[2]:
                    self.genome_info = None
            if event.type == pygame.QUIT:
                exit()

    def clear_screen(self):
        """
        Clear screen

        :return:
        """
        self.screen.fill(Color('cadetblue3'))
        self.dish.fill(Color('aliceblue'))

    def draw(self):
        """
        Draw all elements on the screen

        :return:
        """
        self.foods.draw(self.dish)
        self.lives.draw(self.dish)

        self.screen.blit(self.dish, (0, 0))
        self.draw_statistic()
        # print(pygame.surfarray.array3d((self.dish)))
        pygame.display.update()

    def draw_statistic(self):
        """
        Draw some information

        :return:
        """
        stats1 = self.font.render(
                 f'Time: {datetime.datetime.now() - self.start_time}',
                 False, (0, 0, 0))

        stats2 = self.font.render(
            f'Population: {len(self.lives)}', False, (0, 0, 0))

        stats3 = self.font.render(
            f'regen_amount: {self.regenerate_amount}', False, (0, 0, 0))

        self.screen.blit(stats1, (settings.DISH_SIZE[0] + 5, 20))
        self.screen.blit(stats2, (settings.DISH_SIZE[0] + 5, 60))
        self.screen.blit(stats3, (settings.DISH_SIZE[0] + 5, 100))

        if self.genome_info is not None:
            txt1 = self.font.render('Genome info:', False, (0, 0, 0))
            txt2 = self.font.render(
                f'obs: {self.genome_info}', False, (0, 0, 0))
            self.screen.blit(txt1, (5, 20))
            self.screen.blit(txt2, (5, 60))

    def update(self):
        """
        Update state for all sprites groups

        :return:
        """
        self.lives.update(self.foods, self.lives)
        self.check_collision()
        if random.random() < 0.1 and len(self.foods) < 150:
            self.food_spawn()

    def check_collision(self):
        """
        Check collision with food and another biters

        :return:
        """

        for sprite in self.lives.sprites():
            food = pygame.sprite.spritecollideany(sprite, self.foods)

            if food is not None:
                food.kill()
                self.food_spawn()
                sprite.eat()
                # Tworzymy nowego osobnika
                if sprite.genome.fitness % 3 == 0:
                    new = sprite.reproduction()
                    self.add_new(new)

        """
        TO DO
        Collision with another biters

        """
        # for sprite1 in self.lives:
        #     for sprite2 in self.lives:
        #         if sprite1.rect.colliderect(sprite2.rect):
        #             if sprite1 is not sprite2:
        #                 if sprite1.direction.x > 0 and \
        #                         sprite1.rect.x < sprite2.rect.x:
        #                     sprite1.rect.right = sprite2.rect.left
        #
        #                 elif sprite1.direction.x < 0 and \
        #                         sprite1.rect.x > sprite2.rect.x:
        #                     sprite1.rect.left = sprite2.rect.right
        #
        #                 elif sprite1.direction.y > 0 and \
        #                         sprite1.rect.y < sprite2.rect.y:
        #                     sprite1.rect.bottom = sprite2.rect.top
        #
        #                 elif sprite1.direction.y < 0 and \
        #                         sprite1.rect.y > sprite2.rect.y:
        #                     sprite1.rect.top = sprite2.rect.bottom

    def food_spawn(self):
        food = Food()
        self.foods.add(food)

    def save_genome(self):
        if len(self.lives) <= 5 or self.dump:
            num = 0
            self.dump = False
            for genome in self.lives.sprites():
                with open(f'genome/genome{num}.pkl', 'wb') as f:
                    pickle.dump(genome.genome, f)
                    f.close()
                    num += 1
                if num > 4:
                    break

    def run(self):
        """
        Main loop

        :return:
        """
        clock = pygame.time.Clock()

        self.init()
        print('Init done\nSize of population: {}'.format(len(self.lives)))
                
        while True:
            if self.game_over:
                return

            self.handle_events()

            if not self.paused:
                self.clear_screen()
                # Update state
                self.update()
                self.save_genome()
                if len(self.lives) < 5:
                    self.init()
                    self.regenerate_amount += 1
                self.draw()

            clock.tick(self.max_fps)
