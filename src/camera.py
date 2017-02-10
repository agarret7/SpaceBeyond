from math import *
import numpy as np
import pygame

class Camera():

    def __init__(self):
        
        self.display_size = np.array([1440, 810])
        self.display = pygame.display.set_mode(np.ndarray.tolist(self.display_size), pygame.RESIZABLE)
        self.position = np.array([0,0])
        self.scale = 1.

        self.font = pygame.font.SysFont(None, 25)
        self.clock = pygame.time.Clock()
        self.FPS = 60

        self.white = (255,255,255)
        self.black = (0,0,0)

        self.mode = 0

    def track(self, target):
        self.position = (target.X if abs(target.omega) < 2*pi else target.X_cm) - (self.display_size/2)/self.scale

    def resize(self, w, h):
        self.display_size = np.array([w, h])
        pygame.display.set_mode((w, h), pygame.RESIZABLE)
        pygame.display.update()

    def mouse_to_relative_point(self, ship):
        mouse = self.get_mouse_pos()
        relative_point = np.floor(np.add(-ship.X + ship.size/2, np.add(mouse, self.position)) / ship.size).tolist()
        distance = hypot(relative_point[0], relative_point[1])
        theta0 = atan2(relative_point[0], relative_point[1]) - pi/2

        relative_point = [np.round(p / ship.size) for p in relative_point]
        relative_point[0] = distance*cos(ship.theta - theta0)
        relative_point[1] = distance*sin(ship.theta - theta0)
        relative_point = np.round(relative_point).tolist()
        if relative_point in ship.surrounding_points:
            return relative_point
        else:
            return False

    def get_mouse_pos(self):
        return np.asarray(pygame.mouse.get_pos()) / self.scale

    ### Sprite Transformations ###

    def rot_center(self, image, angle):
        #Rotate an image while keeping its center and size
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

    def zoom(self, increment):
        self.scale *= increment

    def scale_sprite(self, target):
        w, h = target.get_size()
        return pygame.transform.scale(target, (ceil(self.scale * w), ceil(self.scale * h)))

    def draw(self, target):
        if self.position[0] - 1000 <=  target.X[0] <= self.position[0] + self.display_size[0] / self.scale and self.position[1] - 1000 <= target.X[1] <= self.position[1] + self.display_size[1] / self.scale:
            rotated_sprite = self.rot_center(target.current_sprite, degrees(target.theta))
            scaled_sprite = self.scale_sprite(rotated_sprite)
            translated_position = (target.X - target.size/2 - self.position) * self.scale
            self.display.blit(scaled_sprite, translated_position)

    def draw_world(self, world):
        for entry in world.p_obj.values():
            for obj in entry:
                self.draw(obj)
            
    def text_objects(self, text, color):
        textSurface = self.font.render(text, True, color)
        return textSurface, textSurface.get_rect()

    def message_to_screen(self, msg, color, center_x, center_y):
        textSurf, textRect = self.text_objects(msg, color)
        textRect.center = center_x, center_y
        self.display.blit(textSurf, textRect)

    def print_welcome(self):
        self.display.fill(self.white)
        self.message_to_screen("Welcome to my Space Sim! Press any key to start.", self.black, self.display_size[0]/2, self.display_size[1]/2)
        pygame.display.update()

    def print_stats(self, ship):
        self.message_to_screen("Velocity: " + str('%.1f'%(ship.v[0]/8)) + " m/s, " + str('%.1f'%(ship.v[1]/8)) + " m/s", self.black, self.display_size[0] - 120, 20)
        self.message_to_screen("Position: " + str('%.1f'%(ship.X[0]/8)) + " m, " + str('%.1f'%(ship.X[1]/8)) + " m", self.black, self.display_size[0] - 145, 60)
        self.message_to_screen("Accel: " + str('%.1f'%(hypot(ship.a[0], ship.a[1])/(8*9.81)) + " g"), self.black, self.display_size[0] - 120, 100)

