import math
import numpy as np
from scipy.integrate import solve_ivp

from parameters import Parameters as p, Intial as i, Wipe as w 

from q21_fsm import Q21FSM
from q22_fsm import Q22FSM

fsm_21 = Q21FSM()
q_21 = fsm_21.current_state.value # Current state of the global FSM 2.1

def system(t,x,u,q_21):
    theta_l, theta_r, dtheta_l, dtheta_r, imotor_l, imotor_r, t_nozzle, u_cn, i_nozzle, s, tau, x_s, y_s = x

    u_ml, u_mr , u_n = u 
    # Motor voltage left, Motor voltage right, Nozzle voltage

    Jtot = p.Jmotor +(1/2)*p.m*(p.r_m**2)
    b_plus = p.fric_roll + ((p.r_m**2)/4) * (p.fric_lx + p.fric_ly) 
    b_min = ((p.r_m**2)/4) * (p.fric_lx - p.fric_ly)

    d_x_kin = (p.r_m/2)*(dtheta_l + dtheta_r) # x kinematics
    d_y_kin = (p.r_m/2)*(dtheta_l - dtheta_r) # y kinematics

    dd_theta_l = (-b_plus/Jtot)*dtheta_l + (-b_min/Jtot)*dtheta_r + (p.Km/Jtot)* imotor_l
    dd_theta_r = (-b_min/Jtot)*dtheta_l + (-b_plus/Jtot)*dtheta_r + (p.Km/Jtot)*imotor_r
    d_imotor_l = (-p.Km/p.Lm)*dtheta_l +(-p.R_motor/p.Lm)*imotor_l + (u_ml/p.Lm)
    d_imotor_r = (-p.Km/p.Lm)*dtheta_r +(-p.R_motor/p.Lm)*imotor_r + (u_mr/p.Lm)
    d_t_nozzle = (1/p.C_tn)*(((u_cn**2)/p.R_n)-(1/p.R_tn)*(t_nozzle - p.t_env))
    d_ucn = (i_nozzle/p.Cap_n)-(u_cn/(p.R_n*p.Cap_n))
    d_i_nozzle = (-u_cn/p.L_n)+(u_n/p.L_n)
    d_s = np.sqrt(d_x_kin**2+d_y_kin**2) if q_21 == 0 else 0.0
    d_tau = 1 if q_21 in (3,5) else 0
    d_x_s = 0
    d_y_s = 0

    xdot = np.array([dtheta_l,dtheta_r,dd_theta_l,
                     dd_theta_r,d_imotor_l,d_imotor_r,
                     d_t_nozzle,d_ucn,d_i_nozzle,d_s,d_tau,d_x_s, d_y_s])

    return xdot