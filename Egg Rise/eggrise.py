import pyxel
import random

from classes import Egg, Platform, Vector2D
from constants import (
    JUMP_FORCE,
    GRAVITY,
    PLATFORM_WIDTH,
    PLATFORM_GAP,
    PLATFORM_HEIGHT,
    PLATFORM_COLOR,
    PLATFORM_MIN_SPEED,
    PLATFORM_MAX_SPEED,
    RESPAWN_TIME,
    MID_WIDTH,
    MID_HEIGHT,
    WIN_COLOR,
    LOSE_COLOR,
    CAMERA_SPEED,
)


class EggRiseModel:
    def __init__(self, title: str, width: int, height: int, fps: int, egg: Egg, max_eggs: int, num_platforms: int) -> None:
        # Properties
        self.title = title
        self.width = width
        self.height = height
        self.fps = fps
        self.num_platforms = num_platforms

        # Game objects
        self.egg = egg
        self.platforms: list[Platform] = []

        # Game state
        self.is_game_over = False
        self.has_won = False
        self.current_platform = None
        self.max_eggs = max_eggs
        self.eggs_left = self.max_eggs
        self.score = 0
        self.is_respawning = False
        self.is_camera_moving = False

    def update(self) -> None:
        # Don't do anything if game is over or has won
        if self.is_game_over or self.has_won:
            return

        # Move egg horizontally if on platform
        egg_direction = self.current_platform.direction if self.current_platform else 0
        self.egg.move(egg_direction)
        self.egg.apply_gravity(GRAVITY)

        # Move platforms and check if egg is out of bounds
        self.check_out_of_bounds()
        self.move_platforms()
        self.handle_platform_collision()

        # Move the camera if egg is on a platform and reaches at least the 2nd platform
        if self.egg.is_grounded and self.score > 0:
            self.move_camera(CAMERA_SPEED)

    def check_out_of_bounds(self) -> None:
        # Game over if we have no eggs left
        if self.eggs_left <= 0:
            self.is_game_over = True
            return

        # Check if egg falls at the bottom
        if self.egg.y > self.height:

            # Only subtract eggs if not respawning
            if not self.is_respawning:
                self.eggs_left -= 1
                self.is_respawning = True

            # Wait some time before respawning the egg
            if self.has_time_elapsed(RESPAWN_TIME):
                assert self.current_platform is not None

                self.is_respawning = False
                self.reset(self.current_platform.index)

    def has_time_elapsed(self, seconds: int) -> bool:
        return pyxel.frame_count % (self.fps * seconds) == 0

    def generate_platforms(self) -> None:
        # Clear existing platforms
        self.platforms.clear()

        if self.num_platforms < 2:
            raise ValueError("Number of platforms must be greater than 0")

        for idx in range(self.num_platforms):
            pf_x = random.randrange(0, self.width - PLATFORM_WIDTH)
            pf_y = self.height * 0.9 - (PLATFORM_GAP * idx - 1)

            # Randomize speed of platform and starting direction
            random_velocity = Vector2D(random.uniform(
                PLATFORM_MIN_SPEED, PLATFORM_MAX_SPEED), 0)
            random_direction = random.choice([1, -1])

            platform = Platform(idx, pf_x, pf_y, PLATFORM_WIDTH, PLATFORM_HEIGHT,
                                PLATFORM_COLOR, random_velocity, random_direction)

            self.platforms.append(platform)

    def start_game(self) -> None:
        self.is_game_over = False
        self.has_won = False
        self.current_platform = None
        self.eggs_left = self.max_eggs
        self.score = 0
        self.is_respawning = False

        self.generate_platforms()
        self.reset(0)

    def reset(self, platform_index: int) -> None:
        self.current_platform = self.platforms[platform_index]

        # Set egg position depending on platform
        self.egg.x = self.current_platform.x + self.current_platform.width // 2
        self.egg.y = self.current_platform.y - self.egg.radius
        self.egg.is_grounded = True
        self.egg.is_jumping = False
        self.egg.velocity.y = 0
        self.egg.velocity.x = self.current_platform.velocity.x

        # Resetting everything to make sure
        self.is_camera_moving = False
        self.is_game_over = False
        self.has_won = False
        self.is_respawning = False

    def jump(self, force: float) -> None:
        if self.egg.is_jumping:
            return

        self.egg.jump(force)
        self.egg.velocity.x = 0

    def move_platforms(self) -> None:
        if not self.platforms:
            raise ValueError("No platforms to update")

        for platform in self.platforms:
            platform.move()

            # Change platform direction on borders
            if platform.x <= 0:
                platform.x = 0
                platform.direction = 1

            elif platform.x + platform.width >= self.width:
                platform.x = self.width - platform.width
                platform.direction = -1

    def handle_platform_collision(self) -> None:
        assert self.current_platform is not None

        # Check if egg has reached the top
        if self.current_platform == self.platforms[-1]:
            self.has_won = True
            return

        # Only check for collision on next platform
        platform = self.platforms[self.current_platform.index + 1]
        egg_bottom = self.egg.y + self.egg.radius

        # If egg is going down and within platform bounds
        if (self.egg.velocity.y > 0 and
            egg_bottom <= platform.y + platform.height and  # Egg is above platform
            # Small offset for better collision, like creating a box instead of a point
                    egg_bottom >= platform.y - self.egg.velocity.y and
                    self.egg.x >= platform.x and
                    self.egg.x <= platform.x + platform.width
            ):

            # Position egg on platform and adjust state
            self.egg.y = platform.y - self.egg.radius
            self.egg.is_grounded = True
            self.egg.is_jumping = False

            # Can't move and set egg speed same as platform
            self.egg.velocity.y = 0
            self.egg.velocity.x = platform.velocity.x

            # We move to next platform and add score
            self.current_platform = platform
            self.score += 1

    def move_camera(self, speed: float) -> None:
        target_y = self.height * 0.8  # Target is a little bit above the bottom

        # Keep moving until egg position is higher than target
        if self.egg.y < target_y:
            self.is_camera_moving = True

            # Move egg and platforms down together
            self.egg.y += speed

            for platform in self.platforms:
                platform.y += speed

        else:
            self.is_camera_moving = False


