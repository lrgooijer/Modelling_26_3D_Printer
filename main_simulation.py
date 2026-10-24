import math
import numpy as np
from scipy.integrate import solve_ivp

from q21_fsm import Q21FSM
from q22_fsm import Q22FSM



def system(t,x,u):
    theta_l, theta_r, dtheta_l, dtheta_r, imotor_l, imotor_r, t_nozzle, u_cn, i_nozzle, s, tau, x_s, y_s = x

    u_l, u_r , u_n = u