# Internal modules
from helpers import *

class Event:
    def event_text_ncase(self):
        return self.sentence

class Rule:
    def __init__(self,verb,*arg_pairs,**kwargs):
        self.verb = verb
        self.in_objs = tuple(pair[0] for pair in arg_pairs)
        self.out_objs = tuple( (pair[-1] if len(pair)>=2 else '_pass') for pair in arg_pairs)
        self.msg = kwargs.get('msg') or ""

    def get_msg(self):
        return self.msg
    
class Rules(Bunch):
    def get_rule(self,verb,*arg_objs):
        return self.get(verb) and self[verb].get(tuple(obj.key for obj in arg_objs))
    
    def add_reflexive_rule(self,verb,arg_pair1,arg_pair2):
        self.add_rule(verb,arg_pair1,arg_pair2)
        self.add_rule(verb,arg_pair2,arg_pair1)
    
    def add_rule(self,verb,*args,**kwargs):
        rule = Rule(verb,*args,**kwargs)
        if not self.get(verb): self[verb] = {}
        self[verb][rule.in_objs] = rule
