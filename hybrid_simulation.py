import numpy as np
from scipy.integrate import solve_ivp
from parameters import Parameters as p, Events as e, Q14 as f, Intial as i
from feed_forward import draw_ellipse
import matplotlib.pyplot as plt
from q21_fsm import Q21FSM
from q22_fsm import Q22FSM
from system import system

 

q_21 =Q21FSM()
q_22 =Q22FSM()

def u_printing(t,x):
    w  = 2 * np.pi / f.time_loop # TODO placeholder needs to be square
    return draw_ellipse(t, i.x_center,i.y_center, f.a, f.b, w)

def filament_finished(t,x):
    return x[9] - e.S_max
filament_finished.terminal = True
filament_finished.direction = 1

def colour_change(t,x):
    return t - e.t_C
colour_change.terminal = True
colour_change.direction = 1

def u_braking(t, x):
    d_x = (p.r_m/2)*(x[2]+x[3])
    d_y = (p.r_m/2)*(x[2]-x[3])
    u_x = -e.Kd_brake * d_x
    u_y = -e.Kd_brake * d_y
    u_ml = u_x + u_y
    u_mr = u_x - u_y
    return np.array([u_ml, u_mr, p.heater_u_nom])

def stopped(t,x):
    d_theta = np.sqrt((x[2]**2)+(x[3]**2))
    return d_theta - e.cap_dtheta
stopped.terminal = True
stopped.direction = -1

def u_corner_H(t,x):
    u_x = -e.u_corner
    return np.array([u_x, u_x, p.heater_u_nom])

def u_corner_H(t,x):
    u_y = -e.u_corner
    return np.array([u_y, -u_y, p.heater_u_nom])

def x_bound_reached(t,x):
    x = (p.r_m/2)*(x[0] + x[1])
    return x
x_bound_reached.terminal = True
x_bound_reached.direction = -1

def y_bound_reached(t,x):
    y = (p.r_m/2)*(x[0] - x[1])
    return y
y_bound_reached.terminal = True
y_bound_reached.direction = -1

def u_wiping(t, x):
    u_y = e.u_wipe * np.sin(e.w_wipe*x[10])
    u_ml = u_y # only y movement so u_x = 0
    u_mr = - u_y # only y movement so u_x = 0
    return np.array([u_ml, u_mr, p.heater_u_nom])

def wipe_complete(t, x):
    return x[10] - e.dt_wipe
wipe_complete.terminal = True
wipe_complete.direction = 1

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

def reset_save_position(x):
    x = x.copy()
    x[11]= (p.r_m/2)*(x[0]+x[1]) # x_s
    x[12]= (p.r_m/2)*(x[0]-x[1]) #y_s
    return x

def no_reset(x):
    return x

def reset_tau(x):
    x = x.copy(); x[10] = 0.0 # Reset tau
    return x

def reset_filament_loaded(x):
    x =x.copy(); x[9] = 0.0 # Reset filament distance s+ = 0
    return x


GUARDS = {
    0:[(filament_finished, "new_filament_req", reset_save_position),
       (colour_change, "new_colour_req", reset_save_position)], # TODO add colour change, resest not correct
    1:[(stopped,"stopped", no_reset)],
    3:[(wipe_complete, "wipe_complete", reset_tau)],
    4:[(nozzle_cooled, "nozzle_cooled", reset_tau)],
    5:[(filament_loaded, "filament_loaded", reset_filament_loaded)],
    6:[(nozzle_heated, "nozzle_heated", no_reset)]      
          }

CONTROLLERS = {0:u_printing, 1:u_braking, 3:u_wiping, 4: u_cooling, 5:  u_loading, 6: u_heating}

def simulate_hybrid(x0, fsm, t_end):
    t, x= 0.0, x0

    actions = []
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
        actions.append((sol.t, sol.y, q))

        for i, te in enumerate(sol.t_events):
            if len(te)>0:
                k = i
                break
        _, event_name , reset = guards[k]

        t = sol.t_events[k][0]
        x = reset(sol.y_events[k][0])
        fsm.send(event_name)
    return actions

 
if __name__=="__main__":
    fsm = Q21FSM()
    for event in ["new_filament_req", "stopped", "at_wipe_loc"]:
        fsm.send(event)

    x0 = np.zeros(13)
    x0[6] = 220
    x0[7] = 14
    x0[8] = 1

    actions = simulate_hybrid(x0, fsm, t_end=2000)
    fig, ((ax_T, ax_wipe), (ax_q, ax_pos)) = plt.subplots(2,2, figsize=(14,10))
    for t_act, x_act, q in actions:
        x_pos = (p.r_m/2)* (x_act[0] + x_act[1])
        y_pos = (p.r_m/2)* (x_act[0] - x_act[1])
        ax_wipe.plot(t_act, y_pos)
        ax_T.plot(t_act, x_act[6])
        ax_pos.plot(x_pos,y_pos)
        ax_q.step(t_act, np.full_like(t_act, q), where="post")
    ax_T.axhline(e.T_low, ls="--", c="k")
    # ax_T.axhline(e.T_high, ls="--", c="k")
    ax_T.set_title("Nozzle temprature")
    ax_T.set_ylabel("T nozzle [°C]")
    ax_wipe.set_title("Wiping")
    ax_wipe.set_ylabel("y [m]")
    ax_wipe.set_xlabel("t [s]")
    ax_pos.set_ylabel("y [m]")
    ax_pos.set_xlabel("x [m]")
    ax_wipe.set_title("Position")
    ax_q.set_title("State Tranistions")
    ax_q.set_ylabel("State")
    ax_q.set_xlabel("t [s]")
    plt.show()

