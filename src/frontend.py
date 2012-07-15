# Standard modules
import sys
import pickle
from itertools import chain

# Pygame
import pygame
from pygame.locals import *
from pygame.compat import geterror

# Other modules
import txtlib.txtlib as txtlib

# Internal modules
from src.helpers import *
from src.backend import Backend

enable_splash = 'nosplash' not in sys.argv
log_file = open('eventlog.bin', 'wb') if 'logevents' in sys.argv else None

class Frontend:
    def __init__(self,default_room):
        pygame.init()

        self.menu_pos = None
        self.last_mouse_time = pygame.time.get_ticks()
        self.last_mouse_pos = None
        self.last_mouse_tile_pos = None
        self.menu_hit_idx = None
        self.following_with_transitive_verb = None
        
        self.backend = Backend()
        self.backend.load(default_room)

        self.screen = pygame.display.set_mode( tuple(a*b+pad1+pad2 for a,b,pad1,pad2 in zip( self.backend.get_map_size(),
                                                                                            self.get_default_tile_size(),
                                                                                            self.get_screen_padding()[0:2],
                                                                                            self.get_screen_padding()[2:4],
                                                                                            ) ) )
        pygame.display.set_caption('Cartesianventure sample: Alchemical Distillery')

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

        self.clock = pygame.time.Clock()
        
        self.FRAME_TIMER = pygame.USEREVENT+1

    def get_screen_padding(self):
        return 0,0,0,0

    def main(self):
        if enable_splash:
            ret = self.splash()
            if ret == 'quit': return 'quit'
        max_fps = 60
        fixed_fps = False
        if not fixed_fps:
            pygame.time.set_timer(self.FRAME_TIMER,1000//max_fps)
        while True:
            if fixed_fps:
                self.clock.tick(max_fps)
                events = pygame.event.get()
            else:
                events = pygame.event.get() or (pygame.event.wait(),)
            ret = self.loop_step(events)
            if ret == 'quit': break
        if log_file: log_file.close()
        pygame.quit()

    def loop_step(self,events=()):
        for event in events:
            ret = self.handle_event(event)
            if ret == 'quit': return 'quit'
        self.draw_all()
        self.handle_and_draw_menu()
        pygame.display.flip()
        sys.stdout.flush()

    def get_default_tile_size(self):
        return 64,64
        
    def get_tile_from_screen_coords(self,pos):
        off_x, off_y = self.get_screen_padding()[0:2]
        x,y = pos[0]-off_x,pos[1]-off_y
        tile_w, tile_h = self.get_default_tile_size()
        return (x/tile_w,y/tile_h )

    def get_screen_from_tile_coords(self,x,y):
        off_x, off_y = self.get_screen_padding()[0:2]
        tile_w, tile_h = self.get_default_tile_size()
        return (off_x+x*tile_w, off_y+y*tile_h )

    def draw_all(self):
        self.screen.blit(self.background, (0, 0))
        tile_width, tile_height = self.get_default_tile_size()
        for x, y, map_square in enumerate_2d( self.backend.get_mapsquares_by_rows() ):
            tile_screen_x, tile_screen_y = self.get_screen_from_tile_coords(x,y)
            for obj in map_square.get_combined_lst():
                assert obj is not None
                tile_surface = obj.get_surface(tile_width,tile_height)
                blit_pos = tile_screen_x, tile_screen_y + tile_height-tile_surface.get_height()
                self.screen.blit( tile_surface, blit_pos )
            
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

    def handle_event(self, event):
        if log_file: # and event.type in (MOUSEBUTTONDOWN,MOUSEBUTTONUP,MOUSEMOTION,QUIT,KEYDOWN):
            my_event = Struct()
            my_event.type = event.type
            if event.type in (MOUSEBUTTONDOWN,MOUSEBUTTONUP,MOUSEMOTION): my_event.pos = event.pos
            if event.type in (KEYDOWN,): my_event.key, my_event.mod = event.key, event.mod
            pickle.dump(my_event,log_file)
            event = my_event # test it works before we try loading from file
        if event.type in (MOUSEBUTTONDOWN,MOUSEBUTTONUP,MOUSEMOTION):
            tile_x, tile_y = self.get_tile_from_screen_coords(event.pos)
            curr_obj = self.backend.get_obj_at(tile_x,tile_y)
        if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_F4 and event.mod&KMOD_ALT ):
            return 'quit'
        elif event.type == MOUSEMOTION:
            if self.following_with_transitive_verb:
                self.transitive_verb_putative_objects = self.transitive_verb_objects + [curr_obj]
            else:
                if curr_obj.is_hoverable():
                    self.last_mouse_pos = event.pos
                    self.last_mouse_time = pygame.time.get_ticks()
                    self.last_mouse_obj = curr_obj
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
                menu_hit_rect = self.menu_hit_rects[self.menu_hit_idx]
                self.transitive_verb_objects.append(curr_obj)
                if self.menu_obj.get_remaining_verb_arity(menu_hit_rect.verb,*self.transitive_verb_objects)==0:
                    self.backend.do(self.following_with_transitive_verb,self.menu_obj,*self.transitive_verb_objects)
                    self.following_with_transitive_verb = None
                    self.menu_pos = None
                    self.last_mouse_pos = None
            elif self.menu_pos:
                if self.menu_hit_idx is not None:
                    menu_hit_rect = self.menu_hit_rects[self.menu_hit_idx]
                    # Do transitive verb or attach intr verb to mouse cursor
                    if menu_hit_rect.verb == '_undo':
                        self.backend.do_undo(menu_hit_rect.undo_event)
                        self.menu_pos = None
                        self.last_mouse_pos = None
                    elif menu_hit_rect.verb == '_redo':
                        self.backend.do_redo(menu_hit_rect.redo_event)
                        self.menu_pos = None
                        self.last_mouse_pos = None
                    else:
                        self.transitive_verb_objects = []
                        self.transitive_verb_putative_objects = []
                        if self.menu_obj.get_remaining_verb_arity(menu_hit_rect.verb,*self.transitive_verb_objects)==0:
                            self.backend.do(menu_hit_rect.verb,self.menu_obj,*self.transitive_verb_objects)
                            self.menu_pos = None
                            self.last_mouse_pos = None
                        else:
                            self.following_with_transitive_verb = menu_hit_rect.verb
                else:
                    self.menu_pos = None
                    self.last_mouse_pos = None
            else:
                pass
                # # Enable to enable menu for floor, but nothing in it atm
                # self.last_mouse_pos = event.pos
                # self.last_mouse_time = 0
                # self.last_mouse_obj = tile_obj or tile_base
    
    def draw_menu(self,mouse_x,mouse_y):
        x,y = self.get_screen_from_tile_coords( * self.get_tile_from_screen_coords((mouse_x,mouse_y)) )
        x += self.get_default_tile_size()[0]/2
        y += self.get_default_tile_size()[1]/2
        verb_vpadding = 10
        verb_offset_x, verb_offset_y = +0,+20
        
        short_desc = self.menu_obj.get_short_desc()
        if short_desc:
            desc_obj = render_text(short_desc, **render_desc_defaults )
            desc_obj.blit_to( self.screen, (x-20,y-40) )
            
        self.menu_hit_rects = []
        verb_list = self.menu_obj.get_verb_sentences_initcap()
        for idx,(verb,sentence) in enumerate(verb_list):
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
            self.menu_hit_rects.append(hit_rect_struct)
        
        if self.menu_obj.get_undoable_events():
            undo_event = self.menu_obj.get_undoable_events()[-1]
            text = txtlib.Text((undo_width, undo_height), 'freesans')
            text.text = "Undo " + undo_event.event_text_ncase()
            text.update()
            r_undo = text.area.get_rect().move(x+verb_offset_x-undo_width-5, y+verb_offset_y)
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
            text = txtlib.Text((undo_width, undo_height), 'freesans')
            text.text = "Redo " + redo_event.event_text()
            text.update()
            r_redo = text.area.get_rect().move(x+verb_offset_x-undo_width-5, y+verb_offset_y+verb_vstride)
            if (self.menu_hit_idx == len(self.menu_hit_rects)):
                r_redo = r_redo.move(2,1)
            self.screen.blit(text.area, r_redo.topleft)
            #undos.h += verb_vstride
            hit_rect_struct = Struct()
            hit_rect_struct.verb = '_redo'
            hit_rect_struct.redo_event = redo_event
            hit_rect_struct.hit_rect = r_redo
            self.menu_hit_rects.append(hit_rect_struct)

        # Menu rects
        #
        # Menu rects define area where mouse doesn't cause menu to disappear
        # Includes area of menu, slight border, area around mouse, and whole tile
        r_courtesy_area = Rect(x-20,y-20,40,40)
        tile_x,tile_y = self.get_tile_from_screen_coords((x,y))
        r_tile = Rect(self.get_screen_from_tile_coords(tile_x,tile_y),self.get_default_tile_size())
        r_whole_menu = unionall(hit_rect_struct.hit_rect for hit_rect_struct in self.menu_hit_rects)
        self.menu_rects = ( r_courtesy_area, r_tile, r_whole_menu.inflate(15,15) )
    
    def draw_transitive_menu(self,x,y):
        text = txtlib.Text((150,20), 'freesans')
        text.text = self.menu_obj.get_verb_sentence_initcap(self.following_with_transitive_verb,
                                                            *self.transitive_verb_putative_objects)
        text.update()
        r_verb = text.area.get_rect().move(x-30, y-30)
        self.screen.blit(text.area, r_verb.topleft)
       
    def is_in_menu(self,pt):
        return any( ( rect.collidepoint(pt) for rect in self.menu_rects ) )
    
    def splash(self,timeout_ms = None):
        welcome_msg="""\
Cartesianventure sample: Hijinks in the alchemical distillery department

By Jack Vickeridge

Using creative commons graphics by Daniel Harris, Daniel Cook and Florian Berger

Click to continue...
"""
        #self.screen.blit(self.background, (0, 0))
        self.blit_message(welcome_msg)
        end_time = pygame.time.get_ticks() + timeout_ms if timeout_ms else None
        while timeout_ms is None or pygame.time.get_ticks()<end_time:
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

