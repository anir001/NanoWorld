import os
import math

MAX_FPS = 60
# ---------------#
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1000
FONT_PATH = os.path.join('font', 'FFFFORWA.TTF')
# ---------------#
CELL_SIZE = 10
CELL_WIDTH = int((SCREEN_WIDTH - 220) / CELL_SIZE)
CELL_HEIGHT = int(SCREEN_HEIGHT / CELL_SIZE)
# ---------------#
# world settings #
FOOD_AMOUNT = 80
POP_SIZE = 25
MAX_AGE = 50 * MAX_FPS
MAX_ENERGY = 10 * MAX_FPS
# ---------------#
# ---------------#
DISH_SIZE = (CELL_WIDTH * CELL_SIZE, CELL_HEIGHT * CELL_SIZE)
# ---------------#
# ---------------#
MAX_DIST = math.hypot(math.fabs(0 - DISH_SIZE[0]),
                      math.fabs(0 - DISH_SIZE[1]))
# ---------------#
