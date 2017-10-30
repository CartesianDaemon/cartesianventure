# Standard modules
from itertools import izip_longest, chain
import copy
import collections

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

# Contains all immutable properties of object, graphics, etc
# And optionally initial state
# Includes id which uniquely identifies it so it can be recreated from a room spec
# Saving an object constitutes saving the id of the obj spec and the state
class ObjSpec2:
    def __init__(self, other=None):
        self.properties = dict()
        self.properties["id"]= None # UPPER for objects that could be instantiated, Initcase for pure base classes (and mixins?)
        self.properties["ids"] = set() # including this id and all parents
        self.properties["displayname"] = None
        self.properties["desc"] = None # Should this be here or in rules?
        self.properties["graphic"] = None
        self.properties["stratum"] = None
        self.properties["pickable"] = False
        self.properties["pushable"] = False
        self.properties["hoverable"] = False
        self.properties["walkable"] = False
        self.properties["character"] = False
        self.properties["playable"] = False
        self.state = {}
        self.context = '' # TODO: Replace with dict of which 'adj' is one member (?)
        if other is not None:
            self.update(other)
    def __repr__(self):
        return "<<ObjSpec2:"+self.properties['id']+">>"
    def update(self, other):
        if isinstance(other,ObjSpec2) or isinstance(other,Obj2):
            self._update_properties(other.properties)
            self._update_state(other.state)
        elif isinstance(other,collections.Mapping):
            self._update_properties( { k:other[k] for k in other if k!='state'} )
            if 'state' in other:
                self._update_state(other['state'])
        else:
            assert False
        self.validate()
    def _update_properties(self, p):
        assert p['id'] # Changing other properties should always carry a new id
        for k,v in p.items():
            if k in self.properties and self.properties[k] is not None and isinstance(v,ObjValInheritor):
                self.properties[k] = v(self.properties[k])
            elif k=="ids":
                self.properties[k] |= set(v)
            else:
                self.properties[k] = v
    def _update_state(self, s):
        if s:
            # TODO: put ObjValInheritor here
            self.state.update(s)
    def validate(self):
        assert self.key() != "" and isinstance(self.key(),str)
        if self.key().isupper():
            for k,v in self.properties.items():
                assert v is not None
                if callable(v):
                    assert isinstance(v,ObjValCalculator)
                # TODO: check state dict
        # TODO: Check no 'extra' properties once we've added pickable etc (?) or other way of avoiding oopses (?)
    def key(self):
        return self.properties['id']
    def displayname(self):
        return self.properties['displayname']

class Obj2:
    def __init__(self, spec, state={},context=''):
        # TODO: Create from obj or spec?
        self.properties = spec.properties
        self.state = dict(spec.state)
        self.state.update(state)
        self.context = spec.context + context
    def __repr__(self):
        return "<<Obj2:"+self.properties['id']+">>"
    def get_contexts(self):
        return (self.context,) if self.context else ()
    def key(self):
        return self.properties['id']
    def displayname(self):
        return self.properties['displayname']

# Used in constructing an obj spec to calculate a value from a parent obj spec
# In theory should be a pure virtual base type etc

class ObjValInheritor:
    def __init__(self, **kwargs):
        self.append = kwargs['append']
        if self.append is not None:
            "foo" + self.append # Test it can be applied successfully
    def __call__(self,arg):
        if self.append is not None:
            return arg + self.append
        else:
            assert False

# TODO: Move these specific helpers to room definition?
class ModifiedVal(ObjValInheritor):
    def __init__(self,**kwargs):
        ObjValInheritor.__init__(self,**kwargs)

# Used for a property in an obj spec, e.g. walkable if state['open']==True

class ObjValCalculator:
    pass
 
class Obj:
    def __init__(self,name,short_desc="",examine_text="",graphic_source=None,transparent=False):
        # REFACTORING:
        # - immutable state like graphics, actions and rules for derivation of walkable etc properties
        #   should be uniquely determined by room data and ids
        # - ids is a collection of strings, e.g. ("RED_KEY","KEY","Pickable") (is that .key or not?)
        # - any mutable or instance-specific state should be stored in named fields inside state
        #   (e.g. lever position, facing)
        # - combine context (eg. which adjacent walls walls connect to, or character facing) with that

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
        self.pushable = None
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
        
    def map_rect(self):
        return (self.x,self.y,1,1)

    def is_in(self,rect):
        return Rect(rect).collidepoint(self.x,self.y)
    
    def get_surface(self,tile_size,curr_contexts,curr_offsets,frac=0):
        is_transparent = self.transparent or self.transparent=='atbottomofscreen' and pos[1]==7 and 0 < pos[0] < 14
        context_tuple = curr_contexts + self.get_contexts()
        return self.graphic_source.get_surface( (self.x,self.y), tile_size, context_tuple, is_transparent,
            offsets=curr_offsets,frac=frac)
        
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
        l = []
        if self.pickable: l += [ 'move' ]
        if self.pushable: l += [ 'push' ]
        l += [ 'use', 'examine'] # + [ 'QQQ']
        return l
            
    def _get_verb_def(self,verb,*other_objs):
        d = dict(
            # Number of objects is determined by number of text strings, including usually empty string at end
            move = Verb( "move ",    (" to " if not other_objs else " onto "), "" ),
            push = Verb( "push ", ""),
            use  = Verb( "use ", " with ", "") if self.pickable else Verb( "use ", "" ),
            examine = Verb( "examine ", "" ),
            # QQQ = Verb( "qqq ", ""),
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
