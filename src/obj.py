# Standard modules
from itertools import izip_longest, chain
import copy

# Internal modules
from helpers import *

def make_copy(other):
    return copy.copy(other)

class Verb:
    def __init__(self,*args):
        self.verb_parts = args
    
    def arity(self):
        return len(self.verb_parts)-1
    
    def get_sentence_ncase(self,*all_objs):
        # Typical example:
        #  verb_parts = ( "blow ", " with ",   ",",          " and ", " up" )
        #  all_objs   = ( "enemy", "dynamite", "long cable", "...",   ""    )
        # becomes "Blow enemy with dynamite, long cable and ... up"
        sentence = ""
        n_objs = len(all_objs)
        assert n_objs <= self.arity()
        for idx, (verb_part, obj) in enumerate(izip_longest(self.verb_parts,all_objs)):
            sentence += verb_part
            if idx==0:
                sentence += obj.get_name_ncase()
            elif obj is all_objs[0]:
                sentence += "itself"
            elif obj is not None:
                sentence += obj.get_name_ncase()
            elif idx < self.arity():
                sentence += "..."
        return sentence

class Pack(Bunch):
    pass
        
class Obj:
    def __init__(self,name,short_desc="",examine_text="",graphic_source=None,transparent=False):
        # Object descriptions
        self.key='' # set later by add_obj_templates
        self.name=name
        self.short_desc=short_desc
        self.examine_text=examine_text
        
        # Object depiction
        self.graphic_source=graphic_source
        self.transparent = transparent
        self.context = ''
        
        # Object state
        self.state = Struct()

        # Object event history
        self.created_by_event = []
        self.used_in_events_past = []
        self.used_in_events_future = []
        self.destroyed_by_event = []
        
        # Object properties, assume need to be updated by make_obj
        self.moveable = None
        self.pickable = None
        self.hoverable = None
        self.can_support = None
        self.walkable = None
        self.character = None
    
    #TODO: delete this
    def copy(self):
        return make_copy(self)
    
    def update(self,**kwargs):
        for prop,val in kwargs.iteritems():
            self.__dict__[prop]=val
        return self

    def pack(self):
        return Pack(key=self.key,state=self.state)
        
    def set_state(self,state): # From pack
        self.state = state
    
    def get_contexts(self):
        return (self.context,) if self.context else ()
        
    def map_pos(self):
        return Pos(self.x,self.y)
    
    def get_surface(self,tile_size,tock,frac=0):
        is_transparent = self.transparent or self.transparent=='atbottomofscreen' and pos[1]==7 and 0 < pos[0] < 14
        tock_tuple = (context for rect,context in tock.iteritems() if Rect(rect)) # .collidepoint(self.map_pos) 
        context_tuple = chain( tock_tuple, self.get_contexts() )
        if self.character:
            print tuple(context_tuple)
        return self.graphic_source.get_surface( (self.x,self.y), tile_size, context_tuple, is_transparent, frac=frac)
        
    def is_hoverable(self):
        return self.hoverable;
        
    def is_pickable(self):
        # TODO: if we have a link to the data structure we're in, return True if in map, False if in obj_map
        return self.pickable
    
    def get_name_ncase(self):
        return self.name
    
    def get_name_initcap(self):
        return capitalize_first(self.name)
    
    def get_short_desc(self):
        return self.short_desc
    
    def get_examine_text(self):
        return self.examine_text
    
    def _enabled_verbs(self):
        return ['move','use','examine'] if self.pickable else ['use','examine']
            
    def _get_verb_def(self,verb,*other_objs):
        d = dict(
            # Number of objects is determined by number of text strings, including usually empty string at end
            move = Verb( "move ",    (" to " if not other_objs else " onto "), "" ),
            use  = Verb( "use ", " with ", "") if self.pickable else Verb( "use ", "" ),
            examine = Verb( "examine ", "" ),
        )
        return d[verb]

    def get_verb_sentence_ncase(self,verb,*other_objs):
        assert verb in self._enabled_verbs()
        all_objs = (self,) + other_objs
        return self._get_verb_def(verb,*other_objs).get_sentence_ncase(*all_objs)

    # def get_verb_sentences_ncase(self,*other_objs):
    def get_verb_sentences_ncase(self):
        if 'other_objs' not in locals(): other_objs = ()
        all_objs = (self,) + other_objs
        return ( (verb,self.get_verb_sentence_ncase(verb,*other_objs)) for verb in self._enabled_verbs() )

    # def get_verb_sentences_initcap(self,*other_objs):
    def get_verb_sentences_initcap(self):
        if 'other_objs' not in locals(): other_objs = ()
        return ( (verb,capitalize_first(sentence)) for verb,sentence in self.get_verb_sentences_ncase(*other_objs) )

    def get_verb_sentence_initcap(self,verb,*args):
        return capitalize_first(self.get_verb_sentence_ncase(verb,*args))

    def get_verb_arity(self,verb,*other_objs):
        assert verb in self._enabled_verbs()
        return self._get_verb_def(verb,*other_objs).arity()

    def get_remaining_verb_arity(self,verb,*other_objs):
        all_objs = (self,) + other_objs
        remaining_arity = self.get_verb_arity(verb,*other_objs) - len(all_objs)
        assert remaining_arity >= 0
        return max(0,remaining_arity)
        
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
            
    def draw_contiguously_with(self,other_lst):
        return any( self.key == other_obj.key for other_obj in other_lst)
