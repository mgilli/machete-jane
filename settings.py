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
BLOOD_LAYER = 5
MOB_LAYER = 2
EFFECTS_LAYER = 1

# Player settings

PLAYER_IMG = 'jane.png'
PLAYER_ACC = 0.7
PLAYER_FRICTION = -0.12
PLAYER_JUMP = 19

PLAYER_IDLE_IMGS = ['jane-idle0.png', 'jane-idle1.png', 'jane-idle2.png', 'jane-idle3.png', 'jane-idle4.png']
PLAYER_WALK_IMGS = ['jane-walking0.png','jane-walking1.png', 'jane-walking2.png', 'jane-walking3.png' ]

PLAYER_ANIM_SPEED = 180

PLAYER_DEATH_DURATION = 750

# Gun settings

BULLET_IMG = 'bullet.png'
BULLET_SPEED = 20
BULLET_LIFETIME = 2000
MUZZLE_OFFSET = vec(12 * CHARACTER_SIZE_MULTIPLIER, -10 * CHARACTER_SIZE_MULTIPLIER)
GUN_RATE = 350

# Mob settings

MOB_IMG = 'mummy.png'
MOB_ACC = 0.5
MOB_FRICTION = -0.12

MOB_WALK_IMGS = ['mummy_walk0.png', 'mummy_walk1.png','mummy_walk2.png','mummy_walk3.png' ]
MOB_ANIM_SPEED = 270

# Sound settings

BG_MUSIC = 'MJmusic1.ogg'

SHOOT_SND = 'shoot.wav'
JUMP_SND = 'jump.wav'
LOSE_SND = 'lose2.wav'
HIT_SND = 'hit.wav'

#effects settings

BLOOD_IMGS = ['blood1.png','blood2.png','blood3.png','blood4.png']
FLASH_IMG = 'flash.png'

BLOOD_DURATION = 64

GIB_IMGS = ['gib1.png','gib2.png','gib3.png','gib4.png','gib5.png','gib6.png','gib7.png','gib8.png']
PLAYER_GIB_IMGS = ['jane_gib1.png', 'jane_gib2.png', 'jane_gib3.png', 'jane_gib4.png',
                   'jane_gib5.png', 'jane_gib6.png', 'jane_gib7.png', ]
GIB_IMPULSE = 20
GIB_FRICTION = -0.20
