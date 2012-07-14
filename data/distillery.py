from itertools import chain

from src.obj import *
from src.map import *
from src.rules import *
from src.helpers import *

##############################################################
#
# Background objects
#
##############################################################

floor_objs = make_objs(
   floorboards     = Obj("floor", graphic_source=GraphicSource("data/img_circ/VILFLR.bmp",  40, 41,40,40,reps=6)),
   crazypaving     = Obj("floor", graphic_source=GraphicSource("data/img_circ/GRS2ROC.bmp",120,161,40,40)),
   paving          = Obj("floor", graphic_source=GraphicSource("data/img_circ/PAVE.bmp",    40, 41,40,40,reps=4)),
)

for obj in floor_objs.values():
    obj.hoverable = False
    obj.can_support = True

wall_objs = make_objs(
    wall            = Obj("wall",  graphic_source=ContextualGraphicSource(
                                    x  = GraphicSource("data/img_circ/VILINT.bmp",160, 41,40,120,colorkey='topleft'),
                                    lr = GraphicSource("data/img_circ/VILINT.bmp",160, 41,40,120,colorkey='topleft',reps=2,transparent='atbottomofscreen'),
                                    tb = GraphicSource("data/img_circ/VILINT.bmp", 40,201,40,120,colorkey='topleft'),
                                    tl = GraphicSource("data/img_circ/VILINT.bmp",440, 41,40,120,colorkey='topleft'),
                                    tr = GraphicSource("data/img_circ/VILINT.bmp",545, 41,40,120,colorkey='topleft'),
                                    bl = GraphicSource("data/img_circ/VILINT.bmp",345, 41,40,120,colorkey='topleft'),
                                    br = GraphicSource("data/img_circ/VILINT.bmp", 40, 41,40,120,colorkey='topleft'),
                                    )),
)

for obj in wall_objs.values():
    obj.hoverable = False

fixed_objs = make_objs(
    well            = Obj("well", graphic_source=GraphicSource("data/img_test/well.png",0,0,128,128,colorkey='topleft')),
)

for obj in floor_objs.values():
    pass

init_map_str = """\
               
               
###############
#.......W.....#
#.............#
#.............#
#.............#
###############
"""

def base_layers_from_char(char,char_map,x,y):
    if char=='#':
        if x>0:
            return Layers(defs.floorboards, defs.wall)
        else:
            return Layers(defs.paving, defs.wall)
    if char=='.':
        return Layers(defs.floorboards)
    if char==' ':
        return Layers(defs.paving)
    if char=='W':
        return Layers(defs.floorboards,defs.well)

##############################################################
#
# Pick-up-able objects
#
##############################################################
        
pickable_objs = make_objs(
    crucible  = Obj("crucible","An encrusted clay crucible",
                    graphic_source=GraphicSource("data/img_circ/Bench.bmp",510,31,40,40,colorkey='topleft')),
    crucible_w= Obj("crucible","A clay crucible full of water",
                    graphic_source=GraphicSource("data/img_circ/Bench.bmp",508,112,40,40,colorkey='topleft')),
)

for obj in pickable_objs.values():
    obj.pickable = True
        
init_obj_map = ObjMap( [[ None for char in line] for line in init_map_str.splitlines()] )
init_obj_map.create_at(6,4,pickable_objs['crucible'])

##############################################################
#
# Rules
#
##############################################################

rules = Rules()
rules.add_rule('use',('crucible','crucible_w'),('well',))

##############################################################
#
# Global stuff
#
##############################################################

defs = merge(pickable_objs,wall_objs,floor_objs,fixed_objs)



