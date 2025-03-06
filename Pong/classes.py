import pyxel
import math

from dataclasses import dataclass
from constants import (
    PADDLE_SPEED,
    HEIGHT,
    SECTION_HEIGHT,
    BALL_SPEED
)


@dataclass
class Vector2D:
    x: float
    y: float


class Ball:
    def __init__(self, x: float, y: float, radius: float, color: int) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

        # Velocity vector
        self.velocity = Vector2D(BALL_SPEED, 0)

    def move(self) -> None:
        self.x += self.velocity.x
        self.y += self.velocity.y

    def bounce(self, section: int, angle: float, direction: int) -> None:
        self.velocity.x = math.cos(angle) * BALL_SPEED * direction
        self.velocity.y = math.sin(angle) * BALL_SPEED
        print(f"{self.velocity.x=}, {self.velocity.y}")

        # Bounce up if section 1, 2
        if section <= 2:
            self.velocity.y = -abs(self.velocity.y)

        # Bounce down if section 4, 5
        elif section >= 4:
            self.velocity.y = abs(self.velocity.y)

        # Bounce straight if section 3
        else:
            self.velocity.y = 0

    def bounce_off_border(self) -> None:
        self.velocity.y *= -1

    def draw(self) -> None:
        pyxel.circ(self.x, self.y, self.radius, self.color)


class Paddle:
    def __init__(self, x: float, y: float, width: float, height: float, color: int, key_up: int, key_down: int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.key_up = key_up
        self.key_down = key_down

        # Velocity vector
        self.velocity = Vector2D(0, PADDLE_SPEED)

    def move(self) -> None:
        # Move up
        if pyxel.btn(self.key_up) and self.y >= 0:
            self.y -= self.velocity.y

        # Move down
        elif pyxel.btn(self.key_down) and self.y + self.height <= HEIGHT:
            self.y += self.velocity.y

    def get_bounce_section(self, ball_y: float) -> int:
        relative_y = ball_y - self.y
        section = int(relative_y // SECTION_HEIGHT) + 1

        return max(1, min(5, section))

    def get_bounce_angle(self, section: int) -> float:
        angle_map = {
            1: 4*math.pi / 6,
            2: 5*math.pi / 6,
            3: math.pi,
            4: 7*math.pi / 6,
            5: 8*math.pi / 6
        }

        return angle_map[section]

    def draw(self) -> None:
        pyxel.rect(self.x, self.y, self.width, self.height, self.color)
