# Internal modules
from src.helpers import *
from src.obj import Obj
from src.rules import Rules, Rule
from map import Map, ObjMap, Layers

prop_defaults = Bunch(
    pickable =   Bunch(moveable=True , pickable=True , hoverable=True , can_support=False, passable=True  ),
    moveable =   Bunch(moveable=True , pickable=False, hoverable=True , can_support=False, passable=False ),
    stackable =  Bunch(moveable=True , pickable=False, hoverable=True , can_support=False, passable=False ),
    fixed =      Bunch(moveable=False, pickable=False, hoverable=True , can_support=False, passable=False ),
    floor =      Bunch(moveable=False, pickable=False, hoverable=False, can_support=True , passable=False ),
    wall =       Bunch(moveable=False, pickable=False, hoverable=False, can_support=False, passable=False ),
)

class Room:
    def __init__(self):
        self.rules = Rules()
        self.map = Map()
        self.defs = Bunch()

    def add_rule(self,*args,**kwargs):
        self.rules.add_rule(*args,**kwargs)
        
    def create_obj_at(self,x,y,obj):
        self.obj_map.create_at(x,y,obj)
        
    def make_map_from_key(self,init_map_str,charkey_func):
        self.map.make_map_from_key(init_map_str,charkey_func)
        self.obj_map = ObjMap( init_map_str.splitlines() )
        
    def make_objs(self,default_props={}, **kwargs):
        self.defs.update( { key: obj.update(key=key,**default_props) for key, obj in kwargs.iteritems() } )

