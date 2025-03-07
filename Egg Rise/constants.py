# Window properties
WIDTH = 240
HEIGHT = 360
MID_WIDTH = WIDTH // 2
MID_HEIGHT = HEIGHT // 2
FPS = 60  # Speed changes when fps is changed, we're missing delta time

# Game properties
CAMERA_SPEED = 2
RESPAWN_TIME = 1

# Platform properties
PLATFORM_WIDTH = 60
PLATFORM_HEIGHT = 4
PLATFORM_COLOR = 7
PLATFORM_MIN_SPEED = 2
PLATFORM_MAX_SPEED = 4
PLATFORM_GAP = 200

# Egg properties
EGG_RADIUS = 8
EGG_COLOR = 9

# Jump properties, depends on platform gap
GRAVITY = 0.5
JUMP_MULTIPLIER = 1.4
JUMP_FORCE = -((2 * GRAVITY * PLATFORM_GAP * JUMP_MULTIPLIER) ** 0.5)

# Colors
WIN_COLOR = 9
LOSE_COLOR = 8
