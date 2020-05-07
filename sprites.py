# Sprite classes for platform game
import pygame as pg
from settings import *
vec = pg.math.Vector2

def resize_to_multiplier(image):
    resized_img = pg.transform.scale(image, (image.get_width() * SIZE_MULTIPLIER, image.get_height() * SIZE_MULTIPLIER))
    return resized_img

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.image = resize_to_multiplier(self.image)
        self.rect = self.image.get_rect()
        self.image_right = self.image
        self.image_left = pg.transform.flip(self.image, True, False)
        self.pos = vec(x,y)
        self.rect.center = self.pos
        self.vel = vec(0,0)
        self.acc = vec(0,0)

    def get_keys(self):
        self.acc = vec(0,GRAVITY)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.acc.x = - PLAYER_ACC
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.acc.x =  PLAYER_ACC

    def update(self):
        self.get_keys()
        #apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION

        #laws of motion, acceleration is added to velocity.
        #In the x axis ,if the button is not pressed, not change in velocity (except friction)
        self.vel += self.acc

        #makes player stop in case of very low speed (x)
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0

        #update position, v+1/2Gamma (not squared?)
        self.pos += self.vel + 0.5 * self.acc

        #flips image based on velocity
        if self.vel.x > 0:
            self.image = self.image_right
        if self.vel.x < 0:
            self.image = self.image_left

        #applies change in position to rect
        self.rect.midbottom = self.pos

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
