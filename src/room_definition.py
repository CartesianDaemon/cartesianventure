from src.room import Room
from src.obj import Obj
from src.graphic_source import GraphicSource, ContextualGraphicSource
from src.helpers import *

prop_defaults = Bunch(
    pickable =   Bunch(moveable=True , pickable=True , hoverable=True , can_support=False, passable=True  ),
    moveable =   Bunch(moveable=True , pickable=False, hoverable=True , can_support=False, passable=False ),
    stackable =  Bunch(moveable=True , pickable=False, hoverable=True , can_support=False, passable=False ),
    fixed =      Bunch(moveable=False, pickable=False, hoverable=True , can_support=False, passable=False ),
    floor =      Bunch(moveable=False, pickable=False, hoverable=False, can_support=True , passable=False ),
    wall =       Bunch(moveable=False, pickable=False, hoverable=False, can_support=False, passable=False ),
    character =  Bunch(moveable=False, pickable=False, hoverable=False, can_support=False, passable=False, character=True ),
)

# All object assignment in RoomDefinition should be copy
# Nowhere else should copy objects at all, except as a product of rules

class RoomDefinition:
    def __init__(self):
        from src.room import Room
        self.room = Room()
        self.defs = self.room.defs
        
    def make_room(self):
        return self.room.copy()
        
    def add_rule(self,*args,**kwargs):
        self.room._rules.add_rule(*args,**kwargs)

    def create_obj_at(self,x,y,obj):
        self.room.map.create_at(x,y,obj.copy())

    def make_map_from_key(self,init_map_str,charkey_func):
        char_map = init_map_str.splitlines()
        tuple_at = lambda char,x,y : ( obj.copy() for obj in charkey_func(char,x,y) )
        init_map_tuples = ( ( tuple_at(char,x,y) for x, char in enumerate(line) ) for y,line in enumerate(char_map) ) 
        self.room.map.make_map_from_tuples(init_map_tuples)

    def add_obj_templates(self,default_props={}, **kwargs):
        self.room.defs.update( { key: obj.update(key=key,**default_props) for key, obj in kwargs.iteritems() } )
    