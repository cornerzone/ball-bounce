# import asyncio
import app
import display
import time
# from app_components import clear_background
import ctx
import imu
import math

from events.input import Buttons, BUTTON_TYPES
# from system.patterndisplay.events import *
# from system.eventbus import eventbus



class BallBounceApp(app.App):
    def __init__(self):
        self.button_states = Buttons(self)
        self.speed_factor = 1
        self.accel_factor = 0.002
        self.friction = 0.99
        self.colour = [0,0.5,1]
        self.mode = 1
        self.acc_read = None
        self.center = [0,0]
        self.pos = [0,0]
        self.last_pos = [0,0]
        self.vel = [0,0]
        self.size = 40

        # self.time_update = 0
        # self.time_draw = 0

    def update(self, delta):
        # time_start = time.ticks_us()

        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            self.minimise()
        else:
            self.move(delta)

        if self.button_states.get(BUTTON_TYPES["UP"]):
            self.button_states.clear()
            self.change_mode(1)
        if self.button_states.get(BUTTON_TYPES["DOWN"]):
            self.button_states.clear()
            self.change_mode(-1)
            
        # self.time_update = time.ticks_diff(time.ticks_us(),time_start)                
        return

    def change_mode(self,change):
        self.mode +=change
        if self.mode < 1:
            self.mode = 3
        if self.mode > 3:
            self.mode = 1

        if self.mode == 1:
            self.speed_factor = 1
            self.accel_factor = 0.002
            self.friction = 0.99
            self.colour = [0,0.5,1]
        if self.mode == 2:
            self.speed_factor = 1
            self.accel_factor = 0.01
            self.friction = 0.95
            self.colour = [0.5,1,0]
        if self.mode == 3:
            self.speed_factor = 2
            self.accel_factor = 0.001
            self.friction = 0.995
            self.colour = [1,0,0.5]
        return

    def move(self,delta):
        acc_read = imu.acc_read()
        # acc_read = [0.5,9.0,0.02]
 
        # update velocity
        self.vel[0] += acc_read[1] * delta * self.accel_factor
        self.vel[1] += acc_read[0] * delta * self.accel_factor
        self.vel[0] *= self.friction
        self.vel[1] *= self.friction
        
        # update position
        self.last_pos = self.pos
        self.pos[0] += self.vel[0] * self.speed_factor
        self.pos[1] += self.vel[1] * self.speed_factor
        
        # bounce if needed
        dist = math.sqrt(self.pos[0]**2 + self.pos[1]**2)
        # print(dist)
        if dist > 80:
            v = self.vel
            # get normal vector
            n = [ self.pos[0]/dist, self.pos[1]/dist ]
            # dot product of v and n
            v_n_2 = 2 * ( n[0]*v[0] + n[1]*v[1] )
            v2 =  [ v[0] - v_n_2*n[0] , v[1] - v_n_2*n[1] ]
            self.vel = v2
            # hack: bounce from previous position
            # todo: calculate collision intercept, and reflect from there
            self.pos = self.last_pos
            self.pos[0] += self.vel[0] * self.speed_factor
            self.pos[1] += self.vel[1] * self.speed_factor
        return


    def draw(self, ctx):
        ctx.image_smoothing=0

        ctx.save()
        ctx.rgba(0,0,0,0.1).rectangle(-120,-120,240,240).fill()
        
        ctx.rgb(self.colour[0],self.colour[1],self.colour[2]).arc(self.pos[0], self.pos[1], self.size, 0, math.tau, True).fill()

        ctx.restore()

__app_export__ = BallBounceApp