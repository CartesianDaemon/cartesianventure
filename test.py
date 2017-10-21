#! /usr/bin/env python

import unittest
import os
import sys
import fnmatch
import pickle

from src.backend import *
from src.frontend import *
from src.helpers import *
from src.room import *
from src.graphic_source import *
from src.obj import *

class TestSyntax(unittest.TestCase):
    def test_double_comprehension(self):
        self.assertEquals( tuple( b for a in ("abc","ABC") for b in a) , ("a","b","c","A","B","C") )
        
    def test_pickle(self):
        fh = open("foo","wb")
        pickle.dump( [1,2,3], fh)
        fh.close()
        fh = open("foo","rb")
        self.assertEquals(pickle.load(fh),[1,2,3])
        with self.assertRaises(EOFError):
            pickle.load(fh)

    def get_add_x(self,arg):
        def add_x(val):
            return arg+val
        return add_x
        
    def test_closure(self):
        add_1 = self.get_add_x(1)
        add_2 = self.get_add_x(2)
        self.assertEquals(add_1(10),11)    
        self.assertEquals(add_2(10),12)    

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

    def test_enumerate_2d(self):
        self.assertEquals(tuple(enumerate_2d(["ab","pq"])),( (0,0,'a'),(1,0,'b'),(0,1,'p'),(1,1,'q'), ))
        
    def test_pos(self):
        pos1 = Pos(10,20)
        self.assertEquals(pos1.x,10)
        self.assertEquals(pos1.y,20)
        pos2 = (5,6) + pos1
        self.assertEquals(pos2.x,15)
        self.assertEquals(pos2.y,26)
        pos2 += Pos( (-10,-10) )
        self.assertEquals(pos2.x,5)
        self.assertEquals(pos2.y,16)
        for idx,x_y in enumerate(pos2):
            self.assertEquals( x_y, 5 if idx==0 else 16)
        with self.assertRaises(IndexError): pos2[-1]
        with self.assertRaises(IndexError): pos2[2]
        with self.assertRaises(IndexError): pos2['foo']
        self.assertEquals( Pos(10,20)*10, Pos(100,200) )
        self.assertEquals( Pos(10,20)/10, (1,2) )

#     def test_maybe(self):
#         self.assertEquals(Maybe("abc").capitalize(),"Abc")
#         self.assertIsNone(Maybe(None).foo)
#         #with self.assertRaises(AttributeError):
#         #    var = Maybe(None)
#         #    var.capitalize

class TestMultipleImport(unittest.TestCase):
    def test_a(self):
        os.blah = "foo"
        self.assertEquals(os.blah,"foo")
    def test_b(self):
        self.assertEquals(os.blah,"foo")


