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
        
        self.draw_menu_around_tile_not_mouse = True

        self.menu_pos = None
        self.last_mouse_time = pygame.time.get_ticks()
        self.last_mouse_pos = None
        self.last_mouse_tile_pos = None
        self.menu_hit_idx = None
        self.following_with_transitive_verb = None
        self.recent_presses = []
        
        self.backend = Backend()
        self.backend.load(default_room)
        
        self.scene_begin_ticks = self.state_begin_ticks = pygame.time.get_ticks()
        self.default_state_duration = 500
        self.state_duration = self.default_state_duration

        self.screen = pygame.display.set_mode( tuple(a*b+pad1+pad2 for a,b,pad1,pad2 in zip( self.backend.get_map_size(),
                                                                                            self.tile_size(),
                                                                                            self.get_screen_padding_lt(),
                                                                                            self.get_screen_padding_rb(),
                                                                                            ) ) )
        pygame.display.set_caption('Cartesianventure sample: Alchemical Distillery')

        self.background = pygame.Surface(self.screen.get_size()+self.get_screen_padding_lt()+self.get_screen_padding_rb())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

        self.clock = pygame.time.Clock()
        
        self.FRAME_TIMER = pygame.USEREVENT+1

    def get_screen_padding_lt(self):
        return Pos(0,0)

    def get_screen_padding_rb(self):
        return Pos(0,0)

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
            ret = self.loop_step(pygame.time.get_ticks(),events)
            if ret == 'quit': break
        if log_file: log_file.close()
        pygame.quit()

    def loop_step(self,ticks,events=()):
        for event in events:
            ret = self.handle_event(event, ticks)
            if ret == 'quit': return 'quit'
        if self.frac(ticks) >= 1:
            self.advance_state(ticks)
            if self.backend.state_is_idle() and self.recent_presses:
                self.backend.move_player( self.dir_from_key(self.recent_presses[-1]) )
        self.draw_all(ticks)
        self.handle_and_draw_menu(ticks)
        pygame.display.flip()
        sys.stdout.flush()

    def tile_size(self):
        return Pos(64,64)
        
    def get_tile_from_screen_coords(self,pos):
        return ( pos - self.get_screen_padding_lt() ) / self.tile_size()

    def get_screen_from_tile_coords(self,pos):
        return self.get_screen_padding_lt() + pos * self.tile_size()

    def frac(self,ticks):
        return (ticks - self.state_begin_ticks) / float(self.state_duration)

    def advance_state(self,ticks):
        self.backend.advance_state()
        self.state_begin_ticks = ticks
    
    def draw_all(self,ticks):
        self.screen.blit(self.background, (0, 0))
        for tile_surface in self.backend.get_blit_surfaces( self.frac(ticks), self.tile_size() ):
            tile_surface.blit_to( self.screen, self.get_screen_padding_lt() )
            
    def handle_and_draw_menu(self,ticks):
        if self.following_with_transitive_verb:
            if pygame.mouse.get_focused():
                self.draw_transitive_menu(pygame.mouse.get_pos())
            return
        hover_delay_ms, hover_off_delay_ms = 50, 200
        if ( self.menu_pos and self.last_mouse_in_menu_time + hover_off_delay_ms < ticks
                           and pygame.mouse.get_focused() and not self.is_in_menu(pygame.mouse.get_pos()) ):
            self.menu_pos = None
        if ((not self.menu_pos) and self.last_mouse_pos and self.last_mouse_time + hover_delay_ms < ticks
                and pygame.mouse.get_focused() ):
            self.menu_pos = self.last_mouse_pos
            self.menu_obj = self.last_mouse_obj
            self.last_mouse_in_menu_time = ticks
        if self.menu_pos:
            self.draw_menu(self.menu_pos)

    def dir_from_key(self,event_key):
        dir_sets = ( (K_LEFT,K_RIGHT,K_UP,K_DOWN), (K_a,K_d,K_w,K_s) )
        dir_keys = "lrud"
        return first( dir for dir_set in dir_sets for K_,dir in zip(dir_set,dir_keys) if K_==event_key)

    def handle_event(self, event, ticks):
        if log_file: # and event.type in (MOUSEBUTTONDOWN,MOUSEBUTTONUP,MOUSEMOTION,QUIT,KEYDOWN):
            my_event = Struct()
            my_event.type = event.type
            if event.type in (MOUSEBUTTONDOWN,MOUSEBUTTONUP,MOUSEMOTION): my_event.pos = event.pos
            if event.type in (KEYDOWN,): my_event.key, my_event.mod = event.key, event.mod
            pickle.dump(my_event,log_file)
            event = my_event # test it works before we try loading from file
        if event.type in (MOUSEBUTTONDOWN,MOUSEBUTTONUP,MOUSEMOTION):
            curr_obj = self.backend.get_obj_at(self.get_tile_from_screen_coords(event.pos))
        if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_F4 and event.mod&KMOD_ALT ):
            return 'quit'
        elif event.type == KEYDOWN:
            self.recent_presses.append(event.key)
            dir = self.dir_from_key(event.key)
            if self.backend.state_is_idle():
                self.advance_state(ticks)
                if dir: self.backend.move_player(dir)
            elif self.backend.state_is_chainable():
                if dir: self.backend.move_player(dir)
        elif event.type == KEYUP:
            self.recent_presses.remove(event.key)
        elif event.type == MOUSEMOTION:
            if self.following_with_transitive_verb:
                self.transitive_verb_putative_objects = self.transitive_verb_objects + [curr_obj]
            else:
                if curr_obj.is_hoverable():
                    self.last_mouse_pos = event.pos
                    self.last_mouse_time = ticks
                    self.last_mouse_obj = curr_obj
                else:
                    self.last_mouse_pos = None
                    self.last_mouse_tile_pos = None
                self.menu_hit_idx = None
                if self.menu_pos and self.is_in_menu(event.pos):
                    self.last_mouse_in_menu_time = ticks
                    for idx,hit_rect_struct in enumerate(self.menu_hit_rect_structs):
                        if hit_rect_struct.hit_rect.collidepoint(event.pos):
                            self.menu_hit_idx = idx
                            break
        elif event.type == MOUSEBUTTONDOWN:
            if self.following_with_transitive_verb:
                menu_hit_rect = self.menu_hit_rect_structs[self.menu_hit_idx]
                self.transitive_verb_objects.append(curr_obj)
                if self.menu_obj.get_remaining_verb_arity(menu_hit_rect.verb,*self.transitive_verb_objects)==0:
                    self.backend.do(self.following_with_transitive_verb,self.menu_obj,*self.transitive_verb_objects)
                    self.following_with_transitive_verb = None
                    self.menu_pos = None
                    self.last_mouse_pos = None
            elif self.menu_pos:
                if self.menu_hit_idx is not None:
                    menu_hit_rect = self.menu_hit_rect_structs[self.menu_hit_idx]
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
    
    def draw_menu(self,mouse_pos):
        if not self.backend.state_is_idle():
            self.menu_hit_rect_structs = ()
            return
        tile_pos = self.get_screen_from_tile_coords( self.get_tile_from_screen_coords(mouse_pos) )
        if self.draw_menu_around_tile_not_mouse:
            x_y = x,y = tile_pos + self.tile_size() / 2
        else:
            x_y = x,y = mouse_pos
        verb_spacing = 10
        verb_offset_x, verb_offset_y = +0,+20

        short_desc = self.menu_obj.get_short_desc()
        if short_desc:
            render_text(short_desc, **render_desc_defaults ).blit_to( self.screen, (x-20,y-40) )

        verb_width , verb_height = 120 , 20
        undo_width, undo_height = 180, verb_height
        verb_vstride = verb_height+verb_spacing

        verb_list = ( (sentence, dict(verb=verb)) for verb, sentence in self.menu_obj.get_verb_sentences_initcap() )
        
        self.menu_hit_rect_structs = self.draw_and_get_hit_rect_structs(
                                        verb_list, self.menu_hit_idx,render_menu_defaults, topleft=x_y + (+0,+20) )

        undo_list = []
        
        if self.menu_obj.get_undoable_events():
            undo_event = self.menu_obj.get_undoable_events()[-1]
            undo_list.append( ("Undo " + undo_event.event_text_ncase(), dict(verb='_undo', undo_event = undo_event ) ) )
                                        
        if self.menu_obj.get_redoable_events():
            redo_event = self.menu_obj.get_redoable_events()[-1]
            undo_list.append( ("Redo " + redo_event.event_text_ncase(), dict(verb='_redo', redo_event = redo_event ) ) )

        undo_hit_idx = self.menu_hit_idx - len(self.menu_hit_rect_structs) if self.menu_hit_idx else None
        self.menu_hit_rect_structs.extend( self.draw_and_get_hit_rect_structs(
                                           undo_list, undo_hit_idx, render_menu_defaults, topright=x_y + (-5,+20) ) )

        # Menu rects
        #
        # Menu rects define area where mouse doesn't cause menu to disappear
        # Includes area of menu, slight border, area around mouse, and whole tile
        if self.draw_menu_around_tile_not_mouse:
            r_courtesy_area = Rect( x_y + (-20,-20), (40,40) )
        else:
            r_courtesy_area = Rect(tile_pos,self.tile_size())
        r_whole_menu = unionall(hit_rect_struct.hit_rect for hit_rect_struct in self.menu_hit_rect_structs)
        self.menu_rects = ( r_courtesy_area, r_whole_menu.inflate(15,15) )

    def draw_and_get_hit_rect_structs(self,sentences,selected_idx=-1,render_text_props={},topleft=None,topright=None):
        hit_rect_structs = []
        vspacing = 10
        selected_props = merge(render_text_props,render_selected)
        if not sentences : return hit_rect_structs
        
        for idx,(sentence,d) in enumerate(sentences):
            hit_rect_struct = Struct()
            props = render_text_props if idx != selected_idx else selected_props
            hit_rect_struct.render_obj = render_text(sentence, **props)
            # hit_rect_struct.verb = verb
            for k,v in d.iteritems(): setattr(hit_rect_struct,k,v)
            hit_rect_structs.append(hit_rect_struct)

        menu_width = max( hit_rect_struct.render_obj.get_size().x for hit_rect_struct in hit_rect_structs )
        next_pos = topleft if topleft is not None else topright - (menu_width,0)
        
        for hit_rect_struct in hit_rect_structs:
            hit_rect_struct.render_obj.extend_width_to(menu_width)
            hit_rect_struct.render_obj.blit_to( self.screen, next_pos )
            hit_rect_struct.hit_rect = Rect( next_pos, hit_rect_struct.render_obj.get_size() )
            next_pos.y += hit_rect_struct.hit_rect.h + vspacing
        
        return hit_rect_structs
        
    def draw_transitive_menu(self,pos):
        msg = self.menu_obj.get_verb_sentence_initcap(self.following_with_transitive_verb,
                                                      *self.transitive_verb_putative_objects)
        render_obj = render_text( msg, **render_menu_defaults )
        render_obj.blit_to( self.screen, pos + (-30,-30) )
       
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
render_menu_defaults = dict(xpadding=5,ypadding=5,font_size=16,font_col=(0,0,0),back_col=(255,255,255),back_alpha=None)
render_selected = dict(font_col=(255,0,0))

