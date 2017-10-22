# Standard modules
from collections import OrderedDict
from itertools import chain

# Internal modules
from src.obj import Obj2
from src.helpers import *

class MapSquare:
    def __init__(self,floor_layers,obj_layers,char_layers,wall_layers):
        self.strata = OrderedDict()
        self.strata['floor'] = floor_layers
        self.strata['obj'  ] = obj_layers
        self.strata['char' ] = char_layers
        self.strata['wall' ] = wall_layers
    
    # TODO: Refactor this into a general "add object at" functionality
    def get_obj_layers(self):
        return self.strata['obj']
    
    def get_char_layers(self):
        return self.strata['char']

    def get_stratum_layers(self,stratum):
        return self.strata[stratum]

    def add_obj(self,new_obj,stratum):
        self.strata[stratum].add_obj(new_obj)

    def get_combined_mainobj(self):
        # TODO: Do something different if top object isn't always "main" one, eg. overlay of smoke, water, etc
        # TODO: Deal with empty square without crashing?
        #return ( tuple(chain.from_iterable( stratum.get_obj_lst() for stratum in reversed(self.strata.values()) )) + (None,) )[0]
        return ( stratum.get_obj() for stratum in reversed(self.strata.values()) if stratum.get_obj() ).next()

    def get_combined_lst(self):
        return chain.from_iterable( stratum.get_lst() for stratum in self.strata.values() )

class Layers:
    def __init__(self,*init_objs):
        self.lst = list(init_objs)
        self.obj = self.lst[-1] if len(self.lst)>=1 else None
        
    def get_lst(self):
        return self.lst
        
    def get_obj(self):
        return self.obj
        
    def get_obj_lst(self):
        return self.obj or ()

    def add_obj(self, new_obj):
        self.set_obj(new_obj)
        
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
        self.map_squares = []

    def width(self):
        return len(max(self.map_squares, key=len)) if len(self.map_squares)>0 else 0
    
    def height(self):
        return len(self.map_squares) 

    def _expand_to_include(self, x, y):
        self._expand_to_equal(x+1,y+1)

    def _expand_to_equal(self, w, h):
        self.map_squares += [[]] * (h-len(self.map_squares))
        self.map_squares[h-1] += [MapSquare(Layers(),Layers(),Layers(),Layers())] * (w-len(self.map_squares[h-1]))
 
    def add_obj_at(self,x,y,spec,stratum=None):
        assert x>=0 and y>=0
        stratum = stratum or spec.properties['stratum']
        self._expand_to_include(x,y)
        self.map_squares[y][x].add_obj(Obj2(spec),stratum)

    def make_map_from_tuples(self,init_map_tuples):
        self.map_squares = [ [ MapSquare( Layers(tup[0]), Layers(), Layers(), Layers(*tup[1:2]) ) for tup in row ] for row in init_map_tuples]
        for x,y,map_square in enumerate_2d(self.map_squares):
            for obj in map_square.get_combined_lst():
                obj.x, obj.y = x, y
        self.generate_contexts()

    def generate_contexts(self):
        for x,y,map_square in enumerate_2d(self.map_squares):
            adj_coords = ( ('t',0,-1),
                           ('b',0,+1),
                           ('l',-1,0),
                           ('r',+1,0), )
            abs_coords = tuple( (char,x+dx,y+dy) for char,dx,dy in adj_coords if self.is_in_map((x+dx,y+dy)) ) 
            for obj in map_square.get_combined_lst():
                valid_chars = ( char for char,x_,y_ in abs_coords
                                     if obj.draw_contiguously_with( self.map_squares[y_][x_].get_combined_lst() ) )
                obj.context = ''.join( valid_chars )

    def is_in_map(self,pos):
        return 0 <= pos[0] < self.map_size()[0] and 0 <= pos[1] < self.map_size()[1]
        
    def map_size(self):
        return (self.width(),self.height())
        
    def create_obj_at(self,x,y,obj):
        obj.x, obj.y = x, y
        self.map_squares[y][x].get_obj_layers().set_obj(obj)
        
    def create_char_at(self,x,y,obj):
        obj.x, obj.y = x, y
        self.map_squares[y][x].get_char_layers().set_obj(obj)
        
    def remove_obj(self,obj):
        assert self.map_squares[obj.y][obj.x].get_obj_layers().lst == [obj]
        self.map_squares[obj.y][obj.x].get_obj_layers().remove_all()
        obj.x = None
        
    def convert_obj(self,old_obj,new_obj):
        assert self.map_squares[old_obj.y][old_obj.x].get_obj_layers().lst == [old_obj]
        self.map_squares[old_obj.y][old_obj.x].get_obj_layers().remove_all()
        self.map_squares[old_obj.y][old_obj.x].get_obj_layers().set_obj(new_obj)
        new_obj.x, new_obj.y = old_obj.x, old_obj.y
        old_obj.x = None
        
    def move_to(self,new_x,new_y,obj):
        assert self.map_squares[obj.y][obj.x].get_obj_layers().lst == [obj]
        self.map_squares[obj.y][obj.x].get_obj_layers().remove_all()
        self.map_squares[new_y][new_x].get_obj_layers().set_obj(obj)
        obj.x, obj.y = new_x, new_y

    def get_mapsquare_at(self,pos):
        assert self.is_in_map(pos)
        return self.map_squares[pos[1]][pos[0]]

    def get_strata_by_rows(self):
        H = len(self.map_squares[0][0].strata)
        return [ [ [ sq.strata.values()[i].get_lst() for sq in row ] for row in self.map_squares ] for i in range(H) ]
