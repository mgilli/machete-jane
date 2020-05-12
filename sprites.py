# Sprite classes for platform game
import pygame as pg
from settings import *
from random import choice, randint, uniform
vec = pg.math.Vector2

def gimme_gibs(game, pos, qty):
    for i in range(qty):
        impulse = randint(-GIB_IMPULSE, GIB_IMPULSE)
        #print(impulse)
        Gib(game, pos, impulse)

def gimme_player_gibs(game, pos):
    for image in game.player_gibs_imgs:
        impulse = randint(-20, 20)
        #print(impulse)
        Player_Gib(game, pos, impulse, image)

def flip_images(list):
    flipped_imgs = []
    for frame in list:
        flipped_imgs.append(pg.transform.flip(frame, True, False))
    return flipped_imgs

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
        self.load_images()
        self.pos = vec(x,y)
        self.rect.midbottom = self.pos
        self.hit_rect.midbottom = self.pos
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.jumping = False
        self.walking = False
        self.gun_dir = 'right'
        self.last_shot = 0
        self.last_update = 0
        self.current_frame = 0

    def load_images(self):
        self.idle_frames_r = self.game.player_idle_imgs
        self.walk_frames_r = self.game.player_walk_imgs

        self.idle_frames_l = flip_images(self.idle_frames_r)
        self.walk_frames_l = flip_images(self.walk_frames_r)

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
            self.game.jump_snd.play()

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > GUN_RATE:
            self.last_shot = now
            Bullet(self.game, self.pos, self.gun_dir)
            self.game.shoot_snd.play()

    def get_keys(self):
        self.acc = vec(0,GRAVITY)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.acc.x = - PLAYER_ACC
            #self.image = self.image_left
            self.gun_dir = 'left'
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.acc.x =  PLAYER_ACC
            #self.image = self.image_right
            self.gun_dir = 'right'
        if keys[pg.K_LCTRL] or keys[pg.K_LALT]:
            self.shoot()

    def animate(self):
        now = pg.time.get_ticks()
        if abs(self.vel.x) >= 1:
            self.walking = True
        else:
            self.walking = False
        # walk animation:
        if self.walking:
            if now - self.last_update > PLAYER_ANIM_SPEED:
                self.last_update = now
                self.current_frame = (self.current_frame +1) % len(self.walk_frames_r)
                bottom = self.rect.bottom
                if self.gun_dir == 'right':
                    self.image = self.walk_frames_r[self.current_frame]
                else:
                    self.image = self.walk_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        if not self.walking:
            if now - self.last_update > PLAYER_ANIM_SPEED:
                self.last_update = now
                self.current_frame = (self.current_frame +1) % len(self.idle_frames_r)
                bottom = self.rect.bottom
                if self.gun_dir == 'right':
                    self.image = self.idle_frames_r[self.current_frame]
                else:
                    self.image = self.idle_frames_l[self.current_frame]
                    self.rect = self.image.get_rect()
                    self.rect.bottom = bottom



    def update(self):
        self.get_keys()
        self.animate()
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
        self.walk_frames_l = self.game.mob_walk_imgs
        self.walk_frames_r = flip_images(self.walk_frames_l)

        self.last_update = 0
        self.current_frame = 0

    def animate(self):
        now = pg.time.get_ticks()

        # walk animation:

        if now - self.last_update > MOB_ANIM_SPEED:
            self.last_update = now
            self.current_frame = (self.current_frame +1) % len(self.walk_frames_r)
            bottom = self.rect.bottom
            if self.vel.x > 0:
                self.image = self.walk_frames_r[self.current_frame]
            else:
                self.image = self.walk_frames_l[self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom


    def update(self):
        self.animate()
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
        # if self.vel.x > 0:
        #     self.image = self.image_right
        # if self.vel.x < 0:
        #     self.image = self.image_left

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
        MuzzleFlash(self.game, self.pos, direction)

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
        self.groups = game.teleports
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

class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, game, pos, direction):
        self._layer = EFFECTS_LAYER
        self.groups =  game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.pos = pos
        size = randint(3,6)
        self.image = resize_to_multiplier(self.game.flash_img, size)
        self.rect = self.image.get_rect()
        if direction == 'left':
            self.image = pg.transform.flip(self.image, True, False)
            self.rect.midright = self.pos
        else:
            self.rect.midleft = self.pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > 50:
            self.kill()

