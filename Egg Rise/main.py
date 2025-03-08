from eggrise import EggRiseModel, EggRiseView, EggRiseController
from classes import Egg, Vector2D, PlatformGenerator
from constants import (
    WIDTH,
    HEIGHT,
    FPS,
    EGG_RADIUS,
    EGG_COLOR,
    REMOVE_AMOUNT,
)


def main() -> None:
    egg = Egg(0, 0, EGG_RADIUS, EGG_COLOR, Vector2D(0, 0))

    generator = PlatformGenerator(5, True)  # Set to False for limited pf
    check_platform_amount(generator)

    model = EggRiseModel("Egg Rise", WIDTH, HEIGHT, FPS,
                         egg, 3, generator.max, generator, generator.is_infinite)
    view = EggRiseView(model)
    controller = EggRiseController(model, view)

    controller.run()


def check_platform_amount(generator: PlatformGenerator) -> None:
    # Max platform at a time should at least be twice the amount to be removed
    MIN_PLATFORMS = REMOVE_AMOUNT * 2

    if generator.is_infinite and generator.max < MIN_PLATFORMS:
        raise ValueError(
            f"Max Platform at a time should at least be [{MIN_PLATFORMS}]")


if __name__ == "__main__":
    main()