class TestBackend(unittest.TestCase):
    def setUp(self):
        default_room_filename = 'distillery'
        self.backend_distillery = Backend()
        self.backend_distillery.load(default_room_filename)
        self.defs = room_data.load_room(default_room_filename).defs

    def test_add_obj_spec(self):
        room = RoomSpec2()
        self.room = room

        room.add_obj_spec("pickable",pickable=True,pushable=True,hoverable=True,walkable=True, stratum='obj') # aka Moveable anything you can pick up/move anywhere
        room.add_obj_spec("pushable",pushable=True,hoverable=True,walkable=True, stratum='obj') # Can push but not move arbitrarily
        room.add_obj_spec("fixed",hoverable=True, stratum='wall') # e.g. scenery you can't move but can interact with
        room.add_obj_spec("floor",walkable=True, stratum='floor') # Can walk, can't interact
        room.add_obj_spec("wall",stratum='wall') # Can't walk, can't interact

        key = room.add_obj_spec("Key", "pickable", displayname="key", desc="")
        # self.assertEquals(room.obj_specs["Key"], key)
        self.assertEquals(key.key(),"Key")
        key.displayname="key"

        redkey = room.add_obj_spec("REDKEY","Key",
            displayname = "red key",
            desc="An ornate key made from iron with a dull red tint.",
            graphic="FAKEGraphics()",
            state={'bent':False},
        )
        self.assertEquals(redkey.key(),"REDKEY")
        self.assertEquals(redkey.displayname(), "red key")
        
        bluekey = room.add_obj_spec("BLUEKEY", "Key",
            desc="An thick iron key with a wavey watery tint.",
            graphic="FAKEGraphics()",
            state={'bent':False},
        )
        self.assertEquals(bluekey.displayname(),"key")
        # TODO: test ???? bluekey.

        copiedredkey = room.add_obj_spec("COPIEDREDKEY", "REDKEY")
        self.assertEquals(copiedredkey.displayname(),"red key")
        # TODO: Test other properties of COPIEDREDKEY

        # TODO: test using function as desc or other member

        room.add_obj_spec("Bent", state={'bent':True}, desc=ModifiedVal(append=" It's bent too much to use."))
        
        # bluekey_b = room.get_obj_from_spec("BLUEKEY")
        # TODO: Compare bluekey2 to previous expected values

        # Create object from combination of specs with no extra details
        # No way of referring back to this particular spec except by specifying those ids again
        bent_redkey = room.add_obj_spec("","Bent","REDKEY") 
        # TODO: Test properties of bent_redkey as expected

        # An anonymous object created spontaneously that doesn't match anything particular. More useful for scenery than keys.
        decoykey = room.add_obj_spec("","Key",desc="I've no idea what this key fits, it could be anywhere",graphics="FAKEGraphics()") 
        # TODO: Test properties of decoykey

        # And a one-off object made from a combining object and another object
        bent_bluekey = room.add_obj_spec("","Bent","BLUEKEY")

    @unittest.expectedFailure
    def test_add_map(self):
        self.test_add_obj_spec()
        room.add_map(
            "##########",
            "#  1 *   #", {'*': room.obj_specs["REDKEY"]},
            "#  *   2 #", {'*': room.obj_specs["BLUEKEY"]},
            "#   3*   #", {'*': decoykey},
            "##########",
            {
                '#': room.add_obj_spec("WALL", "wall", graphic="FAKEGraphics()"),
                '1': redkey,
                '2': bluekey,
                '3': decoykey,
            }
        )

        room.add_map(
            "          ",
            "          ",
            "..........",
            "..........",
            "..........",
            "..........",
            "..........",
            {
                '.': room.add_obj_spec("FLOORBOARDS", "floor", graphic="FAKEGraphics()")
            }
        )

        # TODO: Decide how to handle layers!
        # TODO: Decide how to handle {} interpreting chaarcters that might already have been interpreted, add warning function?
        
        # TODO: Add rules

        # TODO: Create room from room...?

        # TODO: Create two rooms, test them separately

        # TODO: Test floor, obj, wall appear correctly

    def test_1setup(self):
        pass
    
    def obj_at(self,x,y):
        return self.backend_distillery.get_obj_at((x,y))
    
    def test_contexts(self):
        self.assertEqual(self.obj_at(0,2).get_contexts(),('br',) )
    
    def test_verblist(self):
        crucible = self.defs.crucible
        crucible_w = self.defs.crucible_w
        well = self.defs.well
        self.assertEqual(crucible.get_verb_sentence_ncase('use'),"use crucible with ...")
        self.assertEqual(crucible.get_verb_sentence_initcap('use'),"Use crucible with ...")
        self.assertEqual(crucible.get_verb_sentence_initcap('use',crucible_w),"Use crucible with crucible")
        self.assertEqual(crucible.get_verb_sentence_initcap('use',crucible),"Use crucible with itself")
        self.assertEqual(len(tuple(self.obj_at(6,4).get_verb_sentences_ncase())),3)
        # self.assertEqual(len(tuple(self.obj_at(6,4).get_verb_sentences_ncase(self.obj_at(8,3)))),3)
        self.assertEqual(len(tuple(self.obj_at(8,3).get_verb_sentences_ncase())),2)
        self.assertEqual(len(tuple(self.obj_at(6,4).get_verb_sentences_initcap())),3)
        # self.assertEqual(len(tuple(self.obj_at(6,4).get_verb_sentences_initcap(self.obj_at(8,3)))),3)
        self.assertEqual(len(tuple(self.obj_at(8,3).get_verb_sentences_initcap())),2)
        self.assertEqual(crucible.get_verb_arity('move'),2)
        self.assertEqual(crucible.get_remaining_verb_arity('move'),1)
        self.assertEqual(crucible.get_remaining_verb_arity('move',crucible),0)
    
    def do_verb(self,verb,x1,y1,x2,y2):
        self.backend_distillery.do(verb,self.obj_at(x1,y1),self.obj_at(x2,y2))

    def test_verb_move(self):
        self.assertEquals(self.obj_at(6,4).key,'crucible')
        self.do_verb('move', 6,4 , 7,4)
        self.assertEquals(self.obj_at(6,4).name,'floor')
        self.assertEquals(self.obj_at(7,4).key,'crucible')
    
    # Same test as before, in case we fail to deepcopy the room schema and accidentally alter it!
    # Then separate tests don't work independently
    def test_verb_move2(self):
        self.test_verb_move()
        
    def test_verb_move_twice(self):
        self.assertEquals(self.obj_at(6,4).key,'crucible')
        self.do_verb('move', 6,4 , 7,4)
        self.assertEquals(self.obj_at(6,4).name,'floor')
        self.assertEquals(self.obj_at(7,4).key,'crucible')
        self.do_verb('move', 7,4 , 8,3)
        self.assertEquals(self.obj_at(7,4).name,'floor')
        self.assertEquals(self.obj_at(8,3).key,'crucible')
        self.assertEquals(len(self.obj_at(7,4).get_undoable_events()),0)
        self.assertEquals(len(self.obj_at(7,4).get_redoable_events()),0)

    def test_verb_use(self):
        self.assertEquals(self.obj_at(6,4).key,'crucible')
        self.assertEquals(self.obj_at(10,3).key,'well')
        self.do_verb('use', 6,4 , 10,3)
        self.assertEquals(self.obj_at(6,4).key,'crucible_w')
        self.assertEquals(len(self.obj_at(6,4).get_undoable_events()),1)
    
    def test_map_load(self):
        self.assertEquals(self.obj_at(1,4).key,'floorboards')
        self.assertEquals(self.obj_at(0,4).key,'wall')

@unittest.skipIf(len(sys.argv)>1,"skip frontend for quickness")
class TestFrontend(unittest.TestCase):
    def setUp(self):
        self.frontend = Frontend(default_room='distillery')
    
    def test_1setup(self):
        pass
    
    def test_splash(self):
        self.frontend.splash(timeout_ms=10)
    
    def test_step(self):
        self.frontend.loop_step(0)
        
    def test_playback(self):
        filenames = fnmatch.filter(os.listdir("."),"test*.eventlog.bin")
        self.assertTrue(filenames)
        for filename in filenames:
            # print "\nPlaying back: " + filename + ": "
            my_frontend = Frontend(default_room='distillery')
            fh = open(filename,"rb")
            try:
                while True:
                    event = pickle.load(fh)
                    my_frontend.handle_event(event,0)
            except EOFError:
                fh.close()
            print ""

if __name__ == '__main__':
    unittest.main(verbosity=2)
# History
#
# 9 July 2012
#
# Added NotNone
# Added splash screen
# BaseGraphic takes value from img_circ file
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
# Examine verb. Intransitive verbs for fixed objects.
#
# 15 July 2012
#
# Much refactoring

