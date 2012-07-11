from itertools import chain

from src.obj import *
from src.map import *
from src.rules import *
from src.helpers import *

test_make_objs = make_objs(
    id1 = Obj("Name1","Description1"),
    id2 = Obj("Name2","Description2"),
)

initial_small_objs = make_objs(
    crucible  = Obj("Crucible","An encrusted clay crucible",
                    graphic_source=GraphicSource("data/img_circ/Bench.bmp",520,41,40,40,colorkey='topleft')),
    bottle_ship     = Obj("Bottle with pirate ship","Conical flask with a teeny-weeny pirate ship constructed inside"),
    bottle_chest    = Obj("Bottle with pirate chest","Conical flask with a teeny-weeny pirate chest constructed inside (the wooden sort), not the tatooed sort)"),
    bottle_coin     = Obj("Bottle with doubloon","Conical flask with a giant pirate doubloon inside")
)

other_small_objs = make_objs(
    bottle_a  = Obj("Bottle of dragons blood", "Conical flask with dragons blood (and some debris)"),
    bottle_b  = Obj("Bottle of unicorn sweat", "Conical flask with unicorn sweat (and some debris)"),
    bottle_c  = Obj("Bottle of gryphon tears", "Conical flask with gryphon tears (and some debris)"),
    bottle_ab = Obj("Bottle of stuff", "Conical flask with some sort of murkey mixture in"),
    bottle_ac = Obj("Bottle of stuff", "Conical flask with some sort of murkey mixture in"),
    bottle_bc = Obj("Bottle of stuff", "Conical flask with some sort of murkey mixture in"),
)

background_objs = make_objs(
#   floor           = Obj("Floor",graphic_source=GraphicSource("data/img_test/floor.png")),
#   wall            = Obj("Wall",graphic_source=GraphicSource("data/img_test/wall.png")),

#   floor           = Obj("Floor",graphic_source=GraphicSource("data/img_test/tiles.png",128,128,128,128)),
#   wall            = Obj("Wall",graphic_source=GraphicSource("data/img_test/tiles.png",0,0,128,256,colorkey='topleft')),

    floorboards     = Obj("Floor", graphic_source=GraphicSource("data/img_circ/VILFLR.bmp",  40, 41,40,40,reps=6)),
    crazypaving     = Obj("Floor", graphic_source=GraphicSource("data/img_circ/GRS2ROC.bmp",120,161,40,40)),
    paving          = Obj("Floor", graphic_source=GraphicSource("data/img_circ/PAVE.bmp",    40, 41,40,40,reps=4)),
    wall            = Obj("Wall",  graphic_source=ContextualGraphicSource(
                                    x  = GraphicSource("data/img_circ/VILINT.bmp",160, 41,40,120,colorkey='topleft'),
                                    lr = GraphicSource("data/img_circ/VILINT.bmp",160, 41,40,120,colorkey='topleft',reps=2,transparent='atbottomofscreen'),
                                    tb = GraphicSource("data/img_circ/VILINT.bmp", 40,201,40,120,colorkey='topleft'),
                                    tl = GraphicSource("data/img_circ/VILINT.bmp",440, 41,40,120,colorkey='topleft'),
                                    tr = GraphicSource("data/img_circ/VILINT.bmp",545, 41,40,120,colorkey='topleft'),
                                    bl = GraphicSource("data/img_circ/VILINT.bmp",345, 41,40,120,colorkey='topleft'),
                                    br = GraphicSource("data/img_circ/VILINT.bmp", 40, 41,40,120,colorkey='topleft'),
                                    )),
)

for obj in background_objs.values():
    obj.hoverable = False

big_objs = make_objs(
    meter           = Obj("Coin-operated swamp-gas meter",""),
    bunsen          = Obj("Swamp-gas operated heater",""),
    well            = Obj("Wishing well",""),
    reagent_a       = Obj("Barrel of dragon blood" , "Large barrel of dragons blood with a tap on the side"),
    reagent_b       = Obj("Barrel of unicorn sweat", "Large barrel of unicorn sweat with a tap on the side"),
    reagent_c       = Obj("Barrel of gryphon tears", "Large barrel of gryphon tears with a tap on the side"),
)

defs = merge(initial_small_objs,other_small_objs,background_objs,big_objs)

init_map_str = """\
               
               
###############
#.............#
#.............#
#.............#
#.............#
###############
"""

def obj_from_char(char,char_map,x,y):
    if char=='#':
        if x>0:
            return Layers(defs.floorboards, defs.wall)
        else:
            return Layers(defs.paving, defs.wall)
    if char=='.':
        return Layers(defs.floorboards)
    if char==' ':
        return Layers(defs.paving)

init_obj_map = ObjMap( [[ None for char in line] for line in init_map_str.splitlines()] )

init_obj_map.set_at(3,4,initial_small_objs['crucible'])

initial_objs = merge(initial_small_objs,big_objs)

rules = Rules()

rules['use'] = {

#(bottle_ship,reagent_a): ((bottle_a,), "Glug, glug, glug")
('bottle_ship','reagent_a'): (('bottle_a',), "Glug, glug, glug")

}











