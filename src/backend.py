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
        room.char_map = room.init_map_str.splitlines()
        self.map.map = [[self.obj_from_char(char,room,x,y)
                            for x,char in enumerate(line)] for y,line in enumerate(room.char_map)]
        self.obj_map = room.init_obj_map
    
    def obj_from_char(self,char,room,x,y):
        objs = room.obj_from_char(char,room.char_map,x,y).copy()
        for obj in objs.lst():
            obj.x = x
            obj.y = y
        return objs
    
    def do(self,verb,*arg_objs):
        if verb=='pickup':
            obj = arg_objs[0]
            self.state.carrying[obj] = self.state.free_objs[obj]
            del self.state.free_objs[obj]
        elif verb=='move':
            obj = arg_objs[0]
            target = arg_objs[1]
            if target.can_support:
                self.move_obj(target.x,target.y,obj)
        else:
            rule = self.rules.get_rule(verb,*arg_objs)
            if not rule:
                self.do_default_rule_failure()
            else:
                self.do_rule(rule,arg_objs)
    
    def do_undo(self,undo_event):
        pass
    
    def do_redo(self,redo_event):
        pass

    def do_rule(self,rule,arg_objs):
                new_objs = rule.out_objs
                event = Event()
                event.verb = rule.verb
                event.old_objs = []
                event.new_objs = []
                event.other_prereqs = []
                for i,new_key in enumerate(new_objs):
                    old_obj = arg_objs[i]
                    if new_key == '_pass':
                        old_obj.used_in_events_past.append(event)
                        event.other_prereqs.append(old_obj.copy())
                    elif new_key == '_del':
                        old_obj.used_in_events_past.append(event)
                        self.remove_obj(old_obj)
                        event.old_objs.append(old_obj.copy())
                    else:
                        new_obj = self.defs[new_key].copy()
                        new_obj.created_by_event = [event]
                        old_obj.used_in_events_past.append(event)
                        event.old_objs.append(old_obj.copy())
                        event.new_objs.append(new_obj.copy())
                        self.convert_obj(old_obj,new_obj)
                        # TODO: create extra new objs, eg. shavings
                        # TODO: also work if object is carried
                    #for carried_or_room in self.state.room_list():
                    #    if arg_objs[i] in carried_or_room:
                    #        del carried_or_room[ arg_objs[i] ]
                    #        carried_or_room[new_key] = self.defs[new_key]
                    #        break
                    #else:
                    #    self.state.free_objs[new_key] = self.defs[new_key]
                # TODO: create any entirely new objs
                self.store_new_event(event)
            
    def store_new_event(self,event):
        # currently only stored in links from objects, but may want a list of "initial events" which don't depend on any
        pass
        
    def do_default_rule_failure(self):
        print "I don't know how to do that"
    
    def move_obj(self,x,y,obj):
        self.obj_map.move_to(x,y,obj)
        
    def delete_obj(self,obj):
        # TODO: work with large obj in map, not obj_map
        self.obj_map.remove_obj(obj)
        
    def convert_obj(self,old_obj,new_obj):
        # TODO: work with large obj in map, not obj_map
        self.obj_map.convert_obj(old_obj,new_obj)
    
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
                