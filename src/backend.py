# Internal modules
from src.helpers import *
from src.map import Map, MapSquare
from src.rules import Rules, Rule, Event
import src.room_data as room_data   

class Backend:
    def __init__(self):
        self.rules = Rules()
        self.curr_tock = {}
        self.default_idle_tock = {}
        self.pending_subactions = {}

    def load(self,filename):
        # TODO: need copy?
        self.curr_room = room_data.load_room(filename)
        self.rules.update(self.curr_room.get_rules())
    
    def do(self,verb,*arg_objs):
        print (verb,)+tuple(obj.name for obj in arg_objs)
        if verb=='move':
            assert len(arg_objs)==2
            obj = arg_objs[0]
            target = arg_objs[1]
            if target.can_support:
                self.move_obj(target.x,target.y,obj)
            else:
                self.print_msg("I can't put it there")
        elif verb=='examine':
            assert len(arg_objs)==1
            msg = arg_objs[0].get_examine_text()
            self.print_msg( msg if msg else "I don't see anything special")
        else:
            rule = self.rules.get_rule(verb,*arg_objs)
            if not rule:
                self.do_default_rule_failure()
            else:
                self._do_rule(rule,arg_objs)
    
    def do_undo(self,undo_event):
        print "UNDO"
    
    def do_redo(self,redo_event):
        print "REDO"

    def _do_rule(self,rule,arg_objs):
        new_obj_packs = rule.out_obj_packs
        event = Event()
        event.verb = rule.verb
        event.old_objs = []
        event.new_objs = []
        event.other_prereqs = []
        event.sentence = arg_objs[0].get_verb_sentence_ncase(rule.verb,*arg_objs[1:])
        for i,new_pack in enumerate(new_obj_packs):
            assert i < len(arg_objs) # TODO: Create completely new objects, eg. wood shavings
            old_obj = arg_objs[i]
            if new_pack == '_pass':
                old_obj.used_in_events_past.append(event)
                event.other_prereqs.append(old_obj.copy())
            elif new_pack == '_del':
                old_obj.used_in_events_past.append(event)
                self.remove_obj(old_obj)
                event.old_objs.append(old_obj.copy())
            else:
                new_obj = self.curr_room.defs[new_pack.key].copy()
                new_obj.set_state(new_pack.state)
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
        print ">>> " + msg
    
    def store_new_event(self,event):
        # currently only stored in links from objects, but may want a list of "initial events" which don't depend on any
        pass
        
    def do_default_rule_failure(self):
        self.print_msg("I don't know how to do that")
    
    def move_obj(self,x,y,obj):
        self.curr_room.map.move_to(x,y,obj)
        
    def delete_obj(self,obj):
        self.curr_room.map.remove_obj(obj)
        
    def convert_obj(self,old_obj,new_obj):
        self.curr_room.map.convert_obj(old_obj,new_obj)
    
    def get_obj_at(self,x,y):
        return self.curr_room.map.get_mapsquare_at(x,y).get_combined_mainobj()

    def pop_tock(self):
        ret = self.curr_tock
        if self.pending_subactions:
            raise NotImplementedError # TODO: pass next action to "do"
        else:
            self.curr_tock = self.default_idle_tock
        return ret

    def get_blit_surfaces(self, tock, tile_size, window=Rect(0,0,15,7)):
        blit_surfaces = []
        for stratum in self.curr_room.map.get_strata_by_rows():
            for row in stratum:
                for obj_tuple in row:
                    for obj in obj_tuple:
                        blit_surface = obj.get_surface( tile_size )
                        blit_surface.set_external_offset( obj.map_pos()*tile_size )
                        blit_surfaces.append(blit_surface)
        return blit_surfaces
        
    def get_map_size(self):
        return self.curr_room.map.map_size()
