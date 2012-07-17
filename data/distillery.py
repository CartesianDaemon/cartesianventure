##############################################################
#
# Include default class and function definitions included in
# room definition file. Typically including:
# 
#  Room, prop_defaults, Obj, Layers, GraphicSource, ContextualGraphicSource, helpers.*
#
# It is fine to include extras, eg. modules which define various default sorts of object
# or other standard modules with useful functions
#
##############################################################

from src.room_definition import *

room = RoomDefinition()

##############################################################
#
# Background objects
#
##############################################################

room.add_obj_templates( default_props = prop_defaults.floor,
   floorboards     = Obj("floor", graphic_source=GraphicSource("data/img_circ/VILFLR.bmp",  40, 41,40,40,reps=6)),
   crazypaving     = Obj("floor", graphic_source=GraphicSource("data/img_circ/GRS2ROC.bmp",120,161,40,40)),
   paving          = Obj("floor", graphic_source=GraphicSource("data/img_circ/PAVE.bmp",    40, 41,40,40,reps=4)),
)

room.add_obj_templates( default_props = prop_defaults.wall,
    wall            = Obj("wall",  graphic_source=ContextualGraphicSource(
                                    x  = GraphicSource("data/img_circ/VILINT.bmp",160, 41,40,120,colorkey='topleft'),
                                    lr = GraphicSource("data/img_circ/VILINT.bmp",160, 41,40,120,colorkey='topleft',reps=2),
                                    tb = GraphicSource("data/img_circ/VILINT.bmp", 40,201,40,120,colorkey='topleft'),
                                    tl = GraphicSource("data/img_circ/VILINT.bmp",440, 41,40,120,colorkey='topleft'),
                                    tr = GraphicSource("data/img_circ/VILINT.bmp",545, 41,40,120,colorkey='topleft'),
                                    bl = GraphicSource("data/img_circ/VILINT.bmp",345, 41,40,120,colorkey='topleft'),
                                    br = GraphicSource("data/img_circ/VILINT.bmp", 40, 41,40,120,colorkey='topleft'),
                                    ),transparent='atbottomofscreen'),
)

# TODO: Move to separate character definition file
room.add_obj_templates( default_props = prop_defaults.character,
    marzie            = Obj("wall",  graphic_source=ContextualGraphicSource(
                                    x  = GraphicSource("data/img_circ/VILINT.bmp",160, 41,40,120,colorkey='topleft'),
                                    lr = GraphicSource("data/img_circ/VILINT.bmp",160, 41,40,120,colorkey='topleft',reps=2),
                                    tb = GraphicSource("data/img_circ/VILINT.bmp", 40,201,40,120,colorkey='topleft'),
                                    tl = GraphicSource("data/img_circ/VILINT.bmp",440, 41,40,120,colorkey='topleft'),
                                    tr = GraphicSource("data/img_circ/VILINT.bmp",545, 41,40,120,colorkey='topleft'),
                                    bl = GraphicSource("data/img_circ/VILINT.bmp",345, 41,40,120,colorkey='topleft'),
                                    br = GraphicSource("data/img_circ/VILINT.bmp", 40, 41,40,120,colorkey='topleft'),
                                    ) ),
)

room.add_obj_templates( default_props = prop_defaults.fixed,
    well            = Obj("well", graphic_source=GraphicSource("data/img_test/well.png",0,0,128,128,colorkey='topleft')),
)

init_map_str = """\
               
               
###############
#.......W.....#
#.............#
#.............#
#.............#
###############
"""

def base_tuples_from_char(char,x,y):
    if char=='#':
        if x>0:
            return (room.defs.floorboards, room.defs.wall)
        else:
            return (room.defs.paving, room.defs.wall)
    if char=='.':
        return (room.defs.floorboards,)
    if char==' ':
        return (room.defs.paving,)
    if char=='W':
        return (room.defs.floorboards,room.defs.well)

room.make_map_from_key(init_map_str, base_tuples_from_char)
        
##############################################################
#
# Pick-up-able objects
#
##############################################################

room.add_obj_templates( default_props = prop_defaults.pickable,
    crucible  = Obj("crucible","An encrusted clay crucible", examine_text="There are some occult symbols engraved below",
                    graphic_source=GraphicSource("data/img_circ/Bench.bmp",510,31,40,40,colorkey='topleft')),
    crucible_w= Obj("crucible","A clay crucible full of water",
                    graphic_source=GraphicSource("data/img_circ/Bench.bmp",508,112,40,40,colorkey='topleft')),
)

room.create_obj_at(6,4,room.defs.crucible)

##############################################################
#
# Rules
#
##############################################################

defs = room.defs

room.add_rule('use',(defs.crucible,defs.crucible_w),(defs.well,'_pass'),msg="I fill the crucible from the well")
room.add_rule('use',(defs.well,'_pass'),msg="I wash my face")
