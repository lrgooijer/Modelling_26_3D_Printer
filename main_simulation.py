import math
import numpy as np
from scipy.integrate import solve_ivp

from q21_fsm import Q21FSM,q0State
from q22_fsm import Q22FSM



def system(t,x,u):
    theta_l, theta_r, dtheta_l, dtheta_r, imotor_l, imotor_r, t_nozzle, u_cn, i_nozzle, s, tau, x_s, y_s = x

    u_ml, u_mr , u_n = u 
    # Motor voltage left, Motor voltage right, Nozzle voltage


    # TODO : Come up with better estimates for these
    #        as these are placeholders

    fric_lx = 0.2 # Bearing friction linear x-direction [Ns/m]
    fric_ly = 0.2 # Bearing friction linear y-direction [Ns/m]
    fric_roll = 0.1 #Bearing friction rolling [Nms/rad]
    r_m = 0.05 # Motor pulley radius [m]
    m = 0.100 # Tool Head mass [kg]
    Jmotor = 0.500 # Motor Rotor inertia [kgm^2]
    Km = 2 # Motor torque / back-EMF constant [Nm/a]
    Lm = 1 # Motor inductance [H]
    R_motor = 4 # Motor resistance [ohm]
    Cap_n = 100 # Nozzle Capacitance [F]
    C_tn = 1200 # Nozzle thermal capacity [J/K]
    R_tn = 1000 # Nozzle thermal Resistance [K/W]
    R_n = 4 # Nozzle resistance [ohm]
    t_env = 20 # Celcius
    L_n = 4 # Nozzle inductance [H]


    Jtot = Jmotor +(1/2)*m*(r_m**2)
    b_plus = fric_roll + ((r_m**2)/4) * (fric_lx + fric_ly) 
    b_min = ((r_m**2)/4) * (fric_lx - fric_ly) 

    dd_theta_l = (-b_plus/Jtot)*dtheta_l + (-b_min/Jtot)*dtheta_r + (Km/Jtot)* imotor_l
    dd_theta_r = (-b_min/Jtot)*dtheta_l + (-b_plus/Jtot)*dtheta_r + (Km/Jtot)*imotor_r
    d_imotor_l = (-Km/Lm)*dtheta_l +(-R_motor/Lm)*imotor_l + (u_ml/Lm)
    d_imotor_r = (-Km/Lm)*dtheta_r +(-R_motor/Lm)*imotor_r + (u_mr/Lm)
    d_t_nozzle = (1/C_tn)*(((u_cn**2)/R_n)-(1/R_tn)*(t_nozzle - t_env))
    d_ucn = (i_nozzle/Cap_n)-(u_cn/(R_n*Cap_n))
    d_i_nozzle = (-u_cn/L_n)+(u_n/L_n)
    d_s = np.sqrt(d_x**2+d_y**2) if q0State else 0.0
    d_tau = 1 if in {q3State, q5State} else 0
    


    