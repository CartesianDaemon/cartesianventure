# Internal modules
from src.helpers import *
from src.obj import Obj
from src.rules import Rules, Rule
from map import Map, Layers

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
        self._rules = Rules()
        self.map = Map()
        self.defs = Bunch()
        self.copies = 0
    
    def get_rules(self):
        return self._rules

    def copy(self):
        # TODO: do actual copy
        return self
