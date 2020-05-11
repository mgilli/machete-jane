# Sprite classes for platform game
import pygame as pg
from settings import *
vec = pg.math.Vector2

def resize_to_multiplier(image, mult):
    resized_img = pg.transform.scale(image, (image.get_width() * mult , image.get_height() * mult))
    return resized_img

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

def collide_hit_rect_mob(one, two):
    return one.hit_rect.colliderect(two.hit_rect)

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
            if sprite.__class__.__name__ == 'Mob':
                sprite.direction *= -1
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
        self._layer = PLAYER_LAYER
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
        self.gun_dir = 'right'
        self.last_shot = 0

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

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > GUN_RATE:
            self.last_shot = now
            Bullet(self.game, self.pos, self.gun_dir)

    def get_keys(self):
        self.acc = vec(0,GRAVITY)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.acc.x = - PLAYER_ACC
            self.image = self.image_left
            self.gun_dir = 'left'
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.acc.x =  PLAYER_ACC
            self.image = self.image_right
            self.gun_dir = 'right'
        if keys[pg.K_LCTRL]:
            self.shoot()


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

class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups =  game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((w,h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Spike(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups =  game.spikes
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((w,h))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        self.groups = game.mobs, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img
        self.image = resize_to_multiplier(self.image, CHARACTER_SIZE_MULTIPLIER)
        self.rect = self.image.get_rect()
        self.hit_rect = pg.Rect(0,0,(self.rect.width * 0.25), (self.rect.height * 0.75))
        self.image_left = self.image
        self.image_right = pg.transform.flip(self.image, True, False)
        self.pos = vec(x,y)
        self.rect.midbottom = self.pos
        self.hit_rect.midbottom = self.pos
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.direction = -1

    def update(self):
        self.acc = vec(0,GRAVITY)

        self.acc.x += MOB_ACC * self.direction

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

class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, direction):
        self._layer = BULLET_LAYER
        self.groups = game.bullets, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_img
        self.image = resize_to_multiplier(self.image, CHARACTER_SIZE_MULTIPLIER)
        self.vel = BULLET_SPEED
        if direction == 'left':
            self.image = pg.transform.flip(self.image, True, False)
            self.vel = -BULLET_SPEED
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.pos.y = self.pos.y + MUZZLE_OFFSET.y
        self.pos.x = self.pos.x + (self.vel/BULLET_SPEED) * MUZZLE_OFFSET.x
        self.rect.center = self.pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.pos.x += self.vel
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()

class Teleport(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, dest):
        self._layer = EFFECT_LAYER
        self.groups = game.all_sprites, game.teleports
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((w,h))
        self.image.fill(RED)
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.destination = dest
