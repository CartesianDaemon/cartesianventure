# Internal modules
from src.helpers import *
from src.obj import Obj
from src.rules import Rules, Rule
from map import Map, Layers

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
