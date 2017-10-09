# Standard modules
import copy
import pygame
from pygame.locals import *

# Internal modules
from helpers import *

# TODO: Add helpful classes for files with freeform structure and with individual pics
class TileFile:
    def __init__(filename,w,h,xoff=0,yoff=0):
        self.file_surface = pygame.image.load(self.filename)
        self.w, self.h = w, h

    def tile_surface_at(x,y,hpad=0,vpad=0,lpad=0,rpad=0,tpad=0,bpad=0):
        surface = self.file_surface.subsurface( x, y, self.w+hpad*2+lpad+rpad, self.h+vpad*2+tpad+bpad )
        surface.offset = (lpad+hpad,tpad+vpad)
        return surface

class BlitSurface(pygame.Surface):
    def __init__(self,surface):
        self.surface = surface
        self.internal_offset = Pos(0,0)
        self.external_offset = Pos(0,0)
        
    def set_internal_offset(self,pos):
        self.internal_offset = Pos(pos)

    def add_external_offset(self,offset):
        self.external_offset = self.external_offset + Pos(offset)

    def blit_to(self,target,pos):
        target.blit(self.surface,pos-self.internal_offset+self.external_offset)
        
    def get_rect(self):
        return self.surface.get_rect()
        
class BaseGraphic:
    def __init__(self,filename,x=None,y=None,w=None,h=None,str='1x',reps=1,colorkey=None,slide=None,frames=None):
        self.filename = filename
        self.surfaces = ()
        self.first_subrect = NotNone(x) and Rect(x,y,w,h)
        self.orig_rect = self.first_subrect
        self.reps = reps
        self.colorkey = colorkey
        self.cur_dst_size = None
        self.stride = str

    def load(self,size):
        self.surfaces = []
        if not self.filename:
            surface = pygame.surface()
            self.surfaces.append(surface)
        file_surface = pygame.image.load(self.filename)
        if not self.orig_rect:
            self.orig_rect = file_surface.get_rect()
        # w,h for tile image including possible overlay over tile to North
        w = size.x
        h = size.y * self.orig_rect.h / self.orig_rect.w
        if isinstance(self.stride,str) and self.stride[-1]=='x':
            stride = Pos(int(self.stride[:-1]) * self.orig_rect.w,0)
        if isinstance(self.stride,str) and self.stride[-1]=='y':
            stride = Pos(0,int(self.stride[:-1]) * self.orig_rect.h)
        elif isinstance(self.stride,Number):
            stride = Pos(self.stride,0)
        else:
            stride = stride
            assert isinstance(stride[1],Number)
        for rep in range(self.reps):
            surface = file_surface
            if self.first_subrect is not None:
                surface = surface.subsurface(self.first_subrect.move(stride*rep))
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
        self.cur_dst_size = size
        self.transparent_surfaces = None
        
    def get_transparent_surfaces(self):
        if self.transparent_surfaces is None:
            self.transparent_surfaces = [ orig_surface.copy() for orig_surface in self.surfaces]
            for surface in self.transparent_surfaces: surface.set_alpha(256,RLEACCEL)
        return self.transparent_surfaces

    def get_surface(self,pos,size,is_transparent=False, *args, **kwargs):
        idx = kwargs.get('idx',0)
        if not self.surfaces or self.cur_dst_size != size:
            self.load(size)
        surface = BlitSurface( self.surfaces[idx] if not is_transparent else self.get_transparent_surfaces()[idx] )
        surface.set_internal_offset( surface.get_rect().size - Pos(size) )
        return surface
    
    def nframes(self):
        return len(self.surfaces)

class RandGraphic(BaseGraphic):
    def __init__(self,*args,**kwargs):
        BaseGraphic.__init__(self,*args,**kwargs)
        
    def get_surface(self,pos, *args,**kwargs):
        return BaseGraphic.get_surface(self,pos,*args,idx=hash_to_range(pos,self.reps),**kwargs)

class AnimGraphic(BaseGraphic):
    def __init__(self,*args,**kwargs):
        self.slide = kwargs.get('slide')
        self.frames = kwargs.get('frames')
        if self.frames and 'reps' not in kwargs:
            kwargs['reps'] = 1+max(self.frames)
        if not self.frames:
            self.frames = tuple(range( kwargs.get('reps',1) ))
        BaseGraphic.__init__(self,*args,**kwargs)

    def get_surface(self,pos,size, *args,**kwargs):
        idx = self.frames[int(kwargs['frac']*len(self.frames))]
        surface = BaseGraphic.get_surface(self,pos,size,*args,idx=idx,**kwargs)
        if self.slide:
            assert self.slide=='linear'
            assert kwargs['context'] in 'udlr'
            max_offset = size * offset_from_dir(kwargs['context'])
            rel_offset = (int(max_offset.x*kwargs['frac']),int(max_offset.y*kwargs['frac']))
            surface.add_external_offset( rel_offset )
        return surface
        
class CtxtGraphic:
    def __init__(self,**kwargs):
        self.tiles = kwargs
    
    def load(self,*args):
        for gs in self.tiles: gs.load(*args)
        
    def get_surface(self,pos,size,context_tuple,*args,**kwargs):
        # tile = self.tiles.get(context,self.tiles['x'])
        ctxt, tile = first( (context, self.tiles.get(context)) for context in context_tuple ) or ('x',self.tiles['x']) # Crashes if no match and no default
        kwargs['context'] = ctxt
        return tile.get_surface(pos,size,*args,**kwargs)

