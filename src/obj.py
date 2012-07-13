from graphic_source import *
from helpers import *

class Defs(Bunch):
    pass

class Obj(Bunch):
    def __init__(self,name,description="",graphic_source=None):
        self.update(name=name,description=description,graphic_source=graphic_source)
        self.hoverable = True
        self.can_support = False
        self.background = True
        self.created_by_event = []
        self.used_in_events_past = []
        self.used_in_events_future = []
        self.destroyed_by_event = []
        
    def __hash__(self):
        return hash(self.key)
        
    def __eq__(self, other):
        return self is other or self.key == other
        
    def get_surface(self,*args):
        return self.graphic_source.get_surface(*args)
        
    def is_hoverable(self):
        return self.hoverable;
        
    def copy(self):
        return copy.copy(self)
    
    def is_background(self):
        # TODO: if we have a link to the data structure we're in, return True if in map, False if in obj_map
        return self.background
    
    def get_undoable_events(self):
        if self.is_background():
            return self.created_by_event
        else:
            return self.created_by_event + self.used_in_events_past
        
def make_objs(**kwargs):
    # return { k:Obj(k,*args) for k,args in kwargs.iteritems()}
    d = {}
    for k, obj in kwargs.iteritems():
        obj.key = k
        d[k] = obj
    return Bunch(d)
