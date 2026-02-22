from random import randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Центральная ячейка
CENTER_CELL = ((GRID_WIDTH // 2) * GRID_SIZE, (GRID_HEIGHT // 2) * GRID_SIZE)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Словарь обратных направлений
OPPOSITE_DIRECTIONS = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT
}

# Словарь клавиш в направления
KEY_TO_DIRECTION = {
    pg.K_UP: UP,
    pg.K_DOWN: DOWN,
    pg.K_LEFT: LEFT,
    pg.K_RIGHT: RIGHT,
    pg.K_w: UP,
    pg.K_s: DOWN,
    pg.K_a: LEFT,
    pg.K_d: RIGHT
}

# Цвета
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, body_color=None):
        """
        Инициализирует базовые атрибуты объекта.

        Args:
            body_color (tuple, optional): Цвет объекта в RGB.
        """
        self.position = None
        self.body_color = body_color

    def draw_cell(self, position, color=None):
        """
        Отрисовывает одну ячейку на игровом поле.

        Args:
            position (tuple): Координаты ячейки (x, y)
            color (tuple, optional): Цвет ячейки в RGB. Если не указан,
            используется body_color.
        """
        color = color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        if color != BORDER_COLOR:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """
        Абстрактный метод отрисовки объекта.

        Raises:
            NotImplementedError: Если метод не переопределён в дочернем классе.
        """
        raise NotImplementedError(
            f'Класс {type(self).__name__} не переопределил метод draw()'
        )


class Apple(GameObject):
    """Класс яблока, наследуется от GameObject."""

    def __init__(self, occupied_positions=None, body_color=APPLE_COLOR):
        """
        Инициализирует яблоко.

        Args:
            occupied_positions (list, optional): Список занятых позиций,
            на которые нельзя ставить яблоко.
            body_color (tuple, optional): Цвет яблока в RGB.
        """
        super().__init__(body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=None):
        """
        Устанавливает случайное положение яблока на игровом поле,
        избегая занятых позиций.

        Args:
            occupied_positions (list, optional): Список занятых позиций,
            которые нужно исключить.
        """
        occupied_positions = occupied_positions or []
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс змейки, наследуется от GameObject."""

    def __init__(self, body_color=SNAKE_COLOR):
        """
        Инициализирует змейку с начальными параметрами.

        Args:
            body_color (tuple, optional): Цвет змейки в RGB.
        """
        super().__init__(body_color)
        self.reset()

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.positions = [CENTER_CELL]
        self.length = 1
        self.direction = RIGHT

    def update_direction(self, new_direction):
        """
        Обновляет направление движения змейки.

        Args:
            new_direction (tuple): Новое направление движения.
        """
        if OPPOSITE_DIRECTIONS[new_direction] != self.direction:
            self.direction = new_direction

    def move(self):
        """Обновляет позицию змейки: добавляет новую голову и удаляет хвост."""
        head_x, head_y = self.positions[0]
        dir_x, dir_y = self.direction

        # Вставляем новую голову
        self.positions.insert(0, (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        ))

        # Удаляем хвост, если змейка не выросла
        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self):
        """Отрисовывает все сегменты змейки на экране."""
        for position in self.positions:
            self.draw_cell(position)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def check_collision(self):
        """
        Проверяет, столкнулась ли змейка сама с собой.

        Returns:
            bool: True если произошло столкновение, иначе False.
        """
        return self.get_head_position() in self.positions[4:]


def handle_keys(snake):
    """
    Обрабатывает нажатия клавиш для управления змейкой.

    Args:
        snake (Snake): Объект змейки.
    """
    for event in pg.event.get():
        if (event.type == pg.QUIT
                or (event.type == pg.KEYDOWN
                    and event.key == pg.K_ESCAPE)):
            pg.quit()
            raise SystemExit

        if event.type == pg.KEYDOWN and event.key in KEY_TO_DIRECTION:
            snake.update_direction(KEY_TO_DIRECTION[event.key])


def main():
    """Главная функция игры, содержит основной игровой цикл."""
    pg.init()
    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif snake.check_collision():
            snake.reset()
            apple.randomize_position(snake.positions)

        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
