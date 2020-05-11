
import pygame as pg
import sys
from os import path
import random
from settings import *
from sprites import *
from tilemap import *
from enum import Enum

class Game:
    def __init__(self):
        # initialize game window, etc
        pg.mixer.pre_init(44100, -16, 4, 2048)
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.toggle_hitbox = False
        self.load_data()
        self.state = State.PLAY

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder =  path.join(game_folder, 'img')
        self.map_folder = path.join(game_folder, 'maps')
        self.player_img = pg.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.mob_img = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.bullet_img = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.title_font = path.join(img_folder, 'press_start.ttf')

    def new(self):
        # start a new game
        self.state = State.PLAY
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.spikes = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()

        #creates map image and resize to tile multiplier
        self.map = TiledMap(path.join(self.map_folder, 'level1.tmx'))
        self.map_img = self.map.make_map()
        self.map_img = resize_to_multiplier(self.map_img, TILE_SIZE_MULTIPLIER)
        self.map.rect = self.map_img.get_rect()
        #creates objects based on map filename
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height /2) # will need to sort multiplier
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x * TILE_SIZE_MULTIPLIER, tile_object.y * TILE_SIZE_MULTIPLIER,
                         tile_object.width * TILE_SIZE_MULTIPLIER, tile_object.height * TILE_SIZE_MULTIPLIER)
            if tile_object.name == 'spike':
                Spike(self, tile_object.x * TILE_SIZE_MULTIPLIER, tile_object.y * TILE_SIZE_MULTIPLIER,
                         tile_object.width * TILE_SIZE_MULTIPLIER, tile_object.height * TILE_SIZE_MULTIPLIER)
            if tile_object.name == 'player':
                self.player = Player(self, tile_object.x * TILE_SIZE_MULTIPLIER,
                                     (tile_object.y + tile_object.height) * TILE_SIZE_MULTIPLIER)
            if tile_object.name == 'mob':
                Mob(self, tile_object.x * TILE_SIZE_MULTIPLIER,
                    (tile_object.y + tile_object.height) * TILE_SIZE_MULTIPLIER)


        self.run()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
            #print(self.state)

    def update(self):


        # Game Loop - Update
        self.all_sprites.update()

        #player hits spikes:
        hits = pg.sprite.spritecollide(self.player, self.spikes, False)
        for hit in hits:
            self.state = State.GAME_OVER
            self.playing = False

        #player hits mobs:
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            self.state = State.GAME_OVER
            self.playing = False

        #mobs hits bullets:
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for mob in hits:
            for bullet in hits[mob]:
                mob.kill()


    def events(self):


        # Game Loop - events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_cut()
            if event.type == pg.KEYUP:
                if event.key == pg.K_t:
                    self.toggle_hitbox = not self.toggle_hitbox



    def draw(self):

        # Game Loop - draw
        #self.screen.fill(BLACK)
        self.screen.blit(self.map_img, (0, 0))
        self.all_sprites.draw(self.screen)
        if self.toggle_hitbox:
            pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)
            self.walls.draw(self.screen)
            self.spikes.draw(self.screen)
            for mob in self.mobs:
                pg.draw.rect(self.screen, RED, mob.hit_rect, 2 )
            for bullet in self.bullets:
                pg.draw.rect(self.screen, RED, bullet.rect, 2 )
        # *after* drawing everything, flip the display
        pg.display.flip()


    def show_go_screen(self):
        # game over/continue
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", self.title_font, 50, RED,
                       WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Press a key to start", self.title_font, 25, WHITE,
                       WIDTH / 2, HEIGHT * 3 / 4, align="center")
        pg.display.flip()
        self.wait_for_key()

    def show_start_screen(self):
        # game over/continue
        self.screen.fill(BLACK)
        self.draw_text("MACHETE JANE", self.title_font, 50, RED,
                       WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Press a key to start", self.title_font, 25, WHITE,
                       WIDTH / 2, HEIGHT * 3 / 4, align="center")
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False


    def quit(self):
        pg.quit()
        sys.exit()

class State(Enum):
    SPLASH_SCREEN = 1
    MENU = 2
    PLAY = 3
    GAME_OVER = 4
    CHANGE_LEVEL = 5

g = Game()
g.show_start_screen()

while g.running:
    g.new()
    g.run()
    g.show_go_screen()

pg.quit()
