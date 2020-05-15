import pygame as pg
import pytmx
from settings import *
from sprites import Obstacle

class TiledMap:
    def __init__(self, game, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm
        self.game = game

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth,
                                            y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface

    def create_walls(self):
        tp = self.tmxdata.get_tile_properties_by_gid
        for layer in self.tmxdata.visible_layers:
            if layer.name == 'Walls':
                for x, y, gid, in layer:
                    tile = tp(gid)
                    if tile:
                        Obstacle(self.game, x * self.tmxdata.tilewidth* TILE_SIZE_MULTIPLIER,
                                 y * self.tmxdata.tilewidth * TILE_SIZE_MULTIPLIER,
                                 self.tmxdata.tilewidth* TILE_SIZE_MULTIPLIER,
                                 self.tmxdata.tilewidth* TILE_SIZE_MULTIPLIER)
