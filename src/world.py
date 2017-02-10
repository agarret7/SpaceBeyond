import pygame
import numpy as np

class World():

    def __init__(self, player_ship, camera, initial_objects):
        self.p_obj = {'player ship' : player_ship.attached_modules,
                      'free modules' : [],
                      'other ships' : [],
                      'gravity sources' : [],
                      }

        self.camera = camera

        self.game_over = True
        self.game_exit = False

        for obj in initial_objects:
            if type(obj).__name__ == 'GravitationalBody':
                self.add_obj('gravity sources', obj)

    def add_obj(self, key, obj):
        if key in self.p_obj.keys():
            self.p_obj[key].append(obj)
        else:
            self.p_obj[key] = []
            self.p_obj[key].append(obj)

    ### UNIVERSAL FORCE FUNCTIONS ###

    def apply_gravitation(self):
        for g_source in self.p_obj['gravity sources']:
            for entry in self.p_obj.values():
                for obj in entry:
                    if obj != g_source:
                        g_source.gravitate(obj)

    def apply_other_thrusters(self):
        pass

    def update(self, dt):

        ### APPLYING FORCES ###
        
        self.apply_gravitation()
        self.p_obj['player ship'][0].controls()
        self.apply_other_thrusters()

        ### UPDATING PHYSICS ###

        self.p_obj['player ship'][0].update_physics(dt)

        for module in self.p_obj['player ship'][0].attached_modules:
            module.follow(module.module_coordinates, module.module_orientation, module.core_module)

        for ship in self.p_obj['other ships']:
            ship.update_physics(dt)

        for large_body in self.p_obj['gravity sources']:
            large_body.update_physics(dt)

        self.camera.track(self.p_obj['player ship'][0] if self.camera.mode == 0 else self.p_obj['gravity sources'][1])

        for module in self.p_obj['free modules']:
            if module.following_mouse:
                module.follow_mouse(self.camera.get_mouse_pos() + self.camera.position)
                new_point = self.camera.mouse_to_relative_point(self.p_obj['player ship'][0])
                if new_point:
                    module.follow(new_point, module.module_orientation, self.p_obj['player ship'][0])
            else:
                module.update_physics(dt)

        self.camera.clock.tick(self.camera.FPS)
        pygame.display.set_caption(str(self.camera.clock.get_fps()))

        self.camera.display.fill(self.camera.white)
        self.camera.draw_world(self)
        self.camera.print_stats(self.p_obj['player ship'][0])
        pygame.display.update()

    def welcome(self):
        self.camera.print_welcome()

        for event in pygame.event.get():
                
            if event.type == pygame.QUIT:
                self.game_over = False
                self.game_exit = True
                
            elif event.type == pygame.KEYDOWN:
                self.game_over = False
        
