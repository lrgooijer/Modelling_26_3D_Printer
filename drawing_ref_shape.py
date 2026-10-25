import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from scipy.integrate import solve_ivp

from main_simulation import system
from parameters import Parameters as p, Intial as i, Bounds


Jtot = p.Jmotor +(1/2)*p.m*(p.r_m**2)
b_plus = p.fric_roll + ((p.r_m**2)/4) * (p.fric_lx + p.fric_ly) 
b_min = ((p.r_m**2)/4) * (p.fric_lx - p.fric_ly)

b_x = b_plus +  b_min
b_y = b_plus -  b_min

time_loop = 200
a  = 0.06
b = 0.04
w= 2 * np.pi / time_loop


def reference_ellipse(t, x_c, y_c, a, b, w):
    
    x_ref = x_c + a * np.cos(w*t)
    d_x_ref = -a * w * np.sin(w*t) 
    dd_x_ref =  -a * w**2 * np.cos(w*t) 
    ddd_x_ref =  a * w**3 * np.sin(w*t)

    y_ref = y_c + b * np.sin(w*t)
    d_y_ref = b * w * np.cos(w*t) 
    dd_y_ref =  -b * w**2 * np.sin(w*t) 
    ddd_y_ref =  -b * w**3 * np.cos(w*t)

    return (x_ref,d_x_ref,dd_x_ref,ddd_x_ref), (y_ref,d_y_ref,dd_y_ref, ddd_y_ref)  

def input_i_z(d_z_ref, dd_z_ref, bz):
    input_i_z = (Jtot * dd_z_ref + bz * d_z_ref) / (p.r_m * p.Km) 
    return input_i_z

(x0, d_x0, dd_x0, ddd_x0), (y0, d_y0, dd_y0, ddd_y0) = reference_ellipse(0,i.x_center, i.y_center, a, b, w)

i_x0 = input_i_z(d_x0, dd_x0, b_x)
i_y0  = input_i_z(d_y0, dd_y0, b_y)

state0 = np.zeros(13)
state0[0]= (x0 + y0) / p.r_m # theta_l invert the kinematics
state0[1]= (x0 - y0) / p.r_m # theta_r invert the kinematics
state0[2] = (d_x0 + d_y0) / p.r_m #dtheta_l
state0[3] = (d_x0 - d_y0) / p.r_m #dtheta_r
state0[4] = i_x0 + i_y0 #i_l
state0[5] = i_x0 - i_y0 #i_r
state0[6] = p.t_env     # nozzle temprature TODO maybe jsut start it at 220


def input_u_z(t, d_z_ref, dd_z_ref, ddd_z_ref, b_z):
    input_u_z = (p.Lm * Jtot/ (p.r_m* p.Km)) *ddd_z_ref +((p.Lm * b_z + p.R_motor * Jtot)/(p.r_m*p.Km))*dd_z_ref + (p.R_motor * b_z / (p.r_m * p.Km) + p.Km / p.r_m) * d_z_ref
    return input_u_z

def draw_ellipse( t ,x_c, y_c, a, b, w, u_n = 0): # TODO u_n=0 is placeholder

    (x_ref,d_x_ref,dd_x_ref,ddd_x_ref), (y_ref,d_y_ref,dd_y_ref, ddd_y_ref) = reference_ellipse(t, x_c, y_c, a, b, w)

    u_x = input_u_z(t, d_x_ref,dd_x_ref,ddd_x_ref, b_x)
    u_y = input_u_z(t, d_y_ref,dd_y_ref, ddd_y_ref, b_y)

    u_ml = u_x + u_y
    u_mr = u_x - u_y

    u_inputs_ellipse = np.array([u_ml, u_mr, u_n])
    return u_inputs_ellipse


t_eval =np.linspace(0,time_loop,1000)
q = 0 # TODO move this
ellipse_sol = solve_ivp(lambda t,s:system(t, s, draw_ellipse(t, i.x_center, i.y_center, a, b, w, u_n = 0),q),
                        (0,time_loop), state0, method="Radau",t_eval=t_eval)

x_sim = (p.r_m / 2) * (ellipse_sol.y[0] + ellipse_sol.y[1])
y_sim = (p.r_m / 2) * (ellipse_sol.y[0] - ellipse_sol.y[1])

u_inputs = np.array([draw_ellipse(t,i.x_center,i.y_center,a,b,w) for t in ellipse_sol.t])
u_ml_sim, u_mr_sim  = u_inputs[:,0], u_inputs[:,1]

u_max =np.abs(u_inputs[:,:2]).max()
t_sim = ellipse_sol.t

(x_ref, *_), (y_ref, *_) = reference_ellipse(ellipse_sol.t, i.x_center, i.y_center, a, b, w)


if __name__ == "__main__":

    fig, (ax_path, ax_u) = plt.subplots(1,2, figsize=(12,5))
    ax_path.plot(x_ref, y_ref, "k--")
    line_path, = ax_path.plot([], [], "r-")
    ax_path.set_xlabel("x[m]")
    ax_path.set_ylabel("y[m]")
    ax_path.set_title('Tool head path')
    ax_path.axis('equal')
    ax_path.set_xlim(0,Bounds.xmax)
    ax_path.set_ylim(0, Bounds.ymax)


    line_ml, = ax_u.plot([],[], label="u_ml")
    line_mr, = ax_u.plot([],[], label="u_mr")
    ax_u.set_xlabel("t[s]")
    ax_u.set_ylabel("Voltage[V]")
    ax_u.set_ylim(-1.2*u_max, 1.2*u_max)
    ax_u.set_xlim(t_sim[0], t_sim[-1])
    ax_u.set_title("Motor Voltages")
    ax_u.legend(loc="upper right")

    step = 5
    def update(frame):
        n = frame * step
        line_path.set_data([x_sim[:n+1], y_sim[:n+1]])
        line_ml.set_data(t_sim[:n+1], u_ml_sim[:n+1])
        line_mr.set_data(t_sim[:n+1], u_mr_sim[:n+1])
        return line_path, line_ml, line_mr

    frames = len(ellipse_sol.t) // step
    simulation = animation.FuncAnimation(fig, update,frames=frames, interval=40, blit=True)   
    plt.show()

