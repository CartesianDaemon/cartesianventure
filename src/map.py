from src.helpers import *
from src.obj import *

class Layers:
    def __init__(self,*args):
        self._lst = args
        self._obj = args[-1]
        
    def lst(self):
        return self._lst
        
    def obj(self):
        return self._obj
        
    def add_overlays(*args):
        _lst.extend(args)

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
        
    def set_at(self,x,y,obj):
        obj.x = x
        obj.y = y
        self.obj_map[y][x] = obj
    
    def get_obj_at(self,x,y):
        return self.obj_map[y][x]
    
    def get_lst_at(self,x,y):
        if self.obj_map[y][x]:
            return (self.obj_map[y][x],)
        else:
            return ()
    
                       