class EggRiseView:
    def __init__(self, model: EggRiseModel) -> None:
        self.model = model

    def draw(self) -> None:
        self.clear_screen()

        # Draw game objects
        self.model.egg.draw()

        for platform in self.model.platforms:
            platform.draw()

    def clear_screen(self) -> None:
        pyxel.cls(0)

    def display_status(self, eggs_left: int, score: int, platforms: int) -> None:
        self.display_eggs_left(eggs_left)
        self.display_score(score)
        self.display_num_platforms(platforms)

    def display_eggs_left(self, eggs_left: int) -> None:
        text = f"Eggs Left: {eggs_left}"
        pyxel.text(10, 10, text, 7)

    def display_score(self, score: int) -> None:
        text = f"Score: {score}"
        pyxel.text(10, 20, text, 7)

    def display_num_platforms(self, platforms: int) -> None:
        text = f"Platforms: {platforms}"
        pyxel.text(10, 30, text, 7)

    def display_win(self) -> None:
        text = "You Win!"
        pyxel.text(MID_WIDTH - len(text) * 4 // 2, MID_HEIGHT, text, WIN_COLOR)

    def display_game_over(self) -> None:
        text = "Game Over"
        pyxel.text(MID_WIDTH - len(text) * 4 // 2,
                   MID_HEIGHT, text, LOSE_COLOR)

    def display_restart(self, color: int) -> None:
        text = "Press 'R' to restart"
        pyxel.text(MID_WIDTH - len(text) * 4 // 2,
                   MID_HEIGHT + 10, text, color)


class EggRiseController:
    def __init__(self, model: EggRiseModel, view: EggRiseView) -> None:
        self.model = model
        self.view = view

        # Setup game window
        pyxel.init(self.model.width, self.model.height,
                   title=self.model.title, fps=self.model.fps)

    def run(self) -> None:
        self.model.start_game()
        pyxel.run(self.update, self.draw)

    def update(self) -> None:
        self.model.update()
        self.handle_input()

    def draw(self) -> None:
        self.view.draw()
        self.view.display_status(self.model.eggs_left,
                                 self.model.score,
                                 self.model.num_platforms)

        if self.model.is_game_over:
            self.view.display_game_over()
            self.view.display_restart(LOSE_COLOR)

        if self.model.has_won:
            self.view.display_win()
            self.view.display_restart(WIN_COLOR)

    def handle_input(self) -> None:
        # Quit game
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        # Restart game
        if pyxel.btnp(pyxel.KEY_R) and (self.model.is_game_over or self.model.has_won):
            self.model.start_game()

        # Jump
        if pyxel.btnp(pyxel.KEY_SPACE) and not (self.model.is_game_over or self.model.has_won or self.model.is_camera_moving):
            self.model.jump(JUMP_FORCE)
