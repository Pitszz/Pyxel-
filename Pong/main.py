import pyxel
import random

from classes import Paddle, Ball
from constants import (
    WIDTH,
    HEIGHT,
    MID_HEIGHT,
    MID_WIDTH,
    FPS,
    BALL_COLOR,
    BALL_RADIUS,
    BALL_SPEED,
    PADDLE_COLOR,
    PADDLE_WIDTH,
    PADDLE_HEIGHT,
    PADDLE_OFFSET,
    SCORE_OFFSET,
)


class Game:
    def __init__(self, title: str, p1: Paddle, p2: Paddle, ball: Ball) -> None:
        # Setup game window
        pyxel.init(WIDTH, HEIGHT, title=title, fps=FPS)

        # Game Objects
        self.p1 = p1
        self.p2 = p2
        self.ball = ball

        # Scores
        self.p1_score = 0
        self.p2_score = 0

        self.round_end_time = None

        # Run game
        pyxel.run(self.update, self.draw)

    def update(self) -> None:
        if self.round_end_time is not None:
            self.reset()

            if pyxel.frame_count - self.round_end_time >= FPS * 1:
                self.round_end_time = None

            return

        if not self.is_round_over():
            self.p1.move()
            self.p2.move()
            self.ball.move()

            self.handle_paddle_collisions()
            self.handle_border_collisions()
        else:
            winner = self.get_winner()
            self.update_score(winner)

            self.round_end_time = pyxel.frame_count

    def draw(self) -> None:
        # Clear screen
        pyxel.cls(0)

        self.p1.draw()
        self.p2.draw()
        self.ball.draw()
        self.display_score()

    def handle_paddle_collisions(self) -> None:
        # Right paddle
        if self.ball.x >= self.p2.x:
            if self.ball.y - BALL_RADIUS >= self.p2.y \
                    and self.ball.y + BALL_RADIUS <= self.p2.y + PADDLE_HEIGHT:
                section = self.p2.get_bounce_section(self.ball.y)
                angle = self.p2.get_bounce_angle(section)

                self.ball.bounce(section, angle, 1)

        # Left paddle
        elif self.ball.x <= self.p1.x + PADDLE_WIDTH:
            if self.ball.y - BALL_RADIUS >= self.p1.y \
                    and self.ball.y + BALL_RADIUS <= self.p1.y + PADDLE_HEIGHT:
                section = self.p1.get_bounce_section(self.ball.y)
                angle = self.p1.get_bounce_angle(section)

                self.ball.bounce(section, angle, -1)

    def handle_border_collisions(self) -> None:
        if self.ball.y - BALL_RADIUS <= 0 or self.ball.y + BALL_RADIUS >= HEIGHT:
            self.ball.bounce_off_border()

    def reset(self) -> None:
        # Reset paddles
        self.p1.y = MID_HEIGHT - PADDLE_HEIGHT//2
        self.p2.y = MID_HEIGHT - PADDLE_HEIGHT//2

        # Reset ball
        self.ball.x = MID_WIDTH
        self.ball.y = MID_HEIGHT
        self.ball.velocity.x *= random.choice([1, -1])
        self.ball.velocity.y *= random.choice([1, -1])

    def update_score(self, winner: int) -> None:
        if winner == 1:
            self.p1_score += 1
        elif winner == 2:
            self.p2_score += 1

    def get_winner(self) -> int:
        # If the ball was moving right, then winner is p1
        return 1 if self.ball.velocity.x > 0 else 2

    def is_round_over(self) -> bool:
        return self.ball.x + BALL_RADIUS >= WIDTH or self.ball.x - BALL_RADIUS <= 0

    def display_score(self) -> None:
        pyxel.text(WIDTH//3 - len(str(self.p1_score)) * 4 //
                   2, SCORE_OFFSET, str(self.p1_score), 7)

        pyxel.text(WIDTH//3 * 2 - len(str(self.p2_score)) * 4 //
                   2, SCORE_OFFSET, str(self.p2_score), 7)


if __name__ == "__main__":
    p1 = Paddle(
        PADDLE_OFFSET,
        MID_HEIGHT - PADDLE_HEIGHT//2,
        PADDLE_WIDTH,
        PADDLE_HEIGHT,
        PADDLE_COLOR,
        pyxel.KEY_W,
        pyxel.KEY_S
    )

    p2 = Paddle(
        WIDTH - PADDLE_OFFSET - PADDLE_WIDTH,
        MID_HEIGHT - PADDLE_HEIGHT//2,
        PADDLE_WIDTH,
        PADDLE_HEIGHT,
        PADDLE_COLOR,
        pyxel.KEY_UP,
        pyxel.KEY_DOWN
    )

    ball = Ball(MID_WIDTH, MID_HEIGHT, BALL_RADIUS, BALL_COLOR)

    Game("Pong", p1, p2, ball)
