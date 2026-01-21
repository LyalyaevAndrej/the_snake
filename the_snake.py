"""
Модуль игры Змейка.
Реализует классическую игру змейка с использованием PyGame.
"""

import random
from abc import abstractmethod
import pygame
from typing import Tuple, List

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
TEXT_COLOR = (255, 255, 255)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()

pygame.font.init()
font = pygame.font.Font(None, 36)


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(
        self,
        position: Tuple[int, int] = None,
        body_color: Tuple[int, int, int] = None
    ):
        """Инициализирует игровой объект."""
        self.position = position
        self.body_color = body_color

    @abstractmethod
    def draw(self):
        """Абстрактный метод для отрисовки объекта."""
        pass


class Apple(GameObject):
    """Класс яблока в игре."""

    def __init__(
        self,
        position: Tuple[int, int] = None,
        body_color: Tuple[int, int, int] = APPLE_COLOR
    ):
        """Инициализирует яблоко."""
        super().__init__(position, body_color)
        self.position = self.randomize_position()
        self.body_color = body_color

    def randomize_position(self) -> Tuple[int, int]:
        """Генерирует случайную позицию для яблока."""
        point_x = random.randint(0, SCREEN_WIDTH) // GRID_SIZE * GRID_SIZE
        point_y = random.randint(0, SCREEN_HEIGHT) // GRID_SIZE * GRID_SIZE
        return (point_x, point_y)

    def draw(self):
        """Отрисовывает яблоко на экране."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def respawn(self) -> None:
        """Перемещает яблоко в новую случайную позицию."""
        self.position = self.randomize_position()


class Snake(GameObject):
    """Класс змейки в игре."""

    def __init__(
        self,
        length: int = 1,
        positions: List[Tuple[int, int]] = None,
        direction: Tuple[int, int] = RIGHT,
        next_direction: Tuple[int, int] = None,
        body_color: Tuple[int, int, int] = SNAKE_COLOR
    ):
        """Инициализирует змейку."""
        if positions is None:
            start_x = SCREEN_WIDTH // 2
            start_y = SCREEN_HEIGHT // 2
            positions = [(start_x, start_y)]

        super().__init__(positions[0], body_color)
        self.length = length
        self.positions = positions
        self.body_color = body_color
        self.direction = direction
        self.next_direction = next_direction
        self.last = None
        self.grow_pending = 0

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Перемещает змейку в текущем направлении."""
        # Сохраняем последнюю позицию для затирания
        self.last = self.positions[-1] if self.positions else None

        # Обновляем направление
        self.update_direction()

        head_x, head_y = self.positions[0]

        dx, dy = self.direction
        new_head_x = head_x + dx * GRID_SIZE
        new_head_y = head_y + dy * GRID_SIZE

        new_head_x = new_head_x % SCREEN_WIDTH
        new_head_y = new_head_y % SCREEN_HEIGHT

        new_head = (new_head_x, new_head_y)

        self.positions.insert(0, new_head)
        self.position = new_head

        if self.grow_pending > 0:
            self.grow_pending -= 1
            # Не удаляем хвост, когда растем
        else:
            # Удаляем хвост только если не растем
            if len(self.positions) > self.length:
                self.positions.pop()

    def draw(self):
        """Отрисовывает змейку на экране."""
        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

        length_text = font.render(
            f'Длина: {self.length}', True, TEXT_COLOR
        )
        text_rect = length_text.get_rect()
        text_rect.bottomright = (SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10)
        screen.blit(length_text, text_rect)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        start_x = (SCREEN_WIDTH // 2) // GRID_SIZE * GRID_SIZE
        start_y = (SCREEN_HEIGHT // 2) // GRID_SIZE * GRID_SIZE

        self.positions = [(start_x, start_y)]
        self.position = (start_x, start_y)
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.grow_pending = 0

    def grow(self):
        """Увеличивает длину змейки."""
        self.length += 1
        self.grow_pending += 1

    def check_self_collision(self) -> bool:
        """Проверяет столкновение змейки с собой."""
        head = self.get_head_position()
        return head in self.positions[1:]


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш для управления змейкой."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основная функция игры."""
    # Инициализация PyGame:
    pygame.init()
    # Тут нужно создать экземпляры классов.
    snake = Snake()
    apple = Apple()

    if apple.position in snake.positions:
        apple.respawn()

    while True:
        clock.tick(SPEED)

        # Тут опишите основную логику игры.
        handle_keys(snake)
        snake.move()

        if snake.check_self_collision():
            snake.reset()
            apple.respawn()

            if apple.position in snake.positions:
                apple.respawn()

        if snake.get_head_position() == apple.position:
            snake.grow()
            apple.respawn()
            if apple.position in snake.positions:
                apple.respawn()

        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
