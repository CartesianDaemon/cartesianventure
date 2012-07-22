from __future__ import division

# Standard modules
from itertools import chain
from numbers import Number
from pygame import Rect
import random

class Bunch(dict):
    def __getattr__(self, attr):
        return self[attr]
    def __setattr__(self, attr, val):
        self[attr] = val

class dict_dict:
    def __init__(self):
        self.store = {}

    def __getitem__(self, key):
        if not key in self.store:
            self.store[key] = {}
        return self.store[key]

class Pos:
    def __init__(self,*args):
        iter_args = args[0] if len(args)==1 else args
        self.x, self.y = iter_args
        assert isinstance(self.x,Number)

    def __getitem__(self,idx):
        if not 0 <= idx <=1: raise IndexError
        return (self.x,self.y)[idx]
        
    def __getattr__(self,attr):
        if attr in ('__add__','__sub__','__radd__','__rsub__'):
            return lambda other: self.apply_elementwise(attr,other)
        elif attr in ('__mul__','__div__','__rmul__','__rdiv__',):
            return lambda other: self.apply_distributive_or_elementwise(attr,other)
        else:
            raise AttributeError

    def apply_elementwise(self,attr,other):
        return Pos( getattr(a,attr)(b) for a,b in zip(self,other) )

    def apply_distributive(self,attr,other):
        return Pos( getattr(a,attr)(other) for a in self )

    def apply_distributive_or_elementwise(self,attr,other):
        distributive = isinstance(other,Number)
        if not distributive: assert len(tuple(other))==2
        return self.apply_distributive(attr,other) if distributive else self.apply_elementwise(attr,other)
            
    def __len__(self):
        return 2
    
    def __eq__(self,other):
        return len(other)==2 and self[0]==other[0] and self[1]==other[1]
        
    def __ne__(self,other):
        return not self==other

class Struct:
    pass
    
def add_dicts(*arg):    
    ret = Bunch()
    for k,v in chain.from_iterable(d.iteritems() for d in args):
        assert k not in ret
        ret[k] = v
    return ret
    
def merge(*args):
    ret = Bunch()
    for k,v in chain.from_iterable(d.iteritems() for d in args):
        # assert k not in ret
        ret[k] = v
    return ret
    
def merge_obj_ip(obj,**kwargs):
    ret = obj
    for k,v in kwargs.iteritems():
        ret.__dict__[k] = v
    return ret

def hash_to_range(input, max):
    # input is any hashable object
    random.seed(input)
    return random.randrange(max)
    
# class Maybe:
#     def __init__(self,value=None):
#         self.value = value
#         
#     def __getattr__(self,attr):
#         if self.value is not None:
#             return getattr(self.value,attr)
#         else:
#             return None
            
def NotNone(x):
    if x is not None:
        return True
    else:
        return None

def reverse_enumerate(lst):
    return reversed(list(enumerate(lst)))
    
def unionall(rects):
    first_rect = next(rects,None)
    if first_rect is not None:
        return first_rect.unionall(list(rects))
    else:
        return Rect(0,0,0,0)

DefaultArg = Struct()

def capitalize_first(str):
    ret = str[0].capitalize() + str[1:]
    return ret
    
def enumerate_2d(arr_2d):
    return ( (x, y, val) for y,line in enumerate(arr_2d) for x,val in enumerate(line) )

def first(lst,default=None):
    return chain(lst,(default,)).next()
    
def offset_from_dir(dir):
    if dir=='l': return (-1, 0)
    if dir=='r': return (+1,0)
    if dir=='u': return (0,-1)
    if dir=='d': return (0,+1)
    if dir=='' : return (0,0)
    print "dir = " + str(dir)
    raise NotImplemented