class render_text:
    def __init__(self,msg,xpadding=0,ypadding=0,font_size=16,font_col=(0,0,0),back_col=(255,255,255),back_alpha=None):
        self._text_surface = None
        self._padding = Pos(xpadding,ypadding)
        self._back_col = back_col
        self._back_alpha = back_alpha
        font = pygame.font.Font(None,font_size)
        self._text_surface = font.render(msg,1,font_col)
        self._extend_to_width = 0

    def get_size(self):
        return Pos( max(self._extend_to_width, self._padding[0]*2 + self._text_surface.get_width()),
                                               self._padding[1]*2 + self._text_surface.get_height() )

    def extend_width_to(self, new_width):
        self._extend_to_width = new_width
        
    def _get_back_surface(self):
        surface = pygame.Surface( self.get_size() )
        surface.fill(self._back_col)
        surface.set_alpha(self._back_alpha, RLEACCEL)
        return surface

    def get_surface(self):
        surface = self._get_back_surface()
        surface.blit(self._text_surface, self._padding )
        return surface
        
    def blit_to(self,screen,blit_pos):
        screen.blit( self._get_back_surface(), blit_pos )
        screen.blit( self._text_surface, blit_pos + self._padding )
    
def main():
    Frontend(default_room='distillery').main()        
    
#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()
