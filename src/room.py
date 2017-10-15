# Internal modules
from src.helpers import *
from src.obj import Obj
from src.rules import Rules, Rule
from map import Map, Layers

# Standard modules
import copy

class Room:
    def __init__(self):
        self._rules = Rules()
        self.map = Map()
        self.defs = Bunch()
        self.player = None
    
    def get_rules(self):
        return self._rules

    def copy(self):
        return copy.deepcopy(self)
