# Standard modules
import copy
import random
import pygame
from pygame.locals import *

# Internal modules
from helpers import *

class GraphicSource:
    def __init__(self,filename,x=None,y=None,w=None,h=None,reps=1,colorkey=None):
        self.filename = filename
        self.surfaces = ()
        self.first_subrect = NotNone(x) and Rect(x,y,w,h)
        self.reps = reps
        self.colorkey = colorkey

    def load(self,size):
        self.surfaces = []
        if not self.filename:
            surface = pygame.surface()
            self.surfaces.append(surface)
        file_surface = pygame.image.load(self.filename)
        # w,h for tile image including possible overlay over tile to North
        w = size.x
        h = size.y * self.first_subrect.h / self.first_subrect.w
        # stride = self.first_subrect.x + self.first_subrect.w
        stride = 2 * self.first_subrect.w
        for rep in range(self.reps):
            surface = file_surface
            if self.first_subrect is not None:
                surface = surface.subsurface(self.first_subrect.move(stride*rep,0))
            surface = pygame.transform.scale(surface,(w,h))
            if self.colorkey is not None:
                colorkey = self.colorkey
                if colorkey == 'topleft':
                    colorkey = surface.get_at( (0,0) )
                elif colorkey == 'topright':
                    colorkey = surface.get_at( (w-1,0) )
                surface.set_colorkey(colorkey, RLEACCEL)
            surface = surface.convert()
            self.surfaces.append(surface)
        self.cur_size = self.surfaces[0].get_size()
        self.transparent_surfaces = None
        
    def _get_transparent_surfaces():
        if self._transparent_surfaces is None:
            self._transparent_surfaces = [ orig_surface.copy() for orig_surface in self.surfaces]
            for surface in self._transparent_surfaces: surface.set_alpha(256,RLEACCEL)
        return self._transparent_surfaces

    def get_surface(self,pos,size,context='',is_transparent=False):
        if not self.surfaces or self.cur_size != size:
            self.load(size)
        surfaces = self.surfaces if not is_transparent else self._get_transparent_surfaces()
        return surfaces[self._get_surface_idx(pos)]

    def _get_surface_idx(self,pos):
        if self.reps<=1:
            return 0
        else:
            random.seed(pos[0]+pos[1])
            return random.randrange(self.reps)

class ContextualGraphicSource:
    def __init__(self,**kwargs):
        self.tiles = kwargs
    
    def load(self,*args):
        for gs in self.tiles: gs.load(*args)
        
    def get_surface(self,pos,size,context,is_transparent):
        tile = self.tiles.get(context,self.tiles['x'])
        return tile.get_surface(pos,size,is_transparent)

