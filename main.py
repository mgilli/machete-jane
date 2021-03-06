
import pygame as pg
import sys
from os import path
import random
from settings import *
from sprites import *
from tilemap import *
from enum import Enum
from datetime import timedelta


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
        self.toggle_sound = True
        self.load_data()
        self.state = State.PLAY
        self.kill_counter = 0
        self.death_counter = 0

        # monitors the length of the run, only when playing (and the death delay)
        self.playing_time = 0
        self.starting_time = 0
        self.finishing_time = 0

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
        self.current_level = 'level1.tmx'
        game_folder = path.dirname(__file__)
        self.img_folder =  path.join(game_folder, 'img')
        music_folder = path.join(game_folder, 'music')
        snd_folder = path.join(game_folder, 'snd')
        self.map_folder = path.join(game_folder, 'maps')
        self.player_img = pg.image.load(path.join(self.img_folder, PLAYER_IMG)).convert_alpha()
        self.mob_img = pg.image.load(path.join(self.img_folder, MOB_IMG)).convert_alpha()
        self.player_idle_imgs = []
        self.player_walk_imgs = []
        self.mob_walk_imgs = []
        self.bloods_imgs = []
        self.gibs_imgs = []
        self.player_gibs_imgs = []
        self.temp_plat_dest_imgs = []
        self.player_idle_imgs = self.make_anim_list(PLAYER_IDLE_IMGS, True)
        self.player_walk_imgs = self.make_anim_list(PLAYER_WALK_IMGS, True)
        self.mob_walk_imgs = self.make_anim_list(MOB_WALK_IMGS, True)
        self.bloods_imgs = self.make_anim_list(BLOOD_IMGS, True)
        self.gibs_imgs = self.make_anim_list(GIB_IMGS, True)
        self.temp_plat_dest_imgs = self.make_anim_list(TEMP_PLAT_DEST_IMGS, True)
        self.player_gibs_imgs = self.make_anim_list(PLAYER_GIB_IMGS, True)
        self.bullet_img = pg.image.load(path.join(self.img_folder, BULLET_IMG)).convert_alpha()
        self.flash_img = pg.image.load(path.join(self.img_folder, FLASH_IMG)).convert_alpha()
        self.temp_plat_img = pg.image.load(path.join(self.img_folder, TEMP_PLATFORM_IMG)).convert_alpha()
        self.title_font = path.join(self.img_folder, 'press_start.ttf')



        # Sound loading
        pg.mixer.music.load(path.join(music_folder, BG_MUSIC))
        self.shoot_snd = pg.mixer.Sound(path.join(snd_folder, SHOOT_SND))
        self.jump_snd = pg.mixer.Sound(path.join(snd_folder, JUMP_SND))
        self.hit_snd = pg.mixer.Sound(path.join(snd_folder, HIT_SND))
        self.lose_snd = pg.mixer.Sound(path.join(snd_folder, LOSE_SND))
        self.die_snd = pg.mixer.Sound(path.join(snd_folder, DIE_SND))
        self.sounds =[self.shoot_snd, self.jump_snd, self.hit_snd, self.lose_snd, self.die_snd]



    def make_anim_list(self, list, resize):
        images_list = []
        for frame in list:
            frame = pg.image.load(path.join(self.img_folder, frame))
            if resize:
                frame = resize_to_multiplier(frame, CHARACTER_SIZE_MULTIPLIER)
            images_list.append(frame.convert_alpha())
        return images_list

    def new(self):
        self.starting_time = pg.time.get_ticks()
        # start a new game
        self.state = State.PLAY
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mob_walls = pg.sprite.Group()
        self.spikes = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.teleports = pg.sprite.Group()

        #creates map image and resize to tile multiplier
        self.map = TiledMap(self, path.join(self.map_folder, self.current_level))
        self.map_img = self.map.make_map()
        self.map_img = resize_to_multiplier(self.map_img, TILE_SIZE_MULTIPLIER)
        self.map.rect = self.map_img.get_rect()

        #creates walls based on tile properties in the wall Layers
        self.map.create_walls()




        #creates objects based on map filename
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height /2) # will need to sort multiplier
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x * TILE_SIZE_MULTIPLIER, tile_object.y * TILE_SIZE_MULTIPLIER,
                         tile_object.width * TILE_SIZE_MULTIPLIER, tile_object.height * TILE_SIZE_MULTIPLIER)
            if tile_object.name == 'mob_wall':
                MobWall(self, tile_object.x * TILE_SIZE_MULTIPLIER, tile_object.y * TILE_SIZE_MULTIPLIER,
                         tile_object.width * TILE_SIZE_MULTIPLIER, tile_object.height * TILE_SIZE_MULTIPLIER)
            if tile_object.name == 'temp_plat':
                TempPlatform(self, tile_object.x * TILE_SIZE_MULTIPLIER, tile_object.y * TILE_SIZE_MULTIPLIER,
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
            if tile_object.name == 'teleport':
                dest = tile_object.properties['destination']
                Teleport(self, tile_object.x * TILE_SIZE_MULTIPLIER, tile_object.y * TILE_SIZE_MULTIPLIER,
                         tile_object.width * TILE_SIZE_MULTIPLIER, tile_object.height * TILE_SIZE_MULTIPLIER, dest)


        self.run()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()


    def player_dies(self):
        self.die_snd.play()
        self.hit_snd.play()
        self.state = State.GAME_OVER
        BloodSplatter(self, self.player.pos)
        gimme_player_gibs(self, self.player.rect.center)
        self.player.kill()
        self.player_death_time = pg.time.get_ticks()
        self.death_counter += 1

    def update(self):


        # Game Loop - Update
        self.all_sprites.update()

        if self.state == State.GAME_OVER:
            if pg.time.get_ticks() - self.player_death_time > PLAYER_DEATH_DURATION:
                self.playing = False
        else:
            #player hits spikes:
            hits = pg.sprite.spritecollide(self.player, self.spikes, False, collide_hit_rect)
            for hit in hits:
                self.player_dies()

            #player hits mobs:
            hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect_mob)
            for hit in hits:
                self.player_dies()

            #mobs hits bullets:
            hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
            for mob in hits:
                for bullet in hits[mob]:
                    self.hit_snd.play()
                    BloodSplatter(self, hits[mob][0].pos)
                    gimme_gibs(self, hits[mob][0].pos, 2)
                    #Gib(self, hits[mob][0].pos)
                    mob.kill()
                    self.kill_counter += 1

            # player hits teleports
            hits = pg.sprite.spritecollide(self.player, self.teleports, False)
            for hit in hits:
                self.current_level = hit.destination
                if self.current_level == 'End of Game':
                    self.state = State.GAME_WON
                else:
                    self.state = State.CHANGE_LEVEL
                self.playing = False

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
            if event.type == pg.KEYUP:
                if event.key == pg.K_y:
                    self.toggle_sound = not self.toggle_sound
                    print(self.toggle_sound)
                    if self.toggle_sound:
                        pg.mixer.music.unpause()
                        for sound in self.sounds:
                            sound.set_volume(1)
                    else:
                        pg.mixer.music.pause()
                        for sound in self.sounds:
                            sound.set_volume(0)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_DOWN:
                    self.player_dies()



    def draw(self):

        # Game Loop - draw
        #self.screen.fill(BLACK)
        self.screen.blit(self.map_img, (0, 0))
        self.all_sprites.draw(self.screen)
        if self.toggle_hitbox:
            pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)
            self.walls.draw(self.screen)
            self.mob_walls.draw(self.screen)
            self.spikes.draw(self.screen)
            for mob in self.mobs:
                pg.draw.rect(self.screen, RED, mob.hit_rect, 2 )
            for bullet in self.bullets:
                pg.draw.rect(self.screen, RED, bullet.rect, 2 )
            self.draw_text('FPS: {:.2f}'.format(self.clock.get_fps()), self.title_font, 20,
                           RED, WIDTH -10, 10, align="ne")
        # *after* drawing everything, flip the display
        pg.display.flip()


    def show_go_screen(self):
        # game over/continue
        #self.screen.fill(BLACK)
        self.draw_text("GAME OVER", self.title_font, 50, RED,
                       WIDTH / 2, HEIGHT * 0.45, align="center")
        self.draw_text("Press any key to start", self.title_font, 25, BLACK,
                       WIDTH / 2, HEIGHT * 0.6, align="center")
        pg.display.flip()
        self.wait_for_key()

    def show_next_level_screen(self):

        self.screen.fill(BLACK)
        self.draw_text("NEXT LEVEL", self.title_font, 50, WHITE,
                       WIDTH / 2, HEIGHT * 0.45 , align="center")
        self.draw_text("Press any key to continue", self.title_font, 25, WHITE,
                       WIDTH / 2, HEIGHT * 0.6, align="center")
        pg.display.flip()
        self.wait_for_key()

    def show_end_screen(self):

        self.screen.fill(BLACK)
        self.draw_text("YOU DID IT !!!!", self.title_font, 50, RED,
                       WIDTH / 2, HEIGHT * 0.25 , align="center")
        self.draw_text('You finished the game', self.title_font, 25, WHITE,
                       WIDTH / 2, HEIGHT * 0.4, align="center")
        final_time = str(timedelta(milliseconds = self.playing_time)).split('.')[0]
        self.draw_text('Your time is:  {} '.format(final_time), self.title_font, 20, WHITE,
                       WIDTH / 2, HEIGHT * 0.5, align="center")
        self.draw_text("You murdered {} harmless bystander(s)".format(self.kill_counter), self.title_font, 20, WHITE,
                       WIDTH / 2, HEIGHT * 0.6 , align="center")
        self.draw_text("You died {} time(s)".format(self.death_counter), self.title_font, 20, WHITE,
                       WIDTH / 2, HEIGHT * 0.7 , align="center")
        self.draw_text("Now rest", self.title_font, 20, WHITE,
                       WIDTH / 2, HEIGHT * 0.85,  align="center")
        pg.display.flip()
        self.current_level = 'level1.tmx'
        self.kill_counter = 0
        self.death_counter = 0
        self.playing_time = 0
        self.wait_for_key()

    def show_start_screen(self):
        pg.mixer.music.play(loops=-1)
        self.screen.fill(BLACK)
        self.draw_text("MACHETE JANE", self.title_font, 60, RED,
                       WIDTH / 2, HEIGHT * 0.25, align="center")
        self.draw_text('In', self.title_font, 20, WHITE,
                       WIDTH / 2, HEIGHT * 0.4, align="center")
        self.draw_text('"Who Stole My Machete ?"', self.title_font, 25, WHITE,
                       WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Press any key to start", self.title_font, 20, WHITE,
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
    GAME_WON = 6

g = Game()
g.show_start_screen()


while g.running:
    g.new()
    g.run()
    g.finishing_time = pg.time.get_ticks()
    g.playing_time += g.finishing_time - g.starting_time
    if g.state == State.CHANGE_LEVEL:
        g.show_next_level_screen()
    elif g.state == State.GAME_OVER:
        g.show_go_screen()
    elif g.state == State.GAME_WON:
        g.show_end_screen()

pg.quit()
