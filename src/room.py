# Internal modules
from src.helpers import *
from src.obj import Obj, make_objs
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
        
    def create_obj_at(self,*args,**kwargs):
        self.init_obj_map.create_at(*args,**kwargs)
        
    def make_map_from_key(self,*args,**kwargs):
        self.map.make_map_from_key(*args,**kwargs)
        
    def make_objs(self,*args, **kwargs):
        self.defs.update( make_objs(*args,**kwargs) )