render_desc_defaults = dict(xpadding=3, ypadding=1, font_size=20, font_col=(255,255,255),back_col=(0,0,0), back_alpha=128)
        
class render_text:
    def __init__(self,msg,xpadding=5,ypadding=5,font_size=16,font_col=(0,0,0),back_col=(255,255,255),back_alpha=None):
        self._text_surface = None
        self._xpadding, self._ypadding = xpadding, ypadding
        self._back_col = back_col
        self._back_alpha = back_alpha
        font = pygame.font.Font(None,font_size)
        self._text_surface = font.render(msg,1,font_col)
        self._extend_to_width = 0

    def get_size(self):
        return ( max(self._extend_to_width, self._xpadding*2 + self._text_surface.get_width()),
                                            self._ypadding*2 + self._text_surface.get_height() )

    def extend_width_to(self, new_width):
        self._extend_to_width = new_width
        
    def _get_back_surface(self):
        surface = pygame.Surface( self.get_size() )
        surface.fill(self._back_col)
        surface.set_alpha(self._back_alpha, RLEACCEL)
        return surface

    def get_surface(self):
        surface = self._get_back_surface()
        surface.blit(self._text_surface, (self._xpadding, self._ypadding) )
        return surface
        
    def blit_to(self,screen,blit_pos):
        screen.blit( self._get_back_surface(), blit_pos )
        screen.blit( self._text_surface, (blit_pos[0]+self._xpadding,blit_pos[1]+self._ypadding) )
    
def main():
    Frontend(default_room='distillery').main()        
    
#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()
