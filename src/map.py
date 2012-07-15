# Internal modules
from src.helpers import *
from src.obj import make_copy

class MapSquare:
    def __init__(self,base_layers,obj_layers):
        self.base_layers = base_layers
        self.obj_layers = obj_layers
    
    def get_combined_mainobj(self):
        return self.obj_layers.get_obj() or self.base_layers.get_obj()
    
    def get_combined_lst(self):
        return self.base_layers.get_lst() + self.obj_layers.get_lst()

class Layers:
    def __init__(self,*init_objs):
        # Copy of initial layers is necessary because we assign
        # coords to object, and object may or may not exist elsewhere
        self.lst = [ make_copy(obj) for obj in init_objs]
        self.obj = self.lst[-1] if len(self.lst)>=1 else None
        
    def get_lst(self):
        return self.lst
        
    def get_obj(self):
        return self.obj
        
    def set_obj(self, new_obj):
        assert len(self.lst) == 0
        self.lst.append(new_obj)
        self.obj = self.lst[-1]
        
    def remove_all(self):
        self.lst = []
        self.obj = None
        
    def add_overlays(*args):
        lst.extend(args)
        
class Map:
    def __init__(self):
        self.obj_map = None
    
    def make_map_from_key(self,init_map_str,charkey_func):
        char_map = init_map_str.splitlines()
        self.map_squares = [ [ None for _ in row ] for row in char_map]
        for x,y,char in enumerate_2d(char_map):
            base_layers = Layers(*charkey_func(char,x,y))
            self.map_squares[y][x] = MapSquare( base_layers, Layers() )
            for obj in self.map_squares[y][x].get_combined_lst():
                obj.x = x
                obj.y = y
        self.generate_contexts()

    def generate_contexts(self):
        for x,y,map_square in enumerate_2d(self.map_squares):
            adj_coords = ( ('t',0,-1),
                           ('b',0,+1),
                           ('l',-1,0),
                           ('r',+1,0), )
            abs_coords = tuple( (char,x+dx,y+dy) for char,dx,dy in adj_coords if self.is_in_map(x+dx,y+dy) ) 
            for obj in map_square.get_combined_lst():
                valid_chars = ( char for char,x_,y_ in abs_coords
                                     if obj.draw_contiguously_with( self.map_squares[y_][x_].get_combined_lst() ) )
                obj.context = ''.join( valid_chars )

    def is_in_map(self,x,y):
        return 0 <= x < self.map_size()[0] and 0 <= y < self.map_size()[1]
        
    def map_size(self):
        return (len(self.map_squares[0]),len(self.map_squares))
        
    def create_at(self,x,y,obj):
        obj.x = x
        obj.y = y
        self.map_squares[y][x].obj_layers.set_obj(obj)
        
    def remove_obj(self,obj):
        assert self.map_squares[obj.y][obj.x].obj_layers.lst == [obj]
        self.map_squares[obj.y][obj.x].obj_layers.remove_all()
        obj.x = None
        
    def convert_obj(self,old_obj,new_obj):
        assert self.map_squares[old_obj.y][old_obj.x].obj_layers.lst == [old_obj]
        self.map_squares[old_obj.y][old_obj.x].obj_layers.remove_all()
        self.map_squares[old_obj.y][old_obj.x].obj_layers.set_obj(new_obj)
        new_obj.x, new_obj.y = old_obj.x, old_obj.y
        old_obj.x = None
        
    def move_to(self,new_x,new_y,obj):
        assert self.map_squares[obj.y][obj.x].obj_layers.lst == [obj]
        self.map_squares[obj.y][obj.x].obj_layers.remove_all()
        self.map_squares[new_y][new_x].obj_layers.set_obj(obj)
        obj.x, obj.y = new_x, new_y

    def get_mapsquare_at(self,x,y):
        assert self.is_in_map(x,y)
        return self.map_squares[y][x]

    def get_mapsquares_by_rows(self):
        return self.map_squares

        