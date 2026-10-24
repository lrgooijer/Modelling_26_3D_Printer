import math
import numpy as np
from scipy.integrate import solve_ivp

from q21_fsm import Q21FSM
from q22_fsm import Q22FSM



def system(t,x,u):
    theta_l, theta_r, dtheta_l, dtheta_r, imotor_l, imotor_r, t_nozzle, u_cn, i_nozzle, s, tau, x_s, y_s = x

    u_l, u_r , u_n = u

    # TODO : Come up with better estimates for these
    #        as these are placeholders

    fric_lx = 0.2 # Bearing friction linear x-direction [Ns/m]
    fric_ly = 0.2 # Bearing friction linear y-direction [Ns/m]
    r_m = 0.05 # Motor pulley radius [m]
    m = 0.100 # Mass of the nozzle body [kg]
    Jmotor = 0.500 # Motor Rotor inertia [kgm^2]
    Km = 2 # Motor torque / back-EMF constant [Nm/a]


    Jtot = Jmotor +(1/2)*m*(r_m**2)

    b_plus = ((r_m**2)/4) * (fric_lx + fric_ly) 


    b_min = ((r_m**2)/4) * (fric_lx - fric_ly) 

    dd_theta_l = (-b_plus/Jtot)*dtheta_l + (-b_min/Jtot)*dtheta_r + (Km/Jtot)* imotor_l
    dd_theta_l = (-b_min/Jtot)*dtheta_l + (-b_plus/Jtot)*dtheta_r + (Km/Jtot)*imotor_r