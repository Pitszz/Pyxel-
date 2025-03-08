import pyxel
import random

from dataclasses import dataclass
from constants import (
    PLATFORM_COLOR,
    WIDTH,
    HEIGHT,
    PLATFORM_GAP,
    PLATFORM_WIDTH,
    PLATFORM_MAX_SPEED,
    PLATFORM_MIN_SPEED,
    LAST_PLATFORM_COLOR,
    PLATFORM_HEIGHT,
)


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


# class PlatformGenerator:
#     def __init__(self, _max: int, is_infinite: bool) -> None:
#         self.max = _max
#         self.platforms: list[Platform] = []
#         self.current_idx = 0
#         self.is_infinite = is_infinite

#     def generate(self, last_index: int) -> list[Platform]:
#         while len(self.platforms) < self.max:
#             pf_x = random.randrange(0, WIDTH - PLATFORM_WIDTH)
#             pf_y = HEIGHT * 0.9 - \
#                 (PLATFORM_GAP * (self.current_idx - last_index))

#             # Randomize speed of platform and starting direction
#             random_velocity = Vector2D(random.uniform(
#                 PLATFORM_MIN_SPEED, PLATFORM_MAX_SPEED), 0)
#             random_direction = random.choice([1, -1])

#             # Make last platform color different if not infinite
#             color = PLATFORM_COLOR if self.current_idx < self.max - \
#                 1 or self.is_infinite else LAST_PLATFORM_COLOR

#             platform = Platform(self.current_idx, pf_x, pf_y, PLATFORM_WIDTH, PLATFORM_HEIGHT,
#                                 color, random_velocity, random_direction)

#             self.platforms.append(platform)
#             self.current_idx += 1

#         return self.platforms

#     def remove(self, amount: int) -> None:
#         self.platforms = self.platforms[amount:]
#         print(len(self.platforms))

#     def reset(self) -> None:
#         self.platforms.clear()
#         self.current_idx = 0


class PlatformGenerator:
    def __init__(self, _max: int, is_infinite: bool) -> None:
        self.max = _max
        self.platforms: list[Platform] = []
        self.current_idx = 0
        self.is_infinite = is_infinite

    def generate(self) -> list[Platform]:
        # Find the possible highest y pos of platform
        highest_y = HEIGHT * 0.9

        if self.platforms:
            # higher platform is negative y
            highest_platform = min(self.platforms, key=lambda pf: pf.y)
            highest_y = highest_platform.y

        # Continously generate new platforms until max limit
        while len(self.platforms) < self.max:
            pf_x = random.randrange(0, WIDTH - PLATFORM_WIDTH)

            # New pf_y should be last platform y - platform gap
            if self.platforms:
                pf_y = highest_y - PLATFORM_GAP
            else:
                # For first platform
                pf_y = HEIGHT * 0.9 - (PLATFORM_GAP * self.current_idx)

            # Set new highest y
            highest_y = pf_y

            # Randomize speed of platform and starting direction
            random_velocity = Vector2D(random.uniform(
                PLATFORM_MIN_SPEED, PLATFORM_MAX_SPEED), 0)
            random_direction = random.choice([1, -1])

            # Make last platform color different if not infinite
            color = PLATFORM_COLOR if self.current_idx < self.max - \
                1 or self.is_infinite else LAST_PLATFORM_COLOR

            platform = Platform(self.current_idx, pf_x, pf_y, PLATFORM_WIDTH, PLATFORM_HEIGHT,
                                color, random_velocity, random_direction)

            self.platforms.append(platform)
            self.current_idx += 1

        return self.platforms

    def remove(self, amount: int) -> None:
        self.platforms = self.platforms[amount:]
        # print(f"Removed [{amount}] platforms. Remaining: {len(self.platforms)}")

    def reset(self) -> None:
        self.platforms.clear()
        self.current_idx = 0
