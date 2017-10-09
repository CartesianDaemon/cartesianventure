# Internal modules
from helpers import *

class Event:
    def event_text_ncase(self):
        return self.sentence

class Rule:
    def __init__(self,verb,*arg_pairs,**kwargs):
        self.verb = verb
        self.in_obj_keys = tuple(pair[0].key for pair in arg_pairs)
        self.out_obj_packs = tuple( (pair[1].pack() if not isinstance(pair[1],str) else pair[1]) for pair in arg_pairs)
        self.msg = kwargs.get('msg') or ""

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
