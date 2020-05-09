# Sprite classes for platform game
import pygame as pg
from settings import *
vec = pg.math.Vector2

def resize_to_multiplier(image, mult):
    resized_img = pg.transform.scale(image, (image.get_width() * mult , image.get_height() * mult))
    return resized_img

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.acc.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - 0
                sprite.jumping = False
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height
            sprite.vel.y = 0
            sprite.acc.y = 0
            sprite.hit_rect.bottom = sprite.pos.y

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.image = resize_to_multiplier(self.image, CHARACTER_SIZE_MULTIPLIER)
        self.rect = self.image.get_rect()
        self.hit_rect = pg.Rect(0,0,(self.rect.width * 0.25), (self.rect.height * 0.75))
        self.image_right = self.image
        self.image_left = pg.transform.flip(self.image, True, False)
        self.pos = vec(x,y)
        self.rect.midbottom = self.pos
        self.hit_rect.midbottom = self.pos
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.jumping = False

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3



    def jump(self):
        self.hit_rect.bottom += 1
        hits = pg.sprite.spritecollide(self, self.game.walls, False,  collide_hit_rect)
        self.hit_rect.bottom -= 1
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y -= PLAYER_JUMP

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

        #update position, v+1/2Gamma (not squared?) and collisions
        self.pos.y += self.vel.y + 0.5 * self.acc.y
        self.hit_rect.bottom = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.bottom = self.hit_rect.bottom

        self.pos.x += self.vel.x + 0.5 * self.acc.x
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.rect.centerx = self.hit_rect.centerx




        #flips image based on velocity
        if self.vel.x > 0:
            self.image = self.image_right
        if self.vel.x < 0:
            self.image = self.image_left


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups =  game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((w,h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
