# Internal modules
from src.helpers import *
from src.obj import Obj, Obj2, ObjSpec2
from src.rules import Rules, Rule
from map import Map, Layers

# Standard modules
import copy

# Defined in data file
# Contents important to backend
# Not used otherwise
# Effectively treated as immutable but datafile may add params to an object just after creating it (?)
class RoomSpec2:
    def __init__(self):
        self.obj_specs = dict()
        self.map = Map()
        self.players = ()
        self.next_anon_obj_idx = 1
    # string id, followed by any number of parent ids to copy properties from, then named properties
    # use empty string as id to create an anonymous object spec with an auto-gen id
    def add_obj_spec(self,id,*args,**kwargs):
        # type: str, List[str], str -> ??? # TODO fix
        parents = args
        if id == "":
            id = "anon" + str(self.next_anon_obj_idx) + "".join( "_" + parent_id for parent_id in parents )
            self.next_anon_obj_idx += 1
        assert id not in self.obj_specs
        obj_spec = ObjSpec2()
        for parent_id in reversed(parents):
            obj_spec.update(self.obj_specs[parent_id])
        obj_spec.update(dict(id=id,ids=(id,)+parents,**kwargs))
        self.obj_specs[id] = obj_spec
        return obj_spec

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
