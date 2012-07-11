import copy
import random
import pygame
from pygame.locals import *
from helpers import *

class GraphicSource:
    def __init__(self,filename,x=None,y=None,w=None,h=None,reps=1,colorkey=None,transparent=False):
        self.filename = filename
        self.surfaces = ()
        self.first_subrect = NotNone(x) and Rect(x,y,w,h)
        self.reps = reps
        self.colorkey = colorkey
        self.transparent = transparent

    def load(self,tile_w,tile_h):
        self.surfaces = []
        if not self.filename:
            surface = pygame.surface()
            self.surfaces.append(surface)
        file_surface = pygame.image.load(self.filename)
        # w,h for tile image including possible overlay over tile to North
        w = tile_w
        h = tile_h * self.first_subrect.h / self.first_subrect.w
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
        self.cur_w,self.cur_h = self.surfaces[0].get_size()
        if self.transparent:
            self.transparent_surfaces = []
            for orig_surface in self.surfaces:
                surface = orig_surface.copy()
                surface.set_alpha(256, RLEACCEL)
                self.transparent_surfaces.append(surface)
        
    def get_surface(self,xidx,yidx,w,h,context=''):
        if not self.surfaces or self.cur_w != w or self.cur_h != h:
            self.load(w,h)
        is_transparent = (self.transparent==True) or (self.transparent=='atbottomofscreen' and yidx==7)
        surfaces = self.surfaces if not is_transparent else self.transparent_surfaces
        if self.reps>1:
            return self.get_random_surface(surfaces,xidx,yidx)
        else:
            return surfaces[0]
            
    def get_random_surface(self,surfaces,xidx,yidx):
        random.seed(xidx+yidx)
        idx = random.randrange(self.reps)
        return surfaces[idx]

class ContextualGraphicSource:
    def __init__(self,**kwargs):
        self.tiles = kwargs
    
    def load(self,*args):
        for gs in self.tiles: gs.load(*args)
        
    def get_surface(self,xidx,yidx,w,h,context):
        if context in self.tiles:
            return self.tiles[context].get_surface(xidx,yidx,w,h)
        else:
            return self.tiles['x']

