# Internal modules
from src.helpers import *
from src.map import Map, MapSquare
from src.rules import Rules, Rule, Event, Endgame
import src.room_data as room_data   
import random

# Needs some clarification?
class State:
    def __init__(self,contexts={},offsets={},cleanup_funcs=[],
            idle=False,chainable=False,endgame=False,
            is_done = (lambda frac:frac>=1)):
        self.contexts = contexts
        self.offsets = offsets
        self.cleanup_funcs = cleanup_funcs
        self.idle = idle
        self.chainable = chainable
        self.endgame = endgame
        self.is_done = is_done

class IdleState(State):
    def __init__(self):
       self.idle = True

class MessageState(State):
    def __init__(self,backend):
        State.__init__(self)
        self.idle = True
        self.cleanup_funcs = [ lambda : backend.clear_message() ]
        self.is_done = lambda frac:False

class EndState(MessageState):
    def __init__(self,backend):
        MessageState.__init__(self,backend)
        self.endgame = True

class Backend:
    def __init__(self):
        self.rules = Rules()
        self.curr_state = State(idle=True)
        self.pending_subactions = {}
        self.last_player_move = ('','')
        self.frac = 0
        self.next_act_lambda = None
        self.message = None

    def load(self,filename):
        # TODO: need copy?
        self.curr_room = room_data.load_room(filename).copy()
        self.rules.update(self.curr_room.get_rules())
        self.player = self.curr_room.player
    
    def do(self,verb,*arg_objs):
        # print (verb,)+tuple(obj.name for obj in arg_objs)
        if verb=='move':
            assert len(arg_objs)==2
            obj = arg_objs[0]
            target = arg_objs[1]
            if target.can_support:
                self.move_obj(target.x,target.y,obj)
            else:
                self.display_msg("I can't put it there")
        if verb=='push':
            assert len(arg_objs)==1
            offset = arg_objs[0].map_pos() - self.player.map_pos()
            dir = dir_from_offset( offset )
            if isinstance(dir,Error):
                self.display_msg("I need to be next to it to push it")
            else:
                dir = dir.unwrap()
                assert arg_objs[0].pushable
                objs = self._pushable_objects(dir)
                if objs:
                    for obj in reversed(objs):
                        new_pos = obj.map_pos()+offset
                        self.move_obj(new_pos.x,new_pos.y,obj)
                    self.curr_state = State(
                        contexts = {self.player.map_rect():dir},
                        offsets = {obj.map_rect():dir for obj in objs+[self.player,]},
                        cleanup_funcs = [lambda:self._finish_move(dir)],
                        chainable=True)
                    self.next_act_lambda = lambda: self._begin_facing(dir) # What does this do?
                else:
                    self.display_msg("I can't push it")
        elif verb=='examine':
            assert len(arg_objs)==1
            msg = arg_objs[0].get_examine_text()
            self.display_msg( msg if msg else "I don't see anything special")
        else:
            rule = self.rules.get_rule(verb,*arg_objs)
            if not rule:
                self.do_default_rule_failure()
            else:
                # print(self.curr_room.map)
                self._do_rule(rule,arg_objs)
                # print(self.curr_room.map)
    
    def _pushable_objects(self,dir):
        pos = self.player.map_pos()
        objs = []
        while True:
            pos += offset_from_dir(dir)
            obj = self.get_obj_at(pos)
            if obj.walkable:
                return objs
            elif obj.pushable:
                objs += [obj]
            else:
                return []

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
        for action in rule.out_actions:
            # TODO: replace old rules with implementation of actions
            if isinstance(action, Endgame):
                self.end_game(action.text)
        self.store_new_event(event)
        if rule.get_msg():
            self.display_msg( rule.get_msg() )
    
    def clear_message(self):
        self.message = None

    def display_msg(self,msg):
        self.message = msg
        self.curr_state = MessageState(self)
    
    def store_new_event(self,event):
        # currently only stored in links from objects, but may want a list of "initial events" which don't depend on any
        pass
        
    def do_default_rule_failure(self):
        self.display_msg("I don't know how to do that")
    
    def move_obj(self,x,y,obj):
        self.curr_room.map.move_to(x,y,obj)
        
    def delete_obj(self,obj):
        self.curr_room.map.remove_obj(obj)
        
    def convert_obj(self,old_obj,new_obj):
        self.curr_room.map.convert_obj(old_obj,new_obj)

    def end_game(self, msg):
        self.message = msg
        self.curr_state = EndState(self)

    def get_obj_at(self,pos):
        return self.curr_room.map.get_mapsquare_at(pos).get_combined_mainobj()

    def advance_state(self):
        if self.curr_state.endgame:
            return
        for cleanup_func in self.curr_state.cleanup_funcs:
            cleanup_func()
        self.curr_state = State(idle=True)
        if self.next_act_lambda:
            self.next_act_lambda()
            self.next_act_lambda = None
        else:
            self._idle_fidget()
       
    def state_is_idle(self):
       return self.curr_state.idle
       
    def state_is_chainable(self):
        return self.curr_state.chainable
        
    def start_move(self,dir):
        assert dir in 'lrud'
        if self.state_is_chainable():
            self.next_act_lambda = lambda: self.start_move(dir)
        else:
            if self.get_obj_at(self.player.map_pos() + offset_from_dir(dir)).walkable:
                self.curr_state = State(
                    contexts = {self.player.map_rect():dir},
                    offsets = {self.player.map_rect():dir},
                    cleanup_funcs = [lambda:self._finish_move(dir)],
                    chainable=True)
                self.next_act_lambda = lambda: self._begin_facing(dir) # What does this do?
            else:
                self._begin_facing(dir)
    
    def finished_state(self,frac):
        return self.curr_state.is_done(frac)
    
    def _idle_fidget(self):
        # Only do at random intervals
        random.seed()
        fidget = random.choice(('x','x','x','x','x','x1','x2'))
        self.curr_state = State( contexts={self.player.map_rect():fidget},idle=True)
    
    def _finish_move(self,dir):
        self.player.x, self.player.y = self.player.map_pos() + offset_from_dir(dir)
        # TODO: Use map.move_char()
        
    def _begin_facing(self,dir):
        self.curr_state = State(
            contexts={self.player.map_rect():"f"+dir},
            idle=True,
            is_done = lambda frac:frac>=3 )
    
    def get_blit_surfaces(self, frac, tile_size, window=Rect(0,0,15,7)):
        blit_surfaces = []
        for stratum in self.curr_room.map.get_strata_by_rows():
            for row in stratum:
                for obj_tuple in row:
                    for obj in obj_tuple:
                        contexts = self.curr_state.contexts.iteritems()  
                        offsets = self.curr_state.offsets.iteritems()  
                        curr_contexts =tuple( context for rect,context in contexts if obj.is_in(rect) )
                        curr_offsets =tuple( offset for rect,offset in offsets if obj.is_in(rect) )
                        blit_surface = obj.get_surface( tile_size,curr_contexts,curr_offsets,frac )
                        blit_surface.add_external_offset( obj.map_pos()*tile_size )
                        blit_surfaces.append(blit_surface)
        return blit_surfaces
        
    def get_map_size(self):
        return self.curr_room.map.map_size()
