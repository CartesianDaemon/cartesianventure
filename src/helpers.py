from itertools import chain

class Bunch(dict):
    def __getattr__(self, attr):
        return self[attr]
    def __setattr__(self, attr, val):
        self[attr] = val

class Struct:
    pass

def merge(*args):
    ret = Bunch()
    for k,v in chain.from_iterable(d.iteritems() for d in args):
        assert k not in ret
        ret[k] = v
    return ret

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