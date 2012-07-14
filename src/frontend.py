# Standard modules
import sys
import pygame
from pygame.locals import *
from pygame.compat import geterror
from itertools import chain

# Other modules
import txtlib.txtlib as txtlib

# Internal modules
from src.helpers import *
from src.backend import Backend

enable_splash = 'nosplash' not in sys.argv

class Frontend:
    def main(self,default_room):
        pygame.init()

        self.menu_pos = None
        self.last_mouse_time = pygame.time.get_ticks()
        self.last_mouse_pos = None
        self.last_mouse_tile_pos = None
        self.menu_hit_idx = None
        self.following_with_transitive_verb = None
        
        self.backend = Backend()
        self.backend.load(default_room)

        tile_width, tile_height = self.get_default_tile_size()
        map = self.backend.get_map()
        map_height = len(map)
        map_width = len(map[0])
        self.top_padding = 0 # tile_height*2
        self.screen = pygame.display.set_mode((map_width*tile_width,self.top_padding+map_height*tile_height))
        pygame.display.set_caption('Cartesianventure sample: Alchemical Distillery')

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

        self.clock = pygame.time.Clock()

        if enable_splash:
            if self.splash() == 'quit':
                return 'quit'

        while True:
            if self.loop_step() == 'quit': break
        
        pygame.quit()

    def loop_step(self):
        self.clock.tick(60)
        if self.handle_events() == 'quit':
            return 'quit'
        self.update()
        self.draw_all()
        self.handle_and_draw_menu()
        pygame.display.flip()
        sys.stdout.flush()


    def get_default_tile_size(self):
        return 64,64

    def draw_all(self):
        self.screen.blit(self.background, (0, 0))
        map = self.backend.get_map()
        obj_map = self.backend.get_obj_map()
        contexts = self.backend.get_contexts()
        tile_width, tile_height = self.get_default_tile_size()
        for y, line in enumerate(map):
            for x,layers in enumerate(line):
                for obj in layers.lst() + obj_map.get_lst_at(x,y):
                    if obj is not None:
                        tile_surface = obj.get_surface(x,y,tile_width,tile_height,contexts[y][x])
                        self.screen.blit( tile_surface, (tile_width*x,self.top_padding
                                                        +tile_height*(y+1)-tile_surface.get_height()) )
                
        objs = self.backend.get_visible_objs()
        
        # TODO: draw non-fixed objs
            
    def update(self):
        # Update state of backend other than due to events
        pass

    def handle_and_draw_menu(self):
        if self.following_with_transitive_verb:
            if pygame.mouse.get_focused():
                self.draw_transitive_menu(*pygame.mouse.get_pos())
            return
        hover_delay_ms, hover_off_delay_ms = 200, 200
        if ( self.menu_pos and self.last_mouse_in_menu_time + hover_off_delay_ms < pygame.time.get_ticks()
                           and pygame.mouse.get_focused() and not self.is_in_menu(pygame.mouse.get_pos()) ):
            self.menu_pos = None
        if ((not self.menu_pos) and self.last_mouse_pos and self.last_mouse_time + hover_delay_ms < pygame.time.get_ticks()
                and pygame.mouse.get_focused() ):
            self.menu_pos = self.last_mouse_pos
            self.menu_obj = self.last_mouse_obj
            self.last_mouse_in_menu_time = pygame.time.get_ticks()
        if self.menu_pos:
            self.draw_menu(*self.menu_pos)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type in (MOUSEBUTTONDOWN,MOUSEBUTTONUP,MOUSEMOTION):
                tile_x, tile_y = tile_pos = (xy / tile_wh for xy, tile_wh in zip(event.pos,self.get_default_tile_size()))
                tile_base = self.backend.get_map()[tile_y][tile_x].obj()
                tile_obj = self.backend.get_obj_map().get_obj_at(tile_x,tile_y)
            if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE) :
                return 'quit'
            elif event.type == MOUSEMOTION:
                if self.following_with_transitive_verb:
                    self.transitive_verb_object = tile_obj or tile_base
                else:
                    if tile_base.is_hoverable() or tile_obj:
                        # if self.last_mouse_tile_pos != tile_pos:
                        #     self.last_mouse_tile_pos = tile_pos
                        #     self.last_mouse_pos = event.pos
                        self.last_mouse_pos = event.pos
                        self.last_mouse_time = pygame.time.get_ticks()
                        self.last_mouse_obj = tile_obj or tile_base
                    else:
                        self.last_mouse_pos = None
                        self.last_mouse_tile_pos = None
                    self.menu_hit_idx = None
                    if self.menu_pos and self.is_in_menu(event.pos):
                        self.last_mouse_in_menu_time = pygame.time.get_ticks()
                        for idx,hit_rect_struct in enumerate(self.menu_hit_rects):
                            if hit_rect_struct.hit_rect.collidepoint(event.pos):
                                self.menu_hit_idx = idx
                                break
            elif event.type == MOUSEBUTTONDOWN:
                if self.following_with_transitive_verb:
                    self.backend.do(self.following_with_transitive_verb,self.menu_obj,tile_obj or tile_base)
                    self.following_with_transitive_verb = None
                    self.menu_pos = None
                elif self.menu_pos:
                    if self.menu_hit_idx is not None:
                        # Attach verb to mouse cursor
                        if self.menu_hit_rects[self.menu_hit_idx].verb == '_undo':
                            self.backend.do_undo(self.menu_hit_rects[self.menu_hit_idx].undo_event)
                            self.menu_pos = None
                        elif self.menu_hit_rects[self.menu_hit_idx].verb == '_redo':
                            self.backend.do_undo(self.menu_hit_rects[self.menu_hit_idx].redo_event)
                            self.menu_pos = None
                        elif self.menu_hit_rects[self.menu_hit_idx].tr:
                            # TODO: For verb with more than one target object, add object to list and leave transitive menu open using get_verb_remaining_arities to test if nec
                            self.following_with_transitive_verb = self.menu_hit_rects[self.menu_hit_idx].verb
                            self.transitive_verb_object = tile_obj or tile_base
                        else:
                            self.backend.do(self.following_with_transitive_verb,self.menu_obj)
                            self.menu_pos = None
                    else:
                        self.menu_pos = None
                        self.last_mouse_pos = None
                else:
                    pass
                    # # Enable to enable menu for floor, but nothing in it atm
                    # self.last_mouse_pos = event.pos
                    # self.last_mouse_time = 0
                    # self.last_mouse_obj = tile_obj or tile_base
    
    def draw_menu(self,x,y):
        r1 = Rect(x-20,y-20,40,40)
        verb_width = 150
        verb_height = 20
        verb_vpadding = 10
        verb_vstride = verb_height+verb_vpadding
        verb_offset_x, verb_offset_y = +0,+20
        # r_verbs = Rect(x+verb_offset_x,y+verb_offset_y,verb_width,0)
        # r_undos = Rect(x+verb_offset_x,y+verb_offset_y,verb_width,0)
        
        desc_font = pygame.font.Font(None,25)
        desc_text = desc_font.render(self.menu_obj.description,1,(10,10,10),(255,255,255))
        desc_text.set_alpha(128, RLEACCEL)
        r_desc = desc_text.get_rect().move(x-20,y-40)
        self.screen.blit( desc_text, r_desc.topleft )
        self.menu_hit_rects = []
        verb_list = self.menu_obj.get_verbs()
        arity_list = self.menu_obj.get_verb_remaining_arities()
        for idx,((verb,sentence),tr) in enumerate(zip(verb_list.iteritems(),arity_list)):
            text = txtlib.Text((verb_width, verb_height), 'freesans')
            text.text = sentence
            text.update()
            r_verb = text.area.get_rect().move(x+verb_offset_x, y+verb_offset_y+verb_vstride*idx)
            if idx == self.menu_hit_idx:
                r_verb = r_verb.move(2,1)
            self.screen.blit(text.area, r_verb.topleft)
            #r_verbs.h += verb_vstride
            hit_rect_struct = Struct()
            hit_rect_struct.verb = verb
            hit_rect_struct.hit_rect = r_verb
            hit_rect_struct.tr = tr
            self.menu_hit_rects.append(hit_rect_struct)
        
        if self.menu_obj.get_undoable_events():
            undo_event = self.menu_obj.get_undoable_events()[-1]
            text = txtlib.Text((verb_width, verb_height), 'freesans')
            text.text = "Undo " + undo_event.event_text()
            text.update()
            r_undo = text.area.get_rect().move(x+verb_offset_x-verb_width-5, y+verb_offset_y)
            if (self.menu_hit_idx == len(self.menu_hit_rects)):
                r_undo = r_undo.move(2,1)
            self.screen.blit(text.area, r_undo.topleft)
            #r_undos.h += verb_vstride
            hit_rect_struct = Struct()
            hit_rect_struct.verb = '_undo'
            hit_rect_struct.undo_event = undo_event
            hit_rect_struct.hit_rect = r_undo
            self.menu_hit_rects.append(hit_rect_struct)
        
        if self.menu_obj.get_redoable_events():
            redo_event = self.menu_obj.get_redoable_events()[-1]
            text = txtlib.Text((verb_width, verb_height), 'freesans')
            text.text = "Redo " + redo_event.event_text()
            text.update()
            r_redo = text.area.get_rect().move(x+verb_offset_x-verb_width-5, y+verb_offset_y+verb_vstride)
            if (self.menu_hit_idx == len(self.menu_hit_rects)):
                r_redo = r_redo.move(2,1)
            self.screen.blit(text.area, r_redo.topleft)
            #undos.h += verb_vstride
            hit_rect_struct = Struct()
            hit_rect_struct.verb = '_redo'
            hit_rect_struct.redo_event = redo_event
            hit_rect_struct.hit_rect = r_redo
            self.menu_hit_rects.append(hit_rect_struct)
            
        self.menu_rects = ( r1, unionall(hit_rect_struct.hit_rect for hit_rect_struct in self.menu_hit_rects) )
    
    def draw_transitive_menu(self,x,y):
        text = txtlib.Text((150,20), 'freesans')
        text.text = self.menu_obj.get_verbs(self.transitive_verb_object)[self.following_with_transitive_verb]
        text.update()
        r_verb = text.area.get_rect().move(x-30, y-30)
        self.screen.blit(text.area, r_verb.topleft)
       
    def is_in_menu(self,pt):
        return any( ( rect.collidepoint(pt) for rect in self.menu_rects ) )
    
    def splash(self):
        welcome_msg="""\
Cartesianventure sample: Hijinks in the alchemical distillery department

By Jack Vickeridge

Using creative commons graphics by Daniel Harris, Daniel Cook and Florian Berger

Click to continue...
"""
        #self.screen.blit(self.background, (0, 0))
        self.blit_message(welcome_msg)
        while True:
            self.clock.tick(60)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == QUIT:
                    return 'quit'
                elif event.type == KEYDOWN:
                    return
                elif event.type == MOUSEBUTTONDOWN:
                    return

    def blit_message(self,msg):
        W,H = self.screen.get_size()
        x = W/4
        width = W/2
        y = H/4
        text = txtlib.Text((width, 100), 'freesans')
        text.text = msg
        text.update()
        self.screen.blit(text.area, (x, y))

def main():
    Frontend().main(default_room='distillery')        

#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()
