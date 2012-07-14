# History
#
# 9 July 2012
#
# Added NotNone
# Added splash screen
# GraphicSource takes value from img_circ file
# Randomly chosen tiles for similar surfaces
#
# 10 July 2012
#
# Use tiles from Logic Garden
# Including transparancy
# Fix random tile to use rand based on seed, not hash (which preserves sequences mod 2)
# Tile graphic based on context from adjacent tiles being the same
# Draw floor under walls
# Transparent walls
# obj map
#
# 11 July 2012
# 
# Hover menu
# 
# 14 July 2012
#
# Verb menu, undo menu (nonfunctional), refactored mapsquare, minor fixes
# Move on/onto. Verb blah with itself.
# Fix capitalization. List of verbs from one place.

import unittest

from src.backend import *
from src.frontend import *
from src.helpers import *

class TestSyntax(unittest.TestCase):
    def test_double_comprehension(self):
        self.assertEquals( tuple( b for a in ("abc","ABC") for b in a) , ("a","b","c","A","B","C") )

class TestBunch(unittest.TestCase):
    def test_set(self):
        bunch = Bunch()
        bunch['xxx'] = 'yyy'
        bunch.foo = 'bar'
        self.assertEquals(bunch['foo'],'bar')
        self.assertEquals(bunch.xxx,'yyy')

class TestHelpers(unittest.TestCase):
    def test_merge(self):
        self.assertEquals(merge(dict(one=1),dict(two=2)),dict(one=1,two=2))
        self.assertEquals(merge(),dict())
        
    def test_capitalize_first(self):
        self.assertEquals(capitalize_first("i have an iPad"),"I have an iPad")        

#     def test_maybe(self):
#         self.assertEquals(Maybe("abc").capitalize(),"Abc")
#         self.assertIsNone(Maybe(None).foo)
#         #with self.assertRaises(AttributeError):
#         #    var = Maybe(None)
#         #    var.capitalize

class TestBackend(unittest.TestCase):
    def setUp(self):
        self.backend_distillery = Backend()
        self.backend_distillery.load('distillery')

    def test_1setup(self):
        pass
    
    def test_contexts(self):
        self.assertEqual(self.backend_distillery.get_obj_at(0,2).context,'br' )
    
    def do_verb(self,verb,x1,y1,x2,y2):
        self.backend_distillery.do(verb,self.backend_distillery.get_obj_at(x1,y1),self.backend_distillery.get_obj_at(x2,y2))
    
    def obj_at(self,x,y):
        return self.backend_distillery.get_obj_at(x,y)
    
    def test_verbs(self):
        self.assertEquals(self.obj_at(6,4).key,'crucible')
        self.do_verb('move', 6,4 , 7,4)
        self.assertEquals(self.obj_at(6,4).name,'floor')
        self.assertEquals(self.obj_at(7,4).key,'crucible')
        self.do_verb('move', 7,4 , 8,3)
        self.assertEquals(self.obj_at(7,4).key,'crucible')
        self.assertEquals(len(self.obj_at(7,4).get_undoable_events()),0)
        self.assertEquals(len(self.obj_at(7,4).get_redoable_events()),0)
        self.do_verb('use', 7,4 , 8,3)
        self.assertEquals(self.obj_at(7,4).key,'crucible_w')
        self.assertEquals(len(self.obj_at(7,4).get_undoable_events()),1)
    
    def test_map_load(self):
        self.assertEquals(self.obj_at(1,4).key,'floorboards')
        self.assertEquals(self.obj_at(0,4).key,'wall')

class TestFrontend(unittest.TestCase):
    def setUp(self):
        self.frontend = Frontend(default_room='distillery')
    
    def test_1setup(self):
        pass
    
    def test_splash(self):
        self.frontend.splash(timeout_ms=10)
    
    def test_step(self):
        self.frontend.loop_step()
        
if __name__ == '__main__':
    unittest.main(verbosity=2)