import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from scipy.integrate import solve_ivp
from feed_forward import draw_ellipse, reference_ellipse, intial_state, reference_clover, draw_clover
from system import system
from parameters import Parameters as p, Intial as i, Bounds, Q14 as f


def simulate_ellipse(a,b, time_loop, x_c, y_c, n_points):
    w = 2 * np.pi / time_loop

    x_ref, y_ref = reference_ellipse(0, x_c, y_c, a, b, w)
    state0 = intial_state(x_ref, y_ref)

    t_eval =np.linspace(0,time_loop,n_points)
    q = 0
    ellipse_sol = solve_ivp(lambda t,s:system(t, s, draw_ellipse(t, x_c, y_c, a, b, w, u_n = 0),q),
                            (0,time_loop), state0, method="Radau",t_eval=t_eval)

    x_sim = (p.r_m / 2) * (ellipse_sol.y[0] + ellipse_sol.y[1])
    y_sim = (p.r_m / 2) * (ellipse_sol.y[0] - ellipse_sol.y[1])

    u_inputs = np.array([draw_ellipse(t,x_c ,y_c ,a,b,w) for t in ellipse_sol.t])

    return ellipse_sol, x_sim, y_sim, u_inputs, w

def simulate_clover(a,b, time_loop, x_c, y_c, n_points):
    w = 2 * np.pi / time_loop

    x_ref, y_ref = reference_clover(0, x_c, y_c, a, b, w)
    state0 = intial_state(x_ref, y_ref)

    t_eval =np.linspace(0,time_loop,n_points)
    q = 0
    ellipse_sol = solve_ivp(lambda t,s:system(t, s, draw_clover(t, x_c, y_c, a, b, w, u_n = 0),q),
                            (0,time_loop), state0, method="Radau",t_eval=t_eval)

    x_sim = (p.r_m / 2) * (ellipse_sol.y[0] + ellipse_sol.y[1])
    y_sim = (p.r_m / 2) * (ellipse_sol.y[0] - ellipse_sol.y[1])

    u_inputs = np.array([draw_clover(t,x_c ,y_c ,a,b,w) for t in ellipse_sol.t])

    return ellipse_sol, x_sim, y_sim, u_inputs, w

if __name__ == "__main__":
    ellipse_sol, x_sim, y_sim, u_inputs, w = simulate_ellipse(a=f.a, b=f.b,time_loop=f.time_loop,
                                                            x_c=i.x_center, y_c=i.y_center, n_points=1000)

    t_sim = ellipse_sol.t

    u_ml_sim, u_mr_sim  = u_inputs[:,0], u_inputs[:,1]
    u_max =np.abs(u_inputs[:,:2]).max()

    (x_ref, *_), (y_ref, *_) = reference_ellipse(t_sim, i.x_center, i.y_center, f.a,f.b, w)

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

