import numpy as np
from scipy.integrate import solve_ivp
from parameters import Parameters as p, Events as e, Q14 as f, Intial as i, Bounds as b
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

def u_corner_V(t,x):
    u_y = -e.u_corner
    return np.array([u_y, -u_y, p.heater_u_nom])

def u_corner_both(t,x):
    u_x = -e.u_corner
    u_y = -e.u_corner
    u_ml = u_x + u_y
    u_mr = u_x - u_y
    return np.array([u_ml, u_mr, p.heater_u_nom])

def x_pos(x):
    return (p.r_m/2)*(x[0] + x[1])
def y_pos(x):
    return (p.r_m/2)*(x[0] - x[1])

def x_bound_left(t,x):# H,+
    return x_pos(x) - e.threshold_bound
x_bound_left.terminal = True
x_bound_left.direction = 1

def y_bound_left(t,x): # V,+
    return y_pos(x) - e.threshold_bound
y_bound_left.terminal = True
y_bound_left.direction =1

def x_bound_reached(t,x): # H,0
    return x_pos(x)
x_bound_reached.terminal = True
x_bound_reached.direction = -1

def y_bound_reached(t,x): # V,0
    return y_pos(x)
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

def u_move_to_saved_loc(t, x): 
    # PD Control
    e_x = x[11] - x_pos[x] 
    e_y = x[12] - y_pos[x]
    d_x = (p.r_m/2)*(x[2]+x[3])
    d_y = (p.r_m/2)*(x[2]-x[3])

    u_x = e.Kp_po* e_x - e.Kd_pos*d_x
    u_y = e.Kp_po* e_y - e.Kd_pos*d_y

    u_ml = u_x + u_y
    u_mr = u_x - u_y
    return np.array([u_ml, u_mr, p.heater_u_nom])

def at_saved_loc(t,x):
    s_to_saved = np.sqrt((x_pos(x)-x[11])**2-(y_pos(x)-x[12])**2)
    return s_to_saved - e.threshold_bound
at_saved_loc.terminal = True
at_saved_loc.direction = -1


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

#TODO check the reset with the report
GUARDS = {
    0:[(filament_finished, "new_filament_req", reset_save_position),
       (colour_change, "new_colour_req", reset_save_position)], # TODO add colour change, resest not correct
    (2,"q0State"): [(x_bound_reached, "H0", no_reset),
                    (y_bound_reached, "V0", no_reset)],
    (2,"q1State"): [(y_bound_reached, "V0", no_reset),
                    (x_bound_left, "H1", no_reset)],
    (2,"q2State"): [x_bound_reached, "H0", no_reset,
                    y_bound_left, "V1", no_reset],
    1:[(stopped,"stopped", no_reset)],
    3:[(wipe_complete, "wipe_complete", reset_tau)],
    4:[(nozzle_cooled, "nozzle_cooled", reset_tau)],
    5:[(filament_loaded, "filament_loaded", reset_filament_loaded)],
    6:[(nozzle_heated, "nozzle_heated", no_reset)],
    7:[(at_saved_loc, "at_saved_loc", no_reset)]      
          }

CONTROLLERS = {0:u_printing, 1:u_braking,
               (2,"q0State"): u_corner_both,
               (2,"q1State"): u_corner_V,
               (2,"q2State"): u_corner_H,
               3:u_wiping, 4: u_cooling, 
               5:  u_loading, 6: u_heating,
               7: u_move_to_saved_loc
               }

def simulate_hybrid(x0, fsm, t_end):
    q22 = Q22FSM()

    t, x= 0.0, x0

    actions = []
    while t < t_end:

        q = fsm.current_state.value

        if q ==2:
            key = (2,q22.current_state.id)
        else:
            key = q
            
        if key not in CONTROLLERS:
            print(f"state not in controlles")
            break

        crtl = CONTROLLERS[key]
        guards = GUARDS[key]

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

        if event_name in ("V0", "H0", "H1", "V1"):
            q22.send(event_name)
            if q22.current_state.id == "q3State":
                fsm.send("at_wipe_loc")
        else:
            fsm.send(event_name)
            if fsm.current_state.value == 2:
                q22 = Q22FSM() # Reset the corner finding

    return actions

 
if __name__=="__main__":
    fsm = Q21FSM()
    # for event in ["new_filament_req", "stopped"]:
    #     fsm.send(event)

    x_start = 0.15
    y_start = 0.15
    #TODO move this 
    x0 = np.zeros(13)
    x0[0] = (x_start + y_start) / p.r_m  
    x0[1] = (x_start - y_start) / p.r_m
    x0[6] = 220
    x0[7] = 14
    x0[8] = 1
    x0[11] = x_start
    x0[12] = y_start

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
    ax_pos.set_xlim(-0.02,b.xmax+0.02)
    ax_pos.set_ylim(-0.02,b.ymax+0.02)
    ax_wipe.set_title("Position")
    ax_q.set_title("State Tranistions")
    ax_q.set_ylabel("State")
    ax_q.set_xlabel("t [s]")
    plt.show()

