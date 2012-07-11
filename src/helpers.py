class Bunch(dict):
    def __getattr__(self, attr):
        return self[attr]
    def __setattr__(self, attr, val):
        self[attr] = val

class Struct():
    pass

def merge(*args):
    #return set().union(*args)
    ret = Bunch()
    for x in args: ret.update(x)
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
