import data
from src.helpers import *
from src.obj import *
from src.map import *
from src.rules import *

class Backend:
    def __init__(self):
        self.defs = Bunch()
        self.rules = Rules()

    def load(self,module):
        room = data.__dict__[module];
        self.defs.update(room.defs)
        self.rules.update(room.rules)
        self.map = Map()
        room.char_map = room.init_map_str.splitlines()
        self.map.map = [[self.base_layers_from_char(char,room,x,y)
                            for x,char in enumerate(line)] for y,line in enumerate(room.char_map)]
        self.obj_map = room.init_obj_map
    
    def base_layers_from_char(self,char,room,x,y):
        objs = room.base_layers_from_char(char,room.char_map,x,y).copy()
        for obj in objs.get_lst():
            obj.x = x
            obj.y = y
        return objs
    
    def do(self,verb,*arg_objs):
        print (verb,)+tuple(obj.name for obj in arg_objs)
        if verb=='move':
            obj = arg_objs[0]
            target = arg_objs[1]
            if target.can_support:
                self.move_obj(target.x,target.y,obj)
        else:
            rule = self.rules.get_rule(verb,*arg_objs)
            if not rule:
                self.do_default_rule_failure()
            else:
                self._do_rule(rule,arg_objs)
    
    def do_undo(self,undo_event):
        pass
    
    def do_redo(self,redo_event):
        pass

    def _do_rule(self,rule,arg_objs):
        new_objs = rule.out_objs
        event = Event()
        event.verb = rule.verb
        event.old_objs = []
        event.new_objs = []
        event.other_prereqs = []
        for i,new_key in enumerate(new_objs):
            assert i < len(arg_objs) # TODO: Create completely new objects, eg. wood shavings
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
        # TODO: create any entirely new objs
        self.store_new_event(event)
        if rule.get_msg(): self.print_msg(rule.get_msg())
    
    def print_msg(self,msg):
        print msg
    
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
    
    def _get_mapsquare_at(self,x,y):
        return MapSquare(self.map.get_layers_at(x,y), self.obj_map.get_layers_at(x,y), self.map.get_context_at(x,y))
        
    def get_obj_at(self,x,y):
        return self._get_mapsquare_at(x,y).get_combined_mainobj()
    
    def get_mapsquares_by_rows(self):
        return ( (x,y,self._get_mapsquare_at(x,y)) for x,y in self.map.get_coords_by_rows() )
        
    def get_map_size(self):
        return self.map.map_size()
    
    # def get_map(self):
    #     return self.map.map
    #     
    # def get_contexts(self):
    #     return self.map.get_contexts()
    # 
    # def get_obj_map(self):
    #     return self.obj_map
    
    # def obj_in_room(self,key):
    #     return key in self.state.free_objs
    # 
    # def obj_carried(self,key):
    #     return key in self.state.carrying
                