from helpers import *

class Event:
    pass

class Rules(Bunch):
    def get_rule(self,verb,*arg_objs):
        return self[verb][arg_objs]
