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

# TODO tidies of hover menus:
#  - use consistent text rendering based on font.render
#  - figure out how to get padding with font.render
#  - change colour when over hit rect
#  - background for description
#  - brighter color for following transitive verb box

import unittest

from src.backend import *
from src.helpers import *

class TestBunch(unittest.TestCase):
    def test_set(self):
        bunch = Bunch()
        bunch['xxx'] = 'yyy'
        bunch.foo = 'bar'
        self.assertEquals(bunch['foo'],'bar')
        self.assertEquals(bunch.xxx,'yyy')

class TestMaybe(unittest.TestCase):
    def test_maybe(self):
        self.assertEquals(Maybe("abc").capitalize(),"Abc")
        self.assertIsNone(Maybe(None).foo)
        #with self.assertRaises(AttributeError):
        #    var = Maybe(None)
        #    var.capitalize
        
class TestRules(unittest.TestCase):
    def test_merge(self):
        self.assertEquals(merge(dict(one=1),dict(two=2)),dict(one=1,two=2))
        self.assertEquals(merge(),dict())

    def test_rule(self):
        backend = Backend()
        backend.load('distillery')
        obj1 = backend.defs.bottle_ship
        obj2 = backend.defs.reagent_a
        self.assertFalse(backend.obj_in_room('bottle_a'))
        backend.do('use',obj1,obj2)
        self.assertTrue(backend.obj_in_room('bottle_a'))

    def test_rule2(self):
        backend = Backend()
        backend.load('distillery')
        self.assertTrue(backend.obj_in_room('bottle_ship'))
        self.assertFalse(backend.obj_in_room('bottle_a'))
        backend.do('pickup','bottle_ship')
        self.assertFalse(backend.obj_in_room('bottle_ship'))
        self.assertTrue(backend.obj_carried('bottle_ship'))
        backend.do('use','bottle_ship','reagent_a')
        self.assertFalse(backend.obj_carried('bottle_ship'))
        self.assertTrue(backend.obj_carried('bottle_a'))
    
    def test_map(self):
        backend = Backend()
        backend.load('distillery')
        map = backend.get_map()
        self.assertEquals(map[1][1].obj,'floor')
        self.assertEquals(map[0][1].obj,'wall')
    
    def test_frontend(self):
        pass

if __name__ == '__main__':
    unittest.main()