# Window properties
WIDTH = 240
HEIGHT = 360
MID_WIDTH = WIDTH // 2
MID_HEIGHT = HEIGHT // 2
FPS = 60  # Speed changes when fps is changed, we're missing delta time

# Game properties
CAMERA_SPEED = 2
CAMERA_OFFSET = 0.9  # This is mutliplied to the height
RESPAWN_TIME = 1

# Platform properties
PLATFORM_WIDTH = 60
PLATFORM_HEIGHT = 4
PLATFORM_COLOR = 15
LAST_PLATFORM_COLOR = 11
PLATFORM_MIN_SPEED = 2
PLATFORM_MAX_SPEED = 4
PLATFORM_GAP = 200

REMOVE_AMOUNT = 2

# Egg properties
EGG_RADIUS = 8
EGG_COLOR = 15

# Jump properties, depends on platform gap
GRAVITY = 0.5
JUMP_MULTIPLIER = 1.4
JUMP_FORCE = -((2 * GRAVITY * PLATFORM_GAP * JUMP_MULTIPLIER) ** 0.5)

# Colors
WIN_COLOR = 10
LOSE_COLOR = 8
BG_COLOR = 5
