from graphic_source import *
from helpers import *

class Defs(Bunch):
    pass

class DummyObj:
    def __init__(self,name):
        self.name = name
    def get_name_lower(self):
        return self.name
    
class Obj():
    def __init__(self,name,description="",graphic_source=None):
        self.name=name
        self.description=description
        self.graphic_source=graphic_source
        self.hoverable = True
        self.can_support = False
        self.pickable = False
        self.created_by_event = []
        self.used_in_events_past = []
        self.used_in_events_future = []
        self.destroyed_by_event = []
        self.context = ''
        
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
    
    def is_pickable(self):
        # TODO: if we have a link to the data structure we're in, return True if in map, False if in obj_map
        return self.pickable
    
    def get_name_lower(self):
        return self.name
    
    def get_name_cap(self):
        return self.name.capitalize()

    def get_verbs(self,obj1=DummyObj("...")):
        if self is obj1:
            obj1 = DummyObj("itself")
        move_prep = " to " if obj1.name=="..." else " onto " 
        verb_list = { 'move' : "Move "+self.get_name_lower()+move_prep+obj1.get_name_lower() ,
                      'use'  : "Use "+self.get_name_lower()+" with "+obj1.get_name_lower(),
                    }
        return verb_list

    def get_verb_remaining_arities(self,*args):
        verb_arity_list = { 'move': 2,
                            'use' : 2,
                          }
        return ( max(0,arity - 1 - len(args)) for verb, arity in verb_arity_list.iteritems() )
        
    def get_undoable_events(self):
        if self.is_pickable():
            return self.created_by_event + self.used_in_events_past
        else:
            return self.created_by_event

    def get_redoable_events(self):
        if self.is_pickable():
            return self.destroyed_by_event + self.used_in_events_future
        else:
            return self.destroyed_by_event
            
    def draw_contiguously_with(self,other_layers):
        return any( self.key == other_obj.key for other_obj in other_layers.lst)
        
def make_objs(**kwargs):
    # return { k:Obj(k,*args) for k,args in kwargs.iteritems()}
    d = {}
    for k, obj in kwargs.iteritems():
        obj.key = k
        d[k] = obj
    return Bunch(d)
