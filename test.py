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
        self.assertEqual(self.backend_distillery.get_mapsquare_at(0,2).get_combined_mainobj().context,'br' )
    
    def test_verbs(self):
        # self.backend_distillery.do('move',backend.get_obj_map()[4][6].get_obj())
        pass
    
    def test_map_load(self):
        self.assertEquals(self.backend_distillery.get_mapsquare_at(1,4).get_base_mainobj().key,'floorboards')
        self.assertEquals(self.backend_distillery.get_mapsquare_at(0,4).get_base_mainobj().key,'wall')

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