class BloodSplatter(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = BLOOD_LAYER
        self.groups =  game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.pos = pos
        self.image = pg.transform.flip(choice(self.game.bloods_imgs),
                                       choice([True, False]), choice([True, False]))

        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.spawn_time = pg.time.get_ticks()
        #self.current_size = 1
        #self.last_update = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > BLOOD_DURATION:
            self.kill()
        # Failed attempt to animate blood, small pixles don't look good
        # now = pg.time.get_ticks()
        # if now - self.last_update > 25:
        #     center = self.rect.center
        #     self.last_update = now
        #     self.image = pg.transform.scale(self.image, (self.image.get_width() * self.current_size,
        #                                     self.image.get_height() * self.current_size))
        #     self.current_size += 1
        #     self.rect = self.image.get_rect()
        #     self.rect.center = center
        #
        # if self.current_size == 4:
        #     self.kill()

class Gib(pg.sprite.Sprite):
    def __init__(self, game, pos, impulse):
        self._layer = EFFECTS_LAYER
        self.groups =  game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.pos = vec(pos)
        self.image = pg.transform.flip(choice(self.game.gibs_imgs),
        choice([True, False]), choice([True, False]))

        self.rect = self.image.get_rect()
        self.hit_rect = pg.Rect(0,0,(self.rect.width * 0.25), (self.rect.height * 0.25))
        self.rect.midbottom = self.pos
        self.hit_rect.midbottom = self.pos
        self.impulse = impulse
        self.vel = vec(self.impulse,-abs(self.impulse))
        self.acc = vec(0,-randint(0, abs(self.impulse)))
        self.spawn_time = pg.time.get_ticks()
        #self.current_size = 1
        #self.last_update = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > 500:
            self.kill()

        self.acc = vec(0,GRAVITY)

        #self.acc.x += MOB_ACC * self.direction

        self.acc.x += self.vel.x * GIB_FRICTION

        #laws of motion, acceleration is added to velocity.
        #In the x axis ,if the button is not pressed, not change in velocity (except friction)
        self.vel += self.acc

        #update position, v+1/2Gamma (not squared?) and collisions
        self.pos.y += self.vel.y + 0.5 * self.acc.y
        self.hit_rect.bottom = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.bottom = self.hit_rect.bottom + 25

        self.pos.x += self.vel.x + 0.5 * self.acc.x
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.rect.centerx = self.hit_rect.centerx

class Player_Gib(pg.sprite.Sprite):
    def __init__(self, game, pos, impulse, image):
        self._layer = EFFECTS_LAYER
        self.groups =  game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.pos = vec(pos)
        self.image = pg.transform.flip(image,choice([True, False]), choice([True, False]))
        self.rect = self.image.get_rect()
        self.hit_rect = pg.Rect(0,0,(self.rect.width * 0.25), (self.rect.height * 0.25))
        self.rect.midbottom = self.pos
        self.hit_rect.midbottom = self.pos
        self.impulse = impulse
        self.vel = vec(self.impulse,-abs(self.impulse))
        self.acc = vec(0,-randint(0, abs(self.impulse)))
        self.spawn_time = pg.time.get_ticks()
        #self.current_size = 1
        #self.last_update = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > PLAYER_DEATH_DURATION:
            self.kill()

        self.acc = vec(0,GRAVITY)

        #self.acc.x += MOB_ACC * self.direction

        self.acc.x += self.vel.x * GIB_FRICTION

        #laws of motion, acceleration is added to velocity.
        #In the x axis ,if the button is not pressed, not change in velocity (except friction)
        self.vel += self.acc

        #update position, v+1/2Gamma (not squared?) and collisions
        self.pos.y += self.vel.y + 0.5 * self.acc.y
        self.hit_rect.bottom = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.bottom = self.hit_rect.bottom + 25

        self.pos.x += self.vel.x + 0.5 * self.acc.x
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.rect.centerx = self.hit_rect.centerx
