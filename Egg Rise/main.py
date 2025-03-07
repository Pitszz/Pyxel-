from eggrise import EggRiseModel, EggRiseView, EggRiseController
from classes import Egg, Vector2D
from constants import (
    WIDTH,
    HEIGHT,
    FPS,
    EGG_RADIUS,
    EGG_COLOR,
)


def main() -> None:
    egg = Egg(0, 0, EGG_RADIUS, EGG_COLOR, Vector2D(0, 0))

    model = EggRiseModel("Egg Rise", WIDTH, HEIGHT, FPS, egg, 1000, 1000)
    view = EggRiseView(model)
    controller = EggRiseController(model, view)

    controller.run()


if __name__ == "__main__":
    main()
