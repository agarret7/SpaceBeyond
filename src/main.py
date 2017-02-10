import pygame
import time
import numpy as np

from camera import *
from world import *
from physics import *
from player import *

pygame.init()

def initialize_world():

    ### WORLD'S INITIAL SETTINGS ###

    initial_objects = [GravitationalBody(X = np.array([1.5*10**11, 0]), m = 1.989*10**32, sprites = {'default' : pygame.image.load('../graphics/Sun.png')}),
                       GravitationalBody(X = np.array([-1500, 0]), m = 10**19, sprites = {'default' : pygame.image.load('../graphics/Earth.png')})]

    player_ship = Ship(module_type="Core", v = np.array([0,-500]))
    world = World(player_ship, Camera(), initial_objects)

    return world

def gameLoop():

    t0 = time.time()

    world = initialize_world()
    player = Player(world.p_obj['player ship'][0])
    
    while not world.game_exit:

        while world.game_over: world.welcome()
              
        player.get_controls(world)

        dt = time.time() - t0
        t0 = time.time()

        world.update(dt)

    pygame.quit()
    quit()

gameLoop()
