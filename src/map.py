from src.helpers import *
from src.obj import *

class Layers:
    def __init__(self,*args):
        self._lst = args
        self._obj = args[-1] if len(args)>=1 else None
        
    def lst(self):
        return self._lst
        
    def obj(self):
        return self._obj
        
    def add_overlays(*args):
        _lst.extend(args)
        
    def copy(self):
        cpy = Layers()
        cpy._lst = tuple(obj.copy() for obj in self._lst)
        cpy._obj = cpy._lst[self._lst.index(self._obj)]
        return cpy

class Map:
    def __init__(self):
        self.contexts = None
        
    def get_contexts(self):
        if self.contexts is None:
            map = self.map
            self.contexts = [ [
                                 ''.join( [ char for char,dx,dy in ( ('t',0,-1), ('b',0,+1), ('l',-1,0), ('r',+1,0) )
                                 if x+dx>=0 and x+dx<len(map[0]) and y+dy>=0 and y+dy<len(map) and
                                    layers.obj()==map[y+dy][x+dx].obj()
                                ] )
                              for x,layers in enumerate(line) ] for y,line in enumerate(map) ]
        return self.contexts

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
        # assert self.obj_map[y][x] == obj
        self.obj_map[obj.y][obj.x] = None 
        obj.x, obj.y = x, y
        self.obj_map[y][x] = obj
        # TODO: Make list, not just single obj
    
    def get_obj_at(self,x,y):
        return self.obj_map[y][x]
    
    def get_lst_at(self,x,y):
        if self.obj_map[y][x]:
            return (self.obj_map[y][x],)
        else:
            return ()
    
                       