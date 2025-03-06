import math
import pyxel

from dataclasses import dataclass
from constants import WIDTH, HEIGHT, FPS, GRAVITY, BALL_RADIUS, BALL_COLOR, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_COLOR, BALL_SPEED, PADDLE_SPEED, JUMP_SPEED, PADDLE_SECTIONS


@dataclass
class Vector2D:
    x: float
    y: float


class Paddle:
    def __init__(self, x: int, y: int, width: int, height: int, color: int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

        # Create a velocity vector
        self.velocity = Vector2D(PADDLE_SPEED, 0)

    def update(self) -> None:
        self.move()

    def draw(self) -> None:
        pyxel.rect(self.x, self.y, self.width, self.height, self.color)

    def move(self) -> None:
        # Move left
        if pyxel.btn(pyxel.KEY_A) and self.x > 0:
            self.x -= self.velocity.x

        # Move right
        if pyxel.btn(pyxel.KEY_D) and self.x + self.width < WIDTH:
            self.x += self.velocity.x

    def get_bounce_angle(self, ball_x: int) -> float:
        angle_map = {
            0: 5*math.pi / 6,  # 150 degrees
            1: 2*math.pi / 3,  # 120 degrees
            2: math.pi,  # 180 degrees
            3: math.pi / 6,  # 30 degrees
            4: math.pi / 3  # 60 degrees
        }

        section = self.get_section(ball_x)

        return angle_map[section]

    def get_section(self, ball_x: int) -> int:
        # 10, -> 10 // (100 / 5) = 0, 20 -> 20 // (100 / 5) = 1, relative x, then divide it by the SECTION WIDTH
        relative_x = ball_x - self.x
        section = int(relative_x // (self.width / PADDLE_SECTIONS))

        return max(0, min(section, 4))


class Ball:
    def __init__(self, x: int, y: int, radius: int, color: int) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

        # Create a velocity vector
        self.velocity = Vector2D(0, 0)

    def update(self) -> None:
        self.apply_gravity(GRAVITY)
        self.move()
        self.handle_border_collision()

    def draw(self) -> None:
        pyxel.circ(self.x, self.y, self.radius, self.color)

    def move(self) -> None:
        self.x += self.velocity.x
        self.y += self.velocity.y

    def apply_gravity(self, gravity: float) -> None:
        self.velocity.y += gravity

    def bounce(self, section: int, angle: float) -> None:
        self.velocity.x = math.cos(angle) * BALL_SPEED
        self.velocity.y = JUMP_SPEED

        if section < 2:
            self.velocity.x = -abs(self.velocity.x)
        elif section > 2:
            self.velocity.x = abs(self.velocity.x)
        else:
            self.velocity.x = 0

    def handle_border_collision(self) -> None:
        # Left border
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.velocity.x *= -1

        # Right border
        elif self.x + self.radius >= WIDTH:
            self.x = WIDTH - self.radius
            self.velocity.x *= -1

        # Top border
        if self.y - self.radius < 0:
            self.y = self.radius
            self.velocity.y *= -1


class Game:
    def __init__(self, title: str, paddle: Paddle, ball: Ball) -> None:
        # Setup game window
        pyxel.init(WIDTH, HEIGHT, title=title, fps=FPS)

        # Game objects
        self.paddle = paddle
        self.ball = ball

        self.is_game_over = False
        self.score = 0

        # Run the game
        pyxel.run(self.update, self.draw)

    def update(self) -> None:
        if not self.is_game_over:
            self.handle_paddle_collision()
            self.ball.update()
            self.paddle.update()

            # Game over once ball reaches bottom
            if self.ball.y + self.ball.radius >= HEIGHT:
                self.is_game_over = True
        else:
            # Restart the game
            if pyxel.btnp(pyxel.KEY_R):
                self.restart_game()

    def restart_game(self) -> None:
        self.is_game_over = False

        # Reset ball
        self.ball.x = WIDTH//2
        self.ball.y = HEIGHT//2
        self.ball.velocity = Vector2D(0, 0)

        # Reset paddle
        self.paddle.x = WIDTH//2 - PADDLE_WIDTH//2

        # Reset score
        self.score = 0

    def draw(self) -> None:
        # Clear the screen
        pyxel.cls(0)

        self.display_score()
        self.ball.draw()
        self.paddle.draw()

        self.debug()

        # Display game over
        if self.is_game_over:
            self.display_game_over()

    def display_score(self) -> None:
        score_txt = f"Score: {self.score}"
        pyxel.text(WIDTH//2 - (len(score_txt) * 4 // 2), 10, score_txt, 7)

    def display_game_over(self) -> None:
        txt1 = "Game Over"
        txt2 = "'Press R to restart'"

        # Draw them in center (1 char = 4px)
        pyxel.text(WIDTH//2 - (len(txt1) * 4 // 2), HEIGHT//2 - 10, txt1, 7)
        pyxel.text(WIDTH//2 - (len(txt2) * 4 // 2), HEIGHT//2 + 10, txt2, 7)

    def debug(self) -> None:
        dbc = 3  # Debug text color
        pyxel.text(
            10, 10, f"Ball: ({self.ball.x:.0f}, {self.ball.y:.0f})", dbc)
        pyxel.text(
            10, 20, f"Paddle: ({self.paddle.x:.0f}, {self.paddle.y:.0f})", dbc)

        # Display section and angle
        section = self.paddle.get_section(self.ball.x)
        angle = self.paddle.get_bounce_angle(self.ball.x)
        angle = angle * 180 / math.pi

        pyxel.text(10, 30, f"Section: {section}", dbc)
        pyxel.text(10, 40, f"Angle: {angle:.2f}", dbc)

    def handle_paddle_collision(self) -> None:
        # Make sure ball is going down
        if self.ball.velocity.y > 0:
            # Check if bottom of the ball is at the same level as the paddle
            if self.ball.y + self.ball.radius >= self.paddle.y:
                # Check if the ball is within the paddle's width
                if self.ball.x >= self.paddle.x and self.ball.x <= self.paddle.x + self.paddle.width:
                    # Get the bounce data
                    section = self.paddle.get_section(self.ball.x)
                    angle = self.paddle.get_bounce_angle(self.ball.x)

                    # Bounce the ball and update score
                    self.ball.bounce(section, angle)
                    self.update_score(section)

    def update_score(self, section: int) -> None:
        # You get less score for hitting ball in the middle
        if section in (0, 4):
            self.score += 100
        elif section in (1, 3):
            self.score += 80
        else:
            self.score += 20


if __name__ == "__main__":
    ball = Ball(WIDTH//2, HEIGHT//2, BALL_RADIUS, BALL_COLOR)
    paddle = Paddle(WIDTH//2 - PADDLE_WIDTH//2, HEIGHT -
                    20, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_COLOR)

    Game("Arkanoid", paddle, ball)
