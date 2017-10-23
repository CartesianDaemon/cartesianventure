# Internal modules
from helpers import *

class Action:
    pass

class Message(Action):
    def __init__(self, text):
        self.text = text

class ChangeObj(Action):
    def __init__(self,in_obj_xxx,out_obj_key):
        assert isinstance(in_obj_xxx,ObjArgN) # or isinstance(in_obj_xxx, ????) # Position object or (x,Y) coords with optional stratum
        assert isinstance(out_obj_key,str)
        self.in_obj_xxx = in_obj_xxx
        self.out_obj_key = out_obj_key
        self.out_obj_state = dict()
        # Allow consequent to include new object including state? or state alone? or a transformation function?

class RemoveObj(Action):
    pass

class ObjArgN:
    def __init__(self,arg_num):
        self.n=arg_num-1

class Arg1(ObjArgN):
    def __init__(self):
        ObjArgN.__init__(self,1)

class Arg2(ObjArgN):
    def __init__(self):
        ObjArgN.__init__(self,2)

class Event:
    def event_text_ncase(self):
        return self.sentence

class Rule:
    def __init__(self,verb,*args):
        self.verb = verb
        # TODO: Separate args in str's and Action's in a more natural way
        self.in_obj_keys = []
        args = list(args)
        while args and isinstance(args[0],str):
            self.in_obj_keys.append( args.pop(0) )
        self.in_obj_keys = tuple(self.in_obj_keys)
        assert all( isinstance(arg,Action) for arg in args )
        self.out_actions = args
        self._populate_old_rule()

    def _populate_old_rule(self):
        self.out_obj_packs = [ '_pass' for _ in self.in_obj_keys ]
        for action in self.out_actions:
            if isinstance(action,Message):
                self.msg = action.text
            if isinstance(action,ChangeObj) and isinstance(action.in_obj_xxx,ObjArgN):
                self.out_obj_packs[action.in_obj_xxx.n] = Bunch(key=action.out_obj_key,state=action.out_obj_state)


    @staticmethod
    def make_old_rule(verb,*arg_pairs,**kwargs):
        self = Rule(verb)
        self.verb = verb
        self.in_obj_keys = tuple(pair[0].key for pair in arg_pairs)
        self.out_obj_packs = tuple( (pair[1].pack() if not isinstance(pair[1],str) else pair[1]) for pair in arg_pairs)
        self.msg = kwargs.get('msg') or ""
        return self

    def get_msg(self):
        return self.msg
    
class Rules():
    def __init__(self):
        self._rules = dict_dict()
        
    def update(self,other):
        self._rules.store.update(other._rules.store)
        
    def get_rule(self,verb,*arg_objs):
        return self._rules[verb].get( tuple(obj.key for obj in arg_objs) )
    
    def add_reflexive_rule(self,verb,arg_pair1,arg_pair2):
        self.add_rule(verb,arg_pair1,arg_pair2)
        self.add_rule(verb,arg_pair2,arg_pair1)

    def add_rule(self,verb,*args,**kwargs):
        rule = Rule(verb,*args,**kwargs)
        self._rules[ verb ][ rule.in_obj_keys ] = rule

    def add_old_rule(self,verb,*args,**kwargs):
        rule = Rule.make_old_rule(verb,*args,**kwargs)
        self._rules[ verb ][ rule.in_obj_keys ] = rule
    
