import pygame as pg
vec = pg.math.Vector2

# game options/settings
TITLE = "Machete Jane"

#resize the sprite images during import
CHARACTER_SIZE_MULTIPLIER = 4
TILE_SIZE_MULTIPLIER = 4

WIDTH = 1024
HEIGHT = 576
FPS = 60


# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)


# World settings

GRAVITY = 0.8

# Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
EFFECT_LAYER = 4
MOB_LAYER = 2
EFFECTS_LAYER = 1

# Player settings

PLAYER_IMG = 'jane.png'
PLAYER_ACC = 0.7
PLAYER_FRICTION = -0.12
PLAYER_JUMP = 19

# Gun settings

BULLET_IMG = 'bullet.png'
BULLET_SPEED = 20
BULLET_LIFETIME = 2000
MUZZLE_OFFSET = vec(12 * CHARACTER_SIZE_MULTIPLIER, -11 * CHARACTER_SIZE_MULTIPLIER)
GUN_RATE = 350

# Mob settings

MOB_IMG = 'mummy.png'
MOB_ACC = 0.5
MOB_FRICTION = -0.12

# Sound settings

BG_MUSIC = 'MJmusic1.ogg'

SHOOT_SND = 'shoot.wav'
JUMP_SND = 'jump.wav'
LOSE_SND = 'lose2.wav'
HIT_SND = 'hit.wav'
