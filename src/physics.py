from math import *
import numpy as np
import pygame

class PhysicsObject():
    # All physics terms are represented by their common letters. All vector quantities follow
    # standard convention (X[0] = X, X[1] = y, F[0] = F_X, F[1] = F_y, etc.)

    default_params = {
        'F' : np.array([0,0]),
        'a' : np.array([0,0]),
        'X' : np.array([0,0]),
        'v' : np.array([0,0]),
        'p' : np.array([0,0]),
            
        'tau' : 0,
        'alpha' : 0,
        'omega' : 0,
        'theta' : 0,
        'L' : 0,
            
        'm' : 20000,
        'I' : 850000,

        'rel_X_cm' : np.array([0,0]),
        'orientation' : 0,
        'size' : 32,
        'sprites' : {},
        'alpha_buffer' : 9
    }

    def __init__(self, **kwargs):

        for var in self.default_params:
            exec('self.%s = kwargs.pop("%s", self.default_params["%s"])' % (var,var,var))
            
        self.I = (self.m * self.size**2) / 6
        self.X_cm = self.X + self.rel_X_cm

        if 'default' not in self.sprites.keys():
            self.sprites = {'default' : pygame.image.load("graphics/" + type(self).__name__ + ".png")}
        
        self.current_sprite = self.sprites['default']
        self.size = np.asarray(self.current_sprite.get_size()) - self.alpha_buffer

    def add_params(self, **kwargs):
        for new_param, default in kwargs.items():
            self.default_params[str(new_param)] = default

    def change_F(self, dF):
        self.F = self.F + dF
        
    def change_tau(self, dtau):
        self.tau = self.tau + dtau
        
    def update_physics(self, dt):
        self.alpha = self.tau / self.I
        self.omega = self.omega + self.alpha * dt
        self.theta = (self.theta + self.omega * dt) % (2*pi)

        self.a = self.F / self.m
        self.v = self.v + self.a * dt
        self.X_cm = self.X_cm + self.v * dt
        
        #Distance and Angle relative to X_cm
        distance = hypot(self.rel_X_cm[1], self.rel_X_cm[0])
        theta0 = atan2(self.rel_X_cm[1], self.rel_X_cm[0])
        
        self.X[0] = self.X_cm[0] - distance*cos(self.theta - theta0)
        self.X[1] = self.X_cm[1] + distance*sin(self.theta - theta0)

        self.F = np.array([0,0])
        self.tau = 0

class Module(PhysicsObject):

    module_orientation = 0

    def __init__(self, **kwargs):
        
        self.add_params(module_type="Hull", health=0)
        super().__init__(**kwargs)

        self.sprites['default'] = pygame.image.load("graphics/" + type(self).__name__ + ".png")
                  
        self.following_mouse = False
        

    def follow_mouse(self, mouse_position):
        self.X = mouse_position
        self.X_cm = self.X

    def follow(self, point, orientation, target):
        sized_position = np.multiply(point, self.size)
        
        distance = hypot(target.rel_X_cm[1] - sized_position[1], target.rel_X_cm[0] - sized_position[0])
        theta0 = atan2(target.rel_X_cm[1] - sized_position[1], target.rel_X_cm[0] - sized_position[0])

        self.X[0] = target.X_cm[0] - distance*cos(target.theta - theta0)
        self.X[1] = target.X_cm[1] + distance*sin(target.theta - theta0)
        self.theta = target.theta + orientation * (pi/2)

class GravitationalBody(PhysicsObject):

    G = 6.67408 * 10**-11

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

    def gravitate(self, target):
        r_squared = (self.X_cm[0] - target.X_cm[0])**2 + (self.X_cm[1] - target.X_cm[1])**2
        r_hat = ((self.X_cm - target.X_cm) / sqrt(r_squared))
        F_G = self.G * ((target.m * self.m) / r_squared) * r_hat
        target.change_F(F_G)

class AttachedModule(Module):

    def __init__(self, **kwargs):
        
        self.add_params(module_coordinates=[0,0], module_orientation=0, core_module=self)
        super().__init__(**kwargs)

class Hull(AttachedModule):

    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        
