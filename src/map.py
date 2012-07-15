# Internal modules
from src.helpers import *

class MapSquare:
    def __init__(self,base_layers,obj_layers,base_context):
        self.base_layers = base_layers
        self.obj_layers = obj_layers
        self.base_layers.get_obj().context = base_context
    
    def get_combined_mainobj(self):
        return self.obj_layers.get_obj() or self.base_layers.get_obj()
    
    def get_combined_lst(self):
        return self.base_layers.get_lst() + self.obj_layers.get_lst()

class Layers:
    def __init__(self,*args):
        self.lst = args
        self.obj = args[-1] if len(args)>=1 else None
        
    def get_lst(self):
        return self.lst
        
    def get_obj(self):
        return self.obj
        
    def add_overlays(*args):
        lst.extend(args)
        
    def copy(self):
        cpy = Layers()
        cpy.lst = tuple(obj.copy() for obj in self.lst)
        cpy.obj = cpy.lst[self.lst.index(self.obj)]
        return cpy

class Map:
    def __init__(self):
        self.contexts = None
    
    def make_map_from_key(self,init_map_str,charkey_func):
        char_map = init_map_str.splitlines()
        self.map = [[self._charkey(char,charkey_func,x,y) for x,char in enumerate(line)] for y,line in enumerate(char_map)]

    def _charkey(self,char,charkey_func,x,y):
        obj_layers = charkey_func(char,x,y).copy()
        for obj in obj_layers.get_lst():
            obj.x = x
            obj.y = y
        return obj_layers

    def get_contexts(self):
        if self.contexts is None:
            self.contexts = [ [ get_context_at(x,y,layers.get_obj()) for x,layers in enumerate(line) ]
                                                                     for y,line in enumerate(self.map) ]
        return self.contexts

    def get_context_at(self,x,y,obj = DefaultArg):
        if obj == DefaultArg: obj = self.map[y][x].get_obj()
        adj_coords = ( ('t',0,-1),
                       ('b',0,+1),
                       ('l',-1,0),
                       ('r',+1,0), )
        adj_layers = ( (char,self.get_layers_at_or_none(x+dx,y+dy)) for char,dx,dy in adj_coords)
        return ''.join( char for char,layers in adj_layers if obj.draw_contiguously_with(layers) ) 

    def get_layers_at(self,x,y):
        assert self.is_in_map(x,y)
        return self.map[y][x]

    def get_layers_at_or_none(self,x,y):
        return self.map[y][x] if self.is_in_map(x,y) else Layers()
    
    def is_in_map(self,x,y):
        return 0 <= x < len(self.map[0]) and 0 <= y < len(self.map)
        
    def map_size(self):
        return (len(self.map[0]),len(self.map))
        
    def get_coords_by_rows(self):
        return ( (x,y) for y,line in enumerate(self.map) for x,_ in enumerate(line)  )
        
class ObjMap:
    def __init__(self,obj_map):
        self.obj_map = obj_map
        
    def create_at(self,x,y,obj):
        obj.x = x
        obj.y = y
        self.obj_map[y][x] = obj
        
    def remove_obj(self,obj):
        self.obj_map[obj.y][obj.x]=None
        obj.x = None
        
    def convert_obj(self,old_obj,new_obj):
        self.obj_map[old_obj.y][old_obj.x] = new_obj
        new_obj.x, new_obj.y = old_obj.x, old_obj.y
        old_obj.x = None
        
    def move_to(self,x,y,obj):
        assert self.obj_map[obj.y][obj.x] == obj
        self.obj_map[obj.y][obj.x] = None 
        obj.x, obj.y = x, y
        self.obj_map[y][x] = obj
        # TODO: Make list, not just single obj
    
    def get_layers_at(self,x,y):
        return Layers(*self.get_lst_at(x,y))
    
    def get_obj_at(self,x,y):
        return self.obj_map[y][x]
    
    def get_lst_at(self,x,y):
        return (self.obj_map[y][x],) if self.obj_map[y][x] else ()
    
                       