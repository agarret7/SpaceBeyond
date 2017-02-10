import pygame
import numpy as np

from physics import *

class Player():

    def __init__(self, ship):
        self.ship = ship

    def get_controls(self, world):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                world.game_exit = True

            if event.type == pygame.VIDEORESIZE:
                world.camera.resize(event.w, event.h)

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_t:
                    for module in world.p_obj['free modules']:
                        if module.following_mouse == True:
                            module.module_orientation = (module.module_orientation + 1) % 4

                if event.key == pygame.K_c:
                    world.camera.mode = (world.camera.mode + 1) % 2

                if event.key == pygame.K_n:
                    world.p_obj['other ships'].append(Enemy(X=np.add(world.camera.get_mouse_pos(),world.camera.position)))
                if event.key == pygame.K_m:
                    world.p_obj['free modules'].append(Module(X=np.add(world.camera.get_mouse_pos(),world.camera.position),v=self.ship.v,module_type="Thruster"))
                if event.key == pygame.K_h:
                    world.p_obj['free modules'].append(Module(X=np.add(world.camera.get_mouse_pos(),world.camera.position),module_type="Hull"))
                
                if event.key == pygame.K_w:
                    self.ship.start_forward = True
                if event.key == pygame.K_a:
                    self.ship.start_left = True
                if event.key == pygame.K_s:
                    self.ship.start_backward = True
                if event.key == pygame.K_d:
                    self.ship.start_right = True
                if event.key == pygame.K_q:
                    self.ship.start_rotate_positive = True
                if event.key == pygame.K_e:
                    self.ship.start_rotate_negative = True

                if event.key == pygame.K_r:
                    self.reset()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.ship.stop_forward = True
                if event.key == pygame.K_a:
                    self.ship.stop_left = True
                if event.key == pygame.K_s:
                    self.ship.stop_backward = True
                if event.key == pygame.K_d:
                    self.ship.stop_right = True
                if event.key == pygame.K_q:
                    self.ship.stop_rotate_positive = True
                if event.key == pygame.K_e:
                    self.ship.stop_rotate_negative = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for module in world.p_obj['free modules']:
                        
                        min_x = module.X[0] - module.current_sprite.get_size()[0]/2 * world.camera.scale
                        max_x = module.X[0] + module.current_sprite.get_size()[0]/2 * world.camera.scale
                        min_y = module.X[1] - module.current_sprite.get_size()[1]/2 * world.camera.scale
                        max_y = module.X[1] + module.current_sprite.get_size()[1]/2 * world.camera.scale
                        mouse_pos_x = world.camera.get_mouse_pos()[0] + world.camera.position[0]
                        mouse_pos_y = world.camera.get_mouse_pos()[1] + world.camera.position[1]
                        
                        if min_x < mouse_pos_x < max_x and min_y < mouse_pos_y < max_y:

                            module.following_mouse = True
                            module_already_following = True

                            global following_module
                            following_module = module
                            break
                    '''
                    for module in self.ship.attached_modules:
                        if module.X[0] < world.camera.get_mouse_pos()[0] + world.camera.position[0] < module.X[0] + module.current_sprite.get_rect().size[0] / world.camera.scale and \
                           module.X[1] < world.camera.get_mouse_pos()[1] + world.camera.position[1] < module.X[1] + module.current_sprite.get_rect().size[1] / world.camera.scale:
                            module.following_mouse = True
                            module_already_following = True
                            following_module = module
                    '''

                if event.button == 4:
                    world.camera.zoom(1.15)
                if event.button == 5:
                    world.camera.zoom(1/1.15)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if len(world.p_obj['free modules']) > 0:
                    for module in world.p_obj['free modules']:
                        if module.following_mouse == True:
                            module.following_mouse = False

                            new_point = world.camera.mouse_to_relative_point(self.ship)
                            if new_point != False:
                                self.attach_module(world.p_obj['free modules'].pop(world.p_obj['free modules'].index(following_module)), new_point, module.module_orientation)

                    '''
                    for module in self.ship.attached_modules:
                        if module.following_mouse == True:
                            module.following_mouse = False
                    '''

    def reset(self):
        self.ship.X_cm = [0,0]
        self.ship.v = [0,0]
        self.ship.omega = 0
        self.ship.theta = 0
        #self.ship.attached_modules = []
        #self.ship.surrounding_points = [[0,1],[1,0],[0,-1],[-1,0]]

    def attach_module(self, old_module, point, orientation):

        self.ship.attached_modules.append(eval(old_module.module_type)(m=old_module.m,X=old_module.X,
                                                                  core_module=self.ship,module_coordinates=point,
                                                                  module_type=old_module.module_type,
                                                                  module_orientation=orientation))  
        self.gen_surrounding_points(point)
        self.ship.reset_params()

    def remove_module(self, old_module, point, orientation):

        self.ship.attached_modules.remove(old_module)

        self.gen_surrounding_points(point)
        self.ship.reset_params()

    def gen_surrounding_points(self, point):
        for i in [-1,1]:
            if [point[0]+i, point[1]] not in self.ship.surrounding_points and \
            [point[0]+i, point[1]] not in [self.ship.attached_modules[n].module_coordinates for n in range(len(self.ship.attached_modules))]:
                self.ship.surrounding_points.append([point[0]+i, point[1]])
        for j in [-1,1]:
            if [point[0], point[1]+j] not in self.ship.surrounding_points and \
            [point[0], point[1]+j] not in [self.ship.attached_modules[n].module_coordinates for n in range(len(self.ship.attached_modules))]:
                self.ship.surrounding_points.append([point[0], point[1]+j])
        self.ship.surrounding_points.remove(point)
        if [0,0] in self.ship.surrounding_points:
            self.ship.surrounding_points.remove([0,0])

        