class Thruster(AttachedModule):
                                    
    def __init__(self, **kwargs):
        
        self.add_params(F_max=2000000, tau_max=0)
        super().__init__(**kwargs)

        self.sprites['on'] = pygame.image.load("graphics/" + type(self).__name__ + "_on.png")
        
        if self.module_orientation == 0:
            self.F_max = np.array([self.F_max, 0])
        elif self.module_orientation == 1:
            self.F_max = np.array([0, -self.F_max])
        elif self.module_orientation == 2:
            self.F_max = np.array([-self.F_max, 0])
        elif self.module_orientation == 3:
            self.F_max = np.array([0, self.F_max])
        
        self.start_thruster = False
        self.stop_thruster = False
            
    def thruster(self):
        if self.stop_thruster == True:
            
            self.stop_thruster = False
            self.start_thruster = False

            self.current_sprite = self.sprites['default']
            
        elif self.start_thruster == True:
            self.core_module.net_turn += self.tau_max
            self.core_module.net_thrust += self.F_max
            
            self.current_sprite = self.sprites['on']

class Ship(Thruster):
                                    
    def __init__(self, **kwargs):

        self.add_params(surrounding_points = [[1,0],[0,1],[-1,0],[0,-1]], attached_modules=[self])
        super().__init__(**kwargs)

        #Here are replacement variables to determine mass of the whole ship.
        self.ship_m = self.m
        self.ship_I = self.I
        self.ship_F_max = self.F_max
        self.ship_rel_X_cm = np.array(self.rel_X_cm)

        #These are just some params for the core module itself, separate from its attached modules.
        self.core_m = self.m
        self.core_I = self.I
        self.core_F_max = np.array(self.F_max)
        self.core_rel_X_cm = np.array(self.rel_X_cm)
        self.core_tau_max = -np.cross(self.core_F_max, self.rel_X_cm)

        #These params are for determining whether the ship's thrusters are on or off.
        self.actions = ['forward','left','backward','right','rotate_positive','rotate_negative']
        
        for action in self.actions:
            exec('self.start_' + action + ' = False')
            exec('self.stop_' + action + ' = False')
        
        #These params are for consolidating the components of net torque and force from the ship.
        self.net_turn = 0
        self.net_thrust = np.array([0,0])
        
    def reset_params(self):
        old_rel_X_cm = np.array(self.rel_X_cm)
        
        self.ship_m = 0
        self.ship_tau_max = 0
        self.ship_F_max = np.array([0,0])
        self.rel_X_cm = np.array([0,0])
        
        #Recalculating ship's mass
        for module in self.attached_modules:
            self.ship_m += module.m
            
        #Recaclulating ship's center of mass
        for module in self.attached_modules:
            self.rel_X_cm[0] += (1 / self.ship_m)*(module.m * (module.module_coordinates[0]*module.size[0]))
            self.rel_X_cm[1] += (1 / self.ship_m)*(module.m * (module.module_coordinates[1]*module.size[0]))

        #This makes it so that the ship doesn't jump once the center of mass changes
        deltarel_X_cm = np.add(self.rel_X_cm, -old_rel_X_cm)
        self.X_cm = self.X_cm + deltarel_X_cm

        self.I = self.core_I

        #Recalculating ship's moment of inertia using parallel-axis theorem
        for module in self.attached_modules:
            d = hypot((module.module_coordinates[0]*module.size[0]) - self.rel_X_cm[0],
                           (module.module_coordinates[1]*module.size[0]) - self.rel_X_cm[1])
            self.I += module.I + module.m*d**2
        self.I -= self.core_I

        #Recalculating each module's torque
        for module in self.attached_modules:
            if type(module).__name__ == "Thruster" or type(module).__name__ == "Ship":
                module.tau_max = -np.cross(module.F_max, np.add(self.rel_X_cm, -np.multiply(module.module_coordinates,module.size[0])))

    def controls(self):
        self.reset_thrust()
        
        #Forward
        if self.stop_forward == True:
            for module in self.attached_modules:
                module.stop_thruster = True

            self.start_forward = False
            self.stop_forward = False
        
        elif self.start_forward == True:
            for module in self.attached_modules:
                if (type(module).__name__ == "Thruster" or type(module).__name__ == "Ship") and module.F_max[0] > 0:
                    module.start_thruster = True
    
        #Left
        if self.stop_left == True:
            for module in self.attached_modules:
                module.stop_thruster = True

            self.start_left = False
            self.stop_left = False
        
        elif self.start_left == True:
            for module in self.attached_modules:
                if (type(module).__name__ == "Thruster" or type(module).__name__ == "Ship") and module.F_max[1] < 0:
                    module.start_thruster = True

        #Backward
        if self.stop_backward == True:
            for module in self.attached_modules:
                module.stop_thruster = True

            self.start_backward = False
            self.stop_backward = False
        
        elif self.start_backward == True:
            for module in self.attached_modules:
                if (type(module).__name__ == "Thruster" or type(module).__name__ == "Ship") and module.F_max[0] < 0:
                    module.start_thruster = True

        #Right
        if self.stop_right == True:
            for module in self.attached_modules:
                module.stop_thruster = True

            self.start_right = False
            self.stop_right = False
        
        elif self.start_right == True:
            for module in self.attached_modules:
                if (type(module).__name__ == "Thruster" or type(module).__name__ == "Ship") and module.F_max[1] > 0:
                    module.start_thruster = True

        #Rotate Positive
        if self.stop_rotate_positive == True:
            for module in self.attached_modules:
                module.stop_thruster = True

            self.start_rotate_positive = False
            self.stop_rotate_positive = False
        
        elif self.start_rotate_positive == True:
            for module in self.attached_modules:
                if (type(module).__name__ == "Thruster" or type(module).__name__ == "Ship") and module.tau_max > 0.1:
                    module.start_thruster = True
                    
        #Rotate Negative
        if self.stop_rotate_negative == True:
            for module in self.attached_modules:
                module.stop_thruster = True

            self.start_rotate_negative = False
            self.stop_rotate_negative = False
            
        elif self.start_rotate_negative == True:
            for module in self.attached_modules:
                if (type(module).__name__ == "Thruster" or type(module).__name__ == "Ship") and module.tau_max < -0.1:
                    module.start_thruster = True

        for module in self.attached_modules:
            if type(module).__name__ == "Thruster" or type(module).__name__ == "Ship":
                module.thruster()

        self.apply_thrust()

    def reset_thrust(self):
        #This function removes the previous force so that it may be recalculated and added properly as a new component.
        self.net_turn = 0
        self.net_thrust = np.array([0,0])

    def apply_thrust(self):
        #Rotate Thrust
        self.net_thrust = np.array([self.net_thrust[0] * cos(self.theta) + self.net_thrust[1] * sin(self.theta),
                                   -self.net_thrust[0] * sin(self.theta) + self.net_thrust[1] * cos(self.theta)])

        #Apply Thrust to Ship
        self.change_tau(self.net_turn)
        self.change_F(self.net_thrust)

    '''
    def move_in_circle(self):
        S = hypot(self.v[0], self.v[1])
        self.F = [(-self.v[1] * self.F_max[0]) / S, (self.v[0] * self.F_max[0]) / S]
        
    def brake(self):
        speed = hypot(self.v[0], self.v[1])
        reverse_direction = -np.array(np.multiply(self.v, 1/speed))
        desired_angle = atan2(reverse_direction[1], reverse_direction[0])
        angle = radians(self.theta)

        if 0.05 <= desired_angle - self.theta < pi:
            self.start_rotate_negative = True
        elif pi <= desired_angle - self.theta <= 2*pi - 0.05:
            self.start_rotate_positive = True
    '''

class Enemy(Ship):
                                    
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)

    def run_away(self, threat):
        run_F = 0
        d = hypot(self.X[0] - threat.X[0], self.X[1] - threat.X[1])
        if d != 0 and d < 300:
            angle = atan((self.X[1] - threat.X[1])/(self.X[0] - threat.X[0]))
            run_F = 500000 / d
            if run_F * cos(angle) > self.F_max[0]:
                scale = self.F_max[0] / run_F * cos(angle)
                run_F = hypot(self.F_max, scale * run_F * sin(angle))
            if run_F * sin(angle) > self.F_max[0]:
                scale = self.F_max[0] / run_F*sin(angle)
                run_F = hypot(scale * run_F * cos(angle), self.F_max[0])
                
            if self.X[0] > threat.X[0]:
                self.F = [run_F * cos(angle), run_F * sin(angle)]
            if self.X[0] <= threat.X[0]:
                self.F = [-run_F * cos(angle), -run_F * sin(angle)]
        elif d == 0:
            self.F = [self.F_max[0], self.F_max]
        else:
            self.F = [0,0]
