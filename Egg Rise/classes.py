import pyxel

from dataclasses import dataclass


@dataclass
class Vector2D:
    x: float
    y: float


class Egg:
    def __init__(self, x: float, y: float, radius: float, color: int, velocity: Vector2D) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

        # Movement
        self.velocity = velocity

        self.is_grounded = False
        self.is_jumping = False

    def move(self, direction: int) -> None:
        self.x += self.velocity.x * direction
        self.y += self.velocity.y

    def jump(self, force: float) -> None:
        # Can only jump if on platform
        if not self.is_grounded or self.is_jumping:
            return

        self.is_grounded = False
        self.is_jumping = True
        self.velocity.y = force

    def apply_gravity(self, gravity: float) -> None:
        if not self.is_grounded:
            self.velocity.y += gravity

    def draw(self) -> None:
        pyxel.circ(self.x, self.y, self.radius, self.color)


class Platform:
    def __init__(self, index: int, x: float, y: float, width: float, height: float, color: int, velocity: Vector2D, direction: int) -> None:
        self.index = index
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

        # Movement
        self.velocity = velocity
        self.direction = direction

    def move(self) -> None:
        self.x += self.velocity.x * self.direction

    def draw(self) -> None:
        pyxel.rect(self.x, self.y, self.width, self.height, self.color)
