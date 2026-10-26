import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from scipy.integrate import solve_ivp
from feed_forward import draw_ellipse, reference_ellipse, intial_state, reference_clover, draw_clover
from system import system
from parameters import Parameters as p, Intial as i, Bounds, Q14 as f, Clover as c


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
    c_w = 2 * np.pi / time_loop

    x_ref, y_ref = reference_clover(0, x_c, y_c, a, b, w)
    state0 = intial_state(x_ref, y_ref)

    t_eval =np.linspace(0,time_loop,n_points)
    q = 0
    clover_sol = solve_ivp(lambda t,s:system(t, s, draw_clover(t, x_c, y_c, a, b, w, u_n = 0),q),
                            (0,time_loop), state0, method="Radau",t_eval=t_eval)

    c_x_sim = (p.r_m / 2) * (clover_sol.y[0] + clover_sol.y[1])
    c_y_sim = (p.r_m / 2) * (clover_sol.y[0] - clover_sol.y[1])

    c_u_inputs = np.array([draw_clover(t,x_c ,y_c ,a,b,w) for t in clover_sol.t])

    return clover_sol, c_x_sim, c_y_sim, c_u_inputs, c_w

if __name__ == "__main__":
    ellipse_sol, x_sim, y_sim, u_inputs, w = simulate_ellipse(a=f.a, b=f.b,time_loop=f.time_loop,
                                                            x_c=i.x_center, y_c=i.y_center, n_points=1000)

    t_sim = ellipse_sol.t

    u_ml_sim, u_mr_sim  = u_inputs[:,0], u_inputs[:,1]
    u_max =np.abs(u_inputs[:,:2]).max()

    (x_ref, *_), (y_ref, *_) = reference_ellipse(t_sim, i.x_center, i.y_center, f.a,f.b, w)

    clover_sol, c_x_sim, c_y_sim, c_u_inputs, c_w = simulate_clover(a=c.a, b=c.b,time_loop=c.time_loop,
                                                                x_c=i.x_center, y_c=i.y_center, n_points=1000)

    c_t_sim = clover_sol.t

    c_u_ml_sim, c_u_mr_sim  = c_u_inputs[:,0], u_inputs[:,1]
    c_u_max =np.abs(c_u_inputs[:,:2]).max()

    (c_x_ref, *_), (c_y_ref, *_) = reference_clover(t_sim, i.x_center, i.y_center, c.a,c.b, c_w)

    fig, ((ax_path, ax_u),(ax_clover,ax_clover_u)) = plt.subplots(2,2, figsize=(14,10))
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

    ax_clover.plot(c_x_ref, c_y_ref, "k--")
    line_clover, = ax_clover.plot([], [], "r-")
    ax_clover.set_xlabel("x[m]")
    ax_clover.set_ylabel("y[m]")
    ax_clover.set_title('Tool head Clover')
    ax_clover.axis('equal')
    ax_clover.set_xlim(0,Bounds.xmax)
    ax_clover.set_ylim(0, Bounds.ymax)

    line_ml_clover, = ax_clover_u.plot([],[], label="u_ml")
    line_mr_clover, = ax_clover_u.plot([],[], label="u_mr")
    ax_clover_u.set_xlabel("t[s]")
    ax_clover_u.set_ylabel("Voltage[V]")
    ax_clover_u.set_ylim(-1.2*c_u_max, 1.2*c_u_max)
    ax_clover_u.set_xlim(c_t_sim[0], c_t_sim[-1])
    ax_clover_u.set_title("Motor Voltages")
    ax_clover_u.legend(loc="upper right")


    step = 5
    def update(frame):
        n = frame * step
        line_path.set_data([x_sim[:n+1], y_sim[:n+1]])
        line_ml.set_data(t_sim[:n+1], u_ml_sim[:n+1])
        line_mr.set_data(t_sim[:n+1], u_mr_sim[:n+1])

        line_clover.set_data([c_x_sim[:n+1], c_y_sim[:n+1]])
        line_ml_clover.set_data(c_t_sim[:n+1], c_u_ml_sim[:n+1])
        line_mr_clover.set_data(c_t_sim[:n+1], c_u_mr_sim[:n+1])
        return line_path, line_ml, line_mr,line_clover, line_ml_clover, line_mr_clover

    frames = len(ellipse_sol.t) // step
    simulation = animation.FuncAnimation(fig, update,frames=frames, interval=40, blit=True)   
    plt.show()

