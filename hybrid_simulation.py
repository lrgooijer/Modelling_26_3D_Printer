import numpy as np

from parameters import Parameters as p, Events as e

from q21_fsm import Q21FSM
from q22_fsm import Q22FSM
from system import system
 

q_21 =Q21FSM()
q_22 =Q22FSM()

def u_cooling(t,x):
    return np.array([0,0,0])

def nozzle_cooled(t,x):
    return x[6] - e.T_low
nozzle_cooled.terminal =True
nozzle_cooled.direction = -1

def u_loading(t, x):
    return np.array([0,0,0])

def filament_loaded(t,x):
    return x[10] - e.dt_load
filament_loaded.terminal =True
filament_loaded.direction =-1

def u_heating(t, x):
    return np.array([0, 0, p.heater_u_max])

def nozzle_heated(t,x):
    return x[6] - e.T_high
nozzle_heated.terminal = True
nozzle_heated.direction = -1


def no_reset(x):
    return x
def reset_tau():
    x = x.copy(); x[10] = 0.0 # Reset tau
    return x

def resest_filament_loaded():
    x =x.copy(); x[9] = 0.0 # Reset filament distance s+ = 0
    return x


GUARDS = {
    4:[(nozzle_cooled, "nozzle_cooled", reset_tau)],
    5:[(filament_loaded, "filament_loaded", resest_filament_loaded)],
    6:[(nozzle_heated, "nozzle_heated", no_reset)]      
          }

CONTROLLERS = {4: u_cooling, 5:  u_loading, 6: u_heating}



# def fsm_input_selector(t,x,q):
#     u_x = 0
#     u_y = 0

#     if q == 0:
#         return draw_ellipse(t,)
        
#     elif q in (2,3,7): # move to wipe, wiping or saved location
#         if q == 2: # Finding wipe corner # TODO prob intiate the fsm of 2.2 here 
#             u_x = 
#             u_y =
#         if q == 3: # Wiping, move up and down
#             return draw_ellipse(t, w.x_wipe, w.y_wipe, w.a_wipe, w.b_wipe) 
#         if q == 7: # move to saved
#             u_x = 
#             u_y = 
#     elif q == 6: # Heating
#         u_x = 0
#         u_y = 0
#         u_n = #maximum

#     elif q in (1,4):
#         u_x = 0
#         u_y = 0
#         u_n = 0
