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
        
        pygame.display.flip()
    
    def update(self):
        # Update state of backend other than due to events
        pass

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return 'quit'
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return 'quit'
            elif event.type == MOUSEBUTTONDOWN:
                pass
            elif event.type == MOUSEBUTTONUP:
                pass
                
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
