from helpers import *

class Event:
    def event_text(self):
        return "verb object on otherobject"

class Rule():
    pass
    
class Rules(Bunch):
    def get_rule(self,verb,*arg_objs):
        return self.get(verb) and self[verb].get(tuple(obj.key for obj in arg_objs))
    
    def add_reflexive_rule(self,verb,arg_pair1,arg_pair2):
        self.add_rule(verb,arg_pair1,arg_pair2)
        self.add_rule(verb,arg_pair2,arg_pair1)
    
    def add_rule(self,verb,*arg_pairs):
        if not self.get(verb): self[verb] = {}
        rule = Rule()
        rule.verb = verb
        rule.in_objs = tuple(pair[0] for pair in arg_pairs)
        rule.out_objs = tuple( (pair[-1] if len(pair)>=1 else '_pass') for pair in arg_pairs)
        self[verb][rule.in_objs] = rule