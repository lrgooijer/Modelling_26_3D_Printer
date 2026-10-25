import numpy as np
from scipy.integrate import solve_ivp
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
filament_loaded.direction =1

def u_heating(t, x):
    return np.array([0, 0, p.heater_u_max])

def nozzle_heated(t,x):
    return x[6] - e.T_high
nozzle_heated.terminal = True
nozzle_heated.direction = 1


def no_reset(x):
    return x

def reset_tau(x):
    x = x.copy(); x[10] = 0.0 # Reset tau
    return x

def reset_filament_loaded(x):
    x =x.copy(); x[9] = 0.0 # Reset filament distance s+ = 0
    return x


GUARDS = {
    4:[(nozzle_cooled, "nozzle_cooled", reset_tau)],
    5:[(filament_loaded, "filament_loaded", reset_filament_loaded)],
    6:[(nozzle_heated, "nozzle_heated", no_reset)]      
          }

CONTROLLERS = {4: u_cooling, 5:  u_loading, 6: u_heating}

def simulate_hybrid(x0, fsm, t_end):
    t, x= 0.0, x0

    stints = []
    while t < t_end:

        q = fsm.current_state.value
        if q not in CONTROLLERS:
            print(f"state not in controlles")
            break

        crtl = CONTROLLERS[q]
        guards = GUARDS[q]

        sol =  solve_ivp(lambda t,x :system(t, x, crtl(t,x),q),
                            (t, t_end), x, method="Radau",
                            events=[g for g, _, _ in guards], max_step = 1)
        stints.append((sol.t, sol.y, q))

        for i, te in enumerate(sol.t_events):
            if len(te)>0:
                k = i
                break
        _, event_name , reset = guards[k]

        t = sol.t_events[k][0]
        x = reset(sol.y_events[k][0])
        fsm.send(event_name)
    return stints

 
