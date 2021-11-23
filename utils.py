import random
import settings


def randomize(range_x=settings.CELL_WIDTH, range_y=settings.CELL_HEIGHT):
    """
    Generate random coordinates
    :param:range_x
    :param:range_y
    :return:tuple x, y
    """
    random.seed()
    x = random.randint(0, range_x - 1)
    y = random.randint(0, range_y - 1)

    return (settings.CELL_SIZE * x, settings.CELL_SIZE * y)
