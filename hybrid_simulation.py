import numpy as np
from scipy.integrate import solve_ivp
from parameters import (Parameters as p, Events as e, Q14 as f,
                        Intial as i, Bounds as b, Clover as c,Square as sq)
from feed_forward import (draw_ellipse, reference_ellipse, 
                          intial_state, draw_clover, reference_clover)
import matplotlib.pyplot as plt
from q21_fsm import Q21FSM
from q22_fsm import Q22FSM
from q32_fsm import Q32_SQUARE_FSM
from system import system

SHAPE = "square" # "clover"

SQUARE_DIR = {"q0State":(+1,+1), "q1State":(+1,-1), 
              "q2State":(-1, -1), "q3State":(-1, +1)}


def u_drawing_square(t, x, theta_ref):
    e_theta_l = theta_ref[0] - x[0]
    e_theta_r = theta_ref[1] - x[1]

    u_ml = e.Kp_pos*e_theta_l  - e.Kd_pos*x[2]
    u_mr = e.Kp_pos* e_theta_r - e.Kd_pos*x[3]
    return np.array([u_ml, u_mr, p.heater_u_nom])

def square_corner_reached(t,x,theta_ref):
    offset_theta_l = abs(x[0]-theta_ref[0])
    offset_theta_r = abs(x[1]-theta_ref[1])
    vel_motors = np.sqrt(x[2]**2 + x[3]**2)
    return max(offset_theta_l -e.threshold_bound_theta,
               offset_theta_r - e.threshold_bound_theta,
               vel_motors- e.threshold_bound_omega)
def make_corner_guard(theta_ref):
    def corner_guard(t,x):
        return square_corner_reached(t,x,theta_ref)
    corner_guard.terminal =True
    corner_guard.direction = -1
    return corner_guard

def u_printing(t,x):
    w  = 2 * np.pi / f.time_loop
    #return draw_ellipse (t, i.x_center,i.y_center, f.a, f.b, w)
    return draw_clover(t, i.x_center,i.y_center, c.a,c.b, w)

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
    e_x = x[11] - x_pos(x)
    e_y = x[12] - y_pos(x)
    d_x = (p.r_m/2)*(x[2]+x[3])
    d_y = (p.r_m/2)*(x[2]-x[3])

    u_x = e.Kp_pos* e_x - e.Kd_pos*d_x
    u_y = e.Kp_pos* e_y - e.Kd_pos*d_y

    u_ml = u_x + u_y
    u_mr = u_x - u_y
    return np.array([u_ml, u_mr, p.heater_u_nom])

def at_saved_loc(t,x):
    s_to_saved = np.sqrt((x_pos(x)-x[11])**2 + (y_pos(x)-x[12])**2)
    return s_to_saved - e.threshold_saved_loc
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
    x =x.copy() 
    x[9] = 0.0 # Reset filament distance s+ = 0
    x[10] = 0.0 # Reset tau
    return x

#TODO check the reset with the report
GUARDS = {
    0:[(filament_finished, "new_filament_req", reset_save_position),
       (colour_change, "new_colour_req", reset_save_position)], # TODO add colour change, resest not correct
    (2,"q0State"): [(x_bound_reached, "H0", no_reset),
                    (y_bound_reached, "V0", no_reset)],
    (2,"q1State"): [(y_bound_reached, "V0", no_reset),
                    (x_bound_left, "H1", no_reset)],
    (2,"q2State"): [(x_bound_reached, "H0", no_reset),
                    (y_bound_left, "V1", no_reset)],
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

def time_shift(t,x,shift):
    return u_printing(t-shift, x) 


def simulate_hybrid(x0, fsm, t_end):
    q22 = Q22FSM()

    t, x= 0.0, x0
    t_shift = 0.0
    t_stop = 0.0

    q32 = Q32_SQUARE_FSM()
    theta_ref = None
    dtheta = sq.side_length/p.r_m # dtheta based on L_square

    actions = []
    while t < t_end:
        q = fsm.current_state.value
        if q == 2:
            key = (2,q22.current_state.id)
        else:
            key = q
        if key not in CONTROLLERS:
            print(f"state not in controllers")
            break
        
        crtl = CONTROLLERS[key]
        guards = GUARDS[key]

        if key == 0:
            if SHAPE == "square":
                square_corner = q32.current_state.id
                if square_corner != "q4State":
                    if theta_ref is None:
                        in_l, in_r = SQUARE_DIR[square_corner]
                        theta_ref = (x[0] +in_l*dtheta, x[1] + in_r*dtheta)
                    guards = GUARDS[0] + [(make_corner_guard(theta_ref), "corner", no_reset)]
                crtl = lambda t, x, ref=theta_ref :u_drawing_square(t,x, ref)
            else:
                crtl = lambda t, x: time_shift(t, x, t_shift)

        sol =  solve_ivp(lambda t,x :system(t, x, crtl(t,x),q),
                            (t, t_end), x, method="Radau",
                            events=[g for g, _, _ in guards], max_step = 1)
        actions.append((sol.t, sol.y, q))

        for i, te in enumerate(sol.t_events):
            if len(te)>0:
                k = i
                break
        if sol.status != 1:
            print(f"no event in state {key}")
            break

        _, event_name , reset = guards[k]

        t = sol.t_events[k][0]
        x = reset(sol.y_events[k][0])

        
        if event_name in ("new_filament_req", "new_colour_req"):
            t_stop = t

        if event_name == "at_saved_loc":
            t_shift += t - t_stop

        if event_name == "corner":
            q32.send(f"event{int(square_corner[1])+1}")
            if q32.current_state.id != "q4State":
                theta_ref = None # Reset the theta_ref

        elif event_name in ("V0", "H0", "H1", "V1"):
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

    w = 2*np.pi / f.time_loop
    #x_ref, y_ref = reference_ellipse(0, i.x_center, i.y_center, f.a, f.b, w)
    x_ref, y_ref = reference_clover(0, i.x_center, i.y_center, c.a, c.b, w)    
    x0 = intial_state(x_ref, y_ref)
    if SHAPE == "square":
        x0 = np.zeros(13) #TODO is this correct, cant find it atm
        x0[0] = (sq.y_start + sq.x_start)/p.r_m
        x0[1] = (sq.y_start - sq.x_start)/p.r_m
        x0[6] = 220
    x0[7] = 14
    x0[8] = 1



    actions = simulate_hybrid(x0, fsm, t_end=1500)
    fig, ((ax_T, ax_wipe), (ax_q, ax_pos)) = plt.subplots(2,2, figsize=(14,12))
    for t_act, x_act, q in actions:
        x_pos_plot = (p.r_m/2)* (x_act[0] + x_act[1])
        y_pos_plot = (p.r_m/2)* (x_act[0] - x_act[1])
        ax_wipe.plot(t_act, y_pos_plot)
        ax_T.plot(t_act, x_act[6])
        ax_pos.plot(x_pos_plot,y_pos_plot)
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
    ax_pos.set_title("Position")
    ax_wipe.set_title("Y-Coordinate")
    ax_q.set_title("State Tranistions")
    ax_q.set_ylabel("State")
    ax_q.set_xlabel("t [s]")
    plt.show()

