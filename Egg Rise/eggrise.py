import pyxel
import random

from classes import Egg, Platform, PlatformGenerator
from constants import (
    JUMP_FORCE,
    GRAVITY,
    RESPAWN_TIME,
    MID_WIDTH,
    MID_HEIGHT,
    WIN_COLOR,
    LOSE_COLOR,
    CAMERA_SPEED,
    BG_COLOR,
    CAMERA_OFFSET,
    REMOVE_AMOUNT,
    DEBUG_COLOR,
)


class EggRiseModel:
    def __init__(self, title: str, width: int, height: int, fps: int, egg: Egg, max_eggs: int, num_platforms: int, platform_generator: PlatformGenerator, is_infinite: bool) -> None:
        # Properties
        self.title = title
        self.width = width
        self.height = height
        self.fps = fps
        self.num_platforms = num_platforms

        # Game objects
        self.egg = egg
        self.platforms: list[Platform] = []
        self.platform_generator = platform_generator

        # Game state
        self.is_game_over = False
        self.has_won = False
        self.max_eggs = max_eggs
        self.eggs_left = self.max_eggs
        self.score = 0
        self.is_respawning = False
        self.is_camera_moving = False
        self.is_infinite = is_infinite

        self.last_removed_index = 0

    def update(self) -> None:
        # Don't do anything if game is over or has won
        if self.is_game_over:
            return

        # Continuously generate if infinite
        if self.is_infinite:
            self.generate_new_platforms(REMOVE_AMOUNT)

        # Move egg horizontally if on platform
        egg_direction = self.current_platform.direction if self.current_platform else 0
        self.egg.move(egg_direction)
        self.egg.apply_gravity(GRAVITY)

        # Move platforms and check if egg is out of bounds
        self.check_out_of_bounds()
        self.move_platforms()
        self.handle_platform_collision()

        # Move the camera if egg is on a platform and reaches at least the 2nd platform
        if self.egg.is_grounded and self.has_reached_platform_k(1):
            self.move_camera(CAMERA_SPEED)

    def generate_new_platforms(self, amount: int) -> None:
        if self.current_platform.index >= self.last_removed_index + amount:
            # Only remove and regenerate after reaching twice amount to be removed
            if (self.current_platform.index > 0 and
                self.current_platform.index % amount == 0 and
                    len(self.platforms) == self.num_platforms):

                # Store last index so we don't infinitely remove pf
                self.last_removed_index = self.current_platform.index

                self.platform_generator.remove(amount)
                self.platforms = self.platform_generator.generate()

    def check_out_of_bounds(self) -> None:
        # Game over if we have no eggs left
        if self.eggs_left <= 0:
            self.is_game_over = True
            return

        # Check if egg falls at the bottom
        if self.egg.y > self.height:
            # Stop the egg from falling further
            self.egg.y = self.height + self.egg.radius

            # Only subtract eggs if not respawning
            if not self.is_respawning:
                self.eggs_left -= 1
                self.is_respawning = True

            # Wait some time before respawning the egg
            if self.has_time_elapsed(RESPAWN_TIME):
                self.is_respawning = False
                self.reset(self.current_platform.index)

    def has_time_elapsed(self, seconds: float) -> bool:
        return pyxel.frame_count % (self.fps * seconds) == 0

    def start_game(self) -> None:
        self.is_game_over = False
        self.has_won = False
        self.eggs_left = self.max_eggs
        self.score = 0
        self.is_respawning = False

        self.clear_platforms()
        self.platforms = self.platform_generator.generate()
        self.last_removed_index = 0
        # print("New: ", len(self.platforms))
        self.reset(0)

    def clear_platforms(self) -> None:
        self.platforms.clear()
        self.platform_generator.reset()
        # print("Old: ", len(self.platforms))

    def reset(self, platform_index: int) -> None:
        self.current_platform = self.platforms[self.get_platform_index(
            platform_index)]

        # Set egg position depending on platform
        self.egg.x = self.current_platform.x + self.current_platform.width // 2
        self.egg.y = self.current_platform.y - self.egg.radius
        self.egg.is_grounded = True
        self.egg.is_jumping = False
        self.egg.velocity.y = 0
        self.egg.velocity.x = self.current_platform.velocity.x

        # Randomize egg color
        self.randomize_egg()

        # Resetting everything to make sure
        self.is_camera_moving = False
        self.is_game_over = False
        self.has_won = False
        self.is_respawning = False

    def get_platform_index(self, index: int) -> int:
        for idx, platform in enumerate(self.platforms):
            if platform.index == index:
                return idx

        return 0

    # Cheat for testing
    def teleport(self) -> None:
        self.reset(self.current_platform.index + 1)
        self.score += 1

    def randomize_egg(self) -> None:
        while True:
            color = random.randint(0, 16)

            if color not in [BG_COLOR]:
                self.egg.color = color
                break

    def jump(self, force: float) -> None:
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
        if self.has_reached_platform_k(self.num_platforms - 1) and not self.is_infinite:
            self.has_won = True
            return

        # Only check for collision on next platform
        target_platform = self.platforms[self.get_platform_index(
            self.current_platform.index + 1)]
        egg_bottom = self.egg.y + self.egg.radius

        # If egg is going down and within platform bounds
        if (self.egg.velocity.y >= 0 and
                egg_bottom <= target_platform.y + target_platform.height and  # Egg is above platform
                # Small offset for better collision, like creating a box instead of a point
                egg_bottom >= target_platform.y - self.egg.velocity.y and
                self.egg.x >= target_platform.x and
                self.egg.x <= target_platform.x + target_platform.width
                ):

            # Position egg on platform and adjust state
            self.egg.y = target_platform.y - self.egg.radius
            self.egg.is_grounded = True
            self.egg.is_jumping = False

            # Can't move down and set egg speed same as new platform
            self.egg.velocity.y = 0
            self.egg.velocity.x = target_platform.velocity.x

            # We move to next platform and add score
            self.current_platform = target_platform
            self.score += 1

    def has_reached_platform_k(self, index: int) -> bool:
        return self.current_platform.index >= index

    def move_camera(self, speed: float) -> None:
        # Target position is based on a multiplier of screen height
        target_y = self.height * CAMERA_OFFSET

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
        self.text_amount = 0

    def draw(self) -> None:
        self.clear_screen()

        # Draw game objects
        self.model.egg.draw()

        for platform in self.model.platforms:
            platform.draw()

    def clear_screen(self) -> None:
        pyxel.cls(BG_COLOR)

    def display_status(self, eggs_left: int, score: int) -> None:
        self.display_eggs_left(eggs_left)
        self.display_score(score)

    def display_eggs_left(self, eggs_left: int) -> None:
        text = f"Eggs Left: {eggs_left}"
        pyxel.text(10, 10, text, 7)

    def display_score(self, score: int) -> None:
        text = f"Score: {score}"
        pyxel.text(10, 20, text, 7)

    def display_num_platforms(self, platforms: int) -> None:
        if self.model.is_infinite:
            text = f"Platforms: {platforms} (Infinite)"
        else:
            text = f"Platforms: {platforms}"

        pyxel.text(10, 30, text, DEBUG_COLOR)

    def display_debug(self) -> None:
        next_pf = self.model.platforms[self.model.get_platform_index(
            self.model.current_platform.index + 1)]
        to_display = [f"is_game_over = {self.model.is_game_over}",
                      f"has_won = {self.model.has_won}",
                      f"is_grounded = {self.model.egg.is_grounded}",
                      f"is_camera_moving = {self.model.is_camera_moving}",
                      f"EGG POS = ({self.model.egg.x:.0f}, {self.model.egg.y:.0f})",
                      f"NEXT PF = ({next_pf.x:.0f}, {next_pf.y:.0f})",
                      ]

        for idx, dp in enumerate(to_display, 1):
            pyxel.text(10, 30 + idx * 10, dp, DEBUG_COLOR)

    def display_cheat_help(self) -> None:
        text = "Press 'C' to teleport"
        pyxel.text((MID_WIDTH * 2) - len(text) * 4 - 10, 10, text, 7)

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
        self.view.display_status(self.model.eggs_left, self.model.score)

        # Optional displays
        self.view.display_num_platforms(self.model.num_platforms)
        self.view.display_cheat_help()
        self.view.display_debug()

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
        if pyxel.btnp(pyxel.KEY_R):
            self.model.start_game()

        # Jump
        if pyxel.btnp(pyxel.KEY_SPACE) and not (self.model.is_game_over or self.model.has_won or self.model.is_camera_moving):
            self.model.jump(JUMP_FORCE)

        if pyxel.btn(pyxel.KEY_C) and self.model.has_time_elapsed(0.5):
            self.model.teleport()
