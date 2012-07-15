from src.helpers import *
from src.obj import Obj

prop_defaults = Bunch(
    pickable =   Bunch(moveable=True , pickable=True , hoverable=True , can_support=False, passable=True  ),
    moveable =   Bunch(moveable=True , pickable=False, hoverable=True , can_support=False, passable=False ),
    stackable =  Bunch(moveable=True , pickable=False, hoverable=True , can_support=False, passable=False ),
    fixed =      Bunch(moveable=False, pickable=False, hoverable=True , can_support=False, passable=False ),
    floor =      Bunch(moveable=False, pickable=False, hoverable=False, can_support=True , passable=False ),
    wall =       Bunch(moveable=False, pickable=False, hoverable=False, can_support=False, passable=False ),
)

