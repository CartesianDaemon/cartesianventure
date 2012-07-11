import data
from src.helpers import *
from src.obj import *
from src.map import *
from src.rules import *

class State(Bunch):
    def __init__(self):
        self['free_objs'] = {}
        self['carrying'] = {}
    
    def room_list(self):
        return (self.free_objs,self.carrying)
 
class Backend:
    def __init__(self):
        self.defs = Bunch()
        self.rules = Rules()
        self.state = State()

    def load(self,module):
        room = data.__dict__[module];
        self.defs.update(room.defs)
        self.rules.update(room.rules)
        self.state.free_objs.update(room.initial_objs)
        self.map = Map()
        char_map = room.init_map_str.splitlines()
        self.map.map = [[room.obj_from_char(char,char_map,x,y)
                            for x,char in enumerate(line)] for y,line in enumerate(char_map)]
        self.obj_map = room.init_obj_map

    def do(self,verb,*arg_objs):
        if (verb=='pickup'):
            obj = arg_objs[0]
            self.state.carrying[obj] = self.state.free_objs[obj]
            del self.state.free_objs[obj]
        else:
            rule = self.rules.get_rule(verb,*arg_objs)
            new_objs = rule[0]
            for i,new_key in enumerate(new_objs):
                for carried_or_room in self.state.room_list():
                    if arg_objs[i] in carried_or_room:
                        del carried_or_room[ arg_objs[i] ]
                        carried_or_room[new_key] = self.defs[new_key]
                        break
                else:
                    self.state.free_objs[new_key] = self.defs[new_key]
    
    def get_map(self):
        return self.map.map
        
    def get_contexts(self):
        return self.map.get_contexts()

    def get_obj_map(self):
        return self.obj_map
        
    def get_visible_objs(self):
        return self.state.free_objs
    
    def obj_in_room(self,key):
        return key in self.state.free_objs
    
    def obj_carried(self,key):
        return key in self.state.carrying